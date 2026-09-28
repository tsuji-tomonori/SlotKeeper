"""migrationとseedの再実行を実PostgreSQLで検査する。"""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.apis.resources.common import ResourceKind
from tests.helpers import count_rows, db_connect

pytestmark = pytest.mark.db


def test_migrate_and_seed_repeat(database: None) -> None:
    """Given 既存データ When migrationとseedを繰り返す Then 重複せず既存データを保持する。 [COM-05-AC] [COM-02-AC] [SLOT-AC16]"""
    from tools.project.migrate import migrate, seed

    marker = str(uuid4())
    with db_connect() as connection:
        connection.execute(
            "INSERT INTO slotkeeper.resources"
            "(resource_id,name,description,kind,active,row_version,control_version)"
            " VALUES (%s,%s,'',%s,true,1,0)",
            (marker, "保持確認 " + marker, ResourceKind.ROOM),
        )
    for _ in range(2):
        migrate()
        seed()
    assert count_rows("resources", "resource_id", marker) == 1
    with db_connect() as connection:
        row = connection.execute(
            "SELECT count(*) AS count FROM slotkeeper.resources WHERE resource_id LIKE '00000000-%'"
        ).fetchone()
    assert row is not None and row["count"] == 3
