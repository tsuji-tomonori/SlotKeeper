from typing import Any

from psycopg import AsyncConnection, Connection

class DSQLAsyncConnection(AsyncConnection[Any]):
    @classmethod
    async def connect(cls, conninfo: str = "", **kwargs: Any) -> DSQLAsyncConnection: ...  # pyright: ignore[reportIncompatibleMethodOverride]

def connect(**kwargs: Any) -> Connection[dict[str, Any]]: ...
