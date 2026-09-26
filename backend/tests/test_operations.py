"""HTTP境界の運用ログ、状態コード、公開契約の制約を検査する。"""

import json
import logging
from uuid import uuid4

import pytest
from slotkeeper.app import app

pytestmark = pytest.mark.db


def test_request_log_redacts(client, signed, booking, caplog):
    """Given 目的とtokenを含む作成要求 When API呼出し Then 要求ID・operation・status・所要時間だけを記録する。 [COM-07-AC]"""
    secret = "秘密の会議目的-" + str(uuid4())
    headers = {**signed(), "Idempotency-Key": str(uuid4())}
    with caplog.at_level(logging.INFO, logger="slotkeeper"):
        response = client.post("/reservations", json={**booking, "purpose": secret}, headers=headers)
    assert response.status_code == 201
    records = [json.loads(r.getMessage()) for r in caplog.records if r.name == "slotkeeper"]
    assert records[-1].keys() == {"request_id", "operation", "status", "elapsed_ms"}
    assert records[-1]["operation"] == "reservations_create"
    assert records[-1]["request_id"] == response.headers["X-Request-ID"]
    text = caplog.text
    assert secret not in text
    assert headers["Authorization"].split()[1] not in text
    assert response.headers["Cache-Control"] == "no-store"


def test_http_status_codes(client, signed, booking):
    """Given 不正入力・未認証・対象なし・業務競合 When API呼出し Then 422・401・404・409を区別し入力値を反射しない。 [COM-03-AC]"""
    key = {"Idempotency-Key": str(uuid4())}
    invalid = client.post(
        "/reservations", json={**booking, "purpose": "x" * 201}, headers={**signed(), **key}
    )
    assert invalid.status_code == 422
    assert "x" * 201 not in invalid.text
    assert client.get("/reservations").status_code == 401
    assert client.get("/reservations/" + str(uuid4()), headers=signed()).status_code == 404
    missing = {**booking, "resource_id": str(uuid4())}
    assert (
        client.post(
            "/reservations", json=missing, headers={**signed(), "Idempotency-Key": str(uuid4())}
        ).status_code
        == 404
    )
    assert client.post("/reservations", json=booking, headers=signed()).status_code == 422


def test_public_contract_has_no_clock_or_direct_edit():
    """Given 公開OpenAPI When 入力と操作を列挙 Then 現在時刻の上書き入力と予約日時の直接編集がない。 [RULE-04-AC] [RULE-05-AC]"""
    spec = app.openapi()
    names = {
        p["name"].lower()
        for path in spec["paths"].values()
        for op in path.values()
        for p in op.get("parameters", [])
    }
    assert not names & {"now", "clock", "current_time", "x-now"}
    reservation_paths = [p for p in spec["paths"] if p.startswith("/reservations/")]
    for path in reservation_paths:
        assert not {"put", "patch", "delete"} & set(spec["paths"][path])
    bodies = json.dumps(spec["components"]["schemas"]["CancelInput"])
    assert "start_at" not in bodies and "status" not in bodies


def test_missing_targets_return_404(client, signed, database):
    """Given 存在しない予約・資源 When 取消・編集・予約表取得 Then 404で区別する。 [COM-03-AC]"""
    missing = str(uuid4())
    admin = signed("admin", True)
    assert (
        client.post(
            "/reservations/" + missing + "/cancel", headers=signed(), json={"version": 1}
        ).status_code
        == 404
    )
    edit = {"name": "なし", "description": "", "kind": "room", "active": True, "version": 1}
    assert client.put("/resources/" + missing, headers=admin, json=edit).status_code == 404
    assert (
        client.get(
            "/resources/" + missing + "/schedule?day=2026-09-26", headers=signed()
        ).status_code
        == 404
    )


def test_system_clock_providers():
    """Given 本番の依存 When Clockを取得 Then UTC基準のaware時刻を返し公開入力で置換できない。 [RULE-04-AC]"""
    import importlib

    for name in [
        "resources_update",
        "reservations_create",
        "reservations_cancel",
        "reservations_list",
    ]:
        module = importlib.import_module("slotkeeper.operations." + name + ".endpoint")
        now = module.clock().now()
        assert now.tzinfo is not None and now.utcoffset().total_seconds() == 0


