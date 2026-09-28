from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status
from starlette.responses import JSONResponse

from app.apis.exceptions import ApiFunctionError
from app.apis.responses import ErrorBody, ErrorDetail, ErrorResponse
from app.apis.sequence_types import CallerIdentity
from app.core.logging import current_log_context
from app.integrations.common_errors import (
    ExternalApiConflictError,
    ExternalApiError,
    ExternalApiNotFoundError,
    ExternalApiTimeoutError,
    ExternalApiUnavailableError,
)

ROUTER_HANDLED_EXCEPTIONS = (ApiFunctionError, ExternalApiError, HTTPException)


def router_error_message_id(operation_id: str, error: BaseException) -> str:
    """Routerで捕捉した例外型ごとの運用ログmessageIdを返す。"""
    if isinstance(error, HTTPException):
        suffix = "router_http_exception"
    elif isinstance(error, ApiFunctionError):
        suffix = "router_api_function_error"
    elif isinstance(error, ExternalApiError):
        suffix = "router_external_api_error"
    else:
        suffix = "router_error"
    return f"{operation_id}.{suffix}"


def router_error_summary(base_summary: str, error: BaseException) -> str:
    """Routerで捕捉した例外型が分かる運用ログ概要を返す。"""
    exception_type = type(error).__name__
    return base_summary.replace(
        "Routerで捕捉した例外により", f"Routerで捕捉した{exception_type}により"
    )


def api_error_response(
    status_code: int,
    detail: str,
    *,
    trace_id: str | None = None,
    resource: dict[str, Any] | None = None,
) -> JSONResponse:
    """共通 error schema を HTTP response として返す。"""
    trace_id = trace_id or current_trace_id()
    body = ErrorResponse(
        error=ErrorBody(
            code=_error_code(status_code),
            message=client_action_message(status_code, detail),
            details=[
                ErrorDetail(
                    reason=detail,
                    status_code=status_code,
                    retryable=is_retryable_status(status_code),
                    reference=trace_id,
                    resource=resource,
                )
            ],
            trace_id=trace_id,
        )
    )
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(mode="json", by_alias=True),
    )


def current_trace_id() -> str:
    """HTTP middlewareがbindした要求IDを応答の追跡IDとして返す。"""
    trace_id = current_log_context().get("traceId")
    return str(trace_id) if trace_id else "unavailable"


def error_response_for_router_error(
    error: ApiFunctionError | ExternalApiError | HTTPException,
    *,
    trace_id: str | None = None,
) -> JSONResponse:
    """Router で捕捉した sequence / provider 例外を HTTP error response に変換する。"""
    if isinstance(error, HTTPException):
        return api_error_response(
            error.status_code,
            str(error.detail),
            trace_id=trace_id,
        )
    if isinstance(error, ApiFunctionError):
        return error_response_for_api_function_error(error, trace_id=trace_id)
    return error_response_for_external_error(error, trace_id=trace_id)


def status_code_for_router_error(error: ApiFunctionError | ExternalApiError | HTTPException) -> int:
    """Routerで捕捉した例外をHTTP status codeへ変換する。"""
    if isinstance(error, HTTPException):
        return error.status_code
    if isinstance(error, ApiFunctionError):
        return error.status_code
    if isinstance(error, ExternalApiNotFoundError):
        return status.HTTP_404_NOT_FOUND
    if isinstance(error, ExternalApiConflictError):
        return status.HTTP_409_CONFLICT
    if isinstance(error, ExternalApiTimeoutError | ExternalApiUnavailableError):
        return status.HTTP_503_SERVICE_UNAVAILABLE
    return status.HTTP_502_BAD_GATEWAY


def router_log_context(
    *,
    status_code: int,
    detail: str,
    caller: CallerIdentity | None = None,
    resource: dict[str, Any] | None = None,
    error: BaseException | None = None,
) -> dict[str, Any]:
    """Routerがwarn以上の運用ログをemitするときの共通contextを組み立てる。"""
    context: dict[str, Any] = {
        "api": {"statusCode": status_code},
        "error": {
            "code": _error_code(status_code),
            "message": detail,
        },
    }
    if caller is not None:
        context["actorPrincipalId"] = caller.principal_id
    if resource:
        context["resource"] = resource
    if error is not None:
        context["error"]["exceptionType"] = type(error).__name__
    return context


