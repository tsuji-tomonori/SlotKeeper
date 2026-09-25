"""SQL正本から自動生成した型付きquery。直接編集しない。"""

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from slotkeeper.db import Connection
from slotkeeper.domain import Reservation


class SelectPageParams(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    subject: str
    start: datetime
    end: datetime
    state: str
    future: bool
    now: datetime
    limit: int
    offset: int


def select_page(connection: Connection, params: SelectPageParams) -> list[Reservation]:
    """本人の予約を期間と状態で絞り込む。"""
    statement = Path(__file__).with_name("sql").joinpath("select_page.sql").read_text()
    cursor = connection.execute(statement.encode(), params.model_dump())
    return [Reservation.model_validate(row) for row in cursor.fetchall()]
