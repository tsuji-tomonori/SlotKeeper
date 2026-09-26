"""自分の予約一覧APIを実PostgreSQLで検査する。"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.apis.base import sample_value
from app.apis.exceptions import ApiFunctionError
from app.apis.reservations.list_reservations.samples import (
    LIST_RESERVATIONS_RESPONSE_SAMPLE,
    LIST_RESERVATIONS_STATUS_SAMPLES,
)
from app.integrations.common_errors import ExternalApiError
from tests.app.apis.router_db import RouterDbHarness
from tests.conftest import FixedClock
from tests.helpers import Signer, create_reservation

pytestmark = pytest.mark.db


def test_list_filters_only_own(client: TestClient, signed: Signer, booking: dict[str, str]) -> None:
    """Given 自分と他人の2日分の予約と取消 When 日付・状態で絞込み Then 自分の対象だけ固定順で返す。 [SLOT-AC08] [RULE-07-AC]"""
    later = {**booking, "startAt": "2026-09-27T01:00:00Z", "endAt": "2026-09-27T02:00:00Z"}
    first = create_reservation(client, signed, booking).json()
    second = create_reservation(client, signed, later).json()
    other = create_reservation(
        client,
        signed,
        {**booking, "startAt": "2026-09-26T03:00:00Z", "endAt": "2026-09-26T04:00:00Z"},
        subject="bob",
    ).json()
    client.post(
        "/reservations/" + second["reservationId"] + "/cancel",
        headers=signed(),
        json={"version": 1},
    )

    def ids(query: str) -> list[str]:
        rows = client.get("/reservations?limit=100&" + query, headers=signed()).json()["items"]
        return [r["reservationId"] for r in rows if r["resourceId"] == booking["resourceId"]]

    assert first["reservationId"] in ids("day=2026-09-26&future=false")
    assert other["reservationId"] not in ids("day=2026-09-26&future=false")
    assert second["reservationId"] not in ids("day=2026-09-26&future=false")
    assert ids("day=2026-09-27&status=cancelled&future=false") == [second["reservationId"]]
    assert second["reservationId"] not in ids("future=true")
    assert (
        client.get("/reservations/" + other["reservationId"], headers=signed()).status_code == 403
    )
    assert client.get("/reservations?limit=0", headers=signed()).status_code == 422


def test_reservation_paging_order(
    client: TestClient, signed: Signer, booking: dict[str, str]
) -> None:
    """Given 同じ日の3件の予約 When 継続tokenでページ単位に取得 Then 開始日時とIDの固定順で欠落・重複がない。 [RULE-14-AC]"""
    starts = ["01", "03", "05"]
    created = [
        create_reservation(
            client,
            signed,
            {
                **booking,
                "startAt": f"2026-09-26T{hour}:00:00Z",
                "endAt": f"2026-09-26T{hour}:30:00Z",
            },
            subject="pager",
        ).json()["reservationId"]
        for hour in starts
    ]
    seen: list[str] = []
    token = ""
    while True:
        query = "/reservations?day=2026-09-26&limit=2" + ("&nextToken=" + token if token else "")
        page = client.get(query, headers=signed("pager")).json()
        seen += [
            r["reservationId"] for r in page["items"] if r["resourceId"] == booking["resourceId"]
        ]
        if not page.get("nextToken"):
            break
        token = page["nextToken"]
    assert seen == created
    broken = client.get("/reservations?nextToken=%%%", headers=signed("pager"))
    assert broken.status_code == 422


@pytest.mark.anyio
async def test_list_reservations_router_returns_sample_shaped_response_with_db(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_count_rows: Callable[..., Any],
    router_seed_resource: Callable[..., Any],
    router_seed_reservation: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 利用者固有の予約1件 When 標本queryで一覧取得 Then 標本と同じ形で本人の予約だけを返す。 [SLOT-AC08]"""
    _ = timer
    principal = "list-sample-" + str(uuid4())
    resource = await router_seed_resource(router_db_harness, router_auth_headers("admin", True))
    reservation = await router_seed_reservation(
        router_db_harness, router_auth_headers(principal), resource["resourceId"]
    )
    request = LIST_RESERVATIONS_STATUS_SAMPLES[200]["request"]
    response = await router_db_harness.client.get(
        "/reservations", headers=router_auth_headers(principal), params=request["query"]
    )

    assert response.status_code == 200, response.text
    body = response.json()
    expected = sample_value(LIST_RESERVATIONS_RESPONSE_SAMPLE)
    expected["items"] = [{**expected["items"][0], **reservation}]
    assert body == expected
    where = {"owner_principal_id": principal}
    factory = router_db_harness.session_factory
    assert await router_count_rows(factory, "reservations", where) == 1


