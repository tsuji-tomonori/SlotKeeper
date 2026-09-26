from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.query import fetch_all, fetch_one

# This file is generated from SQL files in the sibling sql directory.
# Do not edit generated models by hand.

SQL_DIR = Path(__file__).parents[1] / "sql"


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
    """同一資源の予約作成・取消と競合させるため、資源の内部制御版を進めて現在値を取得する。"""
    return await fetch_one(
        session,
        SQL_DIR / "001_update_resources_control_version.sql",
        params,
        UpdateResourcesControlVersionRow,
    )


class SelectReservationsParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resource_id: str
    now: datetime


class SelectReservationsRow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    future_reservation_count: int


async def select_reservations(
    session: AsyncSession,
    params: SelectReservationsParams,
) -> list[SelectReservationsRow]:
    """資源の無効化可否を判定するため、開始前の確定予約の件数を取得する。"""
    return await fetch_all(
        session,
        SQL_DIR / "002_select_reservations.sql",
        params,
        SelectReservationsRow,
    )


class UpdateResourcesParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    description: str
    kind: str
    active: bool
    resource_id: str


class UpdateResourcesRow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resource_id: str
    name: str
    description: str
    kind: str
    active: bool
    row_version: int


async def update_resources(
    session: AsyncSession,
    params: UpdateResourcesParams,
) -> UpdateResourcesRow | None:
    """資源の名前・説明・種別・有効状態を更新し、公開版を1つ進める。"""
    return await fetch_one(
        session,
        SQL_DIR / "003_update_resources.sql",
        params,
        UpdateResourcesRow,
    )
