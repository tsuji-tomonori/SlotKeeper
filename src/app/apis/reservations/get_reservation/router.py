from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.apis.base import sample_path_value
from app.apis.deps import get_caller_identity
from app.apis.reservations.get_reservation import functions as api_functions
from app.apis.reservations.get_reservation.samples import (
    GET_RESERVATION_RESPONSE_SAMPLE,
    GET_RESERVATION_STATUS_SAMPLES,
)
from app.apis.reservations.get_reservation.schemas import GetReservationResponse
from app.apis.responses import error_responses, success_response
from app.apis.router_errors import ROUTER_HANDLED_EXCEPTIONS
from app.apis.sequence_types import CallerIdentity
from app.apis.types import ResourceId
from app.db.session import get_session, retry_transaction

router = APIRouter()


@router.get(
    "/reservations/{reservationId}",
    operation_id="getReservation",
    summary="予約詳細を取得する",
    description="予約者本人または管理者に限り、予約の詳細と作成・取消の履歴を取得します。",
    response_model=GetReservationResponse,
    responses={
        status.HTTP_200_OK: success_response(GET_RESERVATION_RESPONSE_SAMPLE),
        **error_responses(
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
            samples=GET_RESERVATION_STATUS_SAMPLES,
        ),
    },
    tags=["reservations"],
)
@retry_transaction(replay_safe=True)
async def get_reservation(
    reservation_id: Annotated[
        ResourceId,
        Path(
            alias="reservationId",
            description="予約を一意に識別するIDです。",
            json_schema_extra={
                "default": sample_path_value(GET_RESERVATION_RESPONSE_SAMPLE, "reservationId")
            },
        ),
    ],
    caller: Annotated[CallerIdentity, Depends(get_caller_identity)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GetReservationResponse | JSONResponse:
    try:
        reservation = await api_functions.get_reservation(reservation_id, session)
        if not await api_functions.has_reservation_view_permission(reservation, caller):
            return await api_functions.build_caller_cannot_view_reservation_response(
                reservation_id,
                caller,
            )
        events = await api_functions.get_reservation_events(reservation, session)
        return await api_functions.build_reservation_detail_response(reservation, events)
    except ROUTER_HANDLED_EXCEPTIONS as error:
        return await api_functions.build_router_error_response(reservation_id, caller, error)