def error_response_for_api_function_error(
    error: ApiFunctionError,
    *,
    trace_id: str | None = None,
) -> JSONResponse:
    """Sequence function の業務例外を HTTP error response に変換する。"""
    return api_error_response(error.status_code, error.detail, trace_id=trace_id)


def error_response_for_external_error(
    error: ExternalApiError,
    *,
    trace_id: str | None = None,
) -> JSONResponse:
    """Provider client の例外を HTTP error response に変換する。"""
    if isinstance(error, ExternalApiNotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(error, ExternalApiConflictError):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(error, ExternalApiTimeoutError | ExternalApiUnavailableError):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        status_code = status.HTTP_502_BAD_GATEWAY
    return api_error_response(
        status_code,
        _external_error_detail(status_code),
        trace_id=trace_id,
    )


def _external_error_detail(status_code: int) -> str:
    if status_code == status.HTTP_404_NOT_FOUND:
        return "external resource was not found"
    if status_code == status.HTTP_409_CONFLICT:
        return "external resource state conflicts with the request"
    if status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
        return "external service is temporarily unavailable"
    return "external service request failed"


def _error_code(status_code: int) -> str:
    return error_code_for_status(status_code)


ERROR_CODES: dict[int, str] = {
    status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
    status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
    status.HTTP_403_FORBIDDEN: "FORBIDDEN",
    status.HTTP_404_NOT_FOUND: "NOT_FOUND",
    status.HTTP_409_CONFLICT: "CONFLICT",
    status.HTTP_422_UNPROCESSABLE_CONTENT: "VALIDATION_ERROR",
    status.HTTP_429_TOO_MANY_REQUESTS: "TOO_MANY_REQUESTS",
    status.HTTP_502_BAD_GATEWAY: "BAD_GATEWAY",
    status.HTTP_503_SERVICE_UNAVAILABLE: "SERVICE_UNAVAILABLE",
}
CLIENT_ACTION_MESSAGES: dict[int, str] = {
    status.HTTP_400_BAD_REQUEST: "リクエスト内容を修正して再送してください。理由: {detail}",
    status.HTTP_401_UNAUTHORIZED: "認証情報を確認し、有効な認証情報で再送してください。",
    status.HTTP_403_FORBIDDEN: "操作権限を確認し、必要な権限を持つ利用者で再送してください。",
    status.HTTP_404_NOT_FOUND: "指定したリソースIDが正しいか確認してから再送してください。",
    status.HTTP_409_CONFLICT: (
        "リソースの最新状態またはIdempotency-Keyを確認してから再送してください。理由: {detail}"
    ),
    status.HTTP_422_UNPROCESSABLE_CONTENT: (
        "リクエストの型、必須項目、制約をOpenAPI仕様に合わせて修正してください。"
    ),
    status.HTTP_429_TOO_MANY_REQUESTS: "呼び出し頻度を下げ、時間をおいてから再送してください。",
    status.HTTP_502_BAD_GATEWAY: (
        "外部サービス連携で失敗しました。時間をおいて再送し、"
        "解消しない場合は追跡IDを添えて問い合わせてください。"
    ),
    status.HTTP_503_SERVICE_UNAVAILABLE: (
        "一時的に処理できません。時間をおいて同じリクエストを再送してください。"
    ),
}
DEFAULT_CLIENT_ACTION_MESSAGE = "想定外のエラーが発生しました。追跡IDを添えて問い合わせてください。"
RETRYABLE_STATUSES = frozenset(
    {
        status.HTTP_429_TOO_MANY_REQUESTS,
        status.HTTP_502_BAD_GATEWAY,
        status.HTTP_503_SERVICE_UNAVAILABLE,
    }
)


def client_action_message(status_code: int, detail: str) -> str:
    """利用者が次に確認・修正・再試行すべき内容をstatusごとに返す。"""
    return CLIENT_ACTION_MESSAGES.get(status_code, DEFAULT_CLIENT_ACTION_MESSAGE).format(
        detail=detail
    )


def is_retryable_status(status_code: int) -> bool:
    """同じリクエストの再送で解消する可能性があるstatusかを返す。"""
    return status_code in RETRYABLE_STATUSES


def error_code_for_status(status_code: int) -> str:
    """HTTP statusを機械判定用のエラーコードへ変換する。"""
    return ERROR_CODES.get(status_code, "INTERNAL_SERVER_ERROR")
