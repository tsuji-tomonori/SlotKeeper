from __future__ import annotations

import asyncio
import functools
import random
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any, cast

from fastapi import status
from psycopg import errors as psycopg_errors
from sqlalchemy.exc import DBAPIError, OperationalError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import Settings, settings

type AsyncSessionFactory = async_sessionmaker[AsyncSession]

RETRY_ATTEMPTS = 12
RETRY_DEADLINE_SECONDS = 8.0
RETRYABLE_SQLSTATES = frozenset({"40001", "40P01", "23505", "OC000", "OC001"})


def _async_database_url(database_url: str) -> str:
    if database_url.startswith("postgresql://"):
        return "postgresql+psycopg://" + database_url.removeprefix("postgresql://")
    return database_url


def create_async_db_engine(config: Settings, *, echo: bool = False) -> AsyncEngine:
    """ローカルはRepeatable Read、DSQLは公式IAM connectorで接続するengineを作成する。"""
    if config.database_mode == "dsql":
        import aurora_dsql_psycopg as dsql

        async def connect_dsql() -> Any:
            return await dsql.DSQLAsyncConnection.connect(
                host=config.dsql_host,
                region=config.region,
                user=config.database_user,
                dbname="postgres",
                sslmode="verify-full",
                connect_timeout=5,
            )

        return create_async_engine(
            "postgresql+psycopg://",
            async_creator=connect_dsql,
            poolclass=NullPool,
            echo=echo,
        )
    return create_async_engine(
        _async_database_url(config.database_url),
        poolclass=NullPool,
        isolation_level="REPEATABLE READ",
        connect_args={"connect_timeout": 5},
        echo=echo,
    )


def create_session_factory(engine: AsyncEngine) -> AsyncSessionFactory:
    return async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


engine = create_async_db_engine(settings, echo=settings.debug)
AsyncSessionLocal = create_session_factory(engine)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


def is_retryable_database_error(error: DBAPIError, *, replay_safe: bool) -> bool:
    """直列化競合・一意性競合・DSQL OCC・成否不明の切断を再実行対象として判定する。"""
    original = error.orig
    sqlstate = getattr(original, "sqlstate", None)
    if sqlstate in RETRYABLE_SQLSTATES:
        return True
    if isinstance(original, psycopg_errors.SerializationFailure | psycopg_errors.DeadlockDetected):
        return True
    return replay_safe and isinstance(error, OperationalError)


def retry_transaction[**P, R](
    *, replay_safe: bool = False
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """同じsessionをrollbackし、新しいsnapshotで上限付きに処理順を再実行する。"""

    def decorate(endpoint: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @functools.wraps(endpoint)
        async def run(*args: P.args, **kwargs: P.kwargs) -> R:
            session = cast(AsyncSession, kwargs["session"])
            loop = asyncio.get_running_loop()
            deadline = loop.time() + RETRY_DEADLINE_SECONDS
            for attempt in range(RETRY_ATTEMPTS):
                try:
                    return await endpoint(*args, **kwargs)
                except DBAPIError as error:
                    await session.rollback()
                    exhausted = attempt == RETRY_ATTEMPTS - 1 or loop.time() >= deadline
                    if exhausted or not is_retryable_database_error(error, replay_safe=replay_safe):
                        return cast(R, storage_unavailable_response(endpoint.__name__, error))
                    await asyncio.sleep(random.uniform(0, min(0.02 * 2**attempt, 0.4)))  # noqa: S311
            raise AssertionError("unreachable")

        return run

    return decorate


def storage_unavailable_response(operation_name: str, error: DBAPIError) -> Any:
    """再試行上限に達したDB障害を運用ログと503応答へ変換する。"""
    from app.apis.router_errors import api_error_response, router_log_context
    from app.core.logging import get_operation_logger

    get_operation_logger(__name__).error(
        "database.storage_temporarily_unavailable",
        catalog_id="DB001",
        summary="DBの競合または接続障害が再試行上限を超えたため、要求を503で終了した。",
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="storage_temporarily_unavailable",
        when="直列化競合、OCC競合、接続断が再試行上限または8秒を超えた場合。",
        check_procedure="traceIdでログを検索し、同時刻のDB競合率と接続数を確認する。",
        remediation_procedure="競合が続く資源と負荷を特定し、時間をおいて同じ要求を再送する。",
        operator_action="DB接続数、直列化失敗率、直近deployを確認する。",
        runbook="RUNBOOK-storage-unavailable",
        context=router_log_context(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="storage_temporarily_unavailable",
            error=error,
        )
        | {"api": {"operation": operation_name, "statusCode": 503}},
    )
    return api_error_response(
        status.HTTP_503_SERVICE_UNAVAILABLE, "storage_temporarily_unavailable"
    )
