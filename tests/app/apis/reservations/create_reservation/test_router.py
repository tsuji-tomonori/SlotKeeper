"""予約作成APIを実PostgreSQLの独立transactionで検査する。"""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from typing import Any
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.apis.base import sample_value
from app.apis.exceptions import ApiFunctionError
from app.apis.reservations.create_reservation.samples import (
    CREATE_RESERVATION_REQUEST_SAMPLE,
    CREATE_RESERVATION_RESPONSE_SAMPLE,
    CREATE_RESERVATION_STATUS_SAMPLES,
)
from app.integrations.common_errors import ExternalApiError
from tests.app.apis.router_db import RouterDbHarness
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


def sample_request_for(resource_id: str) -> dict[str, Any]:
    """標本requestの資源IDだけを試験用資源へ置き換える。"""
    return {**sample_value(CREATE_RESERVATION_REQUEST_SAMPLE), "resourceId": resource_id}


@pytest.mark.anyio
async def test_create_reservation_router_returns_sample_shaped_response_with_db(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_count_rows: Callable[..., Any],
    router_seed_resource: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 標本request When 予約作成 Then 標本と同じ形の応答を返し予約・履歴・成功記録・利用者を保存する。 [SLOT-AC01] [RULE-12-AC]"""
    _ = timer
    resource = await router_seed_resource(router_db_harness, router_auth_headers("admin", True))
    key = "router-sample-" + str(uuid4())
    response = await router_db_harness.client.post(
        "/reservations",
        headers={**router_auth_headers("alice"), "Idempotency-Key": key},
        json=sample_request_for(resource["resourceId"]),
    )

    assert response.status_code == 201, response.text
    body = response.json()
    expected = sample_value(CREATE_RESERVATION_RESPONSE_SAMPLE)
    expected["reservationId"] = body["reservationId"]
    expected["resourceId"] = resource["resourceId"]
    assert body == expected
    factory = router_db_harness.session_factory
    where = {"reservation_id": body["reservationId"]}
    assert await router_count_rows(factory, "reservations", where) == 1
    assert await router_count_rows(factory, "reservation_events", where) == 1
    assert await router_count_rows(factory, "idempotency_records", {"idempotency_key": key}) == 1
    assert await router_count_rows(factory, "users", {"principal_id": "alice"}) == 1
    assert (
        await router_count_rows(factory, "resources", {"resource_id": resource["resourceId"]}) == 1
    )


@pytest.mark.anyio
async def test_create_reservation_sample_request_emits_router_error_log_to_stdio(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    assert_router_error_log: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 標本requestと処理中の業務例外 When 予約作成 Then Router例外の運用ログをcatalogどおり出す。 [COM-07-AC]"""
    _ = timer
    await assert_router_error_log(
        router_db_harness=router_db_harness,
        capsys=capsys,
        monkeypatch=monkeypatch,
        method="POST",
        path_template="/reservations",
        status_samples=CREATE_RESERVATION_STATUS_SAMPLES,
        success_status=201,
        patch_target="app.apis.reservations.create_reservation.functions.get_idempotency_record",
        message_id="createReservation.router_api_function_error",
        catalog_id="M004",
        headers=router_auth_headers("alice"),
    )


# unit-test_gen.md executable cases
@pytest.mark.anyio
async def test_tc001_create_reservation_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_seed_resource: Callable[..., Any],
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 成功済みの要求キー When 異なる入力で再送 Then 409で運用ログを出す。 [SLOT-AC09] [RULE-10-AC]"""
    _ = timer
    resource = await router_seed_resource(router_db_harness, router_auth_headers("admin", True))
    headers = {**router_auth_headers("alice"), "Idempotency-Key": "tc001-" + str(uuid4())}
    first = await router_db_harness.client.post(
        "/reservations", headers=headers, json=sample_request_for(resource["resourceId"])
    )
    assert first.status_code == 201, first.text
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.post(
            "/reservations",
            headers=headers,
            json={**sample_request_for(resource["resourceId"]), "purpose": "別の目的"},
        )

    assert response.status_code == 409, response.text
    assert response.json()["error"]["details"][0]["reason"] == "idempotency_input_mismatch"
    actual_log_event = find_log_event("createReservation.idempotency_key_reused")
    assert actual_log_event["messageId"] == "createReservation.idempotency_key_reused"
    assert (
        actual_log_event["summary"]
        == "同じIdempotency-Keyで異なる入力が送られたため、予約作成を拒否した。"
    )


@pytest.mark.anyio
async def test_tc002_create_reservation_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_seed_resource: Callable[..., Any],
    router_count_rows: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 成功済みの要求キー When 同じ入力で再送 Then 201で元の応答を返し予約を増やさない。 [SLOT-AC07] [RULE-10-AC]"""
    _ = timer
    resource = await router_seed_resource(router_db_harness, router_auth_headers("admin", True))
    headers = {**router_auth_headers("alice"), "Idempotency-Key": "tc002-" + str(uuid4())}
    request = sample_request_for(resource["resourceId"])
    first = await router_db_harness.client.post("/reservations", headers=headers, json=request)
    response = await router_db_harness.client.post("/reservations", headers=headers, json=request)

    assert response.status_code == 201, response.text
    assert response.json() == first.json()
    where = {"resource_id": resource["resourceId"]}
    assert await router_count_rows(router_db_harness.session_factory, "reservations", where) == 1


@pytest.mark.anyio
async def test_tc003_create_reservation_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_seed_resource: Callable[..., Any],
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 無効化した資源 When 予約作成 Then 409で運用ログを出す。 [SLOT-AC05]"""
    _ = timer
    resource = await router_seed_resource(
        router_db_harness, router_auth_headers("admin", True), active=False
    )
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.post(
            "/reservations",
            headers={**router_auth_headers("alice"), "Idempotency-Key": "tc003-" + str(uuid4())},
            json=sample_request_for(resource["resourceId"]),
        )

    assert response.status_code == 409, response.text
    assert response.json()["error"]["details"][0]["reason"] == "resource_inactive"
    actual_log_event = find_log_event("createReservation.resource_inactive")
    assert actual_log_event["messageId"] == "createReservation.resource_inactive"
    assert (
        actual_log_event["summary"] == "予約対象の資源が無効化されているため、予約作成を拒否した。"
    )


@pytest.mark.anyio
async def test_tc004_create_reservation_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_seed_resource: Callable[..., Any],
    router_seed_reservation: Callable[..., Any],
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 同じ時間帯の確定予約 When 予約作成 Then 409で運用ログを出す。 [SLOT-AC02]"""
    _ = timer
    resource = await router_seed_resource(router_db_harness, router_auth_headers("admin", True))
    await router_seed_reservation(
        router_db_harness, router_auth_headers("bob"), resource["resourceId"]
    )
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.post(
            "/reservations",
            headers={**router_auth_headers("alice"), "Idempotency-Key": "tc004-" + str(uuid4())},
            json=sample_request_for(resource["resourceId"]),
        )

    assert response.status_code == 409, response.text
    assert response.json()["error"]["details"][0]["reason"] == "slot_taken"
    actual_log_event = find_log_event("createReservation.slot_taken")
    assert actual_log_event["messageId"] == "createReservation.slot_taken"
    assert (
        actual_log_event["summary"]
        == "同じ資源の確定予約と時間帯が重なるため、予約作成を拒否した。"
    )


@pytest.mark.anyio
async def test_tc005_create_reservation_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_seed_resource: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 空き枠 When 予約作成 Then 201で確定予約を返す。 [SLOT-AC01]"""
    _ = timer
    resource = await router_seed_resource(router_db_harness, router_auth_headers("admin", True))
    response = await router_db_harness.client.post(
        "/reservations",
        headers={**router_auth_headers("alice"), "Idempotency-Key": "tc005-" + str(uuid4())},
        json=sample_request_for(resource["resourceId"]),
    )

    assert response.status_code == 201, response.text
    assert response.json()["status"] == "confirmed"


@pytest.mark.anyio
async def test_tc006_create_reservation_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 予約作成の再送照合で業務例外 When API呼出し Then Routerで500へ変換し運用ログを出す。"""
    _ = timer

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise ApiFunctionError(500, "forced router error", summary="unit-test_gen case")

    monkeypatch.setattr(
        "app.apis.reservations.create_reservation.functions.get_idempotency_record",
        raise_expected_error,
    )
    headers = router_auth_headers("alice")
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.post(
            "/reservations",
            headers={**headers, "Idempotency-Key": "router-error-" + str(uuid4())},
            json=sample_value(CREATE_RESERVATION_REQUEST_SAMPLE),
        )

    assert response.status_code == 500, response.text
    assert response.json()["error"]["details"][0]["reason"] == "forced router error"
    actual_log_event = find_log_event("createReservation.router_api_function_error")
    assert actual_log_event["messageId"] == "createReservation.router_api_function_error"
    assert (
        actual_log_event["summary"] == "Routerで捕捉したApiFunctionErrorにより予約作成が失敗した。"
    )


@pytest.mark.anyio
async def test_tc007_create_reservation_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 予約作成の再送照合で外部API例外 When API呼出し Then Routerで502へ変換し運用ログを出す。"""
    _ = timer

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise ExternalApiError("forced external api error")

    monkeypatch.setattr(
        "app.apis.reservations.create_reservation.functions.get_idempotency_record",
        raise_expected_error,
    )
    headers = router_auth_headers("alice")
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.post(
            "/reservations",
            headers={**headers, "Idempotency-Key": "router-error-" + str(uuid4())},
            json=sample_value(CREATE_RESERVATION_REQUEST_SAMPLE),
        )

    assert response.status_code == 502, response.text
    assert response.json()["error"]["details"][0]["reason"] == "external service request failed"
    actual_log_event = find_log_event("createReservation.router_external_api_error")
    assert actual_log_event["messageId"] == "createReservation.router_external_api_error"
    assert (
        actual_log_event["summary"] == "Routerで捕捉したExternalApiErrorにより予約作成が失敗した。"
    )


@pytest.mark.anyio
async def test_tc008_create_reservation_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 予約作成の再送照合でHTTP例外 When API呼出し Then Routerで400へ変換し運用ログを出す。"""
    _ = timer

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise HTTPException(status_code=400, detail="forced http exception")

    monkeypatch.setattr(
        "app.apis.reservations.create_reservation.functions.get_idempotency_record",
        raise_expected_error,
    )
    headers = router_auth_headers("alice")
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.post(
            "/reservations",
            headers={**headers, "Idempotency-Key": "router-error-" + str(uuid4())},
            json=sample_value(CREATE_RESERVATION_REQUEST_SAMPLE),
        )

    assert response.status_code == 400, response.text
    assert response.json()["error"]["details"][0]["reason"] == "forced http exception"
    actual_log_event = find_log_event("createReservation.router_http_exception")
    assert actual_log_event["messageId"] == "createReservation.router_http_exception"
    assert actual_log_event["summary"] == "Routerで捕捉したHTTPExceptionにより予約作成が失敗した。"
