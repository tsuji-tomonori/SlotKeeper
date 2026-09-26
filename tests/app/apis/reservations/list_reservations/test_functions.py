"""自分の予約一覧の業務関数を単体で検査する。"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from app.apis.exceptions import ApiFunctionError
from app.apis.reservations.list_reservations import functions
from app.apis.reservations.list_reservations.generated import queries
from app.apis.reservations.list_reservations.schemas import ListReservationsQuery
from tests.app.apis.function_helpers import (
    ALICE,
    NOW,
    FixedClock,
    QueryRecorder,
    fake_session,
    response_error,
)

pytestmark = pytest.mark.anyio


def row(index: int) -> queries.SelectReservationsRow:
    return queries.SelectReservationsRow(
        reservation_id=f"reservation-{index}",
        resource_id="resource",
        owner_principal_id="alice",
        start_at=NOW + timedelta(days=1, hours=index),
        end_at=NOW + timedelta(days=1, hours=index + 1),
        purpose="会議",
        status="confirmed",
        row_version=1,
    )


async def test_own_reservations_are_filtered_and_paged(monkeypatch: pytest.MonkeyPatch) -> None:
    """Given 3件の予約と上限2件 When 本人の予約を日付で取得 Then 日本時間の日付範囲で問合せ継続tokenを付ける。 [SLOT-AC08] [RULE-14-AC]"""
    recorder = QueryRecorder()
    recorder.install(monkeypatch, queries, "select_reservations", [row(0), row(1), row(2)])
    query = ListReservationsQuery(day=date(2026, 9, 26), limit=2)
    reservations = await functions.get_own_reservations(query, ALICE, FixedClock(), fake_session())
    params = recorder.params("select_reservations")
    assert params.owner_principal_id == "alice" and params.limit == 3
    assert params.range_start.isoformat() == "2026-09-26T00:00:00+09:00"
    page = await functions.apply_pagination(reservations, query)
    response = await functions.build_reservation_list_response(page)
    assert [item.reservation_id for item in response.items] == ["reservation-0", "reservation-1"]
    assert response.next_token is not None
    next_query = ListReservationsQuery(next_token=response.next_token)
    await functions.get_own_reservations(next_query, ALICE, FixedClock(), fake_session())
    assert recorder.calls[-1][1].after_reservation_id == "reservation-1"


async def test_router_error_response() -> None:
    """Given 不正な継続token When Router例外を変換 Then 422と理由コードを返す。 [COM-03-AC]"""
    error = ApiFunctionError(422, "invalid_page_token", summary="token不正")
    routed = await functions.build_router_error_response(ListReservationsQuery(), ALICE, error)
    assert response_error(routed) == (422, "invalid_page_token")
