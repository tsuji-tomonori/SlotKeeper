from __future__ import annotations

import base64
import binascii
import json
from enum import StrEnum
from typing import NoReturn, cast
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status

from app.apis.exceptions import ApiFunctionError

JST = ZoneInfo("Asia/Tokyo")


class IdentityGroup(StrEnum):
    """CallerIdentity.groups に含まれる認可グループです。"""

    # 資源管理と全予約の取消ができる管理者です。
    ADMIN = "admin"


def raise_missing_runtime_dependency(function_name: str) -> NoReturn:
    """Sequence function に runtime dependency が注入されていない場合の 500 を返す。"""
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"{function_name} requires runtime dependencies.",
    )


def encode_page_token(values: list[str]) -> str:
    """keyset paging の最終行キーを継続tokenへ変換する。"""
    raw = json.dumps(values, ensure_ascii=False, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _page_token_values(token: str) -> object:
    try:
        padded = token + "=" * (-len(token) % 4)
        return json.loads(base64.urlsafe_b64decode(padded.encode()))
    except (binascii.Error, UnicodeDecodeError, ValueError):
        return None


def decode_page_token(token: str | None, size: int) -> list[str] | None:
    """継続tokenを keyset paging の最終行キーへ戻す。"""
    if token is None:
        return None
    values = _page_token_values(token)
    if not isinstance(values, list) or len(cast(list[object], values)) != size:
        raise ApiFunctionError(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "invalid_page_token",
            summary="nextToken が前回レスポンスの継続tokenとして解釈できない場合。",
        )
    return [str(value) for value in cast(list[object], values)]
