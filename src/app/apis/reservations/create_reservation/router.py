from typing import Annotated

from fastapi import APIRouter, Body, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.apis.base import sample_value
from app.apis.deps import get_caller_identity, get_clock
from app.apis.reservations.create_reservation import functions as api_functions
from app.apis.reservations.create_reservation.samples import (
    CREATE_RESERVATION_REQUEST_SAMPLE,
    CREATE_RESERVATION_RESPONSE_SAMPLE,
    CREATE_RESERVATION_STATUS_SAMPLES,
)
from app.apis.reservations.create_reservation.schemas import (
    CreateReservationRequest,
    CreateReservationResponse,
)
from app.apis.responses import error_responses, success_response
from app.apis.router_errors import ROUTER_HANDLED_EXCEPTIONS
from app.apis.sequence_types import CallerIdentity, Clock
from app.apis.types import IdempotencyKey
from app.db.session import get_session, retry_transaction

router = APIRouter()


@router.post(
    "/reservations",
    operation_id="createReservation",
    summary="予約を作成する",
    description=(
        "資源・開始・終了・目的を指定して自分名義の予約を作成します。"
        "同じIdempotency-Keyの再送には24時間、元の作成応答を返します。"
    ),
    response_model=CreateReservationResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: success_response(CREATE_RESERVATION_RESPONSE_SAMPLE),
        **error_responses(
            status.HTTP_404_NOT_FOUND,
            status.HTTP_409_CONFLICT,
            samples=CREATE_RESERVATION_STATUS_SAMPLES,
        ),
    },
    tags=["reservations"],
)
@retry_transaction(replay_safe=True)
async def create_reservation(
    request: Annotated[
        CreateReservationRequest,
        Body(
            openapi_examples={"default": {"value": sample_value(CREATE_RESERVATION_REQUEST_SAMPLE)}}
        ),
    ],
    idempotency_key: Annotated[IdempotencyKey, Header(alias="Idempotency-Key")],
    caller: Annotated[CallerIdentity, Depends(get_caller_identity)],
    clock: Annotated[Clock, Depends(get_clock)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CreateReservationResponse | JSONResponse:
    try:
        idempotency_record = await api_functions.get_idempotency_record(
            idempotency_key,
            caller,
            clock,
            session,
        )
        if await api_functions.has_idempotency_result(idempotency_record):
            if not await api_functions.is_same_idempotent_request(idempotency_record, request):
                return await api_functions.build_idempotency_key_reused_response(
                    request,
                    idempotency_key,
                    caller,
                )
            return await api_functions.build_replayed_reservation_response(idempotency_record)
        validated_request = await api_functions.validate_booking_request(request, clock)
        resource = await api_functions.update_resource_control_version(validated_request.resource_id, session)
        if not await api_functions.is_active_resource(resource):
            return await api_functions.build_resource_inactive_response(
                request,
                idempotency_key,
                caller,
            )
        if await api_functions.has_overlapping_reservation(validated_request, session):
            return await api_functions.build_slot_taken_response(
                request,
                idempotency_key,
                caller,
            )
        await api_functions.delete_expired_idempotency_record(idempotency_record, caller, session)
        await api_functions.save_reservation_owner(caller, clock, session)
        reservation = await api_functions.save_reservation(validated_request, caller, session)
        await api_functions.append_reservation_created_event(reservation, caller, clock, session)
        await api_functions.create_idempotency_record(
            idempotency_key,
            validated_request,
            reservation,
            clock,
            session,
        )
        await session.commit()
        return await api_functions.build_reservation_response(reservation)
    except ROUTER_HANDLED_EXCEPTIONS as error:
        return await api_functions.build_router_error_response(
            request,
            idempotency_key,
            caller,
            error,
        )
