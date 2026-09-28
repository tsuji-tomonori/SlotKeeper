"""HTTP境界の運用ログが要求ID・操作・結果・所要時間だけを残すことを検査する。"""

from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from tests.helpers import Signer, log_events, operational_stdout_handler

pytestmark = pytest.mark.db


def test_request_log_redacts(
    client: TestClient,
    signed: Signer,
    booking: dict[str, str],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Given 目的とtokenを含む作成要求 When API呼出し Then 要求ID・operation・status・所要時間だけを記録する。 [COM-07-AC]"""
    secret = "秘密の会議目的-" + str(uuid4())
    headers = {**signed(), "Idempotency-Key": str(uuid4())}
    capsys.readouterr()
    with operational_stdout_handler():
        response = client.post(
            "/reservations", json={**booking, "purpose": secret}, headers=headers
        )
    assert response.status_code == 201
    output = capsys.readouterr().out
    events = log_events(output)
    completed = [e for e in events if e["messageId"] == "http.request_completed"]
    assert completed[-1]["traceId"] == response.headers["X-Request-ID"]
    assert completed[-1]["api"]["operation"] == "createReservation"
    assert completed[-1]["api"]["statusCode"] == 201
    assert completed[-1]["metrics"]["durationMs"] >= 0
    assert secret not in output
    assert headers["Authorization"].split()[1] not in output
    assert response.headers["Cache-Control"] == "no-store"
