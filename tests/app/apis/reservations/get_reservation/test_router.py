"""予約詳細APIを実PostgreSQLで検査する。"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.apis.base import sample_value
from app.apis.exceptions import ApiFunctionError
from app.apis.reservations.common import ReservationAction
from app.apis.reservations.get_reservation.samples import (
    GET_RESERVATION_RESPONSE_SAMPLE,
    GET_RESERVATION_STATUS_SAMPLES,
)
from app.integrations.common_errors import ExternalApiError
from tests.app.apis.router_db import RouterDbHarness
from tests.conftest import FixedClock
from tests.helpers import Signer, create_reservation, error_reason

pytestmark = pytest.mark.db


def test_owner_and_admin_view_history(
    client: TestClient, signed: Signer, booking: dict[str, str]
) -> None:
    """Given Aの予約 When 本人・管理者・他人が詳細取得 Then 本人と管理者は履歴を閲覧し他人は403。 [SLOT-07-AC] [RULE-09-AC] [COM-04-AC]"""
    reservation_id = create_reservation(client, signed, booking).json()["reservationId"]
    own = client.get("/reservations/" + reservation_id, headers=signed())
    assert own.status_code == 200
    assert [e["action"] for e in own.json()["events"]] == [ReservationAction.CREATED]
    admin = client.get("/reservations/" + reservation_id, headers=signed("manager", True))
    assert admin.json()["reservation"]["purpose"] == booking["purpose"]
    other = client.get("/reservations/" + reservation_id, headers=signed("bob"))
    assert other.status_code == 403
    assert booking["purpose"] not in other.text


def test_missing_reservation_returns_404(
    client: TestClient, signed: Signer, database: None
) -> None:
    """Given 存在しない予約 When 詳細取得 Then 404で区別する。 [COM-03-AC]"""
    response = client.get("/reservations/" + str(uuid4()), headers=signed())
    assert response.status_code == 404
    assert error_reason(response) == "reservation_not_found"


@pytest.mark.anyio
async def test_get_reservation_router_returns_sample_shaped_response_with_db(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_count_rows: Callable[..., Any],
    router_seed_resource: Callable[..., Any],
    router_seed_reservation: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given aliceの予約 When 本人が詳細取得 Then 標本と同じ形で予約と作成履歴を返す。 [SLOT-07-AC]"""
    _ = timer
    resource = await router_seed_resource(router_db_harness, router_auth_headers("manager", True))
    reservation = await router_seed_reservation(
        router_db_harness, router_auth_headers("alice"), resource["resourceId"]
    )
    response = await router_db_harness.client.get(
        "/reservations/" + reservation["reservationId"], headers=router_auth_headers("alice")
    )

    assert response.status_code == 200, response.text
    body = response.json()
    expected = sample_value(GET_RESERVATION_RESPONSE_SAMPLE)
    expected["reservation"] = {**expected["reservation"], **reservation}
    expected["events"][0]["eventId"] = body["events"][0]["eventId"]
    expected["events"][0]["reservationId"] = reservation["reservationId"]
    assert body == expected
    where = {"reservation_id": reservation["reservationId"]}
    factory = router_db_harness.session_factory
    assert await router_count_rows(factory, "reservation_events", where) == 1


@pytest.mark.anyio
async def test_get_reservation_sample_request_emits_router_error_log_to_stdio(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    assert_router_error_log: Callable[..., Any],
) -> None:
    """Given 標本requestと処理中の業務例外 When 予約詳細取得 Then Router例外の運用ログをcatalogどおり出す。 [COM-07-AC]"""
    await assert_router_error_log(
        router_db_harness=router_db_harness,
        capsys=capsys,
        monkeypatch=monkeypatch,
        method="GET",
        path_template="/reservations/{reservationId}",
        status_samples=GET_RESERVATION_STATUS_SAMPLES,
        success_status=200,
        patch_target="app.apis.reservations.get_reservation.functions.get_reservation",
        message_id="getReservation.router_api_function_error",
        catalog_id="M002",
        headers=router_auth_headers("alice"),
    )


