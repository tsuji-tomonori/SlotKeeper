from pydantic import Field

from app.apis.base import ApiBaseModel
from app.apis.reservations.common import ReservationAction, ReservationStatus
from app.apis.types import (
    BookingTimestamp,
    PrincipalId,
    PurposeText,
    ResourceId,
    RowVersion,
    Timestamp,
)


class ErrorResource(ApiBaseModel):
    """予約詳細取得のエラー復帰に使用する対象リソースです。"""

    reservation_id: ResourceId | None = Field(
        default=None,
        description="取得対象予約の存在確認、権限確認、問い合わせに使用する予約IDです。",
    )


class ReservationDetailResponse(ApiBaseModel):
    """予約詳細の予約情報です。"""

    reservation_id: ResourceId = Field(description="予約を一意に識別するIDです。")
    resource_id: ResourceId = Field(description="予約対象の資源を一意に識別するIDです。")
    owner_principal_id: PrincipalId = Field(description="予約者を表す認証主体IDです。")
    start_at: BookingTimestamp = Field(description="予約開始日時です。")
    end_at: BookingTimestamp = Field(description="予約終了日時です。この時刻を含みません。")
    purpose: PurposeText = Field(description="予約目的です。本人と管理者だけに返します。")
    status: ReservationStatus = Field(description="予約の状態です。")
    version: RowVersion = Field(description="予約取消の楽観ロックに使う版です。")


class ReservationEventResponse(ApiBaseModel):
    """予約の作成または取消の履歴です。"""

    event_id: ResourceId = Field(description="履歴を一意に識別するIDです。")
    reservation_id: ResourceId = Field(description="履歴の対象予約IDです。")
    actor_principal_id: PrincipalId = Field(description="操作した利用者の認証主体IDです。")
    action: ReservationAction = Field(description="予約に対する操作種別です。")
    occurred_at: Timestamp = Field(description="操作日時です。")


class GetReservationResponse(ApiBaseModel):
    """予約詳細と操作履歴のレスポンスです。"""

    reservation: ReservationDetailResponse = Field(description="予約の詳細です。")
    events: list[ReservationEventResponse] = Field(
        description="作成と取消の履歴を発生順に並べた一覧です。"
    )
