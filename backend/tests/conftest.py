"""署名付き合成利用者と開発DBから分離したテストDBを提供する。"""

import importlib
import os
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from slotkeeper import auth
from slotkeeper.app import app
from slotkeeper.settings import settings


@pytest.fixture(scope="session")
def private_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture
def signed(private_key, monkeypatch):
    """本番と同じJWT署名検証へテスト公開鍵を渡す。"""
    monkeypatch.setattr(
        auth,
        "jwks",
        lambda: SimpleNamespace(
            get_signing_key_from_jwt=lambda token: SimpleNamespace(key=private_key.public_key())
        ),
    )

    def make(subject="alice", admin=False, **overrides):
        now = datetime.now(UTC)
        claims = {
            "sub": subject,
            "iat": now,
            "exp": now + timedelta(hours=1),
            "iss": settings().issuer,
            "aud": settings().client_id,
            "azp": settings().client_id,
            "typ": "Bearer",
            "realm_access": {"roles": ["admin"] if admin else []},
        }
        claims.update(overrides)
        return {"Authorization": "Bearer " + jwt.encode(claims, private_key, algorithm="RS256")}

    return make


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def database():
    if os.environ.get("SLOT_TEST_DB") != "1":
        pytest.fail("実DB検査は専用PostgreSQLが必要。Compose verifyを実行する。")
    if "slotkeeper_test" not in settings().database_url:
        pytest.fail("開発DBでの受入試験は禁止")
    from tools.project.migrate import migrate

    migrate()


@pytest.fixture
def resource(database, client, signed):
    response = client.post(
        "/resources",
        headers=signed("admin", True),
        json={"name": "試験資源 " + str(uuid4()), "description": "合成データ", "kind": "room"},
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
def timer(monkeypatch):
    class Timer:
        value = datetime(2026, 9, 25, 0, 0, tzinfo=UTC)

        def now(self):
            return self.value

    timer = Timer()
    for name in [
        "resources_update",
        "reservations_create",
        "reservations_cancel",
        "reservations_list",
    ]:
        module = importlib.import_module("slotkeeper.operations." + name + ".endpoint")
        app.dependency_overrides[module.clock] = lambda: timer
    yield timer
    app.dependency_overrides.clear()


@pytest.fixture
def booking(resource, timer):
    return {
        "resource_id": resource["id"],
        "start_at": "2026-09-26T01:00:00Z",
        "end_at": "2026-09-26T02:00:00Z",
        "purpose": "受入試験",
    }
