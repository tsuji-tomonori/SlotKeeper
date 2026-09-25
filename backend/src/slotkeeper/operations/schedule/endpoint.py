"""資源の一日分の予約時間帯を返す。"""

from datetime import date, datetime, time, timedelta
from typing import Annotated

from fastapi import APIRouter, Query

from slotkeeper.auth import Principal
from slotkeeper.db import Connection, transaction
from slotkeeper.domain import JST, BusySlot, Clock, DomainError, SystemClock
from slotkeeper.operations.schedule import queries as q

router = APIRouter()


def clock() -> Clock:
    """現在時刻を依存として提供する。"""
    return SystemClock()


@router.get(
    "/resources/{resource_id}/schedule",
    response_model=list[BusySlot],
    operation_id="schedule",
    tags=["resources"],
    response_model_exclude_none=True,
)
def endpoint(
    resource_id: str,
    day: date,
    user: Principal,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[BusySlot]:
    """一般利用者には他人の識別情報と目的を返さない。"""
    start = datetime.combine(day, time(), JST)

    def work(connection: Connection) -> list[BusySlot]:
        if not q.resource(connection, q.ResourceParams(id=resource_id)):
            raise DomainError("resource_not_found", 404)
        rows = q.bookings(
            connection,
            q.BookingsParams(
                id=resource_id,
                start=start,
                end=start + timedelta(days=1),
                limit=limit,
                offset=offset,
            ),
        )
        return [
            BusySlot(
                start_at=row.start_at,
                end_at=row.end_at,
                reservation=row if user.admin or row.subject == user.subject else None,
            )
            for row in rows
        ]

    return transaction(work)
