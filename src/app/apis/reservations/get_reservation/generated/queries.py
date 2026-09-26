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
    reservation_id: str


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
    """予約詳細を返すため、指定した予約を取得する。"""
    return await fetch_all(
        session,
        SQL_DIR / "001_select_reservations.sql",
        params,
        SelectReservationsRow,
    )


class SelectReservationEventsParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reservation_id: str


class SelectReservationEventsRow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_id: str
    reservation_id: str
    actor_principal_id: str
    action: str
    occurred_at: datetime


async def select_reservation_events(
    session: AsyncSession,
    params: SelectReservationEventsParams,
) -> list[SelectReservationEventsRow]:
    """予約詳細の履歴を返すため、作成と取消の履歴を発生順に取得する。"""
    return await fetch_all(
        session,
        SQL_DIR / "002_select_reservation_events.sql",
        params,
        SelectReservationEventsRow,
    )