class FakeConnection:
    def __init__(self, outcome):
        self.outcome = outcome

    def __enter__(self):
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self

    def __exit__(self, *args):
        return False


@pytest.fixture
def fake_connect(monkeypatch):
    """実transactionの再試行制御だけを検査するため接続を差し替える。"""
    from slotkeeper import db

    monkeypatch.setattr(db, "sleep", lambda _: None)
    attempts = []

    def install(outcomes):
        attempts.clear()

        def connect():
            outcome = outcomes[min(len(attempts), len(outcomes) - 1)]
            attempts.append(outcome)
            return FakeConnection(outcome)

        monkeypatch.setattr(db, "connect", connect)
        return attempts

    return install


def test_transaction_retries_conflicts(fake_connect):
    """Given commit時の直列化競合と一意性競合 When transaction Then 新snapshotで再実行して成功する。 [SLOT-AC03] [SLOT-AC07]"""
    import psycopg
    from slotkeeper.db import transaction

    attempts = fake_connect(
        [psycopg.errors.SerializationFailure(), psycopg.errors.UniqueViolation(), "ok"]
    )
    assert transaction(lambda connection: "committed") == "committed"
    assert len(attempts) == 3


def test_transaction_limits(fake_connect):
    """Given 解消しない競合と成否不明の切断 When transaction Then 上限後503、再送安全でない処理は再試行しない。 [SLOT-AC12]"""
    import psycopg
    from slotkeeper.db import transaction
    from slotkeeper.domain import DomainError

    attempts = fake_connect([psycopg.errors.SerializationFailure()])
    with pytest.raises(DomainError) as conflict:
        transaction(lambda connection: None)
    assert conflict.value.status == 503 and len(attempts) == 12
    attempts = fake_connect([psycopg.OperationalError()])
    with pytest.raises(DomainError):
        transaction(lambda connection: None)
    assert len(attempts) == 1
    attempts = fake_connect([psycopg.OperationalError(), "ok"])
    assert transaction(lambda connection: "again", replay_safe=True) == "again"
    assert len(attempts) == 2


def test_business_errors_are_not_retried(fake_connect):
    """Given 業務上の重複 When transaction Then 再試行せずそのまま409を返す。 [SLOT-AC02]"""
    from slotkeeper.db import transaction
    from slotkeeper.domain import DomainError

    attempts = fake_connect(["ok"])

    def work(connection):
        raise DomainError("slot_taken")

    with pytest.raises(DomainError) as error:
        transaction(work)
    assert error.value.status == 409 and len(attempts) == 1


def test_dsql_connection_uses_official_connector(monkeypatch):
    """Given DSQL設定 When 接続 Then 公式connectorへIAM用の接続先・利用者とTLS検証を渡しRepeatable Readにする。 [TECH-DB-AC]"""
    import sys
    from types import SimpleNamespace

    import psycopg
    from slotkeeper import db

    calls = {}
    connection = SimpleNamespace(isolation_level=None)

    def connect(**kwargs):
        calls.update(kwargs)
        return connection

    monkeypatch.setitem(sys.modules, "aurora_dsql_psycopg", SimpleNamespace(connect=connect))
    monkeypatch.setattr(
        db,
        "settings",
        lambda: SimpleNamespace(
            database_mode="dsql",
            dsql_host="cluster.dsql.ap-northeast-1.on.aws",
            region="ap-northeast-1",
            database_user="slotkeeper_app",
        ),
    )
    assert db.connect() is connection
    assert calls["user"] == "slotkeeper_app" and calls["sslmode"] == "verify-full"
    assert "password" not in calls
    assert connection.isolation_level == psycopg.IsolationLevel.REPEATABLE_READ


def test_jwks_client_is_bounded():
    """Given 設定済みJWKS URL When 鍵取得clientを作る Then 短いtimeoutとcache寿命を持つ。 [SLOT-AC14]"""
    from slotkeeper import auth

    client = auth.jwks()
    assert client.jwk_set_cache is not None
    assert client.timeout == 5