@pytest.mark.anyio
async def test_list_reservations_sample_request_emits_router_error_log_to_stdio(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    assert_router_error_log: Callable[..., Any],
) -> None:
    """Given 標本requestと処理中の業務例外 When 予約一覧取得 Then Router例外の運用ログをcatalogどおり出す。 [COM-07-AC]"""
    await assert_router_error_log(
        router_db_harness=router_db_harness,
        capsys=capsys,
        monkeypatch=monkeypatch,
        method="GET",
        path_template="/reservations",
        status_samples=LIST_RESERVATIONS_STATUS_SAMPLES,
        success_status=200,
        patch_target="app.apis.reservations.list_reservations.functions.get_own_reservations",
        message_id="listReservations.router_api_function_error",
        catalog_id="M001",
        headers=router_auth_headers("alice"),
    )


# unit-test_gen.md executable cases
@pytest.mark.anyio
async def test_tc001_list_reservations_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    timer: FixedClock,
) -> None:
    """Given 予約のない利用者 When 一覧取得 Then 200で空の一覧を返す。 [SLOT-AC08]"""
    _ = timer
    response = await router_db_harness.client.get(
        "/reservations", headers=router_auth_headers("empty-" + str(uuid4()))
    )

    assert response.status_code == 200, response.text
    assert response.json() == {"items": [], "nextToken": None}


@pytest.mark.anyio
async def test_tc002_list_reservations_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 予約一覧の取得で業務例外 When API呼出し Then Routerで500へ変換し運用ログを出す。"""
    _ = timer

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise ApiFunctionError(500, "forced router error", summary="unit-test_gen case")

    monkeypatch.setattr(
        "app.apis.reservations.list_reservations.functions.get_own_reservations",
        raise_expected_error,
    )
    headers = router_auth_headers("alice")
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.get("/reservations", headers=headers)

    assert response.status_code == 500, response.text
    assert response.json()["error"]["details"][0]["reason"] == "forced router error"
    actual_log_event = find_log_event("listReservations.router_api_function_error")
    assert actual_log_event["messageId"] == "listReservations.router_api_function_error"
    assert (
        actual_log_event["summary"]
        == "Routerで捕捉したApiFunctionErrorにより予約一覧取得が失敗した。"
    )


@pytest.mark.anyio
async def test_tc003_list_reservations_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 予約一覧の取得で外部API例外 When API呼出し Then Routerで502へ変換し運用ログを出す。"""
    _ = timer

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise ExternalApiError("forced external api error")

    monkeypatch.setattr(
        "app.apis.reservations.list_reservations.functions.get_own_reservations",
        raise_expected_error,
    )
    headers = router_auth_headers("alice")
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.get("/reservations", headers=headers)

    assert response.status_code == 502, response.text
    assert response.json()["error"]["details"][0]["reason"] == "external service request failed"
    actual_log_event = find_log_event("listReservations.router_external_api_error")
    assert actual_log_event["messageId"] == "listReservations.router_external_api_error"
    assert (
        actual_log_event["summary"]
        == "Routerで捕捉したExternalApiErrorにより予約一覧取得が失敗した。"
    )


@pytest.mark.anyio
async def test_tc004_list_reservations_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 予約一覧の取得でHTTP例外 When API呼出し Then Routerで400へ変換し運用ログを出す。"""
    _ = timer

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise HTTPException(status_code=400, detail="forced http exception")

    monkeypatch.setattr(
        "app.apis.reservations.list_reservations.functions.get_own_reservations",
        raise_expected_error,
    )
    headers = router_auth_headers("alice")
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.get("/reservations", headers=headers)

    assert response.status_code == 400, response.text
    assert response.json()["error"]["details"][0]["reason"] == "forced http exception"
    actual_log_event = find_log_event("listReservations.router_http_exception")
    assert actual_log_event["messageId"] == "listReservations.router_http_exception"
    assert (
        actual_log_event["summary"] == "Routerで捕捉したHTTPExceptionにより予約一覧取得が失敗した。"
    )
