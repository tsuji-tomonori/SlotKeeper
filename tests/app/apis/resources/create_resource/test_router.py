"""資源登録APIを検査する。"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.apis.base import sample_value
from app.apis.exceptions import ApiFunctionError
from app.apis.resources.common import ResourceKind
from app.apis.resources.create_resource.samples import (
    CREATE_RESOURCE_REQUEST_SAMPLE,
    CREATE_RESOURCE_RESPONSE_SAMPLE,
    CREATE_RESOURCE_STATUS_SAMPLES,
)
from app.integrations.common_errors import ExternalApiError
from tests.app.apis.router_db import RouterDbHarness
from tests.conftest import FixedClock
from tests.helpers import Signer, error_reason

pytestmark = pytest.mark.db


def test_user_cannot_create_resource(client: TestClient, signed: Signer) -> None:
    """Given 一般利用者 When 管理API Then 403。 [SLOT-01-AC] [COM-04-AC]"""
    response = client.post("/resources", json={"name": "会議室"}, headers=signed())
    assert response.status_code == 403
    assert error_reason(response) == "forbidden"


def test_admin_creates_active_resource(client: TestClient, signed: Signer, database: None) -> None:
    """Given 管理者 When 前後空白つきの資源名で登録 Then 201で空白を除き有効な初期版を返す。 [SLOT-01-AC] [RULE-14-AC]"""
    response = client.post(
        "/resources",
        json={"name": "  会議室 登録確認  ", "description": "", "kind": ResourceKind.EQUIPMENT},
        headers=signed("manager", True),
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["name"] == "会議室 登録確認"
    assert (
        body["active"] is True and body["version"] == 1 and body["kind"] == ResourceKind.EQUIPMENT
    )


@pytest.mark.anyio
async def test_create_resource_router_returns_sample_shaped_response_with_db(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_fetch_one: Callable[..., Any],
) -> None:
    """Given 管理者 When 標本requestで資源登録 Then 標本と同じ形の応答を返し資源を保存する。 [SLOT-01-AC]"""
    response = await router_db_harness.client.post(
        "/resources",
        headers=router_auth_headers("manager", True),
        json=sample_value(CREATE_RESOURCE_REQUEST_SAMPLE),
    )

    assert response.status_code == 201, response.text
    body = response.json()
    expected = sample_value(CREATE_RESOURCE_RESPONSE_SAMPLE)
    expected["resourceId"] = body["resourceId"]
    assert body == expected
    row = await router_fetch_one(
        router_db_harness.session_factory, "resources", {"resource_id": body["resourceId"]}
    )
    assert row is not None and row["name"] == expected["name"] and row["control_version"] == 0


@pytest.mark.anyio
async def test_create_resource_sample_request_emits_router_error_log_to_stdio(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    assert_router_error_log: Callable[..., Any],
) -> None:
    """Given 標本requestと保存中の業務例外 When 資源登録 Then Router例外の運用ログをcatalogどおり出す。 [COM-07-AC]"""
    await assert_router_error_log(
        router_db_harness=router_db_harness,
        capsys=capsys,
        monkeypatch=monkeypatch,
        method="POST",
        path_template="/resources",
        status_samples=CREATE_RESOURCE_STATUS_SAMPLES,
        success_status=201,
        patch_target="app.apis.resources.create_resource.functions.save_resource",
        message_id="createResource.router_api_function_error",
        catalog_id="M002",
        headers=router_auth_headers("manager", True),
    )


# unit-test_gen.md executable cases
@pytest.mark.anyio
async def test_tc001_create_resource_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
) -> None:
    """Given 一般利用者 When 資源登録 Then 403で運用ログを出す。 [SLOT-01-AC] [COM-04-AC]"""
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.post(
            "/resources",
            headers=router_auth_headers("alice"),
            json=sample_value(CREATE_RESOURCE_REQUEST_SAMPLE),
        )

    assert response.status_code == 403, response.text
    assert response.json()["error"]["details"][0]["reason"] == "forbidden"
    actual_log_event = find_log_event("createResource.caller_cannot_manage_resources")
    assert actual_log_event["messageId"] == "createResource.caller_cannot_manage_resources"
    assert actual_log_event["summary"] == "呼び出し元が管理者ではないため、資源登録を拒否した。"


@pytest.mark.anyio
async def test_tc002_create_resource_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
) -> None:
    """Given 管理者 When 資源登録 Then 201で有効な資源を返す。 [SLOT-01-AC]"""
    response = await router_db_harness.client.post(
        "/resources",
        headers=router_auth_headers("manager", True),
        json=sample_value(CREATE_RESOURCE_REQUEST_SAMPLE),
    )

    assert response.status_code == 201, response.text
    assert response.json()["active"] is True


@pytest.mark.anyio
async def test_tc003_create_resource_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 資源の保存で業務例外 When API呼出し Then Routerで500へ変換し運用ログを出す。"""
    _ = timer

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise ApiFunctionError(500, "forced router error", summary="unit-test_gen case")

    monkeypatch.setattr(
        "app.apis.resources.create_resource.functions.save_resource",
        raise_expected_error,
    )
    headers = router_auth_headers("manager", True)
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.post(
            "/resources", headers=headers, json=sample_value(CREATE_RESOURCE_REQUEST_SAMPLE)
        )

    assert response.status_code == 500, response.text
    assert response.json()["error"]["details"][0]["reason"] == "forced router error"
    actual_log_event = find_log_event("createResource.router_api_function_error")
    assert actual_log_event["messageId"] == "createResource.router_api_function_error"
    assert (
        actual_log_event["summary"] == "Routerで捕捉したApiFunctionErrorにより資源登録が失敗した。"
    )


@pytest.mark.anyio
async def test_tc004_create_resource_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 資源の保存で外部API例外 When API呼出し Then Routerで502へ変換し運用ログを出す。"""
    _ = timer

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise ExternalApiError("forced external api error")

    monkeypatch.setattr(
        "app.apis.resources.create_resource.functions.save_resource",
        raise_expected_error,
    )
    headers = router_auth_headers("manager", True)
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.post(
            "/resources", headers=headers, json=sample_value(CREATE_RESOURCE_REQUEST_SAMPLE)
        )

    assert response.status_code == 502, response.text
    assert response.json()["error"]["details"][0]["reason"] == "external service request failed"
    actual_log_event = find_log_event("createResource.router_external_api_error")
    assert actual_log_event["messageId"] == "createResource.router_external_api_error"
    assert (
        actual_log_event["summary"] == "Routerで捕捉したExternalApiErrorにより資源登録が失敗した。"
    )


@pytest.mark.anyio
async def test_tc005_create_resource_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 資源の保存でHTTP例外 When API呼出し Then Routerで400へ変換し運用ログを出す。"""
    _ = timer

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise HTTPException(status_code=400, detail="forced http exception")

    monkeypatch.setattr(
        "app.apis.resources.create_resource.functions.save_resource",
        raise_expected_error,
    )
    headers = router_auth_headers("manager", True)
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.post(
            "/resources", headers=headers, json=sample_value(CREATE_RESOURCE_REQUEST_SAMPLE)
        )

    assert response.status_code == 400, response.text
    assert response.json()["error"]["details"][0]["reason"] == "forced http exception"
    actual_log_event = find_log_event("createResource.router_http_exception")
    assert actual_log_event["messageId"] == "createResource.router_http_exception"
    assert actual_log_event["summary"] == "Routerで捕捉したHTTPExceptionにより資源登録が失敗した。"
