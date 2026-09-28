from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.apis.common import IdentityGroup, raise_missing_runtime_dependency
from app.apis.exceptions import ApiFunctionError
from app.apis.reservations.common import ReservationAction, ReservationStatus
from app.apis.reservations.get_reservation.generated import queries
from app.apis.reservations.get_reservation.schemas import (
    GetReservationResponse,
    ReservationDetailResponse,
    ReservationEventResponse,
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
from app.apis.types import ResourceId
from app.core.logging import get_operation_logger, operational_log_context_model
from app.integrations.common_errors import ExternalApiError

ops_logger = get_operation_logger(__name__)


async def get_reservation(
    reservation_id: ResourceId,
    session: AsyncSession | None = None,
) -> ReservationDetailResponse:
    """予約詳細を返すため、指定した予約を取得する。"""
    if session is not None:
        rows = await queries.select_reservations(
            session,
            queries.SelectReservationsParams(reservation_id=reservation_id),
        )
        if not rows:
            raise ApiFunctionError(
                status.HTTP_404_NOT_FOUND,
                "reservation_not_found",
                summary="指定された予約が存在しない場合。",
            )
        row = rows[0]
        return ReservationDetailResponse(
            reservation_id=row.reservation_id,
            resource_id=row.resource_id,
            owner_principal_id=row.owner_principal_id,
            start_at=row.start_at,
            end_at=row.end_at,
            purpose=row.purpose,
            status=ReservationStatus(row.status),
            version=row.row_version,
        )
    return raise_missing_runtime_dependency("get_reservation")


async def has_reservation_view_permission(
    reservation: ReservationDetailResponse,
    caller: CallerIdentity,
) -> bool:
    """呼び出し元が予約者本人または管理者であるかを判定する。"""
    return (
        IdentityGroup.ADMIN in caller.groups
        or reservation.owner_principal_id == caller.principal_id
    )


async def get_reservation_events(
    reservation: ReservationDetailResponse,
    session: AsyncSession | None = None,
) -> list[ReservationEventResponse]:
    """予約の作成と取消の履歴を発生順に取得する。"""
    if session is not None:
        rows = await queries.select_reservation_events(
            session,
            queries.SelectReservationEventsParams(reservation_id=reservation.reservation_id),
        )
        return [
            ReservationEventResponse(
                event_id=row.event_id,
                reservation_id=row.reservation_id,
                actor_principal_id=row.actor_principal_id,
                action=ReservationAction(row.action),
                occurred_at=row.occurred_at,
            )
            for row in rows
        ]
    return raise_missing_runtime_dependency("get_reservation_events")


async def build_reservation_detail_response(
    reservation: ReservationDetailResponse,
    events: list[ReservationEventResponse],
) -> GetReservationResponse:
    """予約詳細と操作履歴のレスポンスを組み立てる。"""
    return GetReservationResponse(reservation=reservation, events=events)


async def build_caller_cannot_view_reservation_response(
    reservation_id: ResourceId,
    caller: CallerIdentity,
) -> JSONResponse:
    """予約詳細の参照権限がない場合の運用ログと error response を組み立てる。"""
    ops_logger.warning(
        "getReservation.caller_cannot_view_reservation",
        catalog_id="M001",
        summary="呼び出し元が予約者本人でも管理者でもないため、予約詳細の参照を拒否した。",
        status_code=status.HTTP_403_FORBIDDEN,
        detail="forbidden",
        when="呼び出し元が予約者本人でも管理者でもない場合。",
        why_production="他人の予約目的や履歴の参照試行を運用で追跡するため。",
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
        context=router_log_context(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="forbidden",
            caller=caller,
            resource={"reservationId": reservation_id},
        ),
    )
    return api_error_response(status.HTTP_403_FORBIDDEN, "forbidden")


async def build_router_error_response(
    reservation_id: ResourceId,
    caller: CallerIdentity,
    error: ApiFunctionError | ExternalApiError | HTTPException,
) -> JSONResponse:
    """Router で捕捉した例外を運用ログと HTTP error response に変換する。"""
    ops_logger.error(
        router_error_message_id("getReservation", error),
        catalog_id="M002",
        summary=router_error_summary(
            "Routerで捕捉した例外により予約詳細取得が失敗した。",
            error,
        ),
        when="ROUTER_HANDLED_EXCEPTIONSを捕捉した場合。",
        check_procedure="traceIdでログを検索し、routerで捕捉された例外種別とreservationIdを確認する。",
        remediation_procedure="予約IDを確認し、予約一覧から再取得する。",
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
            resource={"reservationId": reservation_id},
            error=error,
        ),
    )
    return error_response_for_router_error(error)
