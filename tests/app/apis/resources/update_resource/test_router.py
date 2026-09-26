"""資源編集APIを実PostgreSQLの独立transactionで検査する。"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from tests.conftest import FixedClock
from tests.helpers import Signer, create_reservation, error_reason

pytestmark = pytest.mark.db


def edit_payload(resource: dict[str, Any], **changes: object) -> dict[str, Any]:
    payload = {k: resource[k] for k in ["name", "description", "kind", "active", "version"]}
    return {**payload, **changes}


def test_versions_and_inactive(
    client: TestClient, signed: Signer, booking: dict[str, str], resource: dict[str, Any]
) -> None:
    """Given 古い資源版と無効資源 When 更新と作成 Then 409で先行更新維持。 [SLOT-AC05] [SLOT-AC11]"""
    url = "/resources/" + resource["resourceId"]
    admin = signed("admin", True)
    assert (
        client.put(url, headers=admin, json=edit_payload(resource, active=False)).status_code == 200
    )
    stale = client.put(url, headers=admin, json=edit_payload(resource))
    assert stale.status_code == 409 and error_reason(stale) == "stale_version"
    inactive = create_reservation(client, signed, booking)
    assert inactive.status_code == 409 and error_reason(inactive) == "resource_inactive"


def test_future_prevents_disable(
    client: TestClient, signed: Signer, booking: dict[str, str], resource: dict[str, Any]
) -> None:
    """Given 将来の確定予約 When 無効化 Then 409。 [SLOT-AC05] [RULE-08-AC]"""
    assert create_reservation(client, signed, booking).status_code == 201
    response = client.put(
        "/resources/" + resource["resourceId"],
        headers=signed("admin", True),
        json=edit_payload(resource, active=False),
    )
    assert response.status_code == 409
    assert error_reason(response) == "future_reservations_exist"


def test_create_vs_disable(
    client: TestClient, signed: Signer, booking: dict[str, str], resource: dict[str, Any]
) -> None:
    """Given 有効資源 When 予約作成と無効化を競合 Then 両方成功しない。 [SLOT-AC10] [RULE-08-AC]"""
    barrier = Barrier(2)

    def reserve() -> Any:
        barrier.wait()
        return create_reservation(client, signed, booking)

    def disable() -> Any:
        barrier.wait()
        return client.put(
            "/resources/" + resource["resourceId"],
            headers=signed("admin", True),
            json=edit_payload(resource, active=False),
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        reserved = pool.submit(reserve)
        disabled = pool.submit(disable)
        results = [reserved.result().status_code, disabled.result().status_code]
    assert results in ([201, 409], [409, 200])


def test_disable_after_start_keeps_record(
    client: TestClient,
    signed: Signer,
    booking: dict[str, str],
    resource: dict[str, Any],
    timer: FixedClock,
) -> None:
    """Given 開始済みの確定予約 When 資源を無効化 Then 無効化でき既存記録を保持し新規予約は拒否する。 [RULE-07-AC]"""
    reservation = create_reservation(client, signed, booking).json()
    timer.value = timer.value.replace(day=26, hour=1, minute=30)
    response = client.put(
        "/resources/" + resource["resourceId"],
        headers=signed("admin", True),
        json=edit_payload(resource, active=False),
    )
    assert response.status_code == 200, response.text
    kept = client.get("/reservations/" + reservation["reservationId"], headers=signed()).json()
    assert kept["reservation"]["status"] == "confirmed"
    later = {**booking, "startAt": "2026-09-26T05:00:00Z", "endAt": "2026-09-26T06:00:00Z"}
    assert create_reservation(client, signed, later).status_code == 409
    future = client.get("/reservations?future=true&limit=100", headers=signed()).json()["items"]
    assert all(r["resourceId"] != resource["resourceId"] for r in future)


def test_missing_resource_returns_404(client: TestClient, signed: Signer, database: None) -> None:
    """Given 存在しない資源 When 編集 Then 404で区別する。 [COM-03-AC]"""
    edit = {"name": "なし", "description": "", "kind": "room", "active": True, "version": 1}
    response = client.put("/resources/" + str(uuid4()), headers=signed("admin", True), json=edit)
    assert response.status_code == 404
    assert error_reason(response) == "resource_not_found"
