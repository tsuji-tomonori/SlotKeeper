from __future__ import annotations

from functools import lru_cache

from app.core.config import settings
from app.integrations.identity.jwt_provider.client import JwtAccessTokenVerifier
from app.integrations.identity.port import AccessTokenVerifierPort


@lru_cache
def get_access_token_verifier() -> AccessTokenVerifierPort:
    """環境設定に応じた access token verifier を返す。"""
    return JwtAccessTokenVerifier(settings)
