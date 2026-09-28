"""予約取消APIを実PostgreSQLの独立transactionで検査する。"""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from typing import Any
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.apis.base import sample_value
from app.apis.exceptions import ApiFunctionError
from app.apis.reservations.cancel_reservation.samples import (
    CANCEL_RESERVATION_REQUEST_SAMPLE,
    CANCEL_RESERVATION_RESPONSE_SAMPLE,
    CANCEL_RESERVATION_STATUS_SAMPLES,
)
from app.apis.reservations.common import ReservationAction, ReservationStatus
from app.integrations.common_errors import ExternalApiError
from tests.app.apis.router_db import RouterDbHarness
from tests.conftest import FixedClock
from tests.helpers import Signer, create_reservation, db_connect, error_reason

pytestmark = pytest.mark.db


def cancel(client: TestClient, headers: dict[str, str], reservation_id: str, version: int) -> Any:
    return client.post(
        "/reservations/" + reservation_id + "/cancel", headers=headers, json={"version": version}
    )


def test_privacy_and_cancel(
    client: TestClient, signed: Signer, booking: dict[str, str], resource: dict[str, Any]
) -> None:
    """Given Aの予約 When B・Aが詳細取得と取消 Then Bは403で情報非公開、Aは取消。 [SLOT-AC04] [SLOT-AC08] [SLOT-02-AC] [RULE-09-AC] [RULE-13-AC] [RULE-06-AC] [COM-04-AC]"""
    reservation_id = create_reservation(client, signed, booking).json()["reservationId"]
    assert client.get("/reservations/" + reservation_id, headers=signed("bob")).status_code == 403
    assert cancel(client, signed("bob"), reservation_id, 1).status_code == 403
    schedule = client.get(
        "/resources/" + resource["resourceId"] + "/schedule?day=2026-09-26",
        headers=signed("bob"),
    ).json()["items"]
    assert all(set(row) == {"startAt", "endAt", "label"} for row in schedule)
    response = cancel(client, signed(), reservation_id, 1)
    assert response.json()["status"] == ReservationStatus.CANCELLED
    assert (
        len(client.get("/reservations/" + reservation_id, headers=signed()).json()["events"]) == 2
    )
    again = cancel(client, signed(), reservation_id, 2)
    assert again.status_code == 409
    assert error_reason(again) == "already_cancelled"
    assert create_reservation(client, signed, booking).status_code == 201


def test_cancel_boundaries(
    client: TestClient, signed: Signer, booking: dict[str, str], timer: FixedClock
) -> None:
    """Given 確定予約 When 古い版と開始時刻ちょうどの取消 Then 409、履歴1件。 [SLOT-AC11] [SLOT-AC13] [RULE-13-AC]"""
    reservation_id = create_reservation(client, signed, booking).json()["reservationId"]
    stale = cancel(client, signed(), reservation_id, 2)
    assert stale.status_code == 409 and error_reason(stale) == "stale_version"
    timer.value += timedelta(days=1, hours=1)
    started = cancel(client, signed(), reservation_id, 1)
    assert started.status_code == 409 and error_reason(started) == "already_started"
    assert (
        len(client.get("/reservations/" + reservation_id, headers=signed()).json()["events"]) == 1
    )


def test_admin_cancels_other_before_start(
    client: TestClient, signed: Signer, booking: dict[str, str], timer: FixedClock
) -> None:
    """Given Aの開始前予約 When 管理者が取消 Then 取消と履歴2件、開始後は管理者も拒否。 [SLOT-AC04] [SLOT-07-AC] [RULE-09-AC]"""
    reservation_id = create_reservation(client, signed, booking).json()["reservationId"]
    admin = signed("manager", True)
    detail = client.get("/reservations/" + reservation_id, headers=admin)
    assert detail.status_code == 200
    assert detail.json()["reservation"]["purpose"] == booking["purpose"]
    timer.value += timedelta(minutes=5)
    assert cancel(client, admin, reservation_id, 1).status_code == 200
    events = client.get("/reservations/" + reservation_id, headers=signed()).json()["events"]
    assert [e["action"] for e in events] == [ReservationAction.CREATED, ReservationAction.CANCELLED]
    started = create_reservation(
        client,
        signed,
        {**booking, "startAt": "2026-09-26T05:00:00Z", "endAt": "2026-09-26T06:00:00Z"},
    ).json()
    timer.value = timer.value.replace(day=26, hour=5)
    assert cancel(client, admin, started["reservationId"], 1).status_code == 409


