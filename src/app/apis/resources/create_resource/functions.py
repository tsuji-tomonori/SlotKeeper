from __future__ import annotations

from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.apis.common import IdentityGroup, raise_missing_runtime_dependency
from app.apis.exceptions import ApiFunctionError
from app.apis.resources.common import ResourceKind
from app.apis.resources.create_resource.generated import queries
from app.apis.resources.create_resource.schemas import (
    CreateResourceRequest,
    CreateResourceResponse,
)
from app.apis.router_errors import (
    api_error_response,
    error_code_for_status,
    error_response_for_router_error,
    router_error_message_id,
    router_error_summary,
    router_log_context,
    status_code_for_router_error,
)
from app.apis.sequence_types import CallerIdentity
from app.core.logging import get_operation_logger, operational_log_context_model
from app.integrations.common_errors import ExternalApiError

ops_logger = get_operation_logger(__name__)


async def has_resource_management_permission(caller: CallerIdentity) -> bool:
    """呼び出し元が資源を管理できる管理者であるかを判定する。"""
    return IdentityGroup.ADMIN in caller.groups


async def save_resource(
    request: CreateResourceRequest,
    session: AsyncSession | None = None,
) -> CreateResourceResponse:
    """資源を有効な初期版で保存する。"""
    if session is not None:
        row = await queries.insert_resources(
            session,
            queries.InsertResourcesParams(
                resource_id=str(uuid4()),
                name=request.name,
                description=request.description,
                kind=request.kind,
            ),
        )
        if row is None:
            raise ApiFunctionError(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "resource_not_saved",
                summary="資源の保存結果を取得できない場合。",
            )
        return CreateResourceResponse(
            resource_id=row.resource_id,
            name=row.name,
            description=row.description,
            kind=ResourceKind(row.kind),
            active=row.active,
            version=row.row_version,
        )
    return raise_missing_runtime_dependency("save_resource")


async def build_resource_response(resource: CreateResourceResponse) -> CreateResourceResponse:
    """登録した資源のレスポンスを組み立てる。"""
    return CreateResourceResponse(
        resource_id=resource.resource_id,
        name=resource.name,
        description=resource.description,
        kind=resource.kind,
        active=resource.active,
        version=resource.version,
    )


async def build_caller_cannot_manage_resources_response(
    request: CreateResourceRequest,
    caller: CallerIdentity,
) -> JSONResponse:
    """資源管理権限がない場合の運用ログと error response を組み立てる。"""
    ops_logger.warning(
        "createResource.caller_cannot_manage_resources",
        catalog_id="M001",
        summary="呼び出し元が管理者ではないため、資源登録を拒否した。",
        status_code=status.HTTP_403_FORBIDDEN,
        detail="forbidden",
        when="呼び出し元が管理者groupに所属していない場合。",
        why_production="資源管理の認可拒否を運用で追跡するため。",
        context_model=operational_log_context_model(
            trace_id=None,
            actor_principal_id=caller.principal_id,
            api_status_code=status.HTTP_403_FORBIDDEN,
            error_code=error_code_for_status(status.HTTP_403_FORBIDDEN),
            error_message="forbidden",
        ),
        operator_action="actorPrincipalIdと管理者groupの割当てを確認する。",
        runbook="RUNBOOK-authorization-forbidden",
        context=router_log_context(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="forbidden",
            caller=caller,
            resource={"name": request.name},
        ),
    )
    return api_error_response(status.HTTP_403_FORBIDDEN, "forbidden")


async def build_router_error_response(
    request: CreateResourceRequest,
    caller: CallerIdentity,
    error: ApiFunctionError | ExternalApiError | HTTPException,
) -> JSONResponse:
    """Router で捕捉した例外を運用ログと HTTP error response に変換する。"""
    ops_logger.error(
        router_error_message_id("createResource", error),
        catalog_id="M002",
        summary=router_error_summary(
            "Routerで捕捉した例外により資源登録が失敗した。",
            error,
        ),
        when="ROUTER_HANDLED_EXCEPTIONSを捕捉した場合。",
        check_procedure="traceIdでログを検索し、routerで捕捉された例外種別と資源名を確認する。",
        remediation_procedure="原因を特定し、同じ資源が未登録であることを確認してから再送する。",
        context_model=operational_log_context_model(
            trace_id=None,
            actor_principal_id=caller.principal_id,
            api_status_code=status_code_for_router_error(error),
            error_code=error_code_for_status(status_code_for_router_error(error)),
            error_message=str(error),
            error_exception_type=type(error).__name__,
        ),
        operator_action="同一routeの5xx率、直近deploy、DB状態を確認する。",
        runbook="RUNBOOK-unexpected-api-failure",
        context=router_log_context(
            status_code=status_code_for_router_error(error),
            detail=str(error),
            caller=caller,
            resource={"name": request.name},
            error=error,
        ),
    )
    return error_response_for_router_error(error)
