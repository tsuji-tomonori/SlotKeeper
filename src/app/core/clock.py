from __future__ import annotations

from datetime import UTC, datetime


class SystemClock:
    """UTCの現在時刻を返す時計です。"""

    def now(self) -> datetime:
        return datetime.now(UTC)
