"""予約詳細APIを実PostgreSQLで検査する。"""

from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from tests.helpers import Signer, create_reservation, error_reason

pytestmark = pytest.mark.db


def test_owner_and_admin_view_history(
    client: TestClient, signed: Signer, booking: dict[str, str]
) -> None:
    """Given Aの予約 When 本人・管理者・他人が詳細取得 Then 本人と管理者は履歴を閲覧し他人は403。 [SLOT-07-AC] [RULE-09-AC] [COM-04-AC]"""
    reservation_id = create_reservation(client, signed, booking).json()["reservationId"]
    own = client.get("/reservations/" + reservation_id, headers=signed())
    assert own.status_code == 200
    assert [e["action"] for e in own.json()["events"]] == ["created"]
    admin = client.get("/reservations/" + reservation_id, headers=signed("admin", True))
    assert admin.json()["reservation"]["purpose"] == booking["purpose"]
    other = client.get("/reservations/" + reservation_id, headers=signed("bob"))
    assert other.status_code == 403
    assert booking["purpose"] not in other.text


def test_missing_reservation_returns_404(
    client: TestClient, signed: Signer, database: None
) -> None:
    """Given 存在しない予約 When 詳細取得 Then 404で区別する。 [COM-03-AC]"""
    response = client.get("/reservations/" + str(uuid4()), headers=signed())
    assert response.status_code == 404
    assert error_reason(response) == "reservation_not_found"
