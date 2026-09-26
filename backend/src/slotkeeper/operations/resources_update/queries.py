"""SQL正本から自動生成した型付きquery。直接編集しない。"""

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from slotkeeper.db import Connection
from slotkeeper.domain import Resource
from slotkeeper.query_models import Count


class ControlParams(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str


def control(connection: Connection, params: ControlParams) -> list[Resource]:
    """資源の内部版を進め同じ資源の変更を競合させる。"""
    statement = Path(__file__).with_name("sql").joinpath("control.sql").read_text()
    cursor = connection.execute(statement.encode(), params.model_dump())
    return [Resource.model_validate(row) for row in cursor.fetchall()]


class FutureParams(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str
    now: datetime


def future(connection: Connection, params: FutureParams) -> list[Count]:
    """開始前の確定予約を数える。"""
    statement = Path(__file__).with_name("sql").joinpath("future.sql").read_text()
    cursor = connection.execute(statement.encode(), params.model_dump())
    return [Count.model_validate(row) for row in cursor.fetchall()]


class UpdateParams(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str
    name: str
    description: str
    kind: str
    active: bool


def update(connection: Connection, params: UpdateParams) -> list[Resource]:
    """資源を編集し公開版を進める。"""
    statement = Path(__file__).with_name("sql").joinpath("update.sql").read_text()
    cursor = connection.execute(statement.encode(), params.model_dump())
    return [Resource.model_validate(row) for row in cursor.fetchall()]
