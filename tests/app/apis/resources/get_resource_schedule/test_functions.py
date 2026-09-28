"""予約表の業務関数を単体で検査する。"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from app.apis.exceptions import ApiFunctionError
from app.apis.reservations.common import ReservationStatus
from app.apis.resources.get_resource_schedule import functions
from app.apis.resources.get_resource_schedule.generated import queries
from app.apis.resources.get_resource_schedule.schemas import GetResourceScheduleQuery
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


def booking(owner: str, hour: int) -> queries.SelectReservationsRow:
    return queries.SelectReservationsRow(
        reservation_id=f"reservation-{hour}",
        resource_id="resource",
        owner_principal_id=owner,
        start_at=NOW + timedelta(days=1, hours=hour),
        end_at=NOW + timedelta(days=1, hours=hour + 1),
        purpose="会議",
        status=ReservationStatus.CONFIRMED,
        row_version=1,
    )


async def test_schedule_hides_other_details(monkeypatch: pytest.MonkeyPatch) -> None:
    """Given aliceとbobの予約 When 予約表を組み立てる Then 本人と管理者だけに詳細を返し日本時間の日付で問い合わせる。 [SLOT-02-AC] [RULE-09-AC]"""
    recorder = QueryRecorder()
    recorder.install(
        monkeypatch,
        queries,
        "select_resources",
        [queries.SelectResourcesRow(resource_id="resource")],
    )
    recorder.install(
        monkeypatch, queries, "select_reservations", [booking("alice", 1), booking("bob", 3)]
    )
    session = fake_session()
    query = GetResourceScheduleQuery(day=date(2026, 9, 26))
    resource_id = await functions.get_resource("resource", session)
    bookings = await functions.get_resource_bookings(resource_id, query, session)
    assert recorder.params("select_reservations").day_start.isoformat() == (
        "2026-09-26T00:00:00+09:00"
    )
    page = await functions.apply_pagination(bookings, query)
    own = await functions.build_resource_schedule_response(page, ALICE)
    assert [slot.reservation is not None for slot in own.items] == [True, False]
    other = await functions.build_resource_schedule_response(page, BOB)
    assert [slot.reservation is not None for slot in other.items] == [False, True]
    admin = await functions.build_resource_schedule_response(page, ADMIN)
    assert all(slot.reservation is not None for slot in admin.items)
    recorder.install(monkeypatch, queries, "select_resources", [])
    with pytest.raises(ApiFunctionError):
        await functions.get_resource("missing", session)


async def test_router_error_response() -> None:
    """Given 存在しない資源 When Router例外を変換 Then 404と理由コードを返す。 [COM-03-AC]"""
    query = GetResourceScheduleQuery(day=date(2026, 9, 26))
    error = ApiFunctionError(404, "resource_not_found", summary="資源なし")
    routed = await functions.build_router_error_response("resource", query, ALICE, error)
    assert response_error(routed) == (404, "resource_not_found")
