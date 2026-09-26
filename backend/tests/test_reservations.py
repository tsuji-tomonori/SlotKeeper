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
    """Given 空き枠 When 作成・重複・隣接 Then 201・409・201。 [SLOT-AC01] [SLOT-AC02] [RULE-01-AC]"""
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
    """Given Aの予約 When B・Aが詳細取得と取消 Then Bは403で情報非公開、Aは取消。 [SLOT-AC04] [SLOT-AC08] [SLOT-02-AC] [RULE-09-AC] [RULE-13-AC] [RULE-06-AC] [COM-04-AC]"""
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
    """Given 成功後の取消と時刻進行 When 同一キー再送 Then 元の作成応答で履歴は増えない。 [SLOT-AC07] [SLOT-AC09] [SLOT-AC15] [RULE-10-AC]"""
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
    timer.value += timedelta(hours=1)
    assert create(client, signed, booking, key).status_code == 201


def test_replay_after_start(client, signed, booking, timer):
    """Given 作成から24時間以内に予約開始 When 再送 Then 時刻違反にせず元応答。 [SLOT-AC15] [RULE-11-AC]"""
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
    """Given 将来の確定予約 When 無効化 Then 409。 [SLOT-AC05] [RULE-08-AC]"""
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
    """Given 確定予約 When 古い版と開始時刻ちょうどの取消 Then 409、履歴1件。 [SLOT-AC11] [SLOT-AC13] [RULE-13-AC]"""
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
    """Given 有効資源 When 予約作成と無効化を競合 Then 両方成功しない。 [SLOT-AC10] [RULE-08-AC]"""
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
    """Given 履歴保存の障害 When 作成 Then 予約とキーをrollbackし再送は1件だけ成功。 [SLOT-AC12] [RULE-12-AC] [COM-02-AC]"""
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


def test_disable_after_start_keeps_record(client, signed, booking, resource, timer):
    """Given 開始済みの確定予約 When 資源を無効化 Then 無効化でき既存記録を保持し新規予約は拒否する。 [RULE-07-AC]"""
    row = create(client, signed, booking).json()
    timer.value = timer.value.replace(day=26, hour=1, minute=30)
    payload = {k: resource[k] for k in ["name", "description", "kind", "active", "version"]}
    payload["active"] = False
    response = client.put(
        "/resources/" + resource["id"], headers=signed("admin", True), json=payload
    )
    assert response.status_code == 200, response.text
    kept = client.get("/reservations/" + row["id"], headers=signed()).json()["reservation"]
    assert kept["status"] == "confirmed"
    later = {**booking, "start_at": "2026-09-26T05:00:00Z", "end_at": "2026-09-26T06:00:00Z"}
    assert create(client, signed, later).status_code == 409
    future = client.get("/reservations?future=true&limit=100", headers=signed()).json()
    assert all(r["resource_id"] != resource["id"] for r in future)


def test_repeatable_read(database):
    """Given ローカル接続 When 分離レベル取得 Then repeatable read。 [COM-02-AC] [TECH-DB-AC]"""
    with connect() as connection:
        assert (
            connection.execute("SHOW transaction_isolation").fetchone()["transaction_isolation"]
            == "repeatable read"
        )


def count_rows(table, column, value):
    with connect() as connection:
        row = connection.execute(
            "SELECT count(*) AS count FROM slotkeeper." + table + " WHERE " + column + "=%s",
            (value,),
        ).fetchone()
        return row["count"]


def test_list_filters_only_own(client, signed, booking):
    """Given 自分と他人の2日分の予約と取消 When 日付・状態で絞込み Then 自分の対象だけ固定順で返す。 [SLOT-AC08] [RULE-07-AC]"""
    later = {**booking, "start_at": "2026-09-27T01:00:00Z", "end_at": "2026-09-27T02:00:00Z"}
    first = create(client, signed, booking).json()
    second = create(client, signed, later).json()
    other = create(
        client,
        signed,
        {**booking, "start_at": "2026-09-26T03:00:00Z", "end_at": "2026-09-26T04:00:00Z"},
        subject="bob",
    ).json()
    client.post(
        "/reservations/" + second["id"] + "/cancel", headers=signed(), json={"version": 1}
    )

    def ids(query):
        rows = client.get("/reservations?limit=100&" + query, headers=signed()).json()
        return [r["id"] for r in rows if r["resource_id"] == booking["resource_id"]]

    assert first["id"] in ids("day=2026-09-26&future=false")
    assert other["id"] not in ids("day=2026-09-26&future=false")
    assert second["id"] not in ids("day=2026-09-26&future=false")
    assert ids("day=2026-09-27&state=cancelled&future=false") == [second["id"]]
    assert second["id"] not in ids("future=true")
    assert client.get("/reservations/" + other["id"], headers=signed()).status_code == 403
    assert client.get("/reservations?limit=0", headers=signed()).status_code == 422


