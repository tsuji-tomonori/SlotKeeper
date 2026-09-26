from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.apis.base import sample_path_value, sample_value
from app.apis.deps import get_caller_identity, get_clock
from app.apis.reservations.cancel_reservation import functions as api_functions
from app.apis.reservations.cancel_reservation.samples import (
    CANCEL_RESERVATION_REQUEST_SAMPLE,
    CANCEL_RESERVATION_RESPONSE_SAMPLE,
    CANCEL_RESERVATION_STATUS_SAMPLES,
)
from app.apis.reservations.cancel_reservation.schemas import (
    CancelReservationRequest,
    CancelReservationResponse,
)
from app.apis.responses import error_responses, success_response
from app.apis.router_errors import ROUTER_HANDLED_EXCEPTIONS
from app.apis.sequence_types import CallerIdentity, Clock
from app.apis.types import ResourceId
from app.db.session import get_session, retry_transaction

router = APIRouter()


@router.post(
    "/reservations/{reservationId}/cancel",
    operation_id="cancelReservation",
    summary="予約を取消す",
    description=(
        "予約者本人または管理者が、開始前の確定予約を版つきで取消します。"
        "取消と取消履歴は同じtransactionで確定します。"
    ),
    response_model=CancelReservationResponse,
    responses={
        status.HTTP_200_OK: success_response(CANCEL_RESERVATION_RESPONSE_SAMPLE),
        **error_responses(
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_409_CONFLICT,
            samples=CANCEL_RESERVATION_STATUS_SAMPLES,
        ),
    },
    tags=["reservations"],
)
@retry_transaction()
async def cancel_reservation(
    reservation_id: Annotated[
        ResourceId,
        Path(
            alias="reservationId",
            description="予約を一意に識別するIDです。",
            json_schema_extra={
                "default": sample_path_value(CANCEL_RESERVATION_RESPONSE_SAMPLE, "reservationId")
            },
        ),
    ],
    request: Annotated[
        CancelReservationRequest,
        Body(
            openapi_examples={"default": {"value": sample_value(CANCEL_RESERVATION_REQUEST_SAMPLE)}}
        ),
    ],
    caller: Annotated[CallerIdentity, Depends(get_caller_identity)],
    clock: Annotated[Clock, Depends(get_clock)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CancelReservationResponse | JSONResponse:
    try:
        reservation = await api_functions.get_reservation(reservation_id, session)
        if not await api_functions.has_reservation_cancel_permission(reservation, caller):
            return await api_functions.build_caller_cannot_cancel_reservation_response(
                reservation_id,
                request,
                caller,
            )
        await api_functions.get_locked_resource(reservation, session)
        if not await api_functions.is_current_reservation_version(reservation, request):
            return await api_functions.build_stale_reservation_version_response(
                reservation_id,
                request,
                caller,
            )
        if not await api_functions.is_confirmed_reservation(reservation):
            return await api_functions.build_reservation_already_cancelled_response(
                reservation_id,
                request,
                caller,
            )
        if await api_functions.is_started_reservation(reservation, clock):
            return await api_functions.build_reservation_already_started_response(
                reservation_id,
                request,
                caller,
            )
        cancelled = await api_functions.update_reservation_status(reservation, session)
        await api_functions.append_reservation_cancelled_event(cancelled, caller, clock, session)
        await session.commit()
        return await api_functions.build_reservation_response(cancelled)
    except ROUTER_HANDLED_EXCEPTIONS as error:
        return await api_functions.build_router_error_response(
            reservation_id,
            request,
            caller,
            error,
        )
