"""自分の予約を絞り込む。"""

from datetime import UTC, date, datetime, time, timedelta
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query

from slotkeeper.auth import Principal
from slotkeeper.db import Connection, transaction
from slotkeeper.domain import (
    JST,
    Clock,
    Reservation,
    SystemClock,
)
from slotkeeper.operations.reservations_list import queries as q

router = APIRouter()


def clock() -> Clock:
    """現在時刻を依存として提供する。"""
    return SystemClock()


@router.get(
    "/reservations",
    response_model=list[Reservation],
    operation_id="reservations_list",
    tags=["reservations"],
)
def endpoint(
    user: Principal,
    timer: Annotated[Clock, Depends(clock)],
    day: date | None = None,
    state: Literal["confirmed", "cancelled"] | None = None,
    future: bool = True,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Reservation]:
    """本人の予約だけを日本時間の日付と状態で絞り固定順で返す。"""
    start = datetime.combine(day, time(), JST) if day else datetime(1970, 1, 1, tzinfo=UTC)
    end = start + timedelta(days=1) if day else datetime(9999, 1, 1, tzinfo=UTC)

    def work(connection: Connection) -> list[Reservation]:
        return q.select_page(
            connection,
            q.SelectPageParams(
                subject=user.subject,
                start=start,
                end=end,
                state=state or "",
                future=future,
                now=timer.now(),
                limit=limit,
                offset=offset,
            ),
        )

    return transaction(work)
