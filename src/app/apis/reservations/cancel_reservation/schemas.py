from pydantic import ConfigDict, Field

from app.apis.base import ApiBaseModel
from app.apis.reservations.common import ReservationStatus
from app.apis.types import BookingTimestamp, PrincipalId, PurposeText, ResourceId, RowVersion


class CancelReservationRequest(ApiBaseModel):
    """予約取消のリクエストです。"""

    model_config = ConfigDict(extra="forbid")

    version: RowVersion = Field(description="取消前に取得した予約の版です。")


class ErrorResource(ApiBaseModel):
    """予約取消のエラー復帰に使用する対象リソースです。"""

    reservation_id: ResourceId | None = Field(
        default=None,
        description="取消対象予約の存在確認、再取得、問い合わせに使用する予約IDです。",
    )
    version: RowVersion | None = Field(
        default=None,
        description="取消要求で指定した予約の版です。",
    )


class CancelReservationResponse(ApiBaseModel):
    """取消後の予約のレスポンスです。"""

    reservation_id: ResourceId = Field(description="予約を一意に識別するIDです。")
    resource_id: ResourceId = Field(description="予約対象の資源を一意に識別するIDです。")
    owner_principal_id: PrincipalId = Field(description="予約者を表す認証主体IDです。")
    start_at: BookingTimestamp = Field(description="予約開始日時です。")
    end_at: BookingTimestamp = Field(description="予約終了日時です。この時刻を含みません。")
    purpose: PurposeText = Field(description="予約目的です。本人と管理者だけに返します。")
    status: ReservationStatus = Field(description="予約の状態です。")
    version: RowVersion = Field(description="予約取消の楽観ロックに使う版です。")
