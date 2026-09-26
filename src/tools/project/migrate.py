"""ローカルとDSQLに同じテーブルを作り、索引の完了を待つ。"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from time import monotonic, sleep
from typing import Any

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from app.core.config import Settings, settings  # noqa: E402

DDL = ROOT / "src/db/ddl.sql"
LINE_COMMENT = re.compile(r"--[^\n]*")

type Connection = psycopg.Connection[dict[str, Any]]


def connect(config: Settings) -> Connection:
    """DSQLは公式IAM connector、ローカルはlibpq URLで管理用に接続する。"""
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
        return connection
    url = config.database_url.replace("postgresql+psycopg://", "postgresql://")
    return psycopg.Connection[dict[str, Any]].connect(url, row_factory=dict_row, connect_timeout=5)


def statements() -> list[str]:
    """DDLからコメントを除いた実行文を順に返す。"""
    body = LINE_COMMENT.sub("", DDL.read_text(encoding="utf-8"))
    return [statement.strip() for statement in body.split(";") if statement.strip()]


def wait_for_dsql_job(connection: Connection, job_id: object) -> None:
    """DSQLの非同期索引作成jobの完了を待つ。"""
    deadline = monotonic() + 600
    while True:
        state = connection.execute("SELECT * FROM sys.jobs WHERE job_id = %s", (job_id,)).fetchone()
        if state and state.get("status") == "completed":
            return
        if state and state.get("status") == "failed":
            raise RuntimeError("DSQL索引の作成失敗")
        if monotonic() > deadline:
            raise TimeoutError("DSQL索引の完了待ち上限")
        sleep(1)


def migrate(config: Settings = settings) -> None:
    """DDLごとにcommitし、既存テーブルとデータを維持する。"""
    with connect(config) as connection:
        connection.autocommit = True
        for statement in statements():
            is_index = statement.upper().startswith("CREATE INDEX")
            if config.database_mode == "dsql" and is_index:
                async_statement = statement.replace("CREATE INDEX", "CREATE INDEX ASYNC", 1)
                row = connection.execute(async_statement.encode()).fetchone()
                if row:
                    wait_for_dsql_job(connection, next(iter(row.values())))
                continue
            connection.execute(statement.encode())


def seed(config: Settings = settings) -> None:
    """合成資源を一度だけ投入する。AWSでは拒否する。"""
    if config.environment != "local" or config.database_mode != "postgres":
        raise SystemExit("seedはローカルPostgreSQL専用")
    with connect(config) as connection:
        for number, name, description, kind in [
            (1, "会議室 青葉", "4名 · モニター · ホワイトボード", "room"),
            (2, "会議室 こもれび", "8名 · 大型モニター · オンライン会議", "room"),
            (3, "プロジェクター", "持ち運び可能 · HDMI対応", "equipment"),
        ]:
            connection.execute(
                "INSERT INTO slotkeeper.resources"
                "(resource_id,name,description,kind,active,row_version,control_version)"
                " VALUES (%s,%s,%s,%s,true,1,0) ON CONFLICT(resource_id) DO NOTHING",
                (f"00000000-0000-0000-0000-{number:012}", name, description, kind),
            )


def main() -> None:
    """起動時migrationと明示seedを提供する。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", action="store_true")
    args = parser.parse_args()
    migrate()
    if args.seed:
        seed()


if __name__ == "__main__":
    main()
