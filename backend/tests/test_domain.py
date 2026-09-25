"""予約境界と公開入力の規則を検査する。"""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError
from slotkeeper.domain import BookingInput, DomainError, ResourceInput, validate_booking

NOW = datetime(2026, 9, 25, tzinfo=UTC)


def value(start, end):
    return BookingInput(resource_id="resource", purpose=" 会議 ", start_at=start, end_at=end)


@pytest.mark.parametrize(
    "start,end",
    [
        (NOW, NOW + timedelta(minutes=15)),
        (NOW - timedelta(hours=1), NOW),
        (NOW + timedelta(days=31), NOW + timedelta(days=31, hours=1)),
        (NOW + timedelta(hours=1), NOW + timedelta(hours=1)),
        (NOW + timedelta(hours=1), NOW + timedelta(hours=5, minutes=15)),
        (NOW + timedelta(minutes=1), NOW + timedelta(minutes=16)),
        (NOW + timedelta(hours=14), NOW + timedelta(hours=15)),
        (NOW + timedelta(hours=1, seconds=1), NOW + timedelta(hours=2, seconds=1)),
    ],
)
def test_reject_invalid_time(start, end):
    """Given 範囲外または刻み不正 When 時刻検証 Then 入力不正。 [SLOT-AC06]"""
    with pytest.raises(DomainError) as exc:
        validate_booking(value(start, end), NOW)
    assert exc.value.status == 422


@pytest.mark.parametrize("days,minutes", [(1, 15), (1, 240), (30, 15)])
def test_boundaries(days, minutes):
    """Given 15分・4時間・30日境界 When 時刻検証 Then 受け付ける。 [SLOT-AC06]"""
    start = NOW + timedelta(days=days)
    validate_booking(value(start, start + timedelta(minutes=minutes)), NOW)


@pytest.mark.parametrize("name", ["", " " * 4, "a" * 101])
def test_resource_input(name):
    """Given 空白か長すぎる資源名 When 入力解析 Then 拒否。 [COM-03]"""
    with pytest.raises(ValidationError):
        ResourceInput(name=name)


def test_normalized_input():
    """Given 同じ瞬間のoffset差と前後空白 When 正規化 Then 同一要求。 [SLOT-AC09]"""
    a = value("2026-09-26T10:00:00+09:00", "2026-09-26T11:00:00+09:00")
    b = value("2026-09-26T01:00:00Z", "2026-09-26T02:00:00Z")
    assert a.model_dump_json() == b.model_dump_json()
    assert a.purpose == "会議"
