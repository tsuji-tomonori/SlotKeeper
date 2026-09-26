"""予約作成APIを実PostgreSQLの独立transactionで検査する。"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.apis.exceptions import ApiFunctionError
from tests.conftest import FixedClock
from tests.helpers import Signer, count_rows, create_reservation, db_connect, error_reason

pytestmark = pytest.mark.db


def test_create_adjacent_overlap(
    client: TestClient, signed: Signer, booking: dict[str, str]
) -> None:
    """Given 空き枠 When 作成・重複・隣接 Then 201・409・201。 [SLOT-AC01] [SLOT-AC02] [RULE-01-AC]"""
    first = create_reservation(client, signed, booking)
    assert first.status_code == 201, first.text
    overlap = create_reservation(
        client,
        signed,
        {**booking, "startAt": "2026-09-26T01:30:00Z", "endAt": "2026-09-26T02:30:00Z"},
    )
    assert overlap.status_code == 409
    assert error_reason(overlap) == "slot_taken"
    adjacent = create_reservation(
        client,
        signed,
        {**booking, "startAt": "2026-09-26T02:00:00Z", "endAt": "2026-09-26T03:00:00Z"},
    )
    assert adjacent.status_code == 201
    mine = client.get("/reservations?day=2026-09-26", headers=signed()).json()["items"]
    assert first.json()["reservationId"] in [r["reservationId"] for r in mine]


def test_replay_before_validation(
    client: TestClient, signed: Signer, booking: dict[str, str], timer: FixedClock
) -> None:
    """Given 成功後の取消と時刻進行 When 同一キー再送 Then 元の作成応答で履歴は増えない。 [SLOT-AC07] [SLOT-AC09] [SLOT-AC15] [RULE-10-AC]"""
    key = str(uuid4())
    first = create_reservation(client, signed, booking, key)
    assert first.status_code == 201
    mismatch = create_reservation(client, signed, {**booking, "purpose": "別の目的"}, key)
    assert mismatch.status_code == 409
    assert error_reason(mismatch) == "idempotency_input_mismatch"
    client.post(
        "/reservations/" + first.json()["reservationId"] + "/cancel",
        headers=signed(),
        json={"version": 1},
    )
    timer.value += timedelta(hours=23)
    replay = create_reservation(client, signed, booking, key)
    assert replay.json() == first.json()
    timer.value += timedelta(hours=1)
    assert create_reservation(client, signed, booking, key).status_code == 201


def test_replay_after_start(
    client: TestClient, signed: Signer, booking: dict[str, str], timer: FixedClock
) -> None:
    """Given 作成から24時間以内に予約開始 When 再送 Then 時刻違反にせず元応答。 [SLOT-AC15] [RULE-11-AC]"""
    timer.value += timedelta(hours=4)
    key = str(uuid4())
    first = create_reservation(client, signed, booking, key)
    timer.value += timedelta(hours=22)
    assert create_reservation(client, signed, booking, key).json() == first.json()


def test_twenty_concurrent(client: TestClient, signed: Signer, booking: dict[str, str]) -> None:
    """Given 空き枠と20利用者 When 同時送信 Then 1成功19競合で重複なし。 [SLOT-AC03]"""
    barrier = Barrier(20)

    def send(index: int) -> Any:
        barrier.wait(timeout=15)
        return create_reservation(client, signed, booking, subject="parallel-" + str(index))

    with ThreadPoolExecutor(max_workers=20) as pool:
        results = list(pool.map(send, range(20)))
    assert sorted(r.status_code for r in results) == [201] + [409] * 19
    assert count_rows("reservations", "resource_id", booking["resourceId"]) == 1


def test_same_key_concurrent(client: TestClient, signed: Signer, booking: dict[str, str]) -> None:
    """Given 同一キー同一入力 When 20同時再送 Then 同じIDで予約と作成履歴各1件。 [SLOT-AC07]"""
    key = str(uuid4())
    barrier = Barrier(20)

    def send(index: int) -> Any:
        _ = index
        barrier.wait(timeout=15)
        return create_reservation(client, signed, booking, key)

    with ThreadPoolExecutor(max_workers=20) as pool:
        results = list(pool.map(send, range(20)))
    assert {r.status_code for r in results} == {201}
    assert len({r.json()["reservationId"] for r in results}) == 1
    detail = client.get("/reservations/" + results[0].json()["reservationId"], headers=signed())
    assert len(detail.json()["events"]) == 1


def test_rollback_at_event(
    client: TestClient,
    signed: Signer,
    booking: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Given 履歴保存の障害 When 作成 Then 予約とキーをrollbackし再送は1件だけ成功。 [SLOT-AC12] [RULE-12-AC] [COM-02-AC]"""
    from app.apis.reservations.create_reservation.generated import queries

    key = str(uuid4())
    original = queries.insert_reservation_events

    async def fail(*args: object) -> None:
        _ = args
        raise ApiFunctionError(503, "injected_failure", summary="履歴保存の障害を注入した場合。")

    monkeypatch.setattr(queries, "insert_reservation_events", fail)
    assert create_reservation(client, signed, booking, key).status_code == 503
    assert count_rows("reservations", "resource_id", booking["resourceId"]) == 0
    monkeypatch.setattr(queries, "insert_reservation_events", original)
    result = create_reservation(client, signed, booking, key)
    assert result.status_code == 201
    detail = client.get("/reservations/" + result.json()["reservationId"], headers=signed())
    assert len(detail.json()["events"]) == 1


