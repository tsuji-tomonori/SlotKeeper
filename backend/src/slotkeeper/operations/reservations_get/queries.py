"""SQL正本から自動生成した型付きquery。直接編集しない。"""

from pathlib import Path

from pydantic import BaseModel, ConfigDict

from slotkeeper.db import Connection
from slotkeeper.domain import Event, Reservation


class EventsParams(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str


def events(connection: Connection, params: EventsParams) -> list[Event]:
    """予約の作成と取消の履歴を取得する。"""
    statement = Path(__file__).with_name("sql").joinpath("events.sql").read_text()
    cursor = connection.execute(statement.encode(), params.model_dump())
    return [Event.model_validate(row) for row in cursor.fetchall()]


class GetParams(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str


def get(connection: Connection, params: GetParams) -> list[Reservation]:
    """指定した予約を取得する。"""
    statement = Path(__file__).with_name("sql").joinpath("get.sql").read_text()
    cursor = connection.execute(statement.encode(), params.model_dump())
    return [Reservation.model_validate(row) for row in cursor.fetchall()]
