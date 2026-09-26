"""SQLの投影に対応する共有行型を定義する。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid")
    input_hash: str
    response: str
    expires_at: datetime


class Count(BaseModel):
    model_config = ConfigDict(extra="forbid")
    count: int
