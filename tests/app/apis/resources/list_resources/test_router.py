"""資源一覧APIを実PostgreSQLで検査する。"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.apis.base import sample_value
from app.apis.exceptions import ApiFunctionError
from app.apis.resources.common import ResourceKind
from app.apis.resources.list_resources.samples import (
    LIST_RESOURCES_RESPONSE_SAMPLE,
    LIST_RESOURCES_STATUS_SAMPLES,
)
from app.integrations.common_errors import ExternalApiError
from tests.app.apis.router_db import RouterDbHarness
from tests.conftest import FixedClock
from tests.helpers import Signer

pytestmark = pytest.mark.db


def test_resource_paging_order(client: TestClient, signed: Signer, database: None) -> None:
    """Given 同名の資源 When ページ単位で取得 Then 名前とIDの固定順で欠落・重複がない。 [SLOT-01-AC] [RULE-14-AC]"""
    admin = signed("manager", True)
    name = "順序確認 " + str(uuid4())
    created = sorted(
        client.post(
            "/resources",
            headers=admin,
            json={"name": name, "description": "", "kind": ResourceKind.ROOM},
        ).json()["resourceId"]
        for _ in range(3)
    )
    seen: list[str] = []
    token = ""
    while True:
        query = "/resources?limit=2" + ("&nextToken=" + token if token else "")
        page = client.get(query, headers=signed("bob")).json()
        seen += [r["resourceId"] for r in page["items"] if r["name"] == name]
        if not page.get("nextToken"):
            break
        token = page["nextToken"]
    assert seen == created


@pytest.mark.anyio
async def test_list_resources_router_returns_sample_shaped_response_with_db(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_count_rows: Callable[..., Any],
    router_seed_resource: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 先頭に並ぶ名前の資源 When 標本queryで一覧取得 Then 標本と同じ形で資源を返す。 [SLOT-01-AC]"""
    _ = timer
    resource = await router_seed_resource(
        router_db_harness, router_auth_headers("manager", True), name="!先頭資源 " + str(uuid4())
    )
    request = LIST_RESOURCES_STATUS_SAMPLES[200]["request"]
    response = await router_db_harness.client.get(
        "/resources", headers=router_auth_headers("alice"), params={**request["query"], "limit": 1}
    )

    assert response.status_code == 200, response.text
    body = response.json()
    expected = sample_value(LIST_RESOURCES_RESPONSE_SAMPLE)
    expected["items"] = [{**expected["items"][0], **resource}]
    expected["nextToken"] = body["nextToken"]
    assert body == expected
    where = {"resource_id": resource["resourceId"]}
    factory = router_db_harness.session_factory
    assert await router_count_rows(factory, "resources", where) == 1


@pytest.mark.anyio
async def test_list_resources_sample_request_emits_router_error_log_to_stdio(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    assert_router_error_log: Callable[..., Any],
) -> None:
    """Given 標本requestと処理中の業務例外 When 資源一覧取得 Then Router例外の運用ログをcatalogどおり出す。 [COM-07-AC]"""
    await assert_router_error_log(
        router_db_harness=router_db_harness,
        capsys=capsys,
        monkeypatch=monkeypatch,
        method="GET",
        path_template="/resources",
        status_samples=LIST_RESOURCES_STATUS_SAMPLES,
        success_status=200,
        patch_target="app.apis.resources.list_resources.functions.get_resources",
        message_id="listResources.router_api_function_error",
        catalog_id="M001",
        headers=router_auth_headers("alice"),
    )


# unit-test_gen.md executable cases
@pytest.mark.anyio
async def test_tc001_list_resources_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    router_seed_resource: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 登録済みの資源 When 一覧取得 Then 200で資源を返す。 [SLOT-01-AC]"""
    _ = timer
    await router_seed_resource(router_db_harness, router_auth_headers("manager", True))
    response = await router_db_harness.client.get(
        "/resources", headers=router_auth_headers("alice")
    )

    assert response.status_code == 200, response.text
    assert response.json()["items"]


@pytest.mark.anyio
async def test_tc002_list_resources_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 資源一覧の取得で業務例外 When API呼出し Then Routerで500へ変換し運用ログを出す。"""
    _ = timer

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise ApiFunctionError(500, "forced router error", summary="unit-test_gen case")

    monkeypatch.setattr(
        "app.apis.resources.list_resources.functions.get_resources",
        raise_expected_error,
    )
    headers = router_auth_headers("alice")
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.get("/resources", headers=headers)

    assert response.status_code == 500, response.text
    assert response.json()["error"]["details"][0]["reason"] == "forced router error"
    actual_log_event = find_log_event("listResources.router_api_function_error")
    assert actual_log_event["messageId"] == "listResources.router_api_function_error"
    assert (
        actual_log_event["summary"]
        == "Routerで捕捉したApiFunctionErrorにより資源一覧取得が失敗した。"
    )


@pytest.mark.anyio
async def test_tc003_list_resources_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 資源一覧の取得で外部API例外 When API呼出し Then Routerで502へ変換し運用ログを出す。"""
    _ = timer

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise ExternalApiError("forced external api error")

    monkeypatch.setattr(
        "app.apis.resources.list_resources.functions.get_resources",
        raise_expected_error,
    )
    headers = router_auth_headers("alice")
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.get("/resources", headers=headers)

    assert response.status_code == 502, response.text
    assert response.json()["error"]["details"][0]["reason"] == "external service request failed"
    actual_log_event = find_log_event("listResources.router_external_api_error")
    assert actual_log_event["messageId"] == "listResources.router_external_api_error"
    assert (
        actual_log_event["summary"]
        == "Routerで捕捉したExternalApiErrorにより資源一覧取得が失敗した。"
    )


@pytest.mark.anyio
async def test_tc004_list_resources_router_matches_unit_test_gen(
    router_db_harness: RouterDbHarness,
    router_auth_headers: Callable[..., dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    capture_router_logs: Callable[..., Any],
    timer: FixedClock,
) -> None:
    """Given 資源一覧の取得でHTTP例外 When API呼出し Then Routerで400へ変換し運用ログを出す。"""
    _ = timer

    async def raise_expected_error(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        raise HTTPException(status_code=400, detail="forced http exception")

    monkeypatch.setattr(
        "app.apis.resources.list_resources.functions.get_resources",
        raise_expected_error,
    )
    headers = router_auth_headers("alice")
    with capture_router_logs(capsys) as find_log_event:
        response = await router_db_harness.client.get("/resources", headers=headers)

    assert response.status_code == 400, response.text
    assert response.json()["error"]["details"][0]["reason"] == "forced http exception"
    actual_log_event = find_log_event("listResources.router_http_exception")
    assert actual_log_event["messageId"] == "listResources.router_http_exception"
    assert (
        actual_log_event["summary"] == "Routerで捕捉したHTTPExceptionにより資源一覧取得が失敗した。"
    )
