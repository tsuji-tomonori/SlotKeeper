from __future__ import annotations

from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.apis.common import IdentityGroup, raise_missing_runtime_dependency
from app.apis.exceptions import ApiFunctionError
from app.apis.reservations.cancel_reservation.generated import queries
from app.apis.reservations.cancel_reservation.schemas import (
    CancelReservationRequest,
    CancelReservationResponse,
)
from app.apis.reservations.common import ReservationStatus
from app.apis.router_errors import (
    api_error_response,
    error_code_for_status,
    error_response_for_router_error,
    router_error_message_id,
    router_error_summary,
    router_log_context,
    status_code_for_router_error,
)
from app.apis.sequence_types import CallerIdentity, Clock, EventRef, ResourceRef
from app.apis.types import ResourceId
from app.core.logging import get_operation_logger, operational_log_context_model
from app.integrations.common_errors import ExternalApiError

ops_logger = get_operation_logger(__name__)


def _reservation_from_row(
    row: queries.SelectReservationsRow | queries.UpdateReservationsRow,
) -> CancelReservationResponse:
    return CancelReservationResponse(
        reservation_id=row.reservation_id,
        resource_id=row.resource_id,
        owner_principal_id=row.owner_principal_id,
        start_at=row.start_at,
        end_at=row.end_at,
        purpose=row.purpose,
        status=ReservationStatus(row.status),
        version=row.row_version,
    )


async def get_reservation(
    reservation_id: ResourceId,
    session: AsyncSession | None = None,
) -> CancelReservationResponse:
    """取消対象の予約と版を確認するため、指定した予約を取得する。"""
    if session is not None:
        rows = await queries.select_reservations(
            session,
            queries.SelectReservationsParams(reservation_id=reservation_id),
        )
        if not rows:
            raise ApiFunctionError(
                status.HTTP_404_NOT_FOUND,
                "reservation_not_found",
                summary="取消対象の予約が存在しない場合。",
            )
        return _reservation_from_row(rows[0])
    return raise_missing_runtime_dependency("get_reservation")


async def has_reservation_cancel_permission(
    reservation: CancelReservationResponse,
    caller: CallerIdentity,
) -> bool:
    """呼び出し元が予約者本人または管理者であるかを判定する。"""
    return (
        IdentityGroup.ADMIN in caller.groups
        or reservation.owner_principal_id == caller.principal_id
    )


async def update_resource_control_version(
    reservation: CancelReservationResponse,
    session: AsyncSession | None = None,
) -> ResourceRef:
    """同一資源の再予約と取消を競合させるため、資源の内部制御版を進める。"""
    if session is not None:
        row = await queries.update_resources_control_version(
            session,
            queries.UpdateResourcesControlVersionParams(resource_id=reservation.resource_id),
        )
        if row is None:
            raise ApiFunctionError(
                status.HTTP_404_NOT_FOUND,
                "resource_not_found",
                summary="取消対象の予約の資源が存在しない場合。",
            )
        return ResourceRef(
            resource_id=row.resource_id,
            active=row.active,
            row_version=row.row_version,
        )
    return raise_missing_runtime_dependency("update_resource_control_version")


async def is_current_reservation_version(
    reservation: CancelReservationResponse,
    request: CancelReservationRequest,
) -> bool:
    """取消要求の版が予約の現在の版と一致するかを判定する。"""
    return reservation.version == request.version


async def is_confirmed_reservation(reservation: CancelReservationResponse) -> bool:
    """予約が取消前の確定状態であるかを判定する。"""
    return reservation.status == ReservationStatus.CONFIRMED


async def is_started_reservation(reservation: CancelReservationResponse, clock: Clock) -> bool:
    """予約の開始時刻が現在時刻以前であるかを判定する。"""
    return reservation.start_at <= clock.now()


async def update_reservation_status(
    reservation: CancelReservationResponse,
    session: AsyncSession | None = None,
) -> CancelReservationResponse:
    """予約を取消状態へ変更し、版を進める。"""
    if session is not None:
        row = await queries.update_reservations(
            session,
            queries.UpdateReservationsParams(reservation_id=reservation.reservation_id),
        )
        if row is None:
            raise ApiFunctionError(
                status.HTTP_404_NOT_FOUND,
                "reservation_not_found",
                summary="取消時点で予約が存在しない場合。",
            )
        return _reservation_from_row(row)
    return raise_missing_runtime_dependency("update_reservation_status")


