from enum import StrEnum


class ReservationStatus(StrEnum):
    """予約の状態を表す列挙値です。"""

    # 確定済みで重複判定の対象になる予約です。
    CONFIRMED = "confirmed"
    # 取消済みで重複判定から除く予約です。
    CANCELLED = "cancelled"


class ReservationAction(StrEnum):
    """予約履歴の操作種別を表す列挙値です。"""

    # 予約を作成した操作です。
    CREATED = "created"
    # 予約を取消した操作です。
    CANCELLED = "cancelled"


BUSY_SLOT_LABEL = "予約済み"
