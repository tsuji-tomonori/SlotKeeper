"""予約取消APIを実PostgreSQLの独立transactionで検査する。"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from tests.conftest import FixedClock
from tests.helpers import Signer, create_reservation, db_connect, error_reason

pytestmark = pytest.mark.db


def cancel(client: TestClient, headers: dict[str, str], reservation_id: str, version: int) -> Any:
    return client.post(
        "/reservations/" + reservation_id + "/cancel", headers=headers, json={"version": version}
    )


def test_privacy_and_cancel(
    client: TestClient, signed: Signer, booking: dict[str, str], resource: dict[str, Any]
) -> None:
    """Given Aの予約 When B・Aが詳細取得と取消 Then Bは403で情報非公開、Aは取消。 [SLOT-AC04] [SLOT-AC08] [SLOT-02-AC] [RULE-09-AC] [RULE-13-AC] [RULE-06-AC] [COM-04-AC]"""
    reservation_id = create_reservation(client, signed, booking).json()["reservationId"]
    assert client.get("/reservations/" + reservation_id, headers=signed("bob")).status_code == 403
    assert cancel(client, signed("bob"), reservation_id, 1).status_code == 403
    schedule = client.get(
        "/resources/" + resource["resourceId"] + "/schedule?day=2026-09-26",
        headers=signed("bob"),
    ).json()["items"]
    assert all(set(row) == {"startAt", "endAt", "label"} for row in schedule)
    response = cancel(client, signed(), reservation_id, 1)
    assert response.json()["status"] == "cancelled"
    assert (
        len(client.get("/reservations/" + reservation_id, headers=signed()).json()["events"]) == 2
    )
    again = cancel(client, signed(), reservation_id, 2)
    assert again.status_code == 409
    assert error_reason(again) == "already_cancelled"
    assert create_reservation(client, signed, booking).status_code == 201


def test_cancel_boundaries(
    client: TestClient, signed: Signer, booking: dict[str, str], timer: FixedClock
) -> None:
    """Given 確定予約 When 古い版と開始時刻ちょうどの取消 Then 409、履歴1件。 [SLOT-AC11] [SLOT-AC13] [RULE-13-AC]"""
    reservation_id = create_reservation(client, signed, booking).json()["reservationId"]
    stale = cancel(client, signed(), reservation_id, 2)
    assert stale.status_code == 409 and error_reason(stale) == "stale_version"
    timer.value += timedelta(days=1, hours=1)
    started = cancel(client, signed(), reservation_id, 1)
    assert started.status_code == 409 and error_reason(started) == "already_started"
    assert (
        len(client.get("/reservations/" + reservation_id, headers=signed()).json()["events"]) == 1
    )


def test_admin_cancels_other_before_start(
    client: TestClient, signed: Signer, booking: dict[str, str], timer: FixedClock
) -> None:
    """Given Aの開始前予約 When 管理者が取消 Then 取消と履歴2件、開始後は管理者も拒否。 [SLOT-AC04] [SLOT-07-AC] [RULE-09-AC]"""
    reservation_id = create_reservation(client, signed, booking).json()["reservationId"]
    admin = signed("admin", True)
    detail = client.get("/reservations/" + reservation_id, headers=admin)
    assert detail.status_code == 200
    assert detail.json()["reservation"]["purpose"] == booking["purpose"]
    timer.value += timedelta(minutes=5)
    assert cancel(client, admin, reservation_id, 1).status_code == 200
    events = client.get("/reservations/" + reservation_id, headers=signed()).json()["events"]
    assert [e["action"] for e in events] == ["created", "cancelled"]
    started = create_reservation(
        client,
        signed,
        {**booking, "startAt": "2026-09-26T05:00:00Z", "endAt": "2026-09-26T06:00:00Z"},
    ).json()
    timer.value = timer.value.replace(day=26, hour=5)
    assert cancel(client, admin, started["reservationId"], 1).status_code == 409


def test_cancel_and_rebook_concurrent(
    client: TestClient, signed: Signer, booking: dict[str, str]
) -> None:
    """Given 確定予約 When 取消と同じ枠の再予約を同時実行 Then 重なる確定予約は最大1件。 [RULE-06-AC]"""
    reservation_id = create_reservation(client, signed, booking).json()["reservationId"]
    barrier = Barrier(2)

    def cancel_first() -> Any:
        barrier.wait(timeout=15)
        return cancel(client, signed(), reservation_id, 1)

    def rebook() -> Any:
        barrier.wait(timeout=15)
        return create_reservation(client, signed, booking, subject="bob")

    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(cancel_first)
        second = pool.submit(rebook)
        cancelled, rebooked = first.result(), second.result()
    assert cancelled.status_code == 200
    assert rebooked.status_code in (201, 409)
    with db_connect() as connection:
        row = connection.execute(
            "SELECT count(*) AS count FROM slotkeeper.reservations"
            " WHERE resource_id=%s AND status='confirmed'",
            (booking["resourceId"],),
        ).fetchone()
    assert row is not None
    assert row["count"] == (1 if rebooked.status_code == 201 else 0)
    if rebooked.status_code == 409:
        assert create_reservation(client, signed, booking, subject="bob").status_code == 201


def test_missing_reservation_returns_404(
    client: TestClient, signed: Signer, database: None
) -> None:
    """Given 存在しない予約 When 取消 Then 404で区別する。 [COM-03-AC]"""
    response = cancel(client, signed(), str(uuid4()), 1)
    assert response.status_code == 404
    assert error_reason(response) == "reservation_not_found"