def test_invalid_token_leaves_database(
    client: TestClient, signed: Signer, booking: dict[str, str]
) -> None:
    """Given 期限切れ・改ざんroleのtoken When 予約作成と資源登録 Then 401/403でDBは変化しない。 [SLOT-AC14]"""
    before = count_rows("reservations", "resource_id", booking["resourceId"])
    expired = {**signed(exp=0), "Idempotency-Key": str(uuid4())}
    assert client.post("/reservations", json=booking, headers=expired).status_code == 401
    wrong_client = {**signed(azp="other"), "Idempotency-Key": str(uuid4())}
    assert client.post("/reservations", json=booking, headers=wrong_client).status_code == 401
    forged = client.post(
        "/resources",
        headers={**signed(), "X-Role": "admin"},
        json={"name": "偽管理者", "description": "", "kind": "room"},
    )
    assert forged.status_code == 403
    assert count_rows("reservations", "resource_id", booking["resourceId"]) == before
    assert count_rows("resources", "name", "偽管理者") == 0


def test_create_status_codes(client: TestClient, signed: Signer, booking: dict[str, str]) -> None:
    """Given 不正入力・対象なし・キーなし When 予約作成 Then 422・404・422を区別し入力値を反射しない。 [COM-03-AC]"""
    invalid = client.post(
        "/reservations",
        json={**booking, "purpose": "x" * 201},
        headers={**signed(), "Idempotency-Key": str(uuid4())},
    )
    assert invalid.status_code == 422
    assert "x" * 201 not in invalid.text
    missing = create_reservation(client, signed, {**booking, "resourceId": str(uuid4())})
    assert missing.status_code == 404
    assert error_reason(missing) == "resource_not_found"
    assert client.post("/reservations", json=booking, headers=signed()).status_code == 422


def test_rule_violation_is_422(client: TestClient, signed: Signer, booking: dict[str, str]) -> None:
    """Given 15分刻みでない時刻 When 予約作成 Then 422で予約を作らない。 [SLOT-AC06] [RULE-02-AC]"""
    response = create_reservation(
        client,
        signed,
        {**booking, "startAt": "2026-09-26T01:05:00Z", "endAt": "2026-09-26T02:05:00Z"},
    )
    assert response.status_code == 422
    assert error_reason(response) == "quarter_hour_required"
    with db_connect() as connection:
        row = connection.execute(
            "SELECT count(*) AS count FROM slotkeeper.reservations WHERE resource_id=%s",
            (booking["resourceId"],),
        ).fetchone()
    assert row is not None and row["count"] == 0