# unit-test_gen.md executable cases
@pytest.mark.anyio
async def test_tc001_get_reservation_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_seed_resource: Callable[..., Any],
    router_seed_reservation: Callable[..., Any],
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given aliceの予約 When bobが詳細取得 Then 403で運用ログを出す。 [SLOT-07-AC] [COM-04-AC]"""
    _ = timer
    resource = await router_seed_resource(router_db_harness, router_auth_headers("manager", True))
    reservation = await router_seed_reservation(
        router_db_harness, router_auth_headers("alice"), resource["resourceId"]
    )
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.get(
            "/reservations/" + reservation["reservationId"], headers=router_auth_headers("bob")
        )

    assert response.status_code == 403, response.text
    assert response.json()["error"]["details"][0]["reason"] == "forbidden"
    actual_log_event = find_log_event("getReservation.caller_cannot_view_reservation")
    assert actual_log_event["messageId"] == "getReservation.caller_cannot_view_reservation"
    assert (
        actual_log_event["summary"]
        == "呼び出し元が予約者本人でも管理者でもないため、予約詳細の参照を拒否した。"
    )


@pytest.mark.anyio
async def test_tc002_get_reservation_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_seed_resource: Callable[..., Any],
    router_seed_reservation: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given aliceの予約 When 管理者が詳細取得 Then 200で目的を含む詳細を返す。 [SLOT-07-AC] [RULE-09-AC]"""
    _ = timer
    resource = await router_seed_resource(router_db_harness, router_auth_headers("manager", True))
    reservation = await router_seed_reservation(
        router_db_harness, router_auth_headers("alice"), resource["resourceId"]
    )
    response = await router_db_harness.client.get(
        "/reservations/" + reservation["reservationId"],
        headers=router_auth_headers("manager", True),
    )

    assert response.status_code == 200, response.text
    assert response.json()["reservation"]["purpose"] == "router試験"


@pytest.mark.anyio
async def test_tc003_get_reservation_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 予約詳細の取得で業務例外 When API呼出し Then Routerで500へ変換し運用ログを出す。"""
    _ = timer

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise ApiFunctionError(500, "forced router error", summary="unit-test_gen case")

    monkeypatch.setattr(
        "app.apis.reservations.get_reservation.functions.get_reservation",
        raise_expected_error,
    )
    headers = router_auth_headers("alice")
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.get(
            "/reservations/" + str(uuid4()), headers=headers
        )

    assert response.status_code == 500, response.text
    assert response.json()["error"]["details"][0]["reason"] == "forced router error"
    actual_log_event = find_log_event("getReservation.router_api_function_error")
    assert actual_log_event["messageId"] == "getReservation.router_api_function_error"
    assert (
        actual_log_event["summary"]
        == "Routerで捕捉したApiFunctionErrorにより予約詳細取得が失敗した。"
    )


@pytest.mark.anyio
async def test_tc004_get_reservation_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 予約詳細の取得で外部API例外 When API呼出し Then Routerで502へ変換し運用ログを出す。"""
    _ = timer

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise ExternalApiError("forced external api error")

    monkeypatch.setattr(
        "app.apis.reservations.get_reservation.functions.get_reservation",
        raise_expected_error,
    )
    headers = router_auth_headers("alice")
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.get(
            "/reservations/" + str(uuid4()), headers=headers
        )

    assert response.status_code == 502, response.text
    assert response.json()["error"]["details"][0]["reason"] == "external service request failed"
    actual_log_event = find_log_event("getReservation.router_external_api_error")
    assert actual_log_event["messageId"] == "getReservation.router_external_api_error"
    assert (
        actual_log_event["summary"]
        == "Routerで捕捉したExternalApiErrorにより予約詳細取得が失敗した。"
    )


@pytest.mark.anyio
async def test_tc005_get_reservation_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 予約詳細の取得でHTTP例外 When API呼出し Then Routerで400へ変換し運用ログを出す。"""
    _ = timer

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise HTTPException(status_code=400, detail="forced http exception")

    monkeypatch.setattr(
        "app.apis.reservations.get_reservation.functions.get_reservation",
        raise_expected_error,
    )
    headers = router_auth_headers("alice")
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.get(
            "/reservations/" + str(uuid4()), headers=headers
        )

    assert response.status_code == 400, response.text
    assert response.json()["error"]["details"][0]["reason"] == "forced http exception"
    actual_log_event = find_log_event("getReservation.router_http_exception")
    assert actual_log_event["messageId"] == "getReservation.router_http_exception"
    assert (
        actual_log_event["summary"] == "Routerで捕捉したHTTPExceptionにより予約詳細取得が失敗した。"
    )