async def append_reservation_cancelled_event(
    reservation: CancelReservationResponse,
    caller: CallerIdentity,
    clock: Clock,
    session: AsyncSession | None = None,
) -> EventRef:
    """予約取消の履歴を取消と同じtransactionで追記する。"""
    if session is not None:
        event_id = str(uuid4())
        await queries.insert_reservation_events(
            session,
            queries.InsertReservationEventsParams(
                event_id=event_id,
                reservation_id=reservation.reservation_id,
                actor_principal_id=caller.principal_id,
                occurred_at=clock.now(),
            ),
        )
        return EventRef(event_id=event_id)
    return raise_missing_runtime_dependency("append_reservation_cancelled_event")


async def build_reservation_response(
    reservation: CancelReservationResponse,
) -> CancelReservationResponse:
    """取消後の予約のレスポンスを組み立てる。"""
    return CancelReservationResponse(
        reservation_id=reservation.reservation_id,
        resource_id=reservation.resource_id,
        owner_principal_id=reservation.owner_principal_id,
        start_at=reservation.start_at,
        end_at=reservation.end_at,
        purpose=reservation.purpose,
        status=reservation.status,
        version=reservation.version,
    )


def _rejection_context(
    reservation_id: ResourceId,
    request: CancelReservationRequest,
    caller: CallerIdentity,
    status_code: int,
    detail: str,
) -> dict[str, object]:
    return router_log_context(
        status_code=status_code,
        detail=detail,
        caller=caller,
        resource={"reservationId": reservation_id, "version": request.version},
    )


async def build_caller_cannot_cancel_reservation_response(
    reservation_id: ResourceId,
    request: CancelReservationRequest,
    caller: CallerIdentity,
) -> JSONResponse:
    """予約取消の権限がない場合の運用ログと error response を組み立てる。"""
    context = _rejection_context(
        reservation_id, request, caller, status.HTTP_403_FORBIDDEN, "forbidden"
    )
    ops_logger.warning(
        "cancelReservation.caller_cannot_cancel_reservation",
        catalog_id="M001",
        summary="呼び出し元が予約者本人でも管理者でもないため、予約取消を拒否した。",
        status_code=status.HTTP_403_FORBIDDEN,
        detail="forbidden",
        when="呼び出し元が予約者本人でも管理者でもない場合。",
        why_production="他人の予約の取消試行を運用で追跡するため。",
        context_model=operational_log_context_model(
            trace_id=None,
            actor_principal_id=caller.principal_id,
            api_status_code=status.HTTP_403_FORBIDDEN,
            resource_reservation_id=reservation_id,
            error_code=error_code_for_status(status.HTTP_403_FORBIDDEN),
            error_message="forbidden",
        ),
        operator_action="actorPrincipalIdとreservationIdの所有者を確認する。",
        runbook="RUNBOOK-authorization-forbidden",
        context=context,
    )
    return api_error_response(status.HTTP_403_FORBIDDEN, "forbidden")


async def build_stale_reservation_version_response(
    reservation_id: ResourceId,
    request: CancelReservationRequest,
    caller: CallerIdentity,
) -> JSONResponse:
    """予約の版が古い場合の運用ログと error response を組み立てる。"""
    context = _rejection_context(
        reservation_id, request, caller, status.HTTP_409_CONFLICT, "stale_version"
    )
    ops_logger.warning(
        "cancelReservation.stale_reservation_version",
        catalog_id="M002",
        summary="予約の版が現在値と一致しないため、予約取消を拒否した。",
        status_code=status.HTTP_409_CONFLICT,
        detail="stale_version",
        when="取消要求のversionが予約の現在の版と一致しない場合。",
        why_production="同時操作による取消の競合を運用で確認するため。",
        context_model=operational_log_context_model(
            trace_id=None,
            actor_principal_id=caller.principal_id,
            api_status_code=status.HTTP_409_CONFLICT,
            resource_reservation_id=reservation_id,
            error_code=error_code_for_status(status.HTTP_409_CONFLICT),
            error_message="stale_version",
        ),
        operator_action="利用者へ予約を再取得して取消し直すよう案内する。",
        runbook="RUNBOOK-optimistic-lock-conflict",
        context=context,
    )
    return api_error_response(
        status.HTTP_409_CONFLICT,
        "stale_version",
        resource={"reservationId": reservation_id, "version": request.version},
    )


