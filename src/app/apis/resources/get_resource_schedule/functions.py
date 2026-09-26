from __future__ import annotations

from datetime import datetime, time, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.apis.common import (
    JST,
    IdentityGroup,
    decode_page_token,
    encode_page_token,
    raise_missing_runtime_dependency,
)
from app.apis.exceptions import ApiFunctionError
from app.apis.reservations.common import BUSY_SLOT_LABEL, ReservationStatus
from app.apis.resources.get_resource_schedule.generated import queries
from app.apis.resources.get_resource_schedule.schemas import (
    GetResourceScheduleQuery,
    GetResourceScheduleResponse,
    ScheduleReservationResponse,
    ScheduleSlotResponse,
)
from app.apis.router_errors import (
    error_code_for_status,
    error_response_for_router_error,
    router_error_message_id,
    router_error_summary,
    router_log_context,
    status_code_for_router_error,
)
from app.apis.sequence_types import CallerIdentity, SequencePage
from app.apis.types import ResourceId
from app.core.logging import get_operation_logger, operational_log_context_model
from app.integrations.common_errors import ExternalApiError

ops_logger = get_operation_logger(__name__)


async def get_resource(
    resource_id: ResourceId,
    session: AsyncSession | None = None,
) -> ResourceId:
    """予約表の対象資源が存在することを確認して資源IDを取得する。"""
    if session is not None:
        rows = await queries.select_resources(
            session,
            queries.SelectResourcesParams(resource_id=resource_id),
        )
        if not rows:
            raise ApiFunctionError(
                status.HTTP_404_NOT_FOUND,
                "resource_not_found",
                summary="予約表の対象資源が存在しない場合。",
            )
        return rows[0].resource_id
    return raise_missing_runtime_dependency("get_resource")


async def get_resource_bookings(
    resource_id: ResourceId,
    query: GetResourceScheduleQuery,
    session: AsyncSession | None = None,
) -> SequencePage[ScheduleReservationResponse]:
    """日本時間の指定日に重なる確定予約を開始日時とIDの順に取得する。"""
    if session is not None:
        day_start = datetime.combine(query.day, time(), JST)
        after = decode_page_token(query.next_token, 2)
        rows = await queries.select_reservations(
            session,
            queries.SelectReservationsParams(
                resource_id=resource_id,
                day_end=day_start + timedelta(days=1),
                day_start=day_start,
                after_start_at=datetime.fromisoformat(after[0]) if after else None,
                after_reservation_id=after[1] if after else None,
                limit=query.limit + 1,
            ),
        )
        items = [
            ScheduleReservationResponse(
                reservation_id=row.reservation_id,
                resource_id=row.resource_id,
                owner_principal_id=row.owner_principal_id,
                start_at=row.start_at,
                end_at=row.end_at,
                purpose=row.purpose,
                status=ReservationStatus(row.status),
                version=row.row_version,
            )
            for row in rows
        ]
        return SequencePage(items=items, next_token=None)
    return raise_missing_runtime_dependency("get_resource_bookings")


async def apply_pagination(
    bookings: SequencePage[ScheduleReservationResponse],
    query: GetResourceScheduleQuery,
) -> SequencePage[ScheduleReservationResponse]:
    """取得した予約を上限件数へ切り詰め、次ページの継続tokenを付与する。"""
    items = list(bookings.items)
    if len(items) <= query.limit:
        return SequencePage(items=items, next_token=None)
    page = items[: query.limit]
    last = page[-1]
    return SequencePage(
        items=page,
        next_token=encode_page_token([last.start_at.isoformat(), last.reservation_id]),
    )


async def build_resource_schedule_response(
    page: SequencePage[ScheduleReservationResponse],
    caller: CallerIdentity,
) -> GetResourceScheduleResponse:
    """本人と管理者以外には予約済み時間帯と表示名だけを返す予約表を組み立てる。"""
    is_admin = IdentityGroup.ADMIN in caller.groups
    return GetResourceScheduleResponse(
        items=[
            ScheduleSlotResponse(
                start_at=booking.start_at,
                end_at=booking.end_at,
                label=BUSY_SLOT_LABEL,
                reservation=(
                    booking
                    if is_admin or booking.owner_principal_id == caller.principal_id
                    else None
                ),
            )
            for booking in page.items
        ],
        next_token=page.next_token,
    )


async def build_router_error_response(
    resource_id: ResourceId,
    query: GetResourceScheduleQuery,
    caller: CallerIdentity,
    error: ApiFunctionError | ExternalApiError | HTTPException,
) -> JSONResponse:
    """Router で捕捉した例外を運用ログと HTTP error response に変換する。"""
    ops_logger.error(
        router_error_message_id("getResourceSchedule", error),
        catalog_id="M001",
        summary=router_error_summary(
            "Routerで捕捉した例外により予約表取得が失敗した。",
            error,
        ),
        when="ROUTER_HANDLED_EXCEPTIONSを捕捉した場合。",
        check_procedure="traceIdでログを検索し、routerで捕捉された例外種別とresourceIdを確認する。",
        remediation_procedure="資源IDと日付を確認し、継続tokenを破棄して先頭ページから再取得する。",
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
            resource={"resourceId": resource_id, "day": query.day.isoformat()},
            error=error,
        ),
    )
    return error_response_for_router_error(error)
