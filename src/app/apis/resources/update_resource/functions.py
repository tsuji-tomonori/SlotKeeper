from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.apis.common import IdentityGroup, raise_missing_runtime_dependency
from app.apis.exceptions import ApiFunctionError
from app.apis.resources.common import ResourceKind
from app.apis.resources.update_resource.generated import queries
from app.apis.resources.update_resource.schemas import (
    UpdateResourceRequest,
    UpdateResourceResponse,
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
from app.apis.sequence_types import CallerIdentity, Clock, ResourceRef
from app.apis.types import ResourceId
from app.core.logging import get_operation_logger, operational_log_context_model
from app.integrations.common_errors import ExternalApiError

ops_logger = get_operation_logger(__name__)


async def has_resource_management_permission(caller: CallerIdentity) -> bool:
    """呼び出し元が資源を管理できる管理者であるかを判定する。"""
    return IdentityGroup.ADMIN in caller.groups


async def get_locked_resource(
    resource_id: ResourceId,
    session: AsyncSession | None = None,
) -> ResourceRef:
    """同一資源の予約作成・取消と競合させるため、内部制御版を進めて資源を取得する。"""
    if session is not None:
        row = await queries.update_resources_control_version(
            session,
            queries.UpdateResourcesControlVersionParams(resource_id=resource_id),
        )
        if row is None:
            raise ApiFunctionError(
                status.HTTP_404_NOT_FOUND,
                "resource_not_found",
                summary="編集対象の資源が存在しない場合。",
            )
        return ResourceRef(
            resource_id=row.resource_id,
            active=row.active,
            row_version=row.row_version,
        )
    return raise_missing_runtime_dependency("get_locked_resource")


async def is_current_resource_version(
    resource: ResourceRef,
    request: UpdateResourceRequest,
) -> bool:
    """編集要求の公開版が資源の現在の公開版と一致するかを判定する。"""
    return resource.row_version == request.version


async def has_future_reservations(
    resource: ResourceRef,
    request: UpdateResourceRequest,
    clock: Clock,
    session: AsyncSession | None = None,
) -> bool:
    """無効化する資源に開始前の確定予約が残っているかを判定する。"""
    if request.active:
        return False
    if session is not None:
        row = await queries.select_reservations(
            session,
            queries.SelectReservationsParams(
                resource_id=resource.resource_id,
                now=clock.now(),
            ),
        )
        return bool(row and row[0].future_reservation_count)
    return raise_missing_runtime_dependency("has_future_reservations")


async def update_resource(
    resource: ResourceRef,
    request: UpdateResourceRequest,
    session: AsyncSession | None = None,
) -> UpdateResourceResponse:
    """資源の名前・説明・種別・有効状態を更新し、公開版を進める。"""
    if session is not None:
        row = await queries.update_resources(
            session,
            queries.UpdateResourcesParams(
                name=request.name,
                description=request.description,
                kind=request.kind,
                active=request.active,
                resource_id=resource.resource_id,
            ),
        )
        if row is None:
            raise ApiFunctionError(
                status.HTTP_404_NOT_FOUND,
                "resource_not_found",
                summary="更新時点で資源が存在しない場合。",
            )
        return UpdateResourceResponse(
            resource_id=row.resource_id,
            name=row.name,
            description=row.description,
            kind=ResourceKind(row.kind),
            active=row.active,
            version=row.row_version,
        )
    return raise_missing_runtime_dependency("update_resource")


async def build_resource_response(resource: UpdateResourceResponse) -> UpdateResourceResponse:
    """編集後の資源のレスポンスを組み立てる。"""
    return UpdateResourceResponse(
        resource_id=resource.resource_id,
        name=resource.name,
        description=resource.description,
        kind=resource.kind,
        active=resource.active,
        version=resource.version,
    )


def _warning_context(
    resource_id: ResourceId,
    request: UpdateResourceRequest,
    caller: CallerIdentity,
    status_code: int,
    detail: str,
) -> dict[str, object]:
    return router_log_context(
        status_code=status_code,
        detail=detail,
        caller=caller,
        resource={"resourceId": resource_id, "version": request.version},
    )


async def build_caller_cannot_manage_resources_response(
    resource_id: ResourceId,
    request: UpdateResourceRequest,
    caller: CallerIdentity,
) -> JSONResponse:
    """資源管理権限がない場合の運用ログと error response を組み立てる。"""
    ops_logger.warning(
        "updateResource.caller_cannot_manage_resources",
        catalog_id="M001",
        summary="呼び出し元が管理者ではないため、資源編集を拒否した。",
        status_code=status.HTTP_403_FORBIDDEN,
        detail="forbidden",
        when="呼び出し元が管理者groupに所属していない場合。",
        why_production="資源管理の認可拒否を運用で追跡するため。",
        context_model=operational_log_context_model(
            trace_id=None,
            actor_principal_id=caller.principal_id,
            api_status_code=status.HTTP_403_FORBIDDEN,
            resource_resource_id=resource_id,
            error_code=error_code_for_status(status.HTTP_403_FORBIDDEN),
            error_message="forbidden",
        ),
        operator_action="actorPrincipalIdと管理者groupの割当てを確認する。",
        runbook="RUNBOOK-authorization-forbidden",
        context=_warning_context(
            resource_id, request, caller, status.HTTP_403_FORBIDDEN, "forbidden"
        ),
    )
    return api_error_response(status.HTTP_403_FORBIDDEN, "forbidden")


async def build_stale_resource_version_response(
    resource_id: ResourceId,
    request: UpdateResourceRequest,
    caller: CallerIdentity,
) -> JSONResponse:
    """資源の公開版が古い場合の運用ログと error response を組み立てる。"""
    ops_logger.warning(
        "updateResource.stale_resource_version",
        catalog_id="M002",
        summary="資源の公開版が現在値と一致しないため、資源編集を拒否した。",
        status_code=status.HTTP_409_CONFLICT,
        detail="stale_version",
        when="編集要求のversionが資源の現在の公開版と一致しない場合。",
        why_production="同時編集による更新消失の防止を運用で確認するため。",
        context_model=operational_log_context_model(
            trace_id=None,
            actor_principal_id=caller.principal_id,
            api_status_code=status.HTTP_409_CONFLICT,
            resource_resource_id=resource_id,
            error_code=error_code_for_status(status.HTTP_409_CONFLICT),
            error_message="stale_version",
        ),
        operator_action="利用者へ資源を再取得して編集し直すよう案内する。",
        runbook="RUNBOOK-optimistic-lock-conflict",
        context=_warning_context(
            resource_id, request, caller, status.HTTP_409_CONFLICT, "stale_version"
        ),
    )
    return api_error_response(
        status.HTTP_409_CONFLICT,
        "stale_version",
        resource={"resourceId": resource_id, "version": request.version},
    )


async def build_future_reservations_exist_response(
    resource_id: ResourceId,
    request: UpdateResourceRequest,
    caller: CallerIdentity,
) -> JSONResponse:
    """将来予約が残る資源を無効化しようとした場合の運用ログと error response を組み立てる。"""
    ops_logger.warning(
        "updateResource.future_reservations_exist",
        catalog_id="M003",
        summary="開始前の確定予約が残っているため、資源の無効化を拒否した。",
        status_code=status.HTTP_409_CONFLICT,
        detail="future_reservations_exist",
        when="activeをfalseにする要求で、開始前の確定予約が1件以上ある場合。",
        why_production="無効資源に将来予約を残さない規則の適用を運用で確認するため。",
        context_model=operational_log_context_model(
            trace_id=None,
            actor_principal_id=caller.principal_id,
            api_status_code=status.HTTP_409_CONFLICT,
            resource_resource_id=resource_id,
            error_code=error_code_for_status(status.HTTP_409_CONFLICT),
            error_message="future_reservations_exist",
        ),
        operator_action="将来予約の取消または移動を予約者と調整してから無効化する。",
        runbook="RUNBOOK-resource-deactivation",
        context=_warning_context(
            resource_id, request, caller, status.HTTP_409_CONFLICT, "future_reservations_exist"
        ),
    )
    return api_error_response(
        status.HTTP_409_CONFLICT,
        "future_reservations_exist",
        resource={"resourceId": resource_id},
    )


async def build_router_error_response(
    resource_id: ResourceId,
    request: UpdateResourceRequest,
    caller: CallerIdentity,
    error: ApiFunctionError | ExternalApiError | HTTPException,
) -> JSONResponse:
    """Router で捕捉した例外を運用ログと HTTP error response に変換する。"""
    ops_logger.error(
        router_error_message_id("updateResource", error),
        catalog_id="M004",
        summary=router_error_summary(
            "Routerで捕捉した例外により資源編集が失敗した。",
            error,
        ),
        when="ROUTER_HANDLED_EXCEPTIONSを捕捉した場合。",
        check_procedure="traceIdでログを検索し、routerで捕捉された例外種別とresourceIdを確認する。",
        remediation_procedure="資源を再取得し、最新の公開版で再送する。",
        context_model=operational_log_context_model(
            trace_id=None,
            actor_principal_id=caller.principal_id,
            api_status_code=status_code_for_router_error(error),
            resource_resource_id=resource_id,
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
            resource={"resourceId": resource_id, "version": request.version},
            error=error,
        ),
    )
    return error_response_for_router_error(error)
