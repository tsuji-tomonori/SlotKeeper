import asyncio
from typing import Any

from mangum import Mangum

from app.main import app

_adapter = Mangum(app, lifespan="off")


def _ensure_event_loop() -> None:
    """Python 3.14では暗黙のevent loopが作られないため、Mangum用に明示して用意する。"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = None
    if loop is None or loop.is_closed():
        asyncio.set_event_loop(asyncio.new_event_loop())


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """API Gateway HTTP APIのイベントをASGIアプリへ渡す。"""
    _ensure_event_loop()
    return _adapter(event, context)
