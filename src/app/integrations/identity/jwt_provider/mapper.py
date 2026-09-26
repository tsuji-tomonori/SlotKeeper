from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from app.core.config import Settings
from app.integrations.identity.schemas import AccessTokenRejectedError, VerifiedPrincipal


def to_verified_principal(claims: Mapping[str, Any], config: Settings) -> VerifiedPrincipal:
    """CognitoとローカルOIDCのclaimを共通の利用者へ変換し、用途とclientを検証する。"""
    if config.auth_mode == "cognito":
        if claims.get("token_use") != "access" or claims.get("client_id") != config.client_id:
            raise AccessTokenRejectedError("invalid_token")
        roles: object = claims.get("cognito:groups", [])
    else:
        if claims.get("azp") != config.client_id or claims.get("typ") != "Bearer":
            raise AccessTokenRejectedError("invalid_token")
        realm_access: object = claims.get("realm_access", {})
        roles = (
            cast(dict[str, object], realm_access).get("roles", [])
            if isinstance(realm_access, dict)
            else None
        )
    subject = claims.get("sub")
    if not isinstance(subject, str) or not subject or not isinstance(roles, list):
        raise AccessTokenRejectedError("invalid_token")
    return VerifiedPrincipal(
        principal_id=subject,
        groups=tuple(str(role) for role in cast(list[object], roles)),
    )
