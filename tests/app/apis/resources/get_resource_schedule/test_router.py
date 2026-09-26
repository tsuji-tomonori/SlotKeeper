"""予約表APIを実PostgreSQLで検査する。"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from tests.helpers import Signer, create_reservation, error_reason

pytestmark = pytest.mark.db


def test_schedule_hides_other_details(
    client: TestClient, signed: Signer, booking: dict[str, str], resource: dict[str, Any]
) -> None:
    """Given Aの予約 When A・B・管理者が予約表を取得 Then Bには時間帯と予約済みだけを返す。 [SLOT-02-AC] [RULE-09-AC]"""
    create_reservation(client, signed, booking)
    url = "/resources/" + resource["resourceId"] + "/schedule?day=2026-09-26"
    others = client.get(url, headers=signed("bob")).json()["items"]
    assert [set(row) for row in others] == [{"startAt", "endAt", "label"}]
    assert others[0]["label"] == "予約済み"
    own = client.get(url, headers=signed()).json()["items"]
    assert own[0]["reservation"]["purpose"] == booking["purpose"]
    admin = client.get(url, headers=signed("admin", True)).json()["items"]
    assert admin[0]["reservation"]["ownerPrincipalId"] == "alice"


def test_missing_resource_returns_404(client: TestClient, signed: Signer, database: None) -> None:
    """Given 存在しない資源 When 予約表取得 Then 404で区別する。 [COM-03-AC]"""
    response = client.get(
        "/resources/" + str(uuid4()) + "/schedule?day=2026-09-26", headers=signed()
    )
    assert response.status_code == 404
    assert error_reason(response) == "resource_not_found"
