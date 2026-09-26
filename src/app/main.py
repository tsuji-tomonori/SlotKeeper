from collections.abc import Awaitable, Callable
from time import monotonic
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.apis.reservations.cancel_reservation.router import router as cancel_reservation_router
from app.apis.reservations.create_reservation.router import router as create_reservation_router
from app.apis.reservations.get_reservation.router import router as get_reservation_router
from app.apis.reservations.list_reservations.router import router as list_reservations_router
from app.apis.resources.create_resource.router import router as create_resource_router
from app.apis.resources.get_resource_schedule.router import (
    router as get_resource_schedule_router,
)
from app.apis.resources.list_resources.router import router as list_resources_router
from app.apis.resources.update_resource.router import router as update_resource_router
from app.apis.router_errors import api_error_response
from app.core.config import settings
from app.core.logging import (
    bind_log_context,
    configure_operational_logging,
    get_operation_logger,
    reset_log_context,
)

ops_logger = get_operation_logger(__name__)


async def health() -> dict[str, str]:
    """秘密やDB情報を含まない稼働状態を返す。"""
    return {"status": "ok"}


async def request_log(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """予約目的、token、URLの生値を記録せず、要求ID・操作・結果・所要時間を残す。"""
    request_id = str(uuid4())
    request.state.request_id = request_id
    token = bind_log_context(traceId=request_id, requestId=request_id)
    started = monotonic()
    try:
        response = await call_next(request)
        route = request.scope.get("route")
        ops_logger.info(
            "http.request_completed",
            catalog_id="H001",
            summary="HTTP要求の処理が完了した。",
            context={
                "api": {
                    "operation": getattr(route, "operation_id", None) or "unmatched",
                    "statusCode": response.status_code,
                },
                "metrics": {"durationMs": round((monotonic() - started) * 1000, 2)},
            },
        )
    finally:
        reset_log_context(token)
    response.headers["X-Request-ID"] = request_id
    response.headers["Cache-Control"] = "no-store"
    return response


async def http_exception_response(request: Request, error: Exception) -> Response:
    """認証依存などのHTTPExceptionを共通error schemaへ変換する。"""
    _ = request
    if not isinstance(error, HTTPException):
        raise error
    return api_error_response(error.status_code, str(error.detail))


async def validation_error_response(request: Request, error: Exception) -> JSONResponse:
    """不正入力の値や認証情報を応答へ反射せず共通error schemaを返す。"""
    _ = request, error
    return api_error_response(status.HTTP_422_UNPROCESSABLE_CONTENT, "invalid_input")


def create_app() -> FastAPI:
    configure_operational_logging()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.cors_origin],
        allow_methods=["GET", "POST", "PUT"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
        expose_headers=["X-Request-ID"],
    )
    app.middleware("http")(request_log)
    app.add_exception_handler(HTTPException, http_exception_response)
    app.add_exception_handler(RequestValidationError, validation_error_response)

    app.add_api_route("/health", health, methods=["GET"], tags=["system"], operation_id="health")
    app.include_router(list_resources_router)
    app.include_router(create_resource_router)
    app.include_router(update_resource_router)
    app.include_router(get_resource_schedule_router)
    app.include_router(list_reservations_router)
    app.include_router(create_reservation_router)
    app.include_router(get_reservation_router)
    app.include_router(cancel_reservation_router)

    return app


app = create_app()
