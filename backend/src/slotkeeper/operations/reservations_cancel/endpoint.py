"""本人または管理者が開始前の予約を取消する。"""

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends

from slotkeeper.auth import Principal
from slotkeeper.db import Connection, transaction
from slotkeeper.domain import (
    CancelInput,
    Clock,
    DomainError,
    Reservation,
    SystemClock,
    require_owner,
)
from slotkeeper.operations.reservations_cancel import queries as q

router = APIRouter()


def clock() -> Clock:
    """現在時刻を依存として提供する。"""
    return SystemClock()


@router.post(
    "/reservations/{reservation_id}/cancel",
    response_model=Reservation,
    operation_id="reservations_cancel",
    tags=["reservations"],
)
def endpoint(
    reservation_id: str,
    value: CancelInput,
    user: Principal,
    timer: Annotated[Clock, Depends(clock)],
) -> Reservation:
    """所有者、公開版、状態と開始時刻を検査して取消と履歴を確定する。"""

    def work(connection: Connection) -> Reservation:
        rows = q.get(connection, q.GetParams(id=reservation_id))
        if not rows:
            raise DomainError("reservation_not_found", 404)
        current = rows[0]
        require_owner(user, current)
        q.control(connection, q.ControlParams(id=current.resource_id))
        if current.version != value.version:
            raise DomainError("stale_version")
        if current.status != "confirmed":
            raise DomainError("already_cancelled")
        now = timer.now()
        if current.start_at <= now:
            raise DomainError("already_started")
        result = q.cancel(connection, q.CancelParams(id=reservation_id))[0]
        q.event(
            connection,
            q.EventParams(
                id=str(uuid4()),
                reservation_id=reservation_id,
                actor=user.subject,
                action="cancelled",
                at=now,
            ),
        )
        return result

    return transaction(work)
