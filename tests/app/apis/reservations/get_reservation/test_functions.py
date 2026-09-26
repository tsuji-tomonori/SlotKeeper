"""予約詳細の業務関数を単体で検査する。"""

from __future__ import annotations

from datetime import timedelta

import pytest

from app.apis.exceptions import ApiFunctionError
from app.apis.reservations.get_reservation import functions
from app.apis.reservations.get_reservation.generated import queries
from tests.app.apis.function_helpers import (
    ADMIN,
    ALICE,
    BOB,
    NOW,
    QueryRecorder,
    fake_session,
    response_error,
)

pytestmark = pytest.mark.anyio


async def test_get_reservation_with_events(monkeypatch: pytest.MonkeyPatch) -> None:
    """Given 予約と作成・取消履歴 When 詳細を取得 Then 本人と管理者だけが履歴つき詳細を参照できる。 [SLOT-07-AC] [RULE-09-AC]"""
    recorder = QueryRecorder()
    reservation_row = queries.SelectReservationsRow(
        reservation_id="reservation-1",
        resource_id="resource",
        owner_principal_id="alice",
        start_at=NOW + timedelta(days=1),
        end_at=NOW + timedelta(days=1, hours=1),
        purpose="会議",
        status="cancelled",
        row_version=2,
    )
    events = [
        queries.SelectReservationEventsRow(
            event_id=f"event-{index}",
            reservation_id="reservation-1",
            actor_principal_id="alice",
            action=action,
            occurred_at=NOW,
        )
        for index, action in enumerate(["created", "cancelled"])
    ]
    recorder.install(monkeypatch, queries, "select_reservations", [reservation_row])
    recorder.install(monkeypatch, queries, "select_reservation_events", events)
    session = fake_session()
    reservation = await functions.get_reservation("reservation-1", session)
    assert await functions.has_reservation_view_permission(reservation, ALICE)
    assert await functions.has_reservation_view_permission(reservation, ADMIN)
    assert not await functions.has_reservation_view_permission(reservation, BOB)
    history = await functions.get_reservation_events(reservation, session)
    detail = await functions.build_reservation_detail_response(reservation, history)
    assert [event.action for event in detail.events] == ["created", "cancelled"]
    recorder.install(monkeypatch, queries, "select_reservations", [])
    with pytest.raises(ApiFunctionError):
        await functions.get_reservation("missing", session)


async def test_rejection_and_router_error_builders() -> None:
    """Given 他人の予約とRouter例外 When 応答を組み立てる Then 403と例外のstatusを返す。 [COM-04-AC]"""
    forbidden = await functions.build_caller_cannot_view_reservation_response("r", BOB)
    assert response_error(forbidden) == (403, "forbidden")
    error = ApiFunctionError(404, "reservation_not_found", summary="予約なし")
    routed = await functions.build_router_error_response("r", ALICE, error)
    assert response_error(routed) == (404, "reservation_not_found")
