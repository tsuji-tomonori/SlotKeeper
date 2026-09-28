from typing import Any

from pydantic import BaseModel

from app.apis.base import ApiStatusSample, sample_value
from app.apis.responses import ErrorBody, ErrorDetail, ErrorResponse
from app.apis.router_errors import (
    client_action_message,
    error_code_for_status,
    is_retryable_status,
)

RESOURCE_KEY_MAP = {
    "resourceId": "resourceId",
    "reservationId": "reservationId",
    "day": "day",
    "status": "status",
    "version": "version",
}


def request_sample(
    *,
    path: dict[str, Any] | None = None,
    query: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    body: BaseModel | None = None,
) -> dict[str, Any]:
    sample: dict[str, Any] = {}
    if path is not None:
        sample["path"] = path
    if query is not None:
        sample["query"] = query
    if headers is not None:
        sample["headers"] = headers
    if body is not None:
        sample["body"] = sample_value(body)
    return sample


def error_resource_sample(request: dict[str, Any]) -> dict[str, Any] | None:
    resource: dict[str, Any] = {}
    for location in ("path", "query", "body"):
        values = request.get(location)
        if not isinstance(values, dict):
            continue
        for source_key, target_key in RESOURCE_KEY_MAP.items():
            if source_key in values and target_key not in resource:
                resource[target_key] = values[source_key]
    headers = request.get("headers")
    if isinstance(headers, dict) and "Idempotency-Key" in headers:
        resource["idempotencyKey"] = headers["Idempotency-Key"]
    return resource or None


def error_response_sample(
    status_code: int,
    message: str,
    *,
    resource: dict[str, Any] | None = None,
) -> dict[str, Any]:
    trace_id = "trc_01HZY6WJ7X4W9A0V7P9N2Q3R4S"
    sample = ErrorResponse(
        error=ErrorBody(
            code=error_code_for_status(status_code),
            message=client_action_message(status_code, message),
            details=[
                ErrorDetail(
                    reason=message,
                    status_code=status_code,
                    retryable=is_retryable_status(status_code),
                    reference=trace_id,
                    resource=resource,
                )
            ],
            trace_id=trace_id,
        )
    )
    return sample.model_dump(by_alias=True, mode="json", exclude_none=True)


def status_samples(
    *,
    request: dict[str, Any],
    success_status: int,
    success_response: BaseModel,
    errors: dict[int, str],
    error_resource_model: type[BaseModel] | None = None,
) -> dict[int, ApiStatusSample]:
    samples: dict[int, ApiStatusSample] = {
        success_status: {"request": request, "response": sample_value(success_response)}
    }
    raw_resource = error_resource_sample(request)
    resource = (
        error_resource_model.model_validate(raw_resource).model_dump(
            by_alias=True, mode="json", exclude_none=True
        )
        if error_resource_model is not None and raw_resource is not None
        else raw_resource
    )
    for status_code, message in errors.items():
        samples[status_code] = {
            "request": request,
            "response": error_response_sample(status_code, message, resource=resource),
        }
    return samples
