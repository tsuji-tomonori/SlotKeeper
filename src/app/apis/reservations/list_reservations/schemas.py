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
)


class ListReservationsQuery(PageQuery):
    """自分の予約一覧の絞り込み条件です。"""

    day: CalendarDate | None = Field(
        default=None,
        description="日本時間の日付で予約を絞り込みます。未指定なら全期間です。",
    )
    status: ReservationStatus | None = Field(
        default=None,
        description="予約の状態で絞り込みます。未指定なら全状態です。",
    )
    future: bool = Field(
        default=True,
        description="trueの場合、開始前の確定予約だけを返します。",
    )


class ErrorResource(ApiBaseModel):
    """予約一覧取得のエラー復帰に使用する絞り込み条件です。"""

    day: CalendarDate | None = Field(
        default=None,
        description="一覧復帰時に同じ絞り込みを再現するための日付です。",
    )
    status: ReservationStatus | None = Field(
        default=None,
        description="一覧復帰時に同じ絞り込みを再現するための予約状態です。",
    )


class ReservationItemResponse(ApiBaseModel):
    """自分の予約一覧の1件分の予約です。"""

    reservation_id: ResourceId = Field(description="予約を一意に識別するIDです。")
    resource_id: ResourceId = Field(description="予約対象の資源を一意に識別するIDです。")
    owner_principal_id: PrincipalId = Field(description="予約者を表す認証主体IDです。")
    start_at: BookingTimestamp = Field(description="予約開始日時です。")
    end_at: BookingTimestamp = Field(description="予約終了日時です。この時刻を含みません。")
    purpose: PurposeText = Field(description="予約目的です。本人と管理者だけに返します。")
    status: ReservationStatus = Field(description="予約の状態です。")
    version: RowVersion = Field(description="予約取消の楽観ロックに使う版です。")


class ListReservationsResponse(ApiBaseModel):
    """自分の予約一覧のレスポンスです。"""

    items: list[ReservationItemResponse] = Field(
        description="一覧レスポンスに含まれるリソース配列です。"
    )
    next_token: PageToken | None = Field(
        default=None,
        description="次ページを取得するために前回レスポンスから受け取る継続tokenです。",
    )
