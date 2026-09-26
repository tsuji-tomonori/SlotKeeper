"""署名と用途を検証してCognitoとローカルOIDCを共通利用者へ変換する。"""

from functools import lru_cache
from typing import Annotated, Any

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from slotkeeper.domain import DomainError, User
from slotkeeper.settings import settings

bearer = HTTPBearer(auto_error=False)


@lru_cache
def jwks() -> jwt.PyJWKClient:
    """公開鍵を短時間キャッシュし鍵の更新に追従する。"""
    return jwt.PyJWKClient(settings().jwks_url, cache_jwk_set=True, lifespan=300, timeout=5)


def validate_claims(token: str) -> User:
    """署名、有効期限、発行者、clientとaccess用途をすべて確認する。"""
    config = settings()
    try:
        key = jwks().get_signing_key_from_jwt(token).key
        claims: dict[str, Any] = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            issuer=config.issuer,
            options={
                "verify_aud": config.auth_mode != "cognito",
                "require": ["exp", "iat", "sub", "iss"],
            },
            audience=config.client_id if config.auth_mode != "cognito" else None,
        )
        if config.auth_mode == "cognito":
            if claims.get("token_use") != "access" or claims.get("client_id") != config.client_id:
                raise DomainError("invalid_token", 401)
            roles = claims.get("cognito:groups", [])
        else:
            if claims.get("azp") != config.client_id or claims.get("typ") != "Bearer":
                raise DomainError("invalid_token", 401)
            roles = claims.get("realm_access", {}).get("roles", [])
        if not isinstance(claims["sub"], str) or not claims["sub"] or not isinstance(roles, list):
            raise DomainError("invalid_token", 401)
        return User(subject=claims["sub"], admin="admin" in roles)
    except (jwt.PyJWTError, jwt.PyJWKClientError) as exc:
        raise DomainError("invalid_token", 401) from exc


def current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> User:
    """認証なしの業務API呼出しを拒否する。"""
    if credentials is None:
        raise DomainError("authentication_required", 401)
    return validate_claims(credentials.credentials)


Principal = Annotated[User, Depends(current_user)]
