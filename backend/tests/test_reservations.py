"""実PostgreSQLの独立transactionで主要受入条件を検査する。"""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from uuid import uuid4

import pytest
from slotkeeper.db import connect

pytestmark = pytest.mark.db


def create(client, signed, booking, key=None, subject="alice"):
    return client.post(
        "/reservations",
        json=booking,
        headers={**signed(subject), "Idempotency-Key": key or str(uuid4())},
    )


def test_create_adjacent_overlap(client, signed, booking):
    """Given 空き枠 When 作成・重複・隣接 Then 201・409・201。 [SLOT-AC01] [SLOT-AC02]"""
    first = create(client, signed, booking)
    assert first.status_code == 201, first.text
    assert (
        create(
            client,
            signed,
            {**booking, "start_at": "2026-09-26T01:30:00Z", "end_at": "2026-09-26T02:30:00Z"},
        ).status_code
        == 409
    )
    assert (
        create(
            client,
            signed,
            {**booking, "start_at": "2026-09-26T02:00:00Z", "end_at": "2026-09-26T03:00:00Z"},
        ).status_code
        == 201
    )
    mine = client.get("/reservations?day=2026-09-26", headers=signed()).json()
    assert first.json()["id"] in [r["id"] for r in mine]


def test_privacy_and_cancel(client, signed, booking, resource):
    """Given Aの予約 When B・Aが詳細取得と取消 Then Bは403で情報非公開、Aは取消。 [SLOT-AC04] [SLOT-AC08]"""
    reservation = create(client, signed, booking).json()
    id = reservation["id"]
    assert client.get("/reservations/" + id, headers=signed("bob")).status_code == 403
    assert (
        client.post(
            "/reservations/" + id + "/cancel", headers=signed("bob"), json={"version": 1}
        ).status_code
        == 403
    )
    schedule = client.get(
        "/resources/" + resource["id"] + "/schedule?day=2026-09-26", headers=signed("bob")
    ).json()
    assert all(set(row) == {"start_at", "end_at", "label"} for row in schedule)
    response = client.post("/reservations/" + id + "/cancel", headers=signed(), json={"version": 1})
    assert response.json()["status"] == "cancelled"
    assert len(client.get("/reservations/" + id, headers=signed()).json()["events"]) == 2
    assert (
        client.post(
            "/reservations/" + id + "/cancel", headers=signed(), json={"version": 2}
        ).status_code
        == 409
    )
    assert create(client, signed, booking).status_code == 201


def test_replay_before_validation(client, signed, booking, timer):
    """Given 成功後の取消と時刻進行 When 同一キー再送 Then 元の作成応答で履歴は増えない。 [SLOT-AC07] [SLOT-AC09] [SLOT-AC15]"""
    key = str(uuid4())
    first = create(client, signed, booking, key)
    assert first.status_code == 201
    assert create(client, signed, {**booking, "purpose": "別の目的"}, key).status_code == 409
    client.post(
        "/reservations/" + first.json()["id"] + "/cancel", headers=signed(), json={"version": 1}
    )
    timer.value += timedelta(hours=23)
    replay = create(client, signed, booking, key)
    assert replay.json() == first.json()
    timer.value += timedelta(hours=2)
    assert create(client, signed, booking, key).status_code == 201


def test_replay_after_start(client, signed, booking, timer):
    """Given 作成から24時間以内に予約開始 When 再送 Then 時刻違反にせず元応答。 [SLOT-AC15]"""
    timer.value += timedelta(hours=4)
    key = str(uuid4())
    first = create(client, signed, booking, key)
    timer.value += timedelta(hours=22)
    assert create(client, signed, booking, key).json() == first.json()


def test_versions_and_inactive(client, signed, booking, resource):
    """Given 古い資源版と無効資源 When 更新と作成 Then 409で先行更新維持。 [SLOT-AC05] [SLOT-AC11]"""
    url = "/resources/" + resource["id"]
    payload = {k: resource[k] for k in ["name", "description", "kind", "active", "version"]}
    assert (
        client.put(
            url, headers=signed("admin", True), json={**payload, "active": False}
        ).status_code
        == 200
    )
    assert client.put(url, headers=signed("admin", True), json=payload).status_code == 409
    assert create(client, signed, booking).status_code == 409


