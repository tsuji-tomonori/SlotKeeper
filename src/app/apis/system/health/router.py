from fastapi import APIRouter, status
from starlette.responses import JSONResponse

from app.apis.responses import error_responses, success_response
from app.apis.router_errors import ROUTER_HANDLED_EXCEPTIONS
from app.apis.system.health import functions as api_functions
from app.apis.system.health.samples import HEALTH_RESPONSE_SAMPLE, HEALTH_STATUS_SAMPLES
from app.apis.system.health.schemas import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    operation_id="health",
    summary="稼働状態を取得する",
    description="秘密やDB情報を含まない稼働状態を返します。認証は不要です。",
    response_model=HealthResponse,
    responses={
        status.HTTP_200_OK: success_response(HEALTH_RESPONSE_SAMPLE),
        **error_responses(samples=HEALTH_STATUS_SAMPLES),
    },
    tags=["system"],
)
async def health() -> HealthResponse | JSONResponse:
    try:
        return await api_functions.build_health_response()
    except ROUTER_HANDLED_EXCEPTIONS as error:
        return await api_functions.build_router_error_response(error)
