"""ローカルとDSQLに同じテーブルを作り、索引の完了を待つ。"""

import argparse
from pathlib import Path
from time import monotonic, sleep

from slotkeeper.db import connect
from slotkeeper.settings import settings

ROOT = Path(__file__).resolve().parents[2]


def migrate() -> None:
    """DDLごとにcommitし、既存テーブルとデータを維持する。"""
    with connect() as connection:
        connection.autocommit = True
        for filename in ("schema.sql", "indexes.sql"):
            for statement in (ROOT / "backend" / filename).read_text().split(";"):
                if not statement.strip():
                    continue
                if settings().database_mode == "dsql" and filename == "indexes.sql":
                    statement = statement.replace("CREATE INDEX", "CREATE INDEX ASYNC")
                    cursor = connection.execute(statement.encode())
                    row = cursor.fetchone()
                    if row:
                        job_id = next(iter(row.values()))
                        deadline = monotonic() + 600
                        while True:
                            state = connection.execute(
                                "SELECT * FROM sys.jobs WHERE job_id = %s", (job_id,)
                            ).fetchone()
                            if state and state.get("status") == "completed":
                                break
                            if state and state.get("status") == "failed":
                                raise RuntimeError("DSQL索引の作成失敗")
                            if monotonic() > deadline:
                                raise TimeoutError("DSQL索引の完了待ち上限")
                            sleep(1)
                else:
                    connection.execute(statement.encode())


def seed() -> None:
    """合成資源を一度だけ投入する。AWSでは拒否する。"""
    if settings().environment != "local" or settings().database_mode != "postgres":
        raise SystemExit("seedはローカルPostgreSQL専用")
    with connect() as connection:
        for number, name, description, kind in [
            (1, "会議室 青葉", "4名 · モニター · ホワイトボード", "room"),
            (2, "会議室 こもれび", "8名 · 大型モニター · オンライン会議", "room"),
            (3, "プロジェクター", "持ち運び可能 · HDMI対応", "equipment"),
        ]:
            connection.execute(
                "INSERT INTO slotkeeper.resources(id,name,description,kind,active,version,control_version) VALUES (%s,%s,%s,%s,true,1,0) ON CONFLICT(id) DO NOTHING",
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
