"""予約表APIを実PostgreSQLで検査する。"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.apis.exceptions import ApiFunctionError
from app.apis.resources.get_resource_schedule.samples import (
    GET_RESOURCE_SCHEDULE_RESPONSE_SAMPLE,
    GET_RESOURCE_SCHEDULE_STATUS_SAMPLES,
)
from app.integrations.common_errors import ExternalApiError
from tests.app.apis.router_db import RouterDbHarness
from tests.conftest import FixedClock
from tests.helpers import Signer, create_reservation, error_reason

pytestmark = pytest.mark.db


def test_schedule_hides_other_details(
    client: TestClient, signed: Signer, booking: dict[str, str], resource: dict[str, Any]
) -> None:
    """Given Aの予約 When A・B・管理者が予約表を取得 Then Bには時間帯と予約済みだけを返す。 [SLOT-02-AC] [RULE-09-AC]"""
    create_reservation(client, signed, booking)
    url = "/resources/" + resource["resourceId"] + "/schedule?day=2026-09-26"
    others = client.get(url, headers=signed("bob")).json()["items"]
    assert [set(row) for row in others] == [{"startAt", "endAt", "label"}]
    assert others[0]["label"] == "予約済み"
    own = client.get(url, headers=signed()).json()["items"]
    assert own[0]["reservation"]["purpose"] == booking["purpose"]
    admin = client.get(url, headers=signed("admin", True)).json()["items"]
    assert admin[0]["reservation"]["ownerPrincipalId"] == "alice"


def test_missing_resource_returns_404(client: TestClient, signed: Signer, database: None) -> None:
    """Given 存在しない資源 When 予約表取得 Then 404で区別する。 [COM-03-AC]"""
    response = client.get(
        "/resources/" + str(uuid4()) + "/schedule?day=2026-09-26", headers=signed()
    )
    assert response.status_code == 404
    assert error_reason(response) == "resource_not_found"


@pytest.mark.anyio
async def test_get_resource_schedule_router_returns_sample_shaped_response_with_db(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_count_rows: Callable[..., Any],
    router_seed_resource: Callable[..., Any],
    router_seed_reservation: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given aliceとbobの予約 When aliceが標本queryで予約表取得 Then 標本と同じ形で自分の詳細だけを返す。 [SLOT-02-AC] [RULE-09-AC]"""
    _ = timer
    resource = await router_seed_resource(router_db_harness, router_auth_headers("admin", True))
    own = await router_seed_reservation(
        router_db_harness, router_auth_headers("alice"), resource["resourceId"]
    )
    await router_seed_reservation(
        router_db_harness,
        router_auth_headers("bob"),
        resource["resourceId"],
        start_at="2026-09-26T04:00:00Z",
        end_at="2026-09-26T05:00:00Z",
    )
    request = GET_RESOURCE_SCHEDULE_STATUS_SAMPLES[200]["request"]
    response = await router_db_harness.client.get(
        "/resources/" + resource["resourceId"] + "/schedule",
        headers=router_auth_headers("alice"),
        params=request["query"],
    )

    assert response.status_code == 200, response.text
    body = response.json()
    # response_model_exclude_none=True と同じくNoneの項目を除いて比較する。
    expected = GET_RESOURCE_SCHEDULE_RESPONSE_SAMPLE.model_dump(
        by_alias=True, mode="json", exclude_none=True
    )
    expected["items"][0]["reservation"] = {**expected["items"][0]["reservation"], **own}
    assert body == expected
    where = {"resource_id": resource["resourceId"]}
    factory = router_db_harness.session_factory
    assert await router_count_rows(factory, "reservations", where) == 2


@pytest.mark.anyio
async def test_get_resource_schedule_sample_request_emits_router_error_log_to_stdio(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    assert_router_error_log: Callable[..., Any],
) -> None:
    """Given 標本requestと処理中の業務例外 When 予約表取得 Then Router例外の運用ログをcatalogどおり出す。 [COM-07-AC]"""
    await assert_router_error_log(
        router_db_harness=router_db_harness,
        capsys=capsys,
        monkeypatch=monkeypatch,
        method="GET",
        path_template="/resources/{resourceId}/schedule",
        status_samples=GET_RESOURCE_SCHEDULE_STATUS_SAMPLES,
        success_status=200,
        patch_target="app.apis.resources.get_resource_schedule.functions.get_resource",
        message_id="getResourceSchedule.router_api_function_error",
        catalog_id="M001",
        headers=router_auth_headers("alice"),
    )


