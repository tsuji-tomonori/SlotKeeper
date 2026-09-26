"""予約取消の業務関数を単体で検査する。"""

from __future__ import annotations

from datetime import timedelta

import pytest

from app.apis.exceptions import ApiFunctionError
from app.apis.reservations.cancel_reservation import functions
from app.apis.reservations.cancel_reservation.generated import queries
from app.apis.reservations.cancel_reservation.schemas import CancelReservationRequest
from tests.app.apis.function_helpers import (
    ADMIN,
    ALICE,
    BOB,
    NOW,
    FixedClock,
    QueryRecorder,
    fake_session,
    response_error,
)

pytestmark = pytest.mark.anyio


def row(**overrides: object) -> queries.SelectReservationsRow:
    values: dict[str, object] = {
        "reservation_id": "reservation-1",
        "resource_id": "resource",
        "owner_principal_id": "alice",
        "start_at": NOW + timedelta(days=1),
        "end_at": NOW + timedelta(days=1, hours=1),
        "purpose": "会議",
        "status": "confirmed",
        "row_version": 1,
    }
    values.update(overrides)
    return queries.SelectReservationsRow.model_validate(values)


async def test_get_reservation_and_predicates(monkeypatch: pytest.MonkeyPatch) -> None:
    """Given aliceの確定予約 When 取得と取消可否を判定 Then 本人と管理者だけ許可し版・状態・開始を判定する。 [SLOT-AC04] [SLOT-AC11] [SLOT-AC13]"""
    recorder = QueryRecorder()
    recorder.install(monkeypatch, queries, "select_reservations", [row()])
    reservation = await functions.get_reservation("reservation-1", fake_session())
    assert await functions.has_reservation_cancel_permission(reservation, ALICE)
    assert await functions.has_reservation_cancel_permission(reservation, ADMIN)
    assert not await functions.has_reservation_cancel_permission(reservation, BOB)
    assert await functions.is_current_reservation_version(
        reservation, CancelReservationRequest(version=1)
    )
    assert await functions.is_confirmed_reservation(reservation)
    assert not await functions.is_started_reservation(reservation, FixedClock())
    started = FixedClock(reservation.start_at)
    assert await functions.is_started_reservation(reservation, started)
    recorder.install(monkeypatch, queries, "select_reservations", [])
    with pytest.raises(ApiFunctionError) as error:
        await functions.get_reservation("missing", fake_session())
    assert error.value.detail == "reservation_not_found"


async def test_cancel_updates_and_appends_event(monkeypatch: pytest.MonkeyPatch) -> None:
    """Given 取消可能な予約 When 制御版・状態・履歴を更新 Then 取消済みの版2と取消履歴を返す。 [RULE-12-AC] [RULE-06-AC]"""
    recorder = QueryRecorder()
    recorder.install(monkeypatch, queries, "select_reservations", [row()])
    recorder.install(
        monkeypatch,
        queries,
        "update_resources_control_version",
        queries.UpdateResourcesControlVersionRow(
            resource_id="resource", active=True, row_version=1
        ),
    )
    cancelled_row = queries.UpdateReservationsRow.model_validate(
        {**row().model_dump(), "status": "cancelled", "row_version": 2}
    )
    recorder.install(monkeypatch, queries, "update_reservations", cancelled_row)
    recorder.install(monkeypatch, queries, "insert_reservation_events", None)
    session = fake_session()
    reservation = await functions.get_reservation("reservation-1", session)
    await functions.update_resource_control_version(reservation, session)
    cancelled = await functions.update_reservation_status(reservation, session)
    event = await functions.append_reservation_cancelled_event(
        cancelled, ALICE, FixedClock(), session
    )
    assert recorder.params("insert_reservation_events").event_id == event.event_id
    response = await functions.build_reservation_response(cancelled)
    assert response.status == "cancelled" and response.version == 2
    recorder.install(monkeypatch, queries, "update_resources_control_version", None)
    with pytest.raises(ApiFunctionError):
        await functions.update_resource_control_version(reservation, session)
    recorder.install(monkeypatch, queries, "update_reservations", None)
    with pytest.raises(ApiFunctionError):
        await functions.update_reservation_status(reservation, session)


async def test_rejection_builders() -> None:
    """Given 権限なし・古い版・取消済み・開始済み When 拒否応答を組み立てる Then 403と409の理由コードを返す。 [SLOT-AC04] [SLOT-AC11] [SLOT-AC13]"""
    request = CancelReservationRequest(version=1)
    cases = [
        (functions.build_caller_cannot_cancel_reservation_response, (403, "forbidden")),
        (functions.build_stale_reservation_version_response, (409, "stale_version")),
        (functions.build_reservation_already_cancelled_response, (409, "already_cancelled")),
        (functions.build_reservation_already_started_response, (409, "already_started")),
    ]
    for builder, expected in cases:
        assert response_error(await builder("reservation-1", request, ALICE)) == expected
    error = ApiFunctionError(404, "reservation_not_found", summary="予約なし")
    routed = await functions.build_router_error_response("r", request, ALICE, error)
    assert response_error(routed) == (404, "reservation_not_found")
