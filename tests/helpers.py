"""テスト間で共有するAPI呼出しとDB確認の補助関数です。"""

from __future__ import annotations

import json
import logging
import sys
from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any
from uuid import uuid4

import psycopg
from fastapi.testclient import TestClient
from psycopg import sql
from psycopg.rows import dict_row

from app.core.config import settings
from app.core.logging import JsonOperationalLogFormatter

type Headers = dict[str, str]
type Signer = Callable[..., Headers]


def db_connect() -> psycopg.Connection[dict[str, Any]]:
    """検証用に同じDBへ直接接続する。"""
    url = settings.database_url.replace("postgresql+psycopg://", "postgresql://")
    return psycopg.Connection[dict[str, Any]].connect(url, row_factory=dict_row)


def count_rows(table: str, column: str, value: str) -> int:
    with db_connect() as connection:
        query = sql.SQL("SELECT count(*) AS count FROM slotkeeper.{} WHERE {} = %s").format(
            sql.Identifier(table), sql.Identifier(column)
        )
        row = connection.execute(query, (value,)).fetchone()
        return int(row["count"]) if row else 0


def create_reservation(
    client: TestClient,
    signed: Signer,
    booking: dict[str, str],
    key: str | None = None,
    subject: str = "alice",
) -> Any:
    """Idempotency-Key付きで予約作成APIを呼ぶ。"""
    return client.post(
        "/reservations",
        json=booking,
        headers={**signed(subject), "Idempotency-Key": key or str(uuid4())},
    )


def error_reason(response: Any) -> str:
    """共通error schemaから業務上の理由コードを取り出す。"""
    return str(response.json()["error"]["details"][0]["reason"])


@contextmanager
def operational_stdout_handler() -> Generator[None]:
    """capsysが置き換えた標準出力へ運用ログを一時的に出力する。"""
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(JsonOperationalLogFormatter())
    root_logger = logging.getLogger()
    previous_level = root_logger.level
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)
    try:
        yield
    finally:
        root_logger.removeHandler(handler)
        root_logger.setLevel(previous_level)


def log_events(output: str) -> list[dict[str, Any]]:
    """標準出力のJSON行を運用ログeventとして読み取る。"""
    return [json.loads(line) for line in output.splitlines() if line.startswith("{")]
