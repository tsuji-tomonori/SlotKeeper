from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.apis.base import sample_path_value
from app.apis.deps import get_caller_identity
from app.apis.resources.get_resource_schedule import functions as api_functions
from app.apis.resources.get_resource_schedule.samples import (
    GET_RESOURCE_SCHEDULE_RESPONSE_SAMPLE,
    GET_RESOURCE_SCHEDULE_STATUS_SAMPLES,
)
from app.apis.resources.get_resource_schedule.schemas import (
    GetResourceScheduleQuery,
    GetResourceScheduleResponse,
)
from app.apis.responses import error_responses, success_response
from app.apis.router_errors import ROUTER_HANDLED_EXCEPTIONS
from app.apis.sequence_types import CallerIdentity
from app.apis.types import ResourceId
from app.db.session import get_session, retry_transaction

router = APIRouter()


@router.get(
    "/resources/{resourceId}/schedule",
    operation_id="getResourceSchedule",
    summary="予約表を取得する",
    description=(
        "資源と日本時間の日付を指定して予約済み時間帯を取得します。"
        "他人の予約は時間帯と「予約済み」だけを返します。"
    ),
    response_model=GetResourceScheduleResponse,
    response_model_exclude_none=True,
    responses={
        status.HTTP_200_OK: success_response(GET_RESOURCE_SCHEDULE_RESPONSE_SAMPLE),
        **error_responses(
            status.HTTP_404_NOT_FOUND,
            samples=GET_RESOURCE_SCHEDULE_STATUS_SAMPLES,
        ),
    },
    tags=["resources"],
)
@retry_transaction(replay_safe=True)
async def get_resource_schedule(
    resource_id: Annotated[
        ResourceId,
        Path(
            alias="resourceId",
            description="予約対象の資源を一意に識別するIDです。",
            json_schema_extra={
                "default": sample_path_value(GET_RESOURCE_SCHEDULE_RESPONSE_SAMPLE, "resourceId")
            },
        ),
    ],
    query: Annotated[GetResourceScheduleQuery, Query()],
    caller: Annotated[CallerIdentity, Depends(get_caller_identity)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GetResourceScheduleResponse | JSONResponse:
    try:
        schedule_resource_id = await api_functions.get_resource(resource_id, session)
        bookings = await api_functions.get_resource_bookings(
            schedule_resource_id,
            query,
            session,
        )
        page = await api_functions.apply_pagination(bookings, query)
        return await api_functions.build_resource_schedule_response(page, caller)
    except ROUTER_HANDLED_EXCEPTIONS as error:
        return await api_functions.build_router_error_response(
            resource_id,
            query,
            caller,
            error,
        )
