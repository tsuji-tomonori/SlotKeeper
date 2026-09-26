from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.apis.common import decode_page_token, encode_page_token, raise_missing_runtime_dependency
from app.apis.exceptions import ApiFunctionError
from app.apis.resources.common import ResourceKind
from app.apis.resources.list_resources.generated import queries
from app.apis.resources.list_resources.schemas import (
    ListResourcesQuery,
    ListResourcesResponse,
    ResourceItemResponse,
)
from app.apis.router_errors import (
    error_code_for_status,
    error_response_for_router_error,
    router_error_message_id,
    router_error_summary,
    router_log_context,
    status_code_for_router_error,
)
from app.apis.sequence_types import CallerIdentity, SequencePage
from app.core.logging import get_operation_logger, operational_log_context_model
from app.integrations.common_errors import ExternalApiError

ops_logger = get_operation_logger(__name__)


async def get_resources(
    query: ListResourcesQuery,
    session: AsyncSession | None = None,
) -> SequencePage[ResourceItemResponse]:
    """名前とIDの固定順で継続位置より後の資源を取得する。"""
    if session is not None:
        after = decode_page_token(query.next_token, 2)
        rows = await queries.select_resources(
            session,
            queries.SelectResourcesParams(
                after_name=after[0] if after else None,
                after_resource_id=after[1] if after else None,
                limit=query.limit + 1,
            ),
        )
        items = [
            ResourceItemResponse(
                resource_id=row.resource_id,
                name=row.name,
                description=row.description,
                kind=ResourceKind(row.kind),
                active=row.active,
                version=row.row_version,
            )
            for row in rows
        ]
        return SequencePage(items=items, next_token=None)
    return raise_missing_runtime_dependency("get_resources")


async def apply_pagination(
    resources: SequencePage[ResourceItemResponse],
    query: ListResourcesQuery,
) -> SequencePage[ResourceItemResponse]:
    """取得した資源を上限件数へ切り詰め、次ページの継続tokenを付与する。"""
    items = list(resources.items)
    if len(items) <= query.limit:
        return SequencePage(items=items, next_token=None)
    page = items[: query.limit]
    last = page[-1]
    return SequencePage(items=page, next_token=encode_page_token([last.name, last.resource_id]))


async def build_resource_list_response(
    page: SequencePage[ResourceItemResponse],
) -> ListResourcesResponse:
    """資源一覧レスポンスを組み立てる。"""
    return ListResourcesResponse(items=list(page.items), next_token=page.next_token)


async def build_router_error_response(
    query: ListResourcesQuery,
    caller: CallerIdentity,
    error: ApiFunctionError | ExternalApiError | HTTPException,
) -> JSONResponse:
    """Router で捕捉した例外を運用ログと HTTP error response に変換する。"""
    ops_logger.error(
        router_error_message_id("listResources", error),
        catalog_id="M001",
        summary=router_error_summary(
            "Routerで捕捉した例外により資源一覧取得が失敗した。",
            error,
        ),
        when="ROUTER_HANDLED_EXCEPTIONSを捕捉した場合。",
        check_procedure="traceIdでログを検索し、routerで捕捉された例外種別とnextTokenを確認する。",
        remediation_procedure="継続tokenを破棄して先頭ページから再取得する。",
        context_model=operational_log_context_model(
            trace_id=None,
            actor_principal_id=caller.principal_id,
            api_status_code=status_code_for_router_error(error),
            error_code=error_code_for_status(status_code_for_router_error(error)),
            error_message=str(error),
            error_exception_type=type(error).__name__,
        ),
        operator_action="同一routeの5xx率、直近deploy、DB状態を確認する。",
        runbook="RUNBOOK-unexpected-api-failure",
        context=router_log_context(
            status_code=status_code_for_router_error(error),
            detail=str(error),
            caller=caller,
            resource={"nextToken": query.next_token},
            error=error,
        ),
    )
    return error_response_for_router_error(error)
