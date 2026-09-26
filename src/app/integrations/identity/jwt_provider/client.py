from __future__ import annotations

from typing import Any

import anyio.to_thread
import jwt

from app.core.config import Settings
from app.integrations.identity.jwt_provider.mapper import to_verified_principal
from app.integrations.identity.schemas import AccessTokenRejectedError, VerifiedPrincipal


class JwtAccessTokenVerifier:
    """JWKSの公開鍵で access token の署名と claim を検証する provider です。"""

    def __init__(self, config: Settings) -> None:
        self._config = config
        self._jwks = jwt.PyJWKClient(config.jwks_url, cache_jwk_set=True, lifespan=300, timeout=5)

    def signing_key(self, token: str) -> Any:
        """鍵更新に追従しながら token の署名鍵を取得する。"""
        return self._jwks.get_signing_key_from_jwt(token).key

    def decode(self, token: str) -> dict[str, Any]:
        """署名、有効期限、発行者、audienceを検証する。"""
        config = self._config
        verify_audience = config.auth_mode != "cognito"
        return jwt.decode(
            token,
            self.signing_key(token),
            algorithms=["RS256"],
            issuer=config.issuer,
            options={"verify_aud": verify_audience, "require": ["exp", "iat", "sub", "iss"]},
            audience=config.client_id if verify_audience else None,
        )

    async def verify_access_token(self, token: str) -> VerifiedPrincipal:
        """access token を検証し、利用者を返す。"""
        try:
            claims = await anyio.to_thread.run_sync(self.decode, token)
        except (jwt.PyJWTError, jwt.PyJWKClientError) as error:
            raise AccessTokenRejectedError("invalid_token") from error
        return to_verified_principal(claims, self._config)
