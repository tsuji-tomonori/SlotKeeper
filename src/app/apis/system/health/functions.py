from __future__ import annotations

from fastapi import HTTPException
from starlette.responses import JSONResponse

from app.apis.exceptions import ApiFunctionError
from app.apis.router_errors import (
    error_code_for_status,
    error_response_for_router_error,
    router_error_message_id,
    router_error_summary,
    router_log_context,
    status_code_for_router_error,
)
from app.apis.system.health.schemas import HealthResponse
from app.core.logging import get_operation_logger, operational_log_context_model
from app.integrations.common_errors import ExternalApiError

ops_logger = get_operation_logger(__name__)


async def build_health_response() -> HealthResponse:
    """@resource-free
    秘密やDB情報を含まない稼働状態を返す。
    """
    return HealthResponse(status="ok")


async def build_router_error_response(
    error: ApiFunctionError | ExternalApiError | HTTPException,
) -> JSONResponse:
    """Router で捕捉した例外を運用ログと HTTP error response に変換する。"""
    ops_logger.error(
        router_error_message_id("health", error),
        catalog_id="M001",
        summary=router_error_summary("Routerで捕捉した例外により稼働確認が失敗した。", error),
        when="ROUTER_HANDLED_EXCEPTIONSを捕捉した場合。",
        check_procedure="traceIdでログを検索し、routerで捕捉された例外種別を確認する。",
        remediation_procedure="APIプロセスの起動状態と直近deployを確認する。",
        context_model=operational_log_context_model(
            trace_id=None,
            api_status_code=status_code_for_router_error(error),
            error_code=error_code_for_status(status_code_for_router_error(error)),
            error_message=str(error),
            error_exception_type=type(error).__name__,
        ),
        operator_action="Lambdaの起動エラーと直近deployを確認する。",
        runbook="RUNBOOK-unexpected-api-failure",
        context=router_log_context(
            status_code=status_code_for_router_error(error),
            detail=str(error),
            error=error,
        ),
    )
    return error_response_for_router_error(error)