def test_future_prevents_disable(client, signed, booking, resource):
    """Given 将来の確定予約 When 無効化 Then 409。 [SLOT-AC05]"""
    assert create(client, signed, booking).status_code == 201
    payload = {k: resource[k] for k in ["name", "description", "kind", "active", "version"]}
    payload["active"] = False
    assert (
        client.put(
            "/resources/" + resource["id"], headers=signed("admin", True), json=payload
        ).status_code
        == 409
    )


def test_cancel_boundaries(client, signed, booking, timer):
    """Given 確定予約 When 古い版と開始時刻ちょうどの取消 Then 409、履歴1件。 [SLOT-AC11] [SLOT-AC13]"""
    row = create(client, signed, booking).json()
    url = "/reservations/" + row["id"]
    assert client.post(url + "/cancel", headers=signed(), json={"version": 2}).status_code == 409
    timer.value += timedelta(days=1, hours=1)
    assert client.post(url + "/cancel", headers=signed(), json={"version": 1}).status_code == 409
    assert len(client.get(url, headers=signed()).json()["events"]) == 1


def test_twenty_concurrent(client, signed, booking):
    """Given 空き枠と20利用者 When 同時送信 Then 1成功19競合で重複なし。 [SLOT-AC03]"""
    barrier = Barrier(20)

    def send(i):
        barrier.wait(timeout=15)
        return create(client, signed, booking, subject="parallel-" + str(i))

    with ThreadPoolExecutor(max_workers=20) as pool:
        results = list(pool.map(send, range(20)))
    assert sorted(r.status_code for r in results) == [201] + [409] * 19
    with connect() as connection:
        row = connection.execute(
            "SELECT count(*) AS count FROM slotkeeper.reservations WHERE resource_id=%s",
            (booking["resource_id"],),
        ).fetchone()
        assert row["count"] == 1


def test_same_key_concurrent(client, signed, booking):
    """Given 同一キー同一入力 When 20同時再送 Then 同じIDで予約と作成履歴各1件。 [SLOT-AC07]"""
    key = str(uuid4())
    barrier = Barrier(20)

    def send(i):
        barrier.wait(timeout=15)
        return create(client, signed, booking, key)

    with ThreadPoolExecutor(max_workers=20) as pool:
        results = list(pool.map(send, range(20)))
    assert {r.status_code for r in results} == {201}
    assert len({r.json()["id"] for r in results}) == 1
    assert (
        len(
            client.get("/reservations/" + results[0].json()["id"], headers=signed()).json()[
                "events"
            ]
        )
        == 1
    )


def test_create_vs_disable(client, signed, booking, resource):
    """Given 有効資源 When 予約作成と無効化を競合 Then 両方成功しない。 [SLOT-AC10]"""
    barrier = Barrier(2)

    def reserve():
        barrier.wait()
        return create(client, signed, booking)

    def disable():
        barrier.wait()
        payload = {k: resource[k] for k in ["name", "description", "kind", "active", "version"]}
        payload["active"] = False
        return client.put(
            "/resources/" + resource["id"], headers=signed("admin", True), json=payload
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        a = pool.submit(reserve)
        b = pool.submit(disable)
        results = [a.result().status_code, b.result().status_code]
    assert results in ([201, 409], [409, 200])


def test_rollback_at_event(client, signed, booking, monkeypatch):
    """Given 履歴保存の障害 When 作成 Then 予約とキーをrollbackし再送は1件だけ成功。 [SLOT-AC12]"""
    from slotkeeper.domain import DomainError
    from slotkeeper.operations.reservations_create import queries

    key = str(uuid4())
    original = queries.event

    def fail(*args):
        raise DomainError("injected_failure", 503)

    monkeypatch.setattr(queries, "event", fail)
    assert create(client, signed, booking, key).status_code == 503
    monkeypatch.setattr(queries, "event", original)
    result = create(client, signed, booking, key)
    assert result.status_code == 201
    assert (
        len(client.get("/reservations/" + result.json()["id"], headers=signed()).json()["events"])
        == 1
    )


def test_repeatable_read(database):
    """Given ローカル接続 When 分離レベル取得 Then repeatable read。 [COM-02]"""
    with connect() as connection:
        assert (
            connection.execute("SHOW transaction_isolation").fetchone()["transaction_isolation"]
            == "repeatable read"
        )
