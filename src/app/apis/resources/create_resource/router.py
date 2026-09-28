from typing import Annotated

from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.apis.base import sample_value
from app.apis.deps import get_caller_identity
from app.apis.resources.create_resource import functions as api_functions
from app.apis.resources.create_resource.samples import (
    CREATE_RESOURCE_REQUEST_SAMPLE,
    CREATE_RESOURCE_RESPONSE_SAMPLE,
    CREATE_RESOURCE_STATUS_SAMPLES,
)
from app.apis.resources.create_resource.schemas import (
    CreateResourceRequest,
    CreateResourceResponse,
)
from app.apis.responses import error_responses, success_response
from app.apis.router_errors import ROUTER_HANDLED_EXCEPTIONS
from app.apis.sequence_types import CallerIdentity
from app.db.session import get_session, retry_transaction

router = APIRouter()


@router.post(
    "/resources",
    operation_id="createResource",
    summary="資源を登録する",
    description="管理者が会議室または備品を有効な状態で登録します。",
    response_model=CreateResourceResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: success_response(CREATE_RESOURCE_RESPONSE_SAMPLE),
        **error_responses(
            status.HTTP_403_FORBIDDEN,
            samples=CREATE_RESOURCE_STATUS_SAMPLES,
        ),
    },
    tags=["resources"],
)
@retry_transaction()
async def create_resource(
    request: Annotated[
        CreateResourceRequest,
        Body(openapi_examples={"default": {"value": sample_value(CREATE_RESOURCE_REQUEST_SAMPLE)}}),
    ],
    caller: Annotated[CallerIdentity, Depends(get_caller_identity)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CreateResourceResponse | JSONResponse:
    try:
        if not await api_functions.has_resource_management_permission(caller):
            return await api_functions.build_caller_cannot_manage_resources_response(
                request,
                caller,
            )
        resource = await api_functions.save_resource(request, session)
        await session.commit()
        return await api_functions.build_resource_response(resource)
    except ROUTER_HANDLED_EXCEPTIONS as error:
        return await api_functions.build_router_error_response(request, caller, error)
