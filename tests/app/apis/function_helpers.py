"""functions.pyの単体テストでquery wrapperを差し替える補助です。"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from types import ModuleType
from typing import Any, cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.apis.sequence_types import CallerIdentity

NOW = datetime(2026, 9, 25, 0, 0, tzinfo=UTC)
ALICE = CallerIdentity(principal_id="alice", groups=())
BOB = CallerIdentity(principal_id="bob", groups=())
ADMIN = CallerIdentity(principal_id="admin", groups=("admin",))


class FixedClock:
    """単体テスト用の固定時計です。"""

    def __init__(self, value: datetime = NOW) -> None:
        self.value = value

    def now(self) -> datetime:
        return self.value


def fake_session() -> AsyncSession:
    """query wrapperを差し替えるため、実接続を持たないsessionの代わりを返す。"""
    return cast(AsyncSession, object())


@dataclass
class QueryRecorder:
    """差し替えたquery wrapperへ渡された引数を記録します。"""

    calls: list[tuple[str, Any]] = field(default_factory=lambda: [])

    def install(
        self,
        monkeypatch: pytest.MonkeyPatch,
        queries: ModuleType,
        name: str,
        result: object,
    ) -> None:
        async def fake(session: AsyncSession, params: Any) -> object:
            _ = session
            self.calls.append((name, params))
            return result

        monkeypatch.setattr(queries, name, fake)

    def params(self, name: str) -> Any:
        return next(params for called, params in self.calls if called == name)


def response_error(response: JSONResponse) -> tuple[int, str]:
    """error responseのstatusと業務上の理由コードを返す。"""
    body = json.loads(bytes(response.body))
    return response.status_code, str(body["error"]["details"][0]["reason"])
