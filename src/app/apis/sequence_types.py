from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from app.apis.types import PageToken, PrincipalId, ResourceId


@dataclass(frozen=True)
class CallerIdentity:
    """Sequence stepで参照する検証済みの呼び出し元認証情報です。"""

    principal_id: PrincipalId
    groups: Sequence[str]
    scopes: Sequence[str] = ()


@dataclass(frozen=True)
class RequestContext:
    """Sequence stepでログと応答を対応付けるリクエスト文脈です。"""

    correlation_id: str
    source_ip: str
    user_agent: str
    actor_type: str = "USER"


class Clock(Protocol):
    """業務判定で用いる現在時刻の取得契約です。"""

    def now(self) -> datetime: ...


@dataclass(frozen=True)
class SequencePage[T]:
    """Sequence step間で受け渡すページング済み一覧です。"""

    items: Sequence[T]
    next_token: PageToken | None


@dataclass(frozen=True)
class IdempotencyRecordRef:
    """予約作成要求の成功記録の参照情報です。"""

    idempotency_key: str
    request_hash: str | None = None
    response_payload: str | None = None
    expires_at: datetime | None = None
    is_expired: bool = False


@dataclass(frozen=True)
class ResourceRef:
    """同一資源の変更を競合させた資源の参照情報です。"""

    resource_id: ResourceId
    active: bool
    row_version: int


@dataclass(frozen=True)
class EventRef:
    """追記したイベントの参照情報です。"""

    event_id: ResourceId
