from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.apis.deps import get_caller_identity, get_clock
from app.apis.reservations.list_reservations import functions as api_functions
from app.apis.reservations.list_reservations.samples import (
    LIST_RESERVATIONS_RESPONSE_SAMPLE,
    LIST_RESERVATIONS_STATUS_SAMPLES,
)
from app.apis.reservations.list_reservations.schemas import (
    ListReservationsQuery,
    ListReservationsResponse,
)
from app.apis.responses import error_responses, success_response
from app.apis.router_errors import ROUTER_HANDLED_EXCEPTIONS
from app.apis.sequence_types import CallerIdentity, Clock
from app.db.session import get_session, retry_transaction

router = APIRouter()


@router.get(
    "/reservations",
    operation_id="listReservations",
    summary="自分の予約一覧を取得する",
    description="呼び出し元本人の予約だけを日本時間の日付・状態で絞り込み、開始日時とIDの順に取得します。",
    response_model=ListReservationsResponse,
    responses={
        status.HTTP_200_OK: success_response(LIST_RESERVATIONS_RESPONSE_SAMPLE),
        **error_responses(samples=LIST_RESERVATIONS_STATUS_SAMPLES),
    },
    tags=["reservations"],
)
@retry_transaction(replay_safe=True)
async def list_reservations(
    query: Annotated[ListReservationsQuery, Query()],
    caller: Annotated[CallerIdentity, Depends(get_caller_identity)],
    clock: Annotated[Clock, Depends(get_clock)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ListReservationsResponse | JSONResponse:
    try:
        reservations = await api_functions.get_own_reservations(query, caller, clock, session)
        page = await api_functions.apply_pagination(reservations, query)
        return await api_functions.build_reservation_list_response(page)
    except ROUTER_HANDLED_EXCEPTIONS as error:
        return await api_functions.build_router_error_response(query, caller, error)
