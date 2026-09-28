"""公開契約のerror schema・状態コード・入力項目を検査する。"""

from __future__ import annotations

import json

from app.main import create_app


def test_api_error_responses_are_selected_per_operation() -> None:
    """Given 公開OpenAPI When 操作ごとのresponseを列挙 Then 業務上発生する状態だけを共通error schemaで宣言する。 [COM-03-AC]"""
    schema = create_app().openapi()
    common = {"401", "422", "429", "500", "503"}
    expected = {
        "listResources": {"200"} | common,
        "createResource": {"201", "403"} | common,
        "updateResource": {"200", "403", "404", "409"} | common,
        "getResourceSchedule": {"200", "404"} | common,
        "listReservations": {"200"} | common,
        "createReservation": {"201", "404", "409"} | common,
        "getReservation": {"200", "403", "404"} | common,
        "cancelReservation": {"200", "403", "404", "409"} | common,
    }
    actual = {
        operation["operationId"]: set(operation["responses"])
        for path in schema["paths"].values()
        for operation in path.values()
        if operation["operationId"] != "health"
    }
    assert actual == expected
    error = schema["components"]["schemas"]["ErrorResponse"]
    assert error["required"] == ["error"]


def test_public_contract_has_no_clock_or_direct_edit() -> None:
    """Given 公開OpenAPI When 入力と操作を列挙 Then 現在時刻の上書き入力と予約日時の直接編集がない。 [RULE-04-AC] [RULE-05-AC]"""
    spec = create_app().openapi()
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
    body = json.dumps(spec["components"]["schemas"]["CancelReservationRequest"])
    assert "startAt" not in body and "status" not in body
