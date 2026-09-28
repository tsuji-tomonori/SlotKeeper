from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.query import fetch_all

# This file is generated from SQL files in the sibling sql directory.
# Do not edit generated models by hand.

SQL_DIR = Path(__file__).parents[1] / "sql"


class SelectResourcesParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resource_id: str


class SelectResourcesRow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resource_id: str


async def select_resources(
    session: AsyncSession,
    params: SelectResourcesParams,
) -> list[SelectResourcesRow]:
    """予約表の対象資源が存在することを確認するため、資源IDを取得する。"""
    return await fetch_all(
        session,
        SQL_DIR / "001_select_resources.sql",
        params,
        SelectResourcesRow,
    )


class SelectReservationsParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resource_id: str
    day_end: datetime
    day_start: datetime
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
    """指定日の予約表を返すため、日付範囲に重なる確定予約を開始日時とIDの順に取得する。"""
    return await fetch_all(
        session,
        SQL_DIR / "002_select_reservations.sql",
        params,
        SelectReservationsRow,
    )
