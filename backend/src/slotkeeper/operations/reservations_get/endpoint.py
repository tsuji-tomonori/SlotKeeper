"""本人または管理者が予約と履歴を取得する。"""

from fastapi import APIRouter

from slotkeeper.auth import Principal
from slotkeeper.db import Connection, transaction
from slotkeeper.domain import Clock, Detail, DomainError, SystemClock, require_owner
from slotkeeper.operations.reservations_get import queries as q

router = APIRouter()


def clock() -> Clock:
    """現在時刻を依存として提供する。"""
    return SystemClock()


@router.get(
    "/reservations/{reservation_id}",
    response_model=Detail,
    operation_id="reservations_get",
    tags=["reservations"],
)
def endpoint(reservation_id: str, user: Principal) -> Detail:
    """権限のある予約に限って操作履歴を含む詳細を返す。"""

    def work(connection: Connection) -> Detail:
        rows = q.get(connection, q.GetParams(id=reservation_id))
        if not rows:
            raise DomainError("reservation_not_found", 404)
        require_owner(user, rows[0])
        return Detail(
            reservation=rows[0], events=q.events(connection, q.EventsParams(id=reservation_id))
        )

    return transaction(work)
