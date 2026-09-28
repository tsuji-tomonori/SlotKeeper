from datetime import UTC, datetime

from pydantic import ConfigDict, Field, field_validator

from app.apis.base import ApiBaseModel
from app.apis.reservations.common import ReservationStatus
from app.apis.types import BookingTimestamp, PrincipalId, PurposeText, ResourceId, RowVersion


class CreateReservationRequest(ApiBaseModel):
    """予約作成のリクエストです。"""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    resource_id: ResourceId = Field(description="予約する資源を一意に識別するIDです。")
    start_at: BookingTimestamp = Field(
        description="予約開始日時です。15分刻みで、現在より後かつ30日以内です。"
    )
    end_at: BookingTimestamp = Field(
        description="予約終了日時です。15分刻みで、開始と同じ日本時間の日付内です。"
    )
    purpose: PurposeText = Field(description="予約目的です。1〜200文字です。")

    @field_validator("start_at", "end_at")
    @classmethod
    def normalize_to_utc(cls, value: datetime) -> datetime:
        """同じ瞬間の異なるoffset表記をUTCへ正規化する。"""
        return value.astimezone(UTC)


class ErrorResource(ApiBaseModel):
    """予約作成のエラー復帰に使用する対象リソースです。"""

    resource_id: ResourceId | None = Field(
        default=None,
        description="予約対象資源の存在確認、予約表の再取得に使用する資源IDです。",
    )
    idempotency_key: str | None = Field(
        default=None,
        description="同じ要求を再送するときに再利用するIdempotency-Keyです。",
    )


class CreateReservationResponse(ApiBaseModel):
    """作成した予約のレスポンスです。"""

    reservation_id: ResourceId = Field(description="予約を一意に識別するIDです。")
    resource_id: ResourceId = Field(description="予約対象の資源を一意に識別するIDです。")
    owner_principal_id: PrincipalId = Field(description="予約者を表す認証主体IDです。")
    start_at: BookingTimestamp = Field(description="予約開始日時です。")
    end_at: BookingTimestamp = Field(description="予約終了日時です。この時刻を含みません。")
    purpose: PurposeText = Field(description="予約目的です。本人と管理者だけに返します。")
    status: ReservationStatus = Field(description="予約の状態です。")
    version: RowVersion = Field(description="予約取消の楽観ロックに使う版です。")
