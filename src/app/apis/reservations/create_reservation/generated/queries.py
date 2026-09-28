from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.query import execute_sql, fetch_all, fetch_one

# This file is generated from SQL files in the sibling sql directory.
# Do not edit generated models by hand.

SQL_DIR = Path(__file__).parents[1] / "sql"


class SelectIdempotencyRecordsParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    principal_id: str
    idempotency_key: str


class SelectIdempotencyRecordsRow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    idempotency_key: str
    request_hash: str
    response_payload: str
    expires_at: datetime


async def select_idempotency_records(
    session: AsyncSession,
    params: SelectIdempotencyRecordsParams,
) -> list[SelectIdempotencyRecordsRow]:
    """予約作成要求の再送を照合するため、利用者とIdempotency-Keyの成功記録を取得する。"""
    return await fetch_all(
        session,
        SQL_DIR / "001_select_idempotency_records.sql",
        params,
        SelectIdempotencyRecordsRow,
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
    """同一資源の予約作成・取消・無効化を競合させるため、資源の内部制御版を進めて現在値を取得する。"""
    return await fetch_one(
        session,
        SQL_DIR / "002_update_resources_control_version.sql",
        params,
        UpdateResourcesControlVersionRow,
    )


class SelectReservationsParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resource_id: str
    end_at: datetime
    start_at: datetime


class SelectReservationsRow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    overlapping_reservation_count: int


async def select_reservations(
    session: AsyncSession,
    params: SelectReservationsParams,
) -> list[SelectReservationsRow]:
    """予約枠の重複を判定するため、取消済みを除き半開区間が重なる確定予約の件数を取得する。"""
    return await fetch_all(
        session,
        SQL_DIR / "003_select_reservations.sql",
        params,
        SelectReservationsRow,
    )


class DeleteIdempotencyRecordsParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    principal_id: str
    idempotency_key: str


async def delete_idempotency_records(
    session: AsyncSession,
    params: DeleteIdempotencyRecordsParams,
) -> None:
    """有効期限を過ぎた成功記録を新規要求として扱うため削除する。"""
    await execute_sql(
        session,
        SQL_DIR / "004_delete_idempotency_records.sql",
        params,
    )


class InsertUsersParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    principal_id: str
    first_seen_at: datetime


async def insert_users(
    session: AsyncSession,
    params: InsertUsersParams,
) -> None:
    """初めて予約する利用者を記録する。既存利用者は変更しない。"""
    await execute_sql(
        session,
        SQL_DIR / "005_insert_users.sql",
        params,
    )


class InsertReservationsParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reservation_id: str
    resource_id: str
    owner_principal_id: str
    start_at: datetime
    end_at: datetime
    purpose: str


class InsertReservationsRow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reservation_id: str
    resource_id: str
    owner_principal_id: str
    start_at: datetime
    end_at: datetime
    purpose: str
    status: str
    row_version: int


async def insert_reservations(
    session: AsyncSession,
    params: InsertReservationsParams,
) -> InsertReservationsRow | None:
    """予約を確定状態の初期版で保存する。"""
    return await fetch_one(
        session,
        SQL_DIR / "006_insert_reservations.sql",
        params,
        InsertReservationsRow,
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
    """予約作成の履歴を予約と同じtransactionで追記する。"""
    await execute_sql(
        session,
        SQL_DIR / "007_insert_reservation_events.sql",
        params,
    )


class InsertIdempotencyRecordsParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    principal_id: str
    idempotency_key: str
    request_hash: str
    response_payload: str
    expires_at: datetime


async def insert_idempotency_records(
    session: AsyncSession,
    params: InsertIdempotencyRecordsParams,
) -> None:
    """元の成功応答を予約と同じtransactionで24時間の成功記録として保存する。"""
    await execute_sql(
        session,
        SQL_DIR / "008_insert_idempotency_records.sql",
        params,
    )
