from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.apis.deps import get_caller_identity
from app.apis.resources.list_resources import functions as api_functions
from app.apis.resources.list_resources.samples import (
    LIST_RESOURCES_RESPONSE_SAMPLE,
    LIST_RESOURCES_STATUS_SAMPLES,
)
from app.apis.resources.list_resources.schemas import ListResourcesQuery, ListResourcesResponse
from app.apis.responses import error_responses, success_response
from app.apis.router_errors import ROUTER_HANDLED_EXCEPTIONS
from app.apis.sequence_types import CallerIdentity
from app.db.session import get_session, retry_transaction

router = APIRouter()


@router.get(
    "/resources",
    operation_id="listResources",
    summary="資源一覧を取得する",
    description="予約できる会議室と備品を、名前とIDの固定順でページ単位に取得します。",
    response_model=ListResourcesResponse,
    responses={
        status.HTTP_200_OK: success_response(LIST_RESOURCES_RESPONSE_SAMPLE),
        **error_responses(samples=LIST_RESOURCES_STATUS_SAMPLES),
    },
    tags=["resources"],
)
@retry_transaction(replay_safe=True)
async def list_resources(
    query: Annotated[ListResourcesQuery, Query()],
    caller: Annotated[CallerIdentity, Depends(get_caller_identity)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ListResourcesResponse | JSONResponse:
    try:
        resources = await api_functions.get_resources(query, session)
        page = await api_functions.apply_pagination(resources, query)
        return await api_functions.build_resource_list_response(page)
    except ROUTER_HANDLED_EXCEPTIONS as error:
        return await api_functions.build_router_error_response(query, caller, error)