def test_cancel_and_rebook_concurrent(
    client: TestClient, signed: Signer, booking: dict[str, str]
) -> None:
    """Given 確定予約 When 取消と同じ枠の再予約を同時実行 Then 重なる確定予約は最大1件。 [RULE-06-AC]"""
    reservation_id = create_reservation(client, signed, booking).json()["reservationId"]
    barrier = Barrier(2)

    def cancel_first() -> Any:
        barrier.wait(timeout=15)
        return cancel(client, signed(), reservation_id, 1)

    def rebook() -> Any:
        barrier.wait(timeout=15)
        return create_reservation(client, signed, booking, subject="bob")

    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(cancel_first)
        second = pool.submit(rebook)
        cancelled, rebooked = first.result(), second.result()
    assert cancelled.status_code == 200
    assert rebooked.status_code in (201, 409)
    with db_connect() as connection:
        row = connection.execute(
            "SELECT count(*) AS count FROM slotkeeper.reservations"
            " WHERE resource_id=%s AND status='confirmed'",
            (booking["resourceId"],),
        ).fetchone()
    assert row is not None
    assert row["count"] == (1 if rebooked.status_code == 201 else 0)
    if rebooked.status_code == 409:
        assert create_reservation(client, signed, booking, subject="bob").status_code == 201


def test_missing_reservation_returns_404(
    client: TestClient, signed: Signer, database: None
) -> None:
    """Given 存在しない予約 When 取消 Then 404で区別する。 [COM-03-AC]"""
    response = cancel(client, signed(), str(uuid4()), 1)
    assert response.status_code == 404
    assert error_reason(response) == "reservation_not_found"


async def seeded_reservation(
    harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_seed_resource: Callable[..., Any],
    router_seed_reservation: Callable[..., Any],
) -> dict[str, Any]:
    """aliceの開始前予約を1件用意する。"""
    resource = await router_seed_resource(harness, router_auth_headers("manager", True))
    reservation: dict[str, Any] = await router_seed_reservation(
        harness, router_auth_headers("alice"), resource["resourceId"]
    )
    return reservation


def cancel_path(reservation_id: str) -> str:
    return "/reservations/" + reservation_id + "/cancel"


