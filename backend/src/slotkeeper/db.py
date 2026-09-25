"""DB接続と資源ごとの競合を扱い、commit後だけ結果を返す。"""

from collections.abc import Callable
from random import uniform
from time import monotonic, sleep

import psycopg
from psycopg.rows import dict_row

from slotkeeper.domain import DomainError
from slotkeeper.settings import settings

Connection = psycopg.Connection[dict[str, object]]


def connect() -> Connection:
    """DSQLは公式IAM connector、ローカルはRepeatable Readで接続する。"""
    config = settings()
    if config.database_mode == "dsql":
        import aurora_dsql_psycopg as dsql

        connection: Connection = dsql.connect(
            host=config.dsql_host,
            region=config.region,
            user=config.database_user,
            dbname="postgres",
            row_factory=dict_row,
            sslmode="verify-full",
            connect_timeout=5,
        )
    else:
        connection = psycopg.Connection[dict[str, object]].connect(
            config.database_url, row_factory=dict_row, connect_timeout=5
        )
    connection.isolation_level = psycopg.IsolationLevel.REPEATABLE_READ
    return connection


def transaction[T](work: Callable[[Connection], T], *, replay_safe: bool = False) -> T:
    """直列化競合、冪等キー競合、成否不明の接続切断を新snapshotで再実行する。"""
    deadline = monotonic() + 8
    for attempt in range(12):
        try:
            with connect() as connection:
                result = work(connection)
            return result
        except (
            psycopg.errors.SerializationFailure,
            psycopg.errors.DeadlockDetected,
            psycopg.errors.UniqueViolation,
        ) as exc:
            # 一意性競合の再照合も同じ入口から行う。業務例外は対象外。
            if attempt == 11 or monotonic() >= deadline:
                raise DomainError("storage_temporarily_unavailable", 503) from exc
            sleep(uniform(0, min(0.02 * 2**attempt, 0.4)))
        except psycopg.OperationalError as exc:
            if not replay_safe or attempt == 11 or monotonic() >= deadline:
                raise DomainError("storage_temporarily_unavailable", 503) from exc
            sleep(uniform(0, min(0.02 * 2**attempt, 0.4)))
    raise AssertionError("到達不能")
