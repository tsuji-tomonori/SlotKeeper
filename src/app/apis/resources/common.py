from enum import StrEnum


class ResourceKind(StrEnum):
    """予約対象の資源種別を表す列挙値です。"""

    # 会議室です。
    ROOM = "room"
    # 持ち運びできる備品です。
    EQUIPMENT = "equipment"
