"""SQL正本から自動生成した型付きquery。直接編集しない。"""

from pathlib import Path

from pydantic import BaseModel, ConfigDict

from slotkeeper.db import Connection
from slotkeeper.domain import Resource


class CreateParams(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str
    name: str
    description: str
    kind: str


def create(connection: Connection, params: CreateParams) -> list[Resource]:
    """有効な資源を登録する。"""
    statement = Path(__file__).with_name("sql").joinpath("create.sql").read_text()
    cursor = connection.execute(statement.encode(), params.model_dump())
    return [Resource.model_validate(row) for row in cursor.fetchall()]