def test_admin_cancels_other_before_start(client, signed, booking, timer):
    """Given Aの開始前予約 When 管理者が取消 Then 取消と履歴2件、開始後は管理者も拒否。 [SLOT-AC04] [SLOT-07-AC] [RULE-09-AC]"""
    row = create(client, signed, booking).json()
    admin = signed("admin", True)
    detail = client.get("/reservations/" + row["id"], headers=admin)
    assert detail.status_code == 200
    assert detail.json()["reservation"]["purpose"] == booking["purpose"]
    timer.value += timedelta(minutes=5)
    response = client.post(
        "/reservations/" + row["id"] + "/cancel", headers=admin, json={"version": 1}
    )
    assert response.status_code == 200
    events = client.get("/reservations/" + row["id"], headers=signed()).json()["events"]
    assert [e["action"] for e in events] == ["created", "cancelled"]
    started = create(
        client,
        signed,
        {**booking, "start_at": "2026-09-26T05:00:00Z", "end_at": "2026-09-26T06:00:00Z"},
    ).json()
    timer.value = timer.value.replace(day=26, hour=5)
    assert (
        client.post(
            "/reservations/" + started["id"] + "/cancel", headers=admin, json={"version": 1}
        ).status_code
        == 409
    )


def test_cancel_and_rebook_concurrent(client, signed, booking):
    """Given 確定予約 When 取消と同じ枠の再予約を同時実行 Then 重なる確定予約は最大1件。 [RULE-06-AC]"""
    row = create(client, signed, booking).json()
    barrier = Barrier(2)

    def cancel():
        barrier.wait(timeout=15)
        return client.post(
            "/reservations/" + row["id"] + "/cancel", headers=signed(), json={"version": 1}
        )

    def rebook():
        barrier.wait(timeout=15)
        return create(client, signed, booking, subject="bob")

    with ThreadPoolExecutor(max_workers=2) as pool:
        a = pool.submit(cancel)
        b = pool.submit(rebook)
        cancelled, rebooked = a.result(), b.result()
    assert cancelled.status_code == 200
    assert rebooked.status_code in (201, 409)
    with connect() as connection:
        confirmed = connection.execute(
            "SELECT count(*) AS count FROM slotkeeper.reservations"
            " WHERE resource_id=%s AND status='confirmed'",
            (booking["resource_id"],),
        ).fetchone()["count"]
    assert confirmed == (1 if rebooked.status_code == 201 else 0)
    # 取消の確定後は同じ枠を再予約できる。
    if rebooked.status_code == 409:
        assert create(client, signed, booking, subject="bob").status_code == 201


def test_invalid_token_leaves_database(client, signed, booking):
    """Given 期限切れ・改ざんroleのtoken When 予約作成と資源登録 Then 401/403でDBは変化しない。 [SLOT-AC14]"""
    before = count_rows("reservations", "resource_id", booking["resource_id"])
    expired = {**signed(exp=0), "Idempotency-Key": str(uuid4())}
    assert client.post("/reservations", json=booking, headers=expired).status_code == 401
    wrong_client = {**signed(azp="other"), "Idempotency-Key": str(uuid4())}
    assert client.post("/reservations", json=booking, headers=wrong_client).status_code == 401
    assert (
        client.post(
            "/resources",
            headers={**signed(), "X-Role": "admin"},
            json={"name": "偽管理者", "description": "", "kind": "room"},
        ).status_code
        == 403
    )
    assert count_rows("reservations", "resource_id", booking["resource_id"]) == before
    assert count_rows("resources", "name", "偽管理者") == 0


def test_migrate_and_seed_repeat(database):
    """Given 既存データ When migrationとseedを繰り返す Then 重複せず既存データを保持する。 [COM-05-AC] [COM-02-AC] [SLOT-AC16]"""
    from tools.project.migrate import migrate, seed

    marker = str(uuid4())
    with connect() as connection:
        connection.execute(
            "INSERT INTO slotkeeper.resources(id,name,description,kind,active,version,control_version)"
            " VALUES (%s,%s,'',%s,true,1,0)",
            (marker, "保持確認 " + marker, "room"),
        )
    for _ in range(2):
        migrate()
        seed()
    assert count_rows("resources", "id", marker) == 1
    with connect() as connection:
        seeded = connection.execute(
            "SELECT count(*) AS count FROM slotkeeper.resources WHERE id LIKE '00000000-%'"
        ).fetchone()["count"]
    assert seeded == 3


def test_resource_paging_order(client, signed, database):
    """Given 同名の資源 When ページ単位で取得 Then 名前とIDの固定順で欠落・重複がない。 [SLOT-01-AC] [RULE-14-AC]"""
    admin = signed("admin", True)
    name = "順序確認 " + str(uuid4())
    created = sorted(
        client.post(
            "/resources", headers=admin, json={"name": name, "description": "", "kind": "room"}
        ).json()["id"]
        for _ in range(3)
    )
    seen = []
    offset = 0
    while True:
        page = client.get(
            "/resources?limit=2&offset=" + str(offset), headers=signed("bob")
        ).json()
        if not page:
            break
        seen += [r["id"] for r in page if r["name"] == name]
        offset += 2
    assert seen == created
