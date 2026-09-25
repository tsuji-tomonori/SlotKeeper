"""SQL正本から自動生成した型付きquery。直接編集しない。"""

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from slotkeeper.db import Connection
from slotkeeper.domain import Reservation, Resource


class CancelParams(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str


def cancel(connection: Connection, params: CancelParams) -> list[Reservation]:
    """予約を取消状態にして版を進める。"""
    statement = Path(__file__).with_name("sql").joinpath("cancel.sql").read_text()
    cursor = connection.execute(statement.encode(), params.model_dump())
    return [Reservation.model_validate(row) for row in cursor.fetchall()]


class ControlParams(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str


def control(connection: Connection, params: ControlParams) -> list[Resource]:
    """資源の内部版を進め同じ資源の変更を競合させる。"""
    statement = Path(__file__).with_name("sql").joinpath("control.sql").read_text()
    cursor = connection.execute(statement.encode(), params.model_dump())
    return [Resource.model_validate(row) for row in cursor.fetchall()]


class EventParams(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str
    reservation_id: str
    actor: str
    action: str
    at: datetime


def event(connection: Connection, params: EventParams) -> None:
    """予約操作の履歴を登録する。"""
    statement = Path(__file__).with_name("sql").joinpath("event.sql").read_text()
    connection.execute(statement.encode(), params.model_dump())
    return None


class GetParams(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str


def get(connection: Connection, params: GetParams) -> list[Reservation]:
    """指定した予約を取得する。"""
    statement = Path(__file__).with_name("sql").joinpath("get.sql").read_text()
    cursor = connection.execute(statement.encode(), params.model_dump())
    return [Reservation.model_validate(row) for row in cursor.fetchall()]
