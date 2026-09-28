from pathlib import Path

from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.query import fetch_one

# This file is generated from SQL files in the sibling sql directory.
# Do not edit generated models by hand.

SQL_DIR = Path(__file__).parents[1] / "sql"


class InsertResourcesParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resource_id: str
    name: str
    description: str
    kind: str


class InsertResourcesRow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resource_id: str
    name: str
    description: str
    kind: str
    active: bool
    row_version: int


async def insert_resources(
    session: AsyncSession,
    params: InsertResourcesParams,
) -> InsertResourcesRow | None:
    """管理者が登録した資源を有効な初期版で保存する。"""
    return await fetch_one(
        session,
        SQL_DIR / "001_insert_resources.sql",
        params,
        InsertResourcesRow,
    )
