"""SQL正本から自動生成した型付きquery。直接編集しない。"""

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from slotkeeper.db import Connection
from slotkeeper.domain import Reservation, Resource
from slotkeeper.query_models import Count, Record


class ControlParams(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str


def control(connection: Connection, params: ControlParams) -> list[Resource]:
    """資源の内部版を進め同じ資源の変更を競合させる。"""
    statement = Path(__file__).with_name("sql").joinpath("control.sql").read_text()
    cursor = connection.execute(statement.encode(), params.model_dump())
    return [Resource.model_validate(row) for row in cursor.fetchall()]


class CreateParams(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str
    resource_id: str
    subject: str
    start_at: datetime
    end_at: datetime
    purpose: str


def create(connection: Connection, params: CreateParams) -> list[Reservation]:
    """予約を確定状態で登録する。"""
    statement = Path(__file__).with_name("sql").joinpath("create.sql").read_text()
    cursor = connection.execute(statement.encode(), params.model_dump())
    return [Reservation.model_validate(row) for row in cursor.fetchall()]


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


class ExpireParams(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    subject: str
    key: str


def expire(connection: Connection, params: ExpireParams) -> None:
    """期限を確認済みの要求記録を削除する。"""
    statement = Path(__file__).with_name("sql").joinpath("expire.sql").read_text()
    connection.execute(statement.encode(), params.model_dump())
    return None


class OverlapParams(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    resource_id: str
    start: datetime
    end: datetime


def overlap(connection: Connection, params: OverlapParams) -> list[Count]:
    """取消済みを除いて半開区間の重複を調べる。"""
    statement = Path(__file__).with_name("sql").joinpath("overlap.sql").read_text()
    cursor = connection.execute(statement.encode(), params.model_dump())
    return [Count.model_validate(row) for row in cursor.fetchall()]


class RecordParams(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    subject: str
    key: str
    input_hash: str
    response: str
    expires_at: datetime


def record(connection: Connection, params: RecordParams) -> None:
    """元の成功応答を要求キーと同じトランザクションで保存する。"""
    statement = Path(__file__).with_name("sql").joinpath("record.sql").read_text()
    connection.execute(statement.encode(), params.model_dump())
    return None


class ReplayParams(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    subject: str
    key: str


def replay(connection: Connection, params: ReplayParams) -> list[Record]:
    """要求の成功記録を利用者とキーで取得する。"""
    statement = Path(__file__).with_name("sql").joinpath("replay.sql").read_text()
    cursor = connection.execute(statement.encode(), params.model_dump())
    return [Record.model_validate(row) for row in cursor.fetchall()]


class UserParams(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    subject: str
    now: datetime


def user(connection: Connection, params: UserParams) -> None:
    """初めて予約する利用者の業務属性を記録する。"""
    statement = Path(__file__).with_name("sql").joinpath("user.sql").read_text()
    connection.execute(statement.encode(), params.model_dump())
    return None
