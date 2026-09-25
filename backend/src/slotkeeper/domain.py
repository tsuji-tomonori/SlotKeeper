"""通信方式に依存しない予約の規則と例外を定義する。"""

from datetime import UTC, datetime, timedelta
from typing import Literal, Protocol
from zoneinfo import ZoneInfo

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator

JST = ZoneInfo("Asia/Tokyo")


class DomainError(Exception):
    """公開できる固定コードだけを持つ業務例外。"""

    def __init__(self, code: str, status: int = 409) -> None:
        self.code = code
        self.status = status
        super().__init__(code)


class Clock(Protocol):
    """業務判定で用いる現在時刻の取得契約。"""

    def now(self) -> datetime: ...


class SystemClock:
    """UTCの現在時刻を返す。"""

    def now(self) -> datetime:
        return datetime.now(UTC)


class User(BaseModel):
    """認証adapterで検証済みの利用者。"""

    subject: str
    admin: bool = False


class Input(BaseModel):
    """余分な入力を拒否するAPI入力の共通型。"""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ResourceInput(Input):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=1000)
    kind: Literal["room", "equipment"] = "room"


class ResourceEdit(ResourceInput):
    active: bool
    version: int = Field(ge=1)


class Resource(ResourceInput):
    id: str
    active: bool
    version: int


class BookingInput(Input):
    resource_id: str = Field(min_length=1, max_length=36)
    start_at: AwareDatetime
    end_at: AwareDatetime
    purpose: str = Field(min_length=1, max_length=200)

    @field_validator("start_at", "end_at")
    @classmethod
    def utc(cls, value: datetime) -> datetime:
        """同じ瞬間の異なるoffset表記を正規化する。"""
        return value.astimezone(UTC)


class Reservation(BookingInput):
    id: str
    subject: str
    status: Literal["confirmed", "cancelled"]
    version: int


class CancelInput(Input):
    version: int = Field(ge=1)


class Event(BaseModel):
    id: str
    reservation_id: str
    actor: str
    action: str
    at: datetime


class Detail(BaseModel):
    reservation: Reservation
    events: list[Event]


class BusySlot(BaseModel):
    start_at: datetime
    end_at: datetime
    label: str = "予約済み"
    reservation: Reservation | None = None


class ErrorBody(BaseModel):
    code: str
    request_id: str


def validate_booking(value: BookingInput, now: datetime) -> None:
    """新規要求の時刻、刻み、長さと日本時間の日付を検証する。"""
    start, end = value.start_at, value.end_at
    if not now < start <= now + timedelta(days=30):
        raise DomainError("start_out_of_range", 422)
    if not timedelta(minutes=15) <= end - start <= timedelta(hours=4):
        raise DomainError("duration_out_of_range", 422)
    if any(t.minute % 15 or t.second or t.microsecond for t in (start, end)):
        raise DomainError("quarter_hour_required", 422)
    if start.astimezone(JST).date() != end.astimezone(JST).date():
        raise DomainError("same_japan_day_required", 422)


def require_admin(user: User) -> None:
    """管理者に限定する操作の権限を確認する。"""
    if not user.admin:
        raise DomainError("forbidden", 403)


def require_owner(user: User, reservation: Reservation) -> None:
    """本人または管理者だけに詳細と取消を許可する。"""
    if not user.admin and reservation.subject != user.subject:
        raise DomainError("forbidden", 403)
