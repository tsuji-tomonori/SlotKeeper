from __future__ import annotations

from typing import Annotated
from uuid import uuid4

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.apis.sequence_types import CallerIdentity, Clock, RequestContext
from app.core.clock import SystemClock
from app.integrations.identity.deps import get_access_token_verifier
from app.integrations.identity.port import AccessTokenVerifierPort
from app.integrations.identity.schemas import AccessTokenRejectedError

bearer = HTTPBearer(auto_error=False)


async def get_caller_identity(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    verifier: Annotated[AccessTokenVerifierPort, Depends(get_access_token_verifier)],
) -> CallerIdentity:
    """Bearer tokenを検証し、呼び出し元の subject と group を取得する。"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="authentication_required",
        )
    try:
        principal = await verifier.verify_access_token(credentials.credentials)
    except AccessTokenRejectedError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_token",
        ) from error
    return CallerIdentity(principal_id=principal.principal_id, groups=principal.groups)


async def get_request_context(
    request: Request,
    user_agent: Annotated[str | None, Header(alias="User-Agent")] = None,
) -> RequestContext:
    """HTTP middlewareが採番した要求IDをログと応答の追跡IDにする。"""
    client_host = request.client.host if request.client else ""
    correlation_id = str(getattr(request.state, "request_id", "") or uuid4())
    return RequestContext(
        correlation_id=correlation_id,
        source_ip=client_host,
        user_agent=user_agent or "",
    )


def get_clock() -> Clock:
    """業務判定で使う現在時刻を依存として提供する。"""
    return SystemClock()
