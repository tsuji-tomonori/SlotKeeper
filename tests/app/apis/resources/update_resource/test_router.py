"""資源編集APIを実PostgreSQLの独立transactionで検査する。"""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from typing import Any
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.apis.base import sample_value
from app.apis.exceptions import ApiFunctionError
from app.apis.reservations.common import ReservationStatus
from app.apis.resources.common import ResourceKind
from app.apis.resources.update_resource.samples import (
    UPDATE_RESOURCE_REQUEST_SAMPLE,
    UPDATE_RESOURCE_RESPONSE_SAMPLE,
    UPDATE_RESOURCE_STATUS_SAMPLES,
)
from app.integrations.common_errors import ExternalApiError
from tests.app.apis.router_db import RouterDbHarness
from tests.conftest import FixedClock
from tests.helpers import Signer, create_reservation, error_reason

pytestmark = pytest.mark.db


def edit_payload(resource: dict[str, Any], **changes: object) -> dict[str, Any]:
    payload = {k: resource[k] for k in ["name", "description", "kind", "active", "version"]}
    return {**payload, **changes}


def test_versions_and_inactive(
    client: TestClient, signed: Signer, booking: dict[str, str], resource: dict[str, Any]
) -> None:
    """Given 古い資源版と無効資源 When 更新と作成 Then 409で先行更新維持。 [SLOT-AC05] [SLOT-AC11]"""
    url = "/resources/" + resource["resourceId"]
    admin = signed("manager", True)
    assert (
        client.put(url, headers=admin, json=edit_payload(resource, active=False)).status_code == 200
    )
    stale = client.put(url, headers=admin, json=edit_payload(resource))
    assert stale.status_code == 409 and error_reason(stale) == "stale_version"
    inactive = create_reservation(client, signed, booking)
    assert inactive.status_code == 409 and error_reason(inactive) == "resource_inactive"


def test_future_prevents_disable(
    client: TestClient, signed: Signer, booking: dict[str, str], resource: dict[str, Any]
) -> None:
    """Given 将来の確定予約 When 無効化 Then 409。 [SLOT-AC05] [RULE-08-AC]"""
    assert create_reservation(client, signed, booking).status_code == 201
    response = client.put(
        "/resources/" + resource["resourceId"],
        headers=signed("manager", True),
        json=edit_payload(resource, active=False),
    )
    assert response.status_code == 409
    assert error_reason(response) == "future_reservations_exist"


