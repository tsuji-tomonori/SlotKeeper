"""資源の一覧を取得する。"""

from typing import Annotated

from fastapi import APIRouter, Query

from slotkeeper.auth import Principal
from slotkeeper.db import Connection, transaction
from slotkeeper.domain import Resource
from slotkeeper.operations.resources_list import queries as q

router = APIRouter()


@router.get(
    "/resources", response_model=list[Resource], operation_id="resources_list", tags=["resources"]
)
def endpoint(
    user: Principal,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Resource]:
    """認証済み利用者へ固定順とページ単位で資源を返す。"""

    def work(connection: Connection) -> list[Resource]:
        return q.select_page(connection, q.SelectPageParams(limit=limit, offset=offset))

    return transaction(work)
