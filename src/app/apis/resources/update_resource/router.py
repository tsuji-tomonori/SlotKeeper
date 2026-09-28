from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.apis.base import sample_path_value, sample_value
from app.apis.deps import get_caller_identity, get_clock
from app.apis.resources.update_resource import functions as api_functions
from app.apis.resources.update_resource.samples import (
    UPDATE_RESOURCE_REQUEST_SAMPLE,
    UPDATE_RESOURCE_RESPONSE_SAMPLE,
    UPDATE_RESOURCE_STATUS_SAMPLES,
)
from app.apis.resources.update_resource.schemas import (
    UpdateResourceRequest,
    UpdateResourceResponse,
)
from app.apis.responses import error_responses, success_response
from app.apis.router_errors import ROUTER_HANDLED_EXCEPTIONS
from app.apis.sequence_types import CallerIdentity, Clock
from app.apis.types import ResourceId
from app.db.session import get_session, retry_transaction

router = APIRouter()


@router.put(
    "/resources/{resourceId}",
    operation_id="updateResource",
    summary="資源を編集する",
    description=(
        "管理者が資源の名前・説明・種別・有効状態を公開版つきで更新します。"
        "将来予約のある資源は無効化できません。"
    ),
    response_model=UpdateResourceResponse,
    responses={
        status.HTTP_200_OK: success_response(UPDATE_RESOURCE_RESPONSE_SAMPLE),
        **error_responses(
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_409_CONFLICT,
            samples=UPDATE_RESOURCE_STATUS_SAMPLES,
        ),
    },
    tags=["resources"],
)
@retry_transaction()
async def update_resource(
    resource_id: Annotated[
        ResourceId,
        Path(
            alias="resourceId",
            description="予約対象の資源を一意に識別するIDです。",
            json_schema_extra={
                "default": sample_path_value(UPDATE_RESOURCE_RESPONSE_SAMPLE, "resourceId")
            },
        ),
    ],
    request: Annotated[
        UpdateResourceRequest,
        Body(openapi_examples={"default": {"value": sample_value(UPDATE_RESOURCE_REQUEST_SAMPLE)}}),
    ],
    caller: Annotated[CallerIdentity, Depends(get_caller_identity)],
    clock: Annotated[Clock, Depends(get_clock)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UpdateResourceResponse | JSONResponse:
    try:
        if not await api_functions.has_resource_management_permission(caller):
            return await api_functions.build_caller_cannot_manage_resources_response(
                resource_id,
                request,
                caller,
            )
        resource = await api_functions.update_resource_control_version(resource_id, session)
        if not await api_functions.is_current_resource_version(resource, request):
            return await api_functions.build_stale_resource_version_response(
                resource_id,
                request,
                caller,
            )
        if await api_functions.has_future_reservations(resource, request, clock, session):
            return await api_functions.build_future_reservations_exist_response(
                resource_id,
                request,
                caller,
            )
        updated = await api_functions.update_resource(resource, request, session)
        await session.commit()
        return await api_functions.build_resource_response(updated)
    except ROUTER_HANDLED_EXCEPTIONS as error:
        return await api_functions.build_router_error_response(
            resource_id,
            request,
            caller,
            error,
        )
