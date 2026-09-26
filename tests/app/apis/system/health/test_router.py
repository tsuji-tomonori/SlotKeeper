"""稼働確認APIをRouter経由で検査する。"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest
from fastapi import HTTPException

from app.apis.base import sample_value
from app.apis.exceptions import ApiFunctionError
from app.apis.system.health.samples import HEALTH_RESPONSE_SAMPLE, HEALTH_STATUS_SAMPLES
from app.integrations.common_errors import ExternalApiError
from tests.app.apis.router_db import RouterDbHarness

pytestmark = pytest.mark.db


@pytest.mark.anyio
async def test_health_router_returns_sample_shaped_response_with_db(
    router_db_harness: RouterDbHarness,
    router_count_rows: Callable[..., Any],
) -> None:
    """Given 認証情報なし When 稼働確認 Then 標本と同じ稼働状態だけを返しDBを変更しない。 [TECH-PRIVACY-AC]"""
    factory = router_db_harness.session_factory
    before = {
        table: await router_count_rows(factory, table)
        for table in ("resources", "reservations", "reservation_events", "users")
    }
    response = await router_db_harness.client.get("/health")

    assert response.status_code == 200, response.text
    body = response.json()
    expected = sample_value(HEALTH_RESPONSE_SAMPLE)
    assert body == expected
    assert response.headers["x-request-id"]
    for table, count in before.items():
        assert await router_count_rows(factory, table) == count


@pytest.mark.anyio
async def test_health_sample_request_emits_router_error_log_to_stdio(
    router_db_harness: RouterDbHarness,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    assert_router_error_log: Callable[..., Any],
) -> None:
    """Given 標本requestと処理中の業務例外 When 稼働確認 Then Router例外の運用ログをcatalogどおり出す。 [COM-07-AC]"""
    await assert_router_error_log(
        router_db_harness=router_db_harness,
        capsys=capsys,
        monkeypatch=monkeypatch,
        method="GET",
        path_template="/health",
        status_samples=HEALTH_STATUS_SAMPLES,
        success_status=200,
        patch_target="app.apis.system.health.functions.build_health_response",
        message_id="health.router_api_function_error",
        catalog_id="M001",
        headers={},
    )


# unit-test_gen.md executable cases
@pytest.mark.anyio
async def test_tc001_health_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
) -> None:
    """Given 稼働中のAPI When 稼働確認 Then 200でokを返す。"""
    response = await router_db_harness.client.get("/health")

    assert response.status_code == 200, response.text
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_tc002_health_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
) -> None:
    """Given 稼働状態の組立てで業務例外 When API呼出し Then Routerで500へ変換し運用ログを出す。"""

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise ApiFunctionError(500, "forced router error", summary="unit-test_gen case")

    monkeypatch.setattr(
        "app.apis.system.health.functions.build_health_response",
        raise_expected_error,
    )
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.get("/health")

    assert response.status_code == 500, response.text
    assert response.json()["error"]["details"][0]["reason"] == "forced router error"
    actual_log_event = find_log_event("health.router_api_function_error")
    assert actual_log_event["messageId"] == "health.router_api_function_error"
    assert (
        actual_log_event["summary"] == "Routerで捕捉したApiFunctionErrorにより稼働確認が失敗した。"
    )


@pytest.mark.anyio
async def test_tc003_health_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
) -> None:
    """Given 稼働状態の組立てで外部API例外 When API呼出し Then Routerで502へ変換し運用ログを出す。"""

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise ExternalApiError("forced external api error")

    monkeypatch.setattr(
        "app.apis.system.health.functions.build_health_response",
        raise_expected_error,
    )
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.get("/health")

    assert response.status_code == 502, response.text
    assert response.json()["error"]["details"][0]["reason"] == "external service request failed"
    actual_log_event = find_log_event("health.router_external_api_error")
    assert actual_log_event["messageId"] == "health.router_external_api_error"
    assert (
        actual_log_event["summary"] == "Routerで捕捉したExternalApiErrorにより稼働確認が失敗した。"
    )


@pytest.mark.anyio
async def test_tc004_health_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
) -> None:
    """Given 稼働状態の組立てでHTTP例外 When API呼出し Then Routerで400へ変換し運用ログを出す。"""

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise HTTPException(status_code=400, detail="forced http exception")

    monkeypatch.setattr(
        "app.apis.system.health.functions.build_health_response",
        raise_expected_error,
    )
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.get("/health")

    assert response.status_code == 400, response.text
    assert response.json()["error"]["details"][0]["reason"] == "forced http exception"
    actual_log_event = find_log_event("health.router_http_exception")
    assert actual_log_event["messageId"] == "health.router_http_exception"
    assert actual_log_event["summary"] == "Routerで捕捉したHTTPExceptionにより稼働確認が失敗した。"
