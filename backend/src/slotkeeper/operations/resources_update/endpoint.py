"""管理者が資源を編集する。"""

from typing import Annotated

from fastapi import APIRouter, Depends

from slotkeeper.auth import Principal
from slotkeeper.db import Connection, transaction
from slotkeeper.domain import Clock, DomainError, Resource, ResourceEdit, SystemClock, require_admin
from slotkeeper.operations.resources_update import queries as q

router = APIRouter()


def clock() -> Clock:
    """現在時刻を依存として提供する。"""
    return SystemClock()


@router.put(
    "/resources/{resource_id}",
    response_model=Resource,
    operation_id="resources_update",
    tags=["resources"],
)
def endpoint(
    resource_id: str, value: ResourceEdit, user: Principal, timer: Annotated[Clock, Depends(clock)]
) -> Resource:
    """内部版で予約と競合し、公開版と将来予約を検査して編集を確定する。"""
    require_admin(user)

    def work(connection: Connection) -> Resource:
        rows = q.control(connection, q.ControlParams(id=resource_id))
        if not rows:
            raise DomainError("resource_not_found", 404)
        if rows[0].version != value.version:
            raise DomainError("stale_version")
        if (
            not value.active
            and q.future(connection, q.FutureParams(id=resource_id, now=timer.now()))[0].count
        ):
            raise DomainError("future_reservations_exist")
        return q.update(
            connection,
            q.UpdateParams(
                id=resource_id,
                name=value.name,
                description=value.description,
                kind=value.kind,
                active=value.active,
            ),
        )[0]

    return transaction(work)
