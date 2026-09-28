from pydantic import Field

from app.apis.base import ApiBaseModel
from app.apis.reservations.common import ReservationStatus
from app.apis.responses import PageQuery
from app.apis.types import (
    BookingTimestamp,
    CalendarDate,
    PageToken,
    PrincipalId,
    PurposeText,
    ResourceId,
    RowVersion,
    Timestamp,
)


class GetResourceScheduleQuery(PageQuery):
    """予約表の取得条件です。"""

    day: CalendarDate = Field(description="日本時間で予約表を表示する日付です。")
    limit: int = Field(
        default=100, ge=1, le=100, description="一覧APIで1回に返却する最大件数です。"
    )


class ErrorResource(ApiBaseModel):
    """予約表取得のエラー復帰に使用する対象リソースです。"""

    resource_id: ResourceId | None = Field(
        default=None,
        description="予約表の対象資源の存在確認、問い合わせに使用する資源IDです。",
    )
    day: CalendarDate | None = Field(
        default=None,
        description="予約表を再取得するための日付です。",
    )


class ScheduleReservationResponse(ApiBaseModel):
    """本人または管理者だけに返す予約の詳細です。"""

    reservation_id: ResourceId = Field(description="予約を一意に識別するIDです。")
    resource_id: ResourceId = Field(description="予約対象の資源を一意に識別するIDです。")
    owner_principal_id: PrincipalId = Field(description="予約者を表す認証主体IDです。")
    start_at: BookingTimestamp = Field(description="予約開始日時です。")
    end_at: BookingTimestamp = Field(description="予約終了日時です。この時刻を含みません。")
    purpose: PurposeText = Field(description="予約目的です。本人と管理者だけに返します。")
    status: ReservationStatus = Field(description="予約の状態です。")
    version: RowVersion = Field(description="予約取消の楽観ロックに使う版です。")


class ScheduleSlotResponse(ApiBaseModel):
    """予約表の1件分の予約済み時間帯です。"""

    start_at: Timestamp = Field(description="予約済み時間帯の開始日時です。")
    end_at: Timestamp = Field(description="予約済み時間帯の終了日時です。この時刻を含みません。")
    label: str = Field(description="共有予約表に表示する固定の表示名です。")
    reservation: ScheduleReservationResponse | None = Field(
        default=None,
        description="呼び出し元が予約者本人または管理者の場合だけ返す予約の詳細です。",
    )


class GetResourceScheduleResponse(ApiBaseModel):
    """予約表のレスポンスです。"""

    items: list[ScheduleSlotResponse] = Field(
        description="一覧レスポンスに含まれるリソース配列です。"
    )
    next_token: PageToken | None = Field(
        default=None,
        description="次ページを取得するために前回レスポンスから受け取る継続tokenです。",
    )