async def build_reservation_already_cancelled_response(
    reservation_id: ResourceId,
    request: CancelReservationRequest,
    caller: CallerIdentity,
) -> JSONResponse:
    """取消済み予約への取消を拒否する場合の運用ログと error response を組み立てる。"""
    context = _rejection_context(
        reservation_id, request, caller, status.HTTP_409_CONFLICT, "already_cancelled"
    )
    ops_logger.warning(
        "cancelReservation.reservation_already_cancelled",
        catalog_id="M003",
        summary="予約が取消済みのため、予約取消を拒否した。",
        status_code=status.HTTP_409_CONFLICT,
        detail="already_cancelled",
        when="予約の状態がcancelledの場合。",
        why_production="二重取消の試行を運用で確認するため。",
        context_model=operational_log_context_model(
            trace_id=None,
            actor_principal_id=caller.principal_id,
            api_status_code=status.HTTP_409_CONFLICT,
            resource_reservation_id=reservation_id,
            error_code=error_code_for_status(status.HTTP_409_CONFLICT),
            error_message="already_cancelled",
        ),
        operator_action="予約詳細の履歴で取消済みであることを確認する。",
        runbook="RUNBOOK-reservation-conflict",
        context=context,
    )
    return api_error_response(
        status.HTTP_409_CONFLICT,
        "already_cancelled",
        resource={"reservationId": reservation_id},
    )


async def build_reservation_already_started_response(
    reservation_id: ResourceId,
    request: CancelReservationRequest,
    caller: CallerIdentity,
) -> JSONResponse:
    """開始済み予約への取消を拒否する場合の運用ログと error response を組み立てる。"""
    context = _rejection_context(
        reservation_id, request, caller, status.HTTP_409_CONFLICT, "already_started"
    )
    ops_logger.warning(
        "cancelReservation.reservation_already_started",
        catalog_id="M004",
        summary="予約の開始時刻を過ぎているため、予約取消を拒否した。",
        status_code=status.HTTP_409_CONFLICT,
        detail="already_started",
        when="予約の開始時刻が現在時刻以前の場合。",
        why_production="開始後取消の試行を運用で確認するため。",
        context_model=operational_log_context_model(
            trace_id=None,
            actor_principal_id=caller.principal_id,
            api_status_code=status.HTTP_409_CONFLICT,
            resource_reservation_id=reservation_id,
            error_code=error_code_for_status(status.HTTP_409_CONFLICT),
            error_message="already_started",
        ),
        operator_action="開始済み予約は取消できないことを利用者へ案内する。",
        runbook="RUNBOOK-reservation-conflict",
        context=context,
    )
    return api_error_response(
        status.HTTP_409_CONFLICT,
        "already_started",
        resource={"reservationId": reservation_id},
    )


async def build_router_error_response(
    reservation_id: ResourceId,
    request: CancelReservationRequest,
    caller: CallerIdentity,
    error: ApiFunctionError | ExternalApiError | HTTPException,
) -> JSONResponse:
    """Router で捕捉した例外を運用ログと HTTP error response に変換する。"""
    ops_logger.error(
        router_error_message_id("cancelReservation", error),
        catalog_id="M005",
        summary=router_error_summary(
            "Routerで捕捉した例外により予約取消が失敗した。",
            error,
        ),
        when="ROUTER_HANDLED_EXCEPTIONSを捕捉した場合。",
        check_procedure="traceIdでログを検索し、routerで捕捉された例外種別とreservationIdを確認する。",
        remediation_procedure="予約を再取得し、最新の版で再送する。",
        context_model=operational_log_context_model(
            trace_id=None,
            actor_principal_id=caller.principal_id,
            api_status_code=status_code_for_router_error(error),
            resource_reservation_id=reservation_id,
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
            resource={"reservationId": reservation_id, "version": request.version},
            error=error,
        ),
    )
    return error_response_for_router_error(error)
