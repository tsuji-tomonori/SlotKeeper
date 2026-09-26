"""SQL正本から自動生成した型付きquery。直接編集しない。"""

from pathlib import Path

from pydantic import BaseModel, ConfigDict

from slotkeeper.db import Connection
from slotkeeper.domain import Resource


class SelectPageParams(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    limit: int
    offset: int


def select_page(connection: Connection, params: SelectPageParams) -> list[Resource]:
    """資源を名前とIDの順で取得する。"""
    statement = Path(__file__).with_name("sql").joinpath("select_page.sql").read_text()
    cursor = connection.execute(statement.encode(), params.model_dump())
    return [Resource.model_validate(row) for row in cursor.fetchall()]
