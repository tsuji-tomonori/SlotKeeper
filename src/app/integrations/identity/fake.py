from __future__ import annotations

from collections.abc import Mapping

from app.integrations.identity.schemas import AccessTokenRejectedError, VerifiedPrincipal


class FakeAccessTokenVerifier:
    """テストで token 文字列と利用者の対応を固定する verifier です。"""

    def __init__(self, principals: Mapping[str, VerifiedPrincipal]) -> None:
        self._principals = dict(principals)

    async def verify_access_token(self, token: str) -> VerifiedPrincipal:
        """登録済み token だけを受理する。"""
        principal = self._principals.get(token)
        if principal is None:
            raise AccessTokenRejectedError("invalid_token")
        return principal
