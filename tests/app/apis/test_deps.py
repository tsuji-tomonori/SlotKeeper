"""不正な署名、期限、発行者、client、用途を拒否する。"""

from __future__ import annotations

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from tests.helpers import Signer, error_reason


@pytest.mark.parametrize(
    "override",
    [
        {"exp": 0},
        {"iss": "https://wrong.invalid"},
        {"aud": "wrong"},
        {"azp": "wrong"},
        {"typ": "ID"},
        {"sub": ""},
    ],
)
def test_bad_claims(client: TestClient, signed: Signer, override: dict[str, object]) -> None:
    """Given 不正claim When 業務API呼出し Then 401でDB未接続。 [SLOT-AC14]"""
    response = client.get("/resources", headers=signed(**override))
    assert response.status_code == 401
    assert set(response.json()) == {"error"}
    assert error_reason(response) == "invalid_token"
    assert response.json()["error"]["traceId"] == response.headers["X-Request-ID"]


def test_bad_signature(client: TestClient, signed: Signer) -> None:
    """Given 別の秘密鍵による改ざん When 検証 Then 401。 [SLOT-AC14]"""
    token = signed()["Authorization"].split()[1]
    claims = jwt.decode(token, options={"verify_signature": False})
    claims["realm_access"] = {"roles": ["admin"]}
    other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    response = client.get(
        "/resources",
        headers={"Authorization": "Bearer " + jwt.encode(claims, other, algorithm="RS256")},
    )
    assert response.status_code == 401


def test_anonymous_and_health(client: TestClient) -> None:
    """Given 未認証 When 業務APIとhealth Then 業務401・healthは秘密なし。 [COM-04-AC] [COM-03-AC]"""
    anonymous = client.get("/resources")
    assert anonymous.status_code == 401
    assert error_reason(anonymous) == "authentication_required"
    response = client.get("/health")
    assert response.json() == {"status": "ok"}
    assert response.headers["cache-control"] == "no-store"
