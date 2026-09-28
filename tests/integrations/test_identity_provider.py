"""JWT providerのclaim変換と鍵取得clientの境界を検査する。"""

from __future__ import annotations

import pytest

from app.core.config import Settings
from app.integrations.identity.fake import FakeAccessTokenVerifier
from app.integrations.identity.jwt_provider.client import JwtAccessTokenVerifier
from app.integrations.identity.jwt_provider.mapper import to_verified_principal
from app.integrations.identity.schemas import AccessTokenRejectedError, VerifiedPrincipal


def test_cognito_access_and_id() -> None:
    """Given Cognito claim When accessとIDを検証 Then accessだけ受理。 [SLOT-AC14]"""
    config = Settings(auth_mode="cognito")
    principal = to_verified_principal(
        {
            "sub": "alice",
            "token_use": "access",
            "client_id": config.client_id,
            "cognito:groups": ["admin"],
        },
        config,
    )
    assert principal == VerifiedPrincipal(principal_id="alice", groups=("admin",))
    with pytest.raises(AccessTokenRejectedError):
        to_verified_principal(
            {"sub": "alice", "token_use": "id", "client_id": config.client_id}, config
        )


def test_jwks_client_is_bounded() -> None:
    """Given 設定済みJWKS URL When 鍵取得clientを作る Then 短いtimeoutとcache寿命を持つ。 [SLOT-AC14]"""
    verifier = JwtAccessTokenVerifier(Settings())
    jwks = verifier._jwks  # pyright: ignore[reportPrivateUsage]
    assert jwks.jwk_set_cache is not None
    assert jwks.timeout == 5


@pytest.mark.anyio
async def test_fake_verifier_rejects_unknown_token() -> None:
    """Given 登録済みtokenだけを持つfake When 未登録tokenを検証 Then 拒否する。 [SLOT-AC14]"""
    verifier = FakeAccessTokenVerifier({"known": VerifiedPrincipal("alice", ())})
    assert (await verifier.verify_access_token("known")).principal_id == "alice"
    with pytest.raises(AccessTokenRejectedError):
        await verifier.verify_access_token("unknown")
