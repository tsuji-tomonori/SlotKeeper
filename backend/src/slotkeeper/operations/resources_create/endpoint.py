"""管理者が資源を追加する。"""

from uuid import uuid4

from fastapi import APIRouter

from slotkeeper.auth import Principal
from slotkeeper.db import Connection, transaction
from slotkeeper.domain import Clock, Resource, ResourceInput, SystemClock, require_admin
from slotkeeper.operations.resources_create import queries as q

router = APIRouter()


def clock() -> Clock:
    """現在時刻を依存として提供する。"""
    return SystemClock()


@router.post(
    "/resources",
    response_model=Resource,
    status_code=201,
    operation_id="resources_create",
    tags=["resources"],
)
def endpoint(value: ResourceInput, user: Principal) -> Resource:
    """管理者権限を確認して新しい資源を登録する。"""
    require_admin(user)

    def work(connection: Connection) -> Resource:
        return q.create(
            connection,
            q.CreateParams(
                id=str(uuid4()), name=value.name, description=value.description, kind=value.kind
            ),
        )[0]

    return transaction(work)
