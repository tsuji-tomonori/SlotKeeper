"""router testから実PostgreSQLの状態を検査するための非同期harnessです。"""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from dataclasses import dataclass
from typing import Any

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import settings
from app.db.session import create_async_db_engine, create_session_factory
from app.main import app

TABLES = frozenset(
    {"resources", "users", "reservations", "reservation_events", "idempotency_records"}
)
COLUMNS = frozenset(
    {
        "resource_id",
        "reservation_id",
        "principal_id",
        "owner_principal_id",
        "idempotency_key",
        "name",
        "status",
    }
)


@dataclass(frozen=True)
class RouterDbHarness:
    """ASGI clientと検証用session factoryの組です。"""

    client: httpx.AsyncClient
    session_factory: async_sessionmaker[AsyncSession]


async def create_router_db_harness() -> AsyncIterator[RouterDbHarness]:
    """アプリと同じDBへ接続するASGI clientを作る。"""
    engine = create_async_db_engine(settings)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield RouterDbHarness(client=client, session_factory=create_session_factory(engine))
    await engine.dispose()


async def count_rows(
    session_factory: async_sessionmaker[AsyncSession],
    table: str,
    where: Mapping[str, object] | None = None,
) -> int:
    """許可したテーブルと列だけを条件にして行数を数える。"""
    if table not in TABLES or not set(where or {}) <= COLUMNS:
        raise ValueError(f"unsupported table or column: {table} {sorted(where or {})}")
    clauses = " AND ".join(f"{column} = :{column}" for column in where or {})
    sql = f"SELECT count(*) FROM slotkeeper.{table}" + (f" WHERE {clauses}" if clauses else "")  # noqa: S608
    async with session_factory() as session:
        return int((await session.execute(text(sql), dict(where or {}))).scalar_one())


async def fetch_one(
    session_factory: async_sessionmaker[AsyncSession],
    table: str,
    where: Mapping[str, object],
) -> dict[str, Any] | None:
    """許可したテーブルと列だけを条件にして1行を取得する。"""
    if table not in TABLES or not set(where) <= COLUMNS:
        raise ValueError(f"unsupported table or column: {table} {sorted(where)}")
    clauses = " AND ".join(f"{column} = :{column}" for column in where)
    sql = f"SELECT * FROM slotkeeper.{table} WHERE {clauses}"  # noqa: S608
    async with session_factory() as session:
        row = (await session.execute(text(sql), dict(where))).mappings().first()
    return None if row is None else dict(row)


async def seed_resource(
    harness: RouterDbHarness,
    admin_headers: Mapping[str, str],
    *,
    active: bool = True,
    name: str | None = None,
) -> dict[str, Any]:
    """API経由で資源を登録し、必要なら無効化する。"""
    from uuid import uuid4

    created = await harness.client.post(
        "/resources",
        headers=dict(admin_headers),
        json={"name": name or "router試験 " + str(uuid4()), "description": "", "kind": "room"},
    )
    assert created.status_code == 201, created.text
    resource: dict[str, Any] = created.json()
    if active:
        return resource
    updated = await harness.client.put(
        "/resources/" + resource["resourceId"],
        headers=dict(admin_headers),
        json={
            "name": resource["name"],
            "description": resource["description"],
            "kind": resource["kind"],
            "active": False,
            "version": resource["version"],
        },
    )
    assert updated.status_code == 200, updated.text
    body: dict[str, Any] = updated.json()
    return body


async def seed_reservation(
    harness: RouterDbHarness,
    headers: Mapping[str, str],
    resource_id: str,
    *,
    start_at: str = "2026-09-26T01:00:00Z",
    end_at: str = "2026-09-26T02:00:00Z",
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    """API経由で予約を作成する。"""
    from uuid import uuid4

    response = await harness.client.post(
        "/reservations",
        headers={**headers, "Idempotency-Key": idempotency_key or str(uuid4())},
        json={
            "resourceId": resource_id,
            "startAt": start_at,
            "endAt": end_at,
            "purpose": "router試験",
        },
    )
    assert response.status_code == 201, response.text
    body: dict[str, Any] = response.json()
    return body
