"""予約作成の業務関数を単体で検査する。"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from app.apis.exceptions import ApiFunctionError
from app.apis.reservations.create_reservation import functions
from app.apis.reservations.create_reservation.schemas import CreateReservationRequest
from app.apis.sequence_types import IdempotencyRecordRef
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
