from __future__ import annotations

from typing import Protocol

from app.integrations.identity.schemas import VerifiedPrincipal


class AccessTokenVerifierPort(Protocol):
    """アプリ側が依存する access token 検証境界です。"""

    async def verify_access_token(self, token: str) -> VerifiedPrincipal:
        """access token を検証し、利用者を返す。"""
        ...
