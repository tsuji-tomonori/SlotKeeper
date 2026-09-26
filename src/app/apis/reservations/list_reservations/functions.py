from __future__ import annotations

from datetime import UTC, datetime, time, timedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.apis.common import (
    JST,
    decode_page_token,
    encode_page_token,
    raise_missing_runtime_dependency,
)
from app.apis.exceptions import ApiFunctionError
from app.apis.reservations.common import ReservationStatus
from app.apis.reservations.list_reservations.generated import queries
from app.apis.reservations.list_reservations.schemas import (
    ListReservationsQuery,
    ListReservationsResponse,
    ReservationItemResponse,
)
from app.apis.router_errors import (
    error_code_for_status,
    error_response_for_router_error,
    router_error_message_id,
    router_error_summary,
    router_log_context,
    status_code_for_router_error,
)
from app.apis.sequence_types import CallerIdentity, Clock, SequencePage
from app.core.logging import get_operation_logger, operational_log_context_model
from app.integrations.common_errors import ExternalApiError

ops_logger = get_operation_logger(__name__)

EARLIEST = datetime(1970, 1, 1, tzinfo=UTC)
LATEST = datetime(9999, 1, 1, tzinfo=UTC)


async def get_own_reservations(
    query: ListReservationsQuery,
    caller: CallerIdentity,
    clock: Clock,
    session: AsyncSession | None = None,
) -> SequencePage[ReservationItemResponse]:
    """呼び出し元本人の予約だけを日本時間の日付と状態で絞り込み、固定順で取得する。"""
    if session is not None:
        range_start = datetime.combine(query.day, time(), JST) if query.day else EARLIEST
        range_end = range_start + timedelta(days=1) if query.day else LATEST
        after = decode_page_token(query.next_token, 2)
        rows = await queries.select_reservations(
            session,
            queries.SelectReservationsParams(
                owner_principal_id=caller.principal_id,
                range_end=range_end,
                range_start=range_start,
                status=query.status,
                future_only=query.future,
                now=clock.now(),
                after_start_at=datetime.fromisoformat(after[0]) if after else None,
                after_reservation_id=after[1] if after else None,
                limit=query.limit + 1,
            ),
        )
        items = [
            ReservationItemResponse(
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
    return raise_missing_runtime_dependency("get_own_reservations")


# @resource-free
async def apply_pagination(
    reservations: SequencePage[ReservationItemResponse],
    query: ListReservationsQuery,
) -> SequencePage[ReservationItemResponse]:
    """取得した予約を上限件数へ切り詰め、次ページの継続tokenを付与する。"""
    items = list(reservations.items)
    if len(items) <= query.limit:
        return SequencePage(items=items, next_token=None)
    page = items[: query.limit]
    last = page[-1]
    return SequencePage(
        items=page,
        next_token=encode_page_token([last.start_at.isoformat(), last.reservation_id]),
    )


async def build_reservation_list_response(
    page: SequencePage[ReservationItemResponse],
) -> ListReservationsResponse:
    """自分の予約一覧レスポンスを組み立てる。"""
    return ListReservationsResponse(items=list(page.items), next_token=page.next_token)


async def build_router_error_response(
    query: ListReservationsQuery,
    caller: CallerIdentity,
    error: ApiFunctionError | ExternalApiError | HTTPException,
) -> JSONResponse:
    """Router で捕捉した例外を運用ログと HTTP error response に変換する。"""
    ops_logger.error(
        router_error_message_id("listReservations", error),
        catalog_id="M001",
        summary=router_error_summary(
            "Routerで捕捉した例外により予約一覧取得が失敗した。",
            error,
        ),
        when="ROUTER_HANDLED_EXCEPTIONSを捕捉した場合。",
        check_procedure="traceIdでログを検索し、routerで捕捉された例外種別と絞り込み条件を確認する。",
        remediation_procedure="継続tokenを破棄して先頭ページから再取得する。",
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
            resource={
                "day": query.day.isoformat() if query.day else None,
                "status": query.status,
            },
            error=error,
        ),
    )
    return error_response_for_router_error(error)
