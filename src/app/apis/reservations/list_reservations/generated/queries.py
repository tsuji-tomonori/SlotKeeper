from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.query import fetch_all

# This file is generated from SQL files in the sibling sql directory.
# Do not edit generated models by hand.

SQL_DIR = Path(__file__).parents[1] / "sql"


class SelectReservationsParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    owner_principal_id: str
    range_end: datetime
    range_start: datetime
    status: str | None = None
    future_only: bool
    now: datetime
    after_start_at: datetime | None = None
    after_reservation_id: str | None = None
    limit: int


class SelectReservationsRow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reservation_id: str
    resource_id: str
    owner_principal_id: str
    start_at: datetime
    end_at: datetime
    purpose: str
    status: str
    row_version: int


async def select_reservations(
    session: AsyncSession,
    params: SelectReservationsParams,
) -> list[SelectReservationsRow]:
    """自分の予約一覧を返すため、日付・状態・将来予約の条件で開始日時とIDの順に取得する。"""
    return await fetch_all(
        session,
        SQL_DIR / "001_select_reservations.sql",
        params,
        SelectReservationsRow,
    )