# unit-test_gen.md executable cases
@pytest.mark.anyio
async def test_tc001_get_resource_schedule_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_seed_resource: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 予約のない資源 When 予約表取得 Then 200で空の予約表を返す。 [SLOT-02-AC]"""
    _ = timer
    resource = await router_seed_resource(router_db_harness, router_auth_headers("admin", True))
    response = await router_db_harness.client.get(
        "/resources/" + resource["resourceId"] + "/schedule",
        headers=router_auth_headers("alice"),
        params={"day": "2026-09-26"},
    )

    assert response.status_code == 200, response.text
    assert response.json() == {"items": []}


@pytest.mark.anyio
async def test_tc002_get_resource_schedule_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 予約表の資源取得で業務例外 When API呼出し Then Routerで500へ変換し運用ログを出す。"""
    _ = timer

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise ApiFunctionError(500, "forced router error", summary="unit-test_gen case")

    monkeypatch.setattr(
        "app.apis.resources.get_resource_schedule.functions.get_resource",
        raise_expected_error,
    )
    headers = router_auth_headers("alice")
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.get(
            "/resources/" + str(uuid4()) + "/schedule",
            headers=headers,
            params={"day": "2026-09-26"},
        )

    assert response.status_code == 500, response.text
    assert response.json()["error"]["details"][0]["reason"] == "forced router error"
    actual_log_event = find_log_event("getResourceSchedule.router_api_function_error")
    assert actual_log_event["messageId"] == "getResourceSchedule.router_api_function_error"
    assert (
        actual_log_event["summary"]
        == "Routerで捕捉したApiFunctionErrorにより予約表取得が失敗した。"
    )


@pytest.mark.anyio
async def test_tc003_get_resource_schedule_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 予約表の資源取得で外部API例外 When API呼出し Then Routerで502へ変換し運用ログを出す。"""
    _ = timer

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise ExternalApiError("forced external api error")

    monkeypatch.setattr(
        "app.apis.resources.get_resource_schedule.functions.get_resource",
        raise_expected_error,
    )
    headers = router_auth_headers("alice")
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.get(
            "/resources/" + str(uuid4()) + "/schedule",
            headers=headers,
            params={"day": "2026-09-26"},
        )

    assert response.status_code == 502, response.text
    assert response.json()["error"]["details"][0]["reason"] == "external service request failed"
    actual_log_event = find_log_event("getResourceSchedule.router_external_api_error")
    assert actual_log_event["messageId"] == "getResourceSchedule.router_external_api_error"
    assert (
        actual_log_event["summary"]
        == "Routerで捕捉したExternalApiErrorにより予約表取得が失敗した。"
    )


@pytest.mark.anyio
async def test_tc004_get_resource_schedule_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 予約表の資源取得でHTTP例外 When API呼出し Then Routerで400へ変換し運用ログを出す。"""
    _ = timer

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise HTTPException(status_code=400, detail="forced http exception")

    monkeypatch.setattr(
        "app.apis.resources.get_resource_schedule.functions.get_resource",
        raise_expected_error,
    )
    headers = router_auth_headers("alice")
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.get(
            "/resources/" + str(uuid4()) + "/schedule",
            headers=headers,
            params={"day": "2026-09-26"},
        )

    assert response.status_code == 400, response.text
    assert response.json()["error"]["details"][0]["reason"] == "forced http exception"
    actual_log_event = find_log_event("getResourceSchedule.router_http_exception")
    assert actual_log_event["messageId"] == "getResourceSchedule.router_http_exception"
    assert (
        actual_log_event["summary"] == "Routerで捕捉したHTTPExceptionにより予約表取得が失敗した。"
    )
