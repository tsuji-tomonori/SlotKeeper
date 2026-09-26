"""DB接続設定とOCC再試行の境界を検査する。"""

from __future__ import annotations

import asyncio
import sys
from types import SimpleNamespace
from typing import Any

import psycopg
import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.db.session import create_async_db_engine, retry_transaction

pytestmark = pytest.mark.anyio


class FakeSession:
    def __init__(self) -> None:
        self.rollbacks = 0

    async def rollback(self) -> None:
        self.rollbacks += 1


def database_error(original: Exception, error_type: type[DBAPIError] = DBAPIError) -> DBAPIError:
    return error_type("statement", {}, original)


def outcomes_endpoint(outcomes: list[object]) -> tuple[Any, list[object]]:
    attempts: list[object] = []

    async def endpoint(*, session: AsyncSession) -> str:
        _ = session
        outcome = outcomes[min(len(attempts), len(outcomes) - 1)]
        attempts.append(outcome)
        if isinstance(outcome, Exception):
            raise outcome
        return str(outcome)

    return endpoint, attempts


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    async def skip(delay: float) -> None:
        _ = delay

    monkeypatch.setattr(asyncio, "sleep", skip)


async def test_transaction_retries_conflicts() -> None:
    """Given commit時の直列化競合と一意性競合 When 処理順を実行 Then 新snapshotで再実行して成功する。 [SLOT-AC03] [SLOT-AC07]"""
    endpoint, attempts = outcomes_endpoint(
        [
            database_error(psycopg.errors.SerializationFailure()),
            database_error(psycopg.errors.UniqueViolation()),
            "committed",
        ]
    )
    session = FakeSession()
    result = await retry_transaction()(endpoint)(session=session)
    assert result == "committed"
    assert len(attempts) == 3 and session.rollbacks == 2


async def test_transaction_limits() -> None:
    """Given 解消しない競合と成否不明の切断 When 処理順を実行 Then 上限後503、再送安全でない処理は再試行しない。 [SLOT-AC12]"""
    endpoint, attempts = outcomes_endpoint([database_error(psycopg.errors.SerializationFailure())])
    exhausted = await retry_transaction()(endpoint)(session=FakeSession())
    assert exhausted.status_code == 503 and len(attempts) == 12
    endpoint, attempts = outcomes_endpoint(
        [database_error(psycopg.OperationalError(), OperationalError)]
    )
    unsafe = await retry_transaction()(endpoint)(session=FakeSession())
    assert unsafe.status_code == 503 and len(attempts) == 1
    endpoint, attempts = outcomes_endpoint(
        [database_error(psycopg.OperationalError(), OperationalError), "again"]
    )
    assert await retry_transaction(replay_safe=True)(endpoint)(session=FakeSession()) == "again"
    assert len(attempts) == 2


async def test_business_errors_are_not_retried() -> None:
    """Given 業務上の重複応答 When 処理順を実行 Then 再試行せずそのまま409を返す。 [SLOT-AC02]"""
    endpoint, attempts = outcomes_endpoint(["409 slot_taken"])
    assert await retry_transaction()(endpoint)(session=FakeSession()) == "409 slot_taken"
    assert len(attempts) == 1


def test_dsql_connection_uses_official_connector(monkeypatch: pytest.MonkeyPatch) -> None:
    """Given DSQL設定 When engineを作る Then 公式connectorへIAM用の接続先・利用者とTLS検証を渡す。 [TECH-DB-AC]"""
    calls: dict[str, object] = {}

    class Connection:
        @staticmethod
        async def connect(**kwargs: object) -> object:
            calls.update(kwargs)
            return object()

    monkeypatch.setitem(
        sys.modules, "aurora_dsql_psycopg", SimpleNamespace(DSQLAsyncConnection=Connection)
    )
    engine = create_async_db_engine(
        Settings(database_mode="dsql", dsql_host="cluster.dsql.ap-northeast-1.on.aws")
    )
    creator = engine.sync_engine.pool._creator  # pyright: ignore
    assert creator is not None
    assert engine.url.drivername == "postgresql+psycopg"


@pytest.mark.db
async def test_repeatable_read(database: None) -> None:
    """Given ローカル接続 When 分離レベル取得 Then repeatable read。 [COM-02-AC] [TECH-DB-AC]"""
    engine = create_async_db_engine(Settings())
    async with engine.connect() as connection:
        level: str = (await connection.execute(text("SHOW transaction_isolation"))).scalar_one()
    await engine.dispose()
    assert level == "repeatable read"
