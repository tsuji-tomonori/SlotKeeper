"""資源登録APIを検査する。"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from tests.helpers import Signer, error_reason

pytestmark = pytest.mark.db


def test_user_cannot_create_resource(client: TestClient, signed: Signer) -> None:
    """Given 一般利用者 When 管理API Then 403。 [SLOT-01-AC] [COM-04-AC]"""
    response = client.post("/resources", json={"name": "会議室"}, headers=signed())
    assert response.status_code == 403
    assert error_reason(response) == "forbidden"


def test_admin_creates_active_resource(client: TestClient, signed: Signer, database: None) -> None:
    """Given 管理者 When 前後空白つきの資源名で登録 Then 201で空白を除き有効な初期版を返す。 [SLOT-01-AC] [RULE-14-AC]"""
    response = client.post(
        "/resources",
        json={"name": "  会議室 登録確認  ", "description": "", "kind": "equipment"},
        headers=signed("admin", True),
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["name"] == "会議室 登録確認"
    assert body["active"] is True and body["version"] == 1 and body["kind"] == "equipment"
