"""予約作成の業務関数を単体で検査する。"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from app.apis.exceptions import ApiFunctionError
from app.apis.reservations.common import ReservationStatus
from app.apis.reservations.create_reservation import functions
from app.apis.reservations.create_reservation.generated import queries
from app.apis.reservations.create_reservation.schemas import CreateReservationRequest
from app.apis.sequence_types import IdempotencyRecordRef
from tests.app.apis.function_helpers import ALICE, QueryRecorder, fake_session, response_error
from tests.conftest import FixedClock

pytestmark = pytest.mark.anyio

NOW = datetime(2026, 9, 25, tzinfo=UTC)


def request(start: datetime | str, end: datetime | str) -> CreateReservationRequest:
    return CreateReservationRequest.model_validate(
        {"resourceId": "resource", "purpose": " 会議 ", "startAt": start, "endAt": end}
    )


def clock() -> FixedClock:
    fixed = FixedClock()
    fixed.value = NOW
    return fixed


@pytest.mark.parametrize(
    ("start", "end", "reason"),
    [
        (NOW, NOW + timedelta(minutes=15), "start_out_of_range"),
        (NOW - timedelta(hours=1), NOW, "start_out_of_range"),
        (NOW + timedelta(days=31), NOW + timedelta(days=31, hours=1), "start_out_of_range"),
        (NOW + timedelta(hours=1), NOW + timedelta(hours=1), "duration_out_of_range"),
        (NOW + timedelta(hours=1), NOW + timedelta(hours=5, minutes=15), "duration_out_of_range"),
        (NOW + timedelta(minutes=1), NOW + timedelta(minutes=16), "quarter_hour_required"),
        (NOW + timedelta(hours=14), NOW + timedelta(hours=15), "same_japan_day_required"),
        (
            NOW + timedelta(hours=1, seconds=1),
            NOW + timedelta(hours=2, seconds=1),
            "quarter_hour_required",
        ),
    ],
)
async def test_reject_invalid_time(start: datetime, end: datetime, reason: str) -> None:
    """Given 範囲外または刻み不正 When 時刻検証 Then 入力不正。 [SLOT-AC06] [RULE-02-AC] [RULE-03-AC]"""
    with pytest.raises(ApiFunctionError) as error:
        await functions.validate_booking_request(request(start, end), clock())
    assert error.value.status_code == 422
    assert error.value.detail == reason


@pytest.mark.parametrize(("days", "minutes"), [(1, 15), (1, 240), (30, 15)])
async def test_boundaries(days: int, minutes: int) -> None:
    """Given 15分・4時間・30日境界 When 時刻検証 Then 受け付ける。 [SLOT-AC06] [RULE-02-AC] [RULE-03-AC]"""
    start = NOW + timedelta(days=days)
    validated = await functions.validate_booking_request(
        request(start, start + timedelta(minutes=minutes)), clock()
    )
    assert validated.start_at == start


async def test_normalized_input() -> None:
    """Given 同じ瞬間のoffset差と前後空白 When 正規化 Then 同一要求。 [SLOT-AC09]"""
    first = request("2026-09-26T10:00:00+09:00", "2026-09-26T11:00:00+09:00")
    second = request("2026-09-26T01:00:00Z", "2026-09-26T02:00:00Z")
    record = IdempotencyRecordRef(
        idempotency_key="key",
        request_hash=functions._request_hash(first),  # pyright: ignore[reportPrivateUsage]
        response_payload="{}",
    )
    assert await functions.is_same_idempotent_request(record, second)
    assert first.purpose == "会議"


async def test_expired_record_is_not_replayed() -> None:
    """Given 期限切れの成功記録 When 再送判定 Then 元応答を返さず新規要求として扱う。 [SLOT-AC15] [RULE-10-AC]"""
    expired = IdempotencyRecordRef(idempotency_key="key", response_payload="{}", is_expired=True)
    assert not await functions.has_idempotency_result(expired)
    assert await functions.delete_expired_idempotency_record(
        IdempotencyRecordRef(idempotency_key="key"),
        caller=None,  # type: ignore[arg-type]
    ) == IdempotencyRecordRef(idempotency_key="key")


def test_request_rejects_unknown_fields() -> None:
    """Given 公開契約にない項目 When 予約作成の入力解析 Then 拒否する。 [COM-03-AC] [RULE-04-AC]"""
    with pytest.raises(ValidationError):
        CreateReservationRequest.model_validate(
            {
                "resourceId": "resource",
                "purpose": "会議",
                "startAt": "2026-09-26T01:00:00Z",
                "endAt": "2026-09-26T02:00:00Z",
                "now": "2026-09-01T00:00:00Z",
            }
        )


def reservation_row(**overrides: object) -> queries.InsertReservationsRow:
    values: dict[str, object] = {
        "reservation_id": "reservation-1",
        "resource_id": "resource",
        "owner_principal_id": "alice",
        "start_at": NOW + timedelta(days=1),
        "end_at": NOW + timedelta(days=1, hours=1),
        "purpose": "会議",
        "status": ReservationStatus.CONFIRMED,
        "row_version": 1,
    }
    values.update(overrides)
    return queries.InsertReservationsRow.model_validate(values)


def valid_request() -> CreateReservationRequest:
    start = NOW + timedelta(days=1)
    return request(start, start + timedelta(hours=1))


async def test_get_idempotency_record_marks_expiry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Given 期限切れと未登録の要求キー When 成功記録を取得 Then 期限切れを区別し未登録は空の参照を返す。 [SLOT-AC15]"""
    recorder = QueryRecorder()
    row = queries.SelectIdempotencyRecordsRow(
        idempotency_key="key", request_hash="h", response_payload="{}", expires_at=NOW
    )
    recorder.install(monkeypatch, queries, "select_idempotency_records", [row])
    record = await functions.get_idempotency_record("key", ALICE, clock(), fake_session())
    assert record.is_expired and record.response_payload == "{}"
    assert recorder.params("select_idempotency_records").principal_id == "alice"
    recorder.install(monkeypatch, queries, "select_idempotency_records", [])
    empty = await functions.get_idempotency_record("key", ALICE, clock(), fake_session())
    assert empty == IdempotencyRecordRef(idempotency_key="key")


