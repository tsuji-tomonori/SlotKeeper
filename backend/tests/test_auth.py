"""不正な署名、期限、発行者、client、用途を拒否する。"""

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from slotkeeper.auth import validate_claims
from slotkeeper.domain import DomainError


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
def test_bad_claims(client, signed, override):
    """Given 不正claim When 業務API呼出し Then 401でDB未接続。 [SLOT-AC14]"""
    response = client.get("/resources", headers=signed(**override))
    assert response.status_code == 401
    assert set(response.json()) == {"code", "request_id"}


def test_bad_signature(client, signed):
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


def test_anonymous_and_health(client):
    """Given 未認証 When 業務APIとhealth Then 業務401・healthは秘密なし。 [COM-04-AC] [COM-03-AC]"""
    assert client.get("/resources").status_code == 401
    response = client.get("/health")
    assert response.json() == {"status": "ok"}
    assert response.headers["cache-control"] == "no-store"


def test_user_cannot_create_resource(client, signed):
    """Given 一般利用者 When 管理API Then 403。 [SLOT-01-AC] [COM-04-AC]"""
    assert client.post("/resources", json={"name": "会議室"}, headers=signed()).status_code == 403


def test_cognito_access_and_id(monkeypatch, signed, private_key):
    """Given Cognito claim When accessとIDを検証 Then accessだけ受理。 [SLOT-AC14]"""
    monkeypatch.setenv("SLOT_AUTH_MODE", "cognito")
    from slotkeeper.settings import settings

    settings.cache_clear()
    try:
        token = signed(token_use="access", client_id="slotkeeper", **{"cognito:groups": ["admin"]})[
            "Authorization"
        ].split()[1]
        assert validate_claims(token).admin
        token = signed(token_use="id", client_id="slotkeeper")["Authorization"].split()[1]
        with pytest.raises(DomainError):
            validate_claims(token)
    finally:
        monkeypatch.delenv("SLOT_AUTH_MODE")
        settings.cache_clear()