@pytest.mark.anyio
async def test_cancel_reservation_router_returns_sample_shaped_response_with_db(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_count_rows: Callable[..., Any],
    router_fetch_one: Callable[..., Any],
    router_seed_resource: Callable[..., Any],
    router_seed_reservation: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 開始前の確定予約 When 標本requestで取消 Then 標本と同じ形の応答を返し取消と履歴を保存する。 [SLOT-AC04] [RULE-12-AC]"""
    _ = timer
    reservation = await seeded_reservation(
        router_db_harness, router_auth_headers, router_seed_resource, router_seed_reservation
    )
    response = await router_db_harness.client.post(
        cancel_path(reservation["reservationId"]),
        headers=router_auth_headers("alice"),
        json=sample_value(CANCEL_RESERVATION_REQUEST_SAMPLE),
    )

    assert response.status_code == 200, response.text
    body = response.json()
    expected = sample_value(CANCEL_RESERVATION_RESPONSE_SAMPLE)
    expected["reservationId"] = reservation["reservationId"]
    expected["resourceId"] = reservation["resourceId"]
    expected["purpose"] = reservation["purpose"]
    assert body == expected
    factory = router_db_harness.session_factory
    where = {"reservation_id": reservation["reservationId"]}
    row = await router_fetch_one(factory, "reservations", where)
    assert row is not None and row["status"] == ReservationStatus.CANCELLED
    assert await router_count_rows(factory, "reservation_events", where) == 2
    resource_where = {"resource_id": reservation["resourceId"]}
    assert await router_count_rows(factory, "resources", resource_where) == 1


@pytest.mark.anyio
async def test_cancel_reservation_sample_request_emits_router_error_log_to_stdio(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    assert_router_error_log: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 標本requestと処理中の業務例外 When 予約取消 Then Router例外の運用ログをcatalogどおり出す。 [COM-07-AC]"""
    _ = timer
    await assert_router_error_log(
        router_db_harness=router_db_harness,
        capsys=capsys,
        monkeypatch=monkeypatch,
        method="POST",
        path_template="/reservations/{reservationId}/cancel",
        status_samples=CANCEL_RESERVATION_STATUS_SAMPLES,
        success_status=200,
        patch_target="app.apis.reservations.cancel_reservation.functions.get_reservation",
        message_id="cancelReservation.router_api_function_error",
        catalog_id="M005",
        headers=router_auth_headers("alice"),
    )


# unit-test_gen.md executable cases
@pytest.mark.anyio
async def test_tc001_cancel_reservation_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_seed_resource: Callable[..., Any],
    router_seed_reservation: Callable[..., Any],
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given aliceの予約 When bobが取消 Then 403で運用ログを出す。 [SLOT-AC04] [COM-04-AC]"""
    _ = timer
    reservation = await seeded_reservation(
        router_db_harness, router_auth_headers, router_seed_resource, router_seed_reservation
    )
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.post(
            cancel_path(reservation["reservationId"]),
            headers=router_auth_headers("bob"),
            json={"version": 1},
        )

    assert response.status_code == 403, response.text
    assert response.json()["error"]["details"][0]["reason"] == "forbidden"
    actual_log_event = find_log_event("cancelReservation.caller_cannot_cancel_reservation")
    assert actual_log_event["messageId"] == "cancelReservation.caller_cannot_cancel_reservation"
    assert (
        actual_log_event["summary"]
        == "呼び出し元が予約者本人でも管理者でもないため、予約取消を拒否した。"
    )


@pytest.mark.anyio
async def test_tc002_cancel_reservation_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_seed_resource: Callable[..., Any],
    router_seed_reservation: Callable[..., Any],
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 版1の予約 When 版2で取消 Then 409で運用ログを出す。 [SLOT-AC11]"""
    _ = timer
    reservation = await seeded_reservation(
        router_db_harness, router_auth_headers, router_seed_resource, router_seed_reservation
    )
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.post(
            cancel_path(reservation["reservationId"]),
            headers=router_auth_headers("alice"),
            json={"version": 2},
        )

    assert response.status_code == 409, response.text
    assert response.json()["error"]["details"][0]["reason"] == "stale_version"
    actual_log_event = find_log_event("cancelReservation.stale_reservation_version")
    assert actual_log_event["messageId"] == "cancelReservation.stale_reservation_version"
    assert actual_log_event["summary"] == "予約の版が現在値と一致しないため、予約取消を拒否した。"


@pytest.mark.anyio
async def test_tc003_cancel_reservation_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_seed_resource: Callable[..., Any],
    router_seed_reservation: Callable[..., Any],
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 取消済みの予約 When 最新版で再取消 Then 409で運用ログを出す。 [SLOT-AC13] [RULE-13-AC]"""
    _ = timer
    reservation = await seeded_reservation(
        router_db_harness, router_auth_headers, router_seed_resource, router_seed_reservation
    )
    path = cancel_path(reservation["reservationId"])
    first = await router_db_harness.client.post(
        path, headers=router_auth_headers("alice"), json={"version": 1}
    )
    assert first.status_code == 200, first.text
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.post(
            path, headers=router_auth_headers("alice"), json={"version": 2}
        )

    assert response.status_code == 409, response.text
    assert response.json()["error"]["details"][0]["reason"] == "already_cancelled"
    actual_log_event = find_log_event("cancelReservation.reservation_already_cancelled")
    assert actual_log_event["messageId"] == "cancelReservation.reservation_already_cancelled"
    assert actual_log_event["summary"] == "予約が取消済みのため、予約取消を拒否した。"


@pytest.mark.anyio
async def test_tc004_cancel_reservation_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_seed_resource: Callable[..., Any],
    router_seed_reservation: Callable[..., Any],
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 開始時刻を迎えた予約 When 取消 Then 409で運用ログを出す。 [SLOT-AC13]"""
    reservation = await seeded_reservation(
        router_db_harness, router_auth_headers, router_seed_resource, router_seed_reservation
    )
    timer.value += timedelta(days=1, hours=1)
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.post(
            cancel_path(reservation["reservationId"]),
            headers=router_auth_headers("alice"),
            json={"version": 1},
        )

    assert response.status_code == 409, response.text
    assert response.json()["error"]["details"][0]["reason"] == "already_started"
    actual_log_event = find_log_event("cancelReservation.reservation_already_started")
    assert actual_log_event["messageId"] == "cancelReservation.reservation_already_started"
    assert actual_log_event["summary"] == "予約の開始時刻を過ぎているため、予約取消を拒否した。"


@pytest.mark.anyio
async def test_tc005_cancel_reservation_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_seed_resource: Callable[..., Any],
    router_seed_reservation: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 開始前の確定予約 When 本人が取消 Then 200で取消済みを返す。 [SLOT-AC04]"""
    _ = timer
    reservation = await seeded_reservation(
        router_db_harness, router_auth_headers, router_seed_resource, router_seed_reservation
    )
    response = await router_db_harness.client.post(
        cancel_path(reservation["reservationId"]),
        headers=router_auth_headers("alice"),
        json={"version": 1},
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == ReservationStatus.CANCELLED


@pytest.mark.anyio
async def test_tc006_cancel_reservation_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 予約取消の対象取得で業務例外 When API呼出し Then Routerで500へ変換し運用ログを出す。"""
    _ = timer

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise ApiFunctionError(500, "forced router error", summary="unit-test_gen case")

    monkeypatch.setattr(
        "app.apis.reservations.cancel_reservation.functions.get_reservation",
        raise_expected_error,
    )
    headers = router_auth_headers("alice")
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.post(
            cancel_path(str(uuid4())), headers=headers, json={"version": 1}
        )

    assert response.status_code == 500, response.text
    assert response.json()["error"]["details"][0]["reason"] == "forced router error"
    actual_log_event = find_log_event("cancelReservation.router_api_function_error")
    assert actual_log_event["messageId"] == "cancelReservation.router_api_function_error"
    assert (
        actual_log_event["summary"] == "Routerで捕捉したApiFunctionErrorにより予約取消が失敗した。"
    )


@pytest.mark.anyio
async def test_tc007_cancel_reservation_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 予約取消の対象取得で外部API例外 When API呼出し Then Routerで502へ変換し運用ログを出す。"""
    _ = timer

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise ExternalApiError("forced external api error")

    monkeypatch.setattr(
        "app.apis.reservations.cancel_reservation.functions.get_reservation",
        raise_expected_error,
    )
    headers = router_auth_headers("alice")
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.post(
            cancel_path(str(uuid4())), headers=headers, json={"version": 1}
        )

    assert response.status_code == 502, response.text
    assert response.json()["error"]["details"][0]["reason"] == "external service request failed"
    actual_log_event = find_log_event("cancelReservation.router_external_api_error")
    assert actual_log_event["messageId"] == "cancelReservation.router_external_api_error"
    assert (
        actual_log_event["summary"] == "Routerで捕捉したExternalApiErrorにより予約取消が失敗した。"
    )


@pytest.mark.anyio
async def test_tc008_cancel_reservation_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 予約取消の対象取得でHTTP例外 When API呼出し Then Routerで400へ変換し運用ログを出す。"""
    _ = timer

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise HTTPException(status_code=400, detail="forced http exception")

    monkeypatch.setattr(
        "app.apis.reservations.cancel_reservation.functions.get_reservation",
        raise_expected_error,
    )
    headers = router_auth_headers("alice")
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.post(
            cancel_path(str(uuid4())), headers=headers, json={"version": 1}
        )

    assert response.status_code == 400, response.text
    assert response.json()["error"]["details"][0]["reason"] == "forced http exception"
    actual_log_event = find_log_event("cancelReservation.router_http_exception")
    assert actual_log_event["messageId"] == "cancelReservation.router_http_exception"
    assert actual_log_event["summary"] == "Routerで捕捉したHTTPExceptionにより予約取消が失敗した。"