async def test_update_resource_control_version_locks_or_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Given 存在する資源と存在しない資源 When 内部制御版を進める Then 資源参照か404を返す。 [SLOT-AC10]"""
    recorder = QueryRecorder()
    row = queries.UpdateResourcesControlVersionRow(
        resource_id="resource", active=False, row_version=2
    )
    recorder.install(monkeypatch, queries, "update_resources_control_version", row)
    resource = await functions.update_resource_control_version("resource", fake_session())
    assert not await functions.is_active_resource(resource)
    recorder.install(monkeypatch, queries, "update_resources_control_version", None)
    with pytest.raises(ApiFunctionError) as error:
        await functions.update_resource_control_version("missing", fake_session())
    assert error.value.status_code == 404 and error.value.detail == "resource_not_found"


async def test_has_overlapping_reservation_uses_half_open_interval(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Given 重なる確定予約の件数 When 重複を判定 Then 開始と終了を半開区間の条件として渡す。 [RULE-01-AC]"""
    recorder = QueryRecorder()
    count = queries.SelectReservationsRow(overlapping_reservation_count=1)
    recorder.install(monkeypatch, queries, "select_reservations", [count])
    assert await functions.has_overlapping_reservation(valid_request(), fake_session())
    params = recorder.params("select_reservations")
    assert params.start_at == valid_request().start_at and params.end_at == valid_request().end_at


async def test_save_reservation_owner_event_and_record(monkeypatch: pytest.MonkeyPatch) -> None:
    """Given 検証済み要求 When 利用者・予約・履歴・成功記録を保存 Then 同じ予約と要求hashで記録する。 [RULE-12-AC]"""
    recorder = QueryRecorder()
    for name in ("insert_users", "insert_reservation_events", "insert_idempotency_records"):
        recorder.install(monkeypatch, queries, name, None)
    recorder.install(monkeypatch, queries, "insert_reservations", reservation_row())
    session = fake_session()
    assert await functions.save_reservation_owner(ALICE, clock(), session) == ALICE
    reservation = await functions.save_reservation(valid_request(), ALICE, session)
    event = await functions.append_reservation_created_event(reservation, ALICE, clock(), session)
    record = await functions.create_idempotency_record(
        "key", valid_request(), reservation, clock(), session
    )
    assert recorder.params("insert_reservation_events").event_id == event.event_id
    assert record.expires_at == NOW + timedelta(hours=24)
    replayed = await functions.build_replayed_reservation_response(record)
    assert replayed == await functions.build_reservation_response(reservation)
    recorder.install(monkeypatch, queries, "insert_reservations", None)
    with pytest.raises(ApiFunctionError):
        await functions.save_reservation(valid_request(), ALICE, session)


async def test_rejection_builders_return_conflicts() -> None:
    """Given 再送誤用・無効資源・重複 When 拒否応答を組み立てる Then それぞれ409と理由コードを返す。 [SLOT-AC02] [SLOT-AC05] [SLOT-AC09]"""
    cases = {
        functions.build_idempotency_key_reused_response: "idempotency_input_mismatch",
        functions.build_resource_inactive_response: "resource_inactive",
        functions.build_slot_taken_response: "slot_taken",
    }
    for builder, reason in cases.items():
        assert response_error(await builder(valid_request(), "key", ALICE)) == (409, reason)


async def test_router_error_response_maps_exceptions() -> None:
    """Given Routerで捕捉した業務例外 When error responseへ変換 Then 例外のstatusと理由を返す。 [COM-03-AC]"""
    error = ApiFunctionError(404, "resource_not_found", summary="資源なし")
    response = await functions.build_router_error_response(valid_request(), "key", ALICE, error)
    assert response_error(response) == (404, "resource_not_found")
