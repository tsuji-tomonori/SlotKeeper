"""HTTP境界で公開例外と構造化ログを生成する。"""

import importlib
import json
import logging
from collections.abc import Awaitable, Callable
from time import monotonic
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum

from slotkeeper.domain import DomainError, ErrorBody
from slotkeeper.settings import settings

app = FastAPI(
    title="SlotKeeper",
    version="0.1.0",
    responses={s: {"model": ErrorBody} for s in (401, 403, 404, 409, 422, 503)},
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings().cors_origin],
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
    expose_headers=["X-Request-ID"],
)
for operation in (
    "resources_list",
    "resources_create",
    "resources_update",
    "schedule",
    "reservations_list",
    "reservations_create",
    "reservations_get",
    "reservations_cancel",
):
    app.include_router(
        importlib.import_module("slotkeeper.operations." + operation + ".endpoint").router
    )


@app.middleware("http")
async def request_log(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """予約目的、token、URLの生値を記録せず結果と所要時間を残す。"""
    request.state.request_id = str(uuid4())
    started = monotonic()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    response.headers["Cache-Control"] = "no-store"
    route = request.scope.get("route")
    logging.getLogger("slotkeeper").info(
        json.dumps(
            {
                "request_id": request.state.request_id,
                "operation": getattr(route, "operation_id", "unmatched"),
                "status": response.status_code,
                "elapsed_ms": round((monotonic() - started) * 1000, 2),
            }
        )
    )
    return response


@app.exception_handler(DomainError)
async def domain_error(request: Request, exc: DomainError) -> JSONResponse:
    """業務例外の固定コードだけを公開する。"""
    return JSONResponse(
        status_code=exc.status, content={"code": exc.code, "request_id": request.state.request_id}
    )


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """不正入力の値や認証情報を応答へ反射しない。"""
    return JSONResponse(
        status_code=422, content={"code": "invalid_input", "request_id": request.state.request_id}
    )


@app.get("/health", operation_id="health", tags=["system"])
def health() -> dict[str, str]:
    """秘密やDB情報を含まない稼働状態を返す。"""
    return {"status": "ok"}


handler = Mangum(app, lifespan="off")
