from pathlib import Path

from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.query import fetch_all

# This file is generated from SQL files in the sibling sql directory.
# Do not edit generated models by hand.

SQL_DIR = Path(__file__).parents[1] / "sql"


class SelectResourcesParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    after_name: str | None = None
    after_resource_id: str | None = None
    limit: int


class SelectResourcesRow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resource_id: str
    name: str
    description: str
    kind: str
    active: bool
    row_version: int


async def select_resources(
    session: AsyncSession,
    params: SelectResourcesParams,
) -> list[SelectResourcesRow]:
    """資源一覧を返すため、名前とIDの固定順で継続位置より後の資源を取得する。"""
    return await fetch_all(
        session,
        SQL_DIR / "001_select_resources.sql",
        params,
        SelectResourcesRow,
    )
