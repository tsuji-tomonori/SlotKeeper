from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.query import execute_sql, fetch_all, fetch_one

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
    """取消対象の予約と版を確認するため、指定した予約を取得する。"""
    return await fetch_all(
        session,
        SQL_DIR / "001_select_reservations.sql",
        params,
        SelectReservationsRow,
    )


class UpdateResourcesControlVersionParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resource_id: str


class UpdateResourcesControlVersionRow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resource_id: str
    active: bool
    row_version: int


async def update_resources_control_version(
    session: AsyncSession,
    params: UpdateResourcesControlVersionParams,
) -> UpdateResourcesControlVersionRow | None:
    """同一資源の再予約と取消を競合させるため、資源の内部制御版を進めて現在値を取得する。"""
    return await fetch_one(
        session,
        SQL_DIR / "002_update_resources_control_version.sql",
        params,
        UpdateResourcesControlVersionRow,
    )


class UpdateReservationsParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reservation_id: str


class UpdateReservationsRow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reservation_id: str
    resource_id: str
    owner_principal_id: str
    start_at: datetime
    end_at: datetime
    purpose: str
    status: str
    row_version: int


async def update_reservations(
    session: AsyncSession,
    params: UpdateReservationsParams,
) -> UpdateReservationsRow | None:
    """予約を取消状態へ変更し、版を1つ進める。"""
    return await fetch_one(
        session,
        SQL_DIR / "003_update_reservations.sql",
        params,
        UpdateReservationsRow,
    )


class InsertReservationEventsParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_id: str
    reservation_id: str
    actor_principal_id: str
    occurred_at: datetime


async def insert_reservation_events(
    session: AsyncSession,
    params: InsertReservationEventsParams,
) -> None:
    """予約取消の履歴を取消と同じtransactionで追記する。"""
    await execute_sql(
        session,
        SQL_DIR / "004_insert_reservation_events.sql",
        params,
    )
