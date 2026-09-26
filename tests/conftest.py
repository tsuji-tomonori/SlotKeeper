"""署名付き合成利用者と開発DBから分離したテストDBを提供する。"""

from __future__ import annotations

import os
from collections.abc import Callable, Iterator
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

os.environ.setdefault(
    "SLOT_DATABASE_URL", "postgresql+psycopg://slotkeeper:test-only@localhost:5432/slotkeeper_test"
)

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from app.apis.deps import get_clock
from app.core.config import settings
from app.integrations.identity.deps import get_access_token_verifier
from app.integrations.identity.jwt_provider.client import JwtAccessTokenVerifier
from app.main import app

type Headers = dict[str, str]
type Signer = Callable[..., Headers]


class FixedClock:
    """テストで進められる現在時刻です。"""

    def __init__(self) -> None:
        self.value = datetime(2026, 9, 25, 0, 0, tzinfo=UTC)

    def now(self) -> datetime:
        return self.value


class TestKeyVerifier(JwtAccessTokenVerifier):
    """本番と同じJWT検証へテスト公開鍵を渡すverifierです。"""

    def __init__(self, public_key: Any) -> None:
        super().__init__(settings)
        self._public_key = public_key

    def signing_key(self, token: str) -> Any:
        _ = token
        return self._public_key


@pytest.fixture(scope="session")
def private_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture
def signed(private_key: rsa.RSAPrivateKey) -> Iterator[Signer]:
    """署名済みのOIDC access tokenを作り、検証器へテスト公開鍵を渡す。"""
    app.dependency_overrides[get_access_token_verifier] = lambda: TestKeyVerifier(
        private_key.public_key()
    )

    def make(subject: str = "alice", admin: bool = False, **overrides: object) -> Headers:
        now = datetime.now(UTC)
        claims: dict[str, object] = {
            "sub": subject,
            "iat": now,
            "exp": now + timedelta(hours=1),
            "iss": settings.issuer,
            "aud": settings.client_id,
            "azp": settings.client_id,
            "typ": "Bearer",
            "realm_access": {"roles": ["admin"] if admin else []},
        }
        claims.update(overrides)
        return {"Authorization": "Bearer " + jwt.encode(claims, private_key, algorithm="RS256")}

    yield make
    app.dependency_overrides.pop(get_access_token_verifier, None)


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def database() -> None:
    if os.environ.get("SLOT_TEST_DB") != "1":
        pytest.fail("実DB検査は専用PostgreSQLが必要。Compose verifyを実行する。")
    if "slotkeeper_test" not in settings.database_url:
        pytest.fail("開発DBでの受入試験は禁止")
    from tools.project.migrate import migrate

    migrate()


@pytest.fixture
def timer() -> Iterator[FixedClock]:
    clock = FixedClock()
    app.dependency_overrides[get_clock] = lambda: clock
    yield clock
    app.dependency_overrides.pop(get_clock, None)


@pytest.fixture
def resource(database: None, client: TestClient, signed: Signer) -> dict[str, Any]:
    response = client.post(
        "/resources",
        headers=signed("admin", True),
        json={"name": "試験資源 " + str(uuid4()), "description": "合成データ", "kind": "room"},
    )
    assert response.status_code == 201, response.text
    body: dict[str, Any] = response.json()
    return body


@pytest.fixture
def booking(resource: dict[str, Any], timer: FixedClock) -> dict[str, str]:
    _ = timer
    return {
        "resourceId": resource["resourceId"],
        "startAt": "2026-09-26T01:00:00Z",
        "endAt": "2026-09-26T02:00:00Z",
        "purpose": "受入試験",
    }