def test_create_vs_disable(
    client: TestClient, signed: Signer, booking: dict[str, str], resource: dict[str, Any]
) -> None:
    """Given 有効資源 When 予約作成と無効化を競合 Then 両方成功しない。 [SLOT-AC10] [RULE-08-AC]"""
    barrier = Barrier(2)

    def reserve() -> Any:
        barrier.wait()
        return create_reservation(client, signed, booking)

    def disable() -> Any:
        barrier.wait()
        return client.put(
            "/resources/" + resource["resourceId"],
            headers=signed("manager", True),
            json=edit_payload(resource, active=False),
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        reserved = pool.submit(reserve)
        disabled = pool.submit(disable)
        results = [reserved.result().status_code, disabled.result().status_code]
    assert results in ([201, 409], [409, 200])


def test_disable_after_start_keeps_record(
    client: TestClient,
    signed: Signer,
    booking: dict[str, str],
    resource: dict[str, Any],
    timer: FixedClock,
) -> None:
    """Given 開始済みの確定予約 When 資源を無効化 Then 無効化でき既存記録を保持し新規予約は拒否する。 [RULE-07-AC]"""
    reservation = create_reservation(client, signed, booking).json()
    timer.value = timer.value.replace(day=26, hour=1, minute=30)
    response = client.put(
        "/resources/" + resource["resourceId"],
        headers=signed("manager", True),
        json=edit_payload(resource, active=False),
    )
    assert response.status_code == 200, response.text
    kept = client.get("/reservations/" + reservation["reservationId"], headers=signed()).json()
    assert kept["reservation"]["status"] == ReservationStatus.CONFIRMED
    later = {**booking, "startAt": "2026-09-26T05:00:00Z", "endAt": "2026-09-26T06:00:00Z"}
    assert create_reservation(client, signed, later).status_code == 409
    future = client.get("/reservations?future=true&limit=100", headers=signed()).json()["items"]
    assert all(r["resourceId"] != resource["resourceId"] for r in future)


def test_missing_resource_returns_404(client: TestClient, signed: Signer, database: None) -> None:
    """Given 存在しない資源 When 編集 Then 404で区別する。 [COM-03-AC]"""
    edit = {
        "name": "なし",
        "description": "",
        "kind": ResourceKind.ROOM,
        "active": True,
        "version": 1,
    }
    response = client.put("/resources/" + str(uuid4()), headers=signed("manager", True), json=edit)
    assert response.status_code == 404
    assert error_reason(response) == "resource_not_found"


@pytest.mark.anyio
async def test_update_resource_router_returns_sample_shaped_response_with_db(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_fetch_one: Callable[..., Any],
    router_seed_resource: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 版1の資源 When 標本requestで編集 Then 標本と同じ形で版2の資源を返し保存する。 [SLOT-01-AC] [SLOT-AC11]"""
    _ = timer
    resource = await router_seed_resource(router_db_harness, router_auth_headers("manager", True))
    response = await router_db_harness.client.put(
        "/resources/" + resource["resourceId"],
        headers=router_auth_headers("manager", True),
        json=sample_value(UPDATE_RESOURCE_REQUEST_SAMPLE),
    )

    assert response.status_code == 200, response.text
    body = response.json()
    expected = sample_value(UPDATE_RESOURCE_RESPONSE_SAMPLE)
    expected["resourceId"] = resource["resourceId"]
    assert body == expected
    row = await router_fetch_one(
        router_db_harness.session_factory, "resources", {"resource_id": resource["resourceId"]}
    )
    assert row is not None and row["row_version"] == 2 and row["control_version"] == 1


@pytest.mark.anyio
async def test_update_resource_sample_request_emits_router_error_log_to_stdio(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    assert_router_error_log: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 標本requestと処理中の業務例外 When 資源編集 Then Router例外の運用ログをcatalogどおり出す。 [COM-07-AC]"""
    _ = timer
    await assert_router_error_log(
        router_db_harness=router_db_harness,
        capsys=capsys,
        monkeypatch=monkeypatch,
        method="PUT",
        path_template="/resources/{resourceId}",
        status_samples=UPDATE_RESOURCE_STATUS_SAMPLES,
        success_status=200,
        patch_target=(
            "app.apis.resources.update_resource.functions.update_resource_control_version"
        ),
        message_id="updateResource.router_api_function_error",
        catalog_id="M004",
        headers=router_auth_headers("manager", True),
    )


# unit-test_gen.md executable cases
@pytest.mark.anyio
async def test_tc001_update_resource_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_seed_resource: Callable[..., Any],
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 一般利用者 When 資源編集 Then 403で運用ログを出す。 [SLOT-01-AC] [COM-04-AC]"""
    _ = timer
    resource = await router_seed_resource(router_db_harness, router_auth_headers("manager", True))
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.put(
            "/resources/" + resource["resourceId"],
            headers=router_auth_headers("alice"),
            json=sample_value(UPDATE_RESOURCE_REQUEST_SAMPLE),
        )

    assert response.status_code == 403, response.text
    assert response.json()["error"]["details"][0]["reason"] == "forbidden"
    actual_log_event = find_log_event("updateResource.caller_cannot_manage_resources")
    assert actual_log_event["messageId"] == "updateResource.caller_cannot_manage_resources"
    assert actual_log_event["summary"] == "呼び出し元が管理者ではないため、資源編集を拒否した。"


@pytest.mark.anyio
async def test_tc002_update_resource_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_seed_resource: Callable[..., Any],
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 版1の資源 When 版2を指定して編集 Then 409で運用ログを出す。 [SLOT-AC11]"""
    _ = timer
    resource = await router_seed_resource(router_db_harness, router_auth_headers("manager", True))
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.put(
            "/resources/" + resource["resourceId"],
            headers=router_auth_headers("manager", True),
            json={**sample_value(UPDATE_RESOURCE_REQUEST_SAMPLE), "version": 2},
        )

    assert response.status_code == 409, response.text
    assert response.json()["error"]["details"][0]["reason"] == "stale_version"
    actual_log_event = find_log_event("updateResource.stale_resource_version")
    assert actual_log_event["messageId"] == "updateResource.stale_resource_version"
    assert (
        actual_log_event["summary"] == "資源の公開版が現在値と一致しないため、資源編集を拒否した。"
    )


@pytest.mark.anyio
async def test_tc003_update_resource_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_seed_resource: Callable[..., Any],
    router_seed_reservation: Callable[..., Any],
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 将来予約のある資源 When 無効化 Then 409で運用ログを出す。 [SLOT-AC05] [RULE-08-AC]"""
    _ = timer
    resource = await router_seed_resource(router_db_harness, router_auth_headers("manager", True))
    await router_seed_reservation(
        router_db_harness, router_auth_headers("alice"), resource["resourceId"]
    )
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.put(
            "/resources/" + resource["resourceId"],
            headers=router_auth_headers("manager", True),
            json={**sample_value(UPDATE_RESOURCE_REQUEST_SAMPLE), "active": False},
        )

    assert response.status_code == 409, response.text
    assert response.json()["error"]["details"][0]["reason"] == "future_reservations_exist"
    actual_log_event = find_log_event("updateResource.future_reservations_exist")
    assert actual_log_event["messageId"] == "updateResource.future_reservations_exist"
    assert (
        actual_log_event["summary"] == "開始前の確定予約が残っているため、資源の無効化を拒否した。"
    )


@pytest.mark.anyio
async def test_tc004_update_resource_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_seed_resource: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 将来予約のない資源 When 無効化 Then 200で無効な資源を返す。 [SLOT-01-AC]"""
    _ = timer
    resource = await router_seed_resource(router_db_harness, router_auth_headers("manager", True))
    response = await router_db_harness.client.put(
        "/resources/" + resource["resourceId"],
        headers=router_auth_headers("manager", True),
        json={**sample_value(UPDATE_RESOURCE_REQUEST_SAMPLE), "active": False},
    )

    assert response.status_code == 200, response.text
    assert response.json()["active"] is False


@pytest.mark.anyio
async def test_tc005_update_resource_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 資源編集の制御版更新で業務例外 When API呼出し Then Routerで500へ変換し運用ログを出す。"""
    _ = timer

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise ApiFunctionError(500, "forced router error", summary="unit-test_gen case")

    monkeypatch.setattr(
        "app.apis.resources.update_resource.functions.update_resource_control_version",
        raise_expected_error,
    )
    headers = router_auth_headers("manager", True)
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.put(
            "/resources/" + str(uuid4()),
            headers=headers,
            json=sample_value(UPDATE_RESOURCE_REQUEST_SAMPLE),
        )

    assert response.status_code == 500, response.text
    assert response.json()["error"]["details"][0]["reason"] == "forced router error"
    actual_log_event = find_log_event("updateResource.router_api_function_error")
    assert actual_log_event["messageId"] == "updateResource.router_api_function_error"
    assert (
        actual_log_event["summary"] == "Routerで捕捉したApiFunctionErrorにより資源編集が失敗した。"
    )


@pytest.mark.anyio
async def test_tc006_update_resource_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 資源編集の制御版更新で外部API例外 When API呼出し Then Routerで502へ変換し運用ログを出す。"""
    _ = timer

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise ExternalApiError("forced external api error")

    monkeypatch.setattr(
        "app.apis.resources.update_resource.functions.update_resource_control_version",
        raise_expected_error,
    )
    headers = router_auth_headers("manager", True)
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.put(
            "/resources/" + str(uuid4()),
            headers=headers,
            json=sample_value(UPDATE_RESOURCE_REQUEST_SAMPLE),
        )

    assert response.status_code == 502, response.text
    assert response.json()["error"]["details"][0]["reason"] == "external service request failed"
    actual_log_event = find_log_event("updateResource.router_external_api_error")
    assert actual_log_event["messageId"] == "updateResource.router_external_api_error"
    assert (
        actual_log_event["summary"] == "Routerで捕捉したExternalApiErrorにより資源編集が失敗した。"
    )


@pytest.mark.anyio
async def test_tc007_update_resource_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 資源編集の制御版更新でHTTP例外 When API呼出し Then Routerで400へ変換し運用ログを出す。"""
    _ = timer

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise HTTPException(status_code=400, detail="forced http exception")

    monkeypatch.setattr(
        "app.apis.resources.update_resource.functions.update_resource_control_version",
        raise_expected_error,
    )
    headers = router_auth_headers("manager", True)
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.put(
            "/resources/" + str(uuid4()),
            headers=headers,
            json=sample_value(UPDATE_RESOURCE_REQUEST_SAMPLE),
        )

    assert response.status_code == 400, response.text
    assert response.json()["error"]["details"][0]["reason"] == "forced http exception"
    actual_log_event = find_log_event("updateResource.router_http_exception")
    assert actual_log_event["messageId"] == "updateResource.router_http_exception"
    assert actual_log_event["summary"] == "Routerで捕捉したHTTPExceptionにより資源編集が失敗した。"
