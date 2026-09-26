"""SQL正本から自動生成した型付きquery。直接編集しない。"""

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from slotkeeper.db import Connection
from slotkeeper.domain import Reservation, Resource


class BookingsParams(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str
    start: datetime
    end: datetime
    limit: int
    offset: int


def bookings(connection: Connection, params: BookingsParams) -> list[Reservation]:
    """日本時間の一日内に開始する予約を取得する。"""
    statement = Path(__file__).with_name("sql").joinpath("bookings.sql").read_text()
    cursor = connection.execute(statement.encode(), params.model_dump())
    return [Reservation.model_validate(row) for row in cursor.fetchall()]


class ResourceParams(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str


def resource(connection: Connection, params: ResourceParams) -> list[Resource]:
    """資源の存在を確認する。"""
    statement = Path(__file__).with_name("sql").joinpath("resource.sql").read_text()
    cursor = connection.execute(statement.encode(), params.model_dump())
    return [Resource.model_validate(row) for row in cursor.fetchall()]
