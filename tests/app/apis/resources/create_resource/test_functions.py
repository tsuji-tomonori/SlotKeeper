"""資源登録の入力規則と権限判定を単体で検査する。"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.apis.common import IdentityGroup
from app.apis.exceptions import ApiFunctionError
from app.apis.resources.common import ResourceKind
from app.apis.resources.create_resource import functions
from app.apis.resources.create_resource.generated import queries
from app.apis.resources.create_resource.schemas import CreateResourceRequest
from app.apis.sequence_types import CallerIdentity
from tests.app.apis.function_helpers import ADMIN, BOB, QueryRecorder, fake_session, response_error


@pytest.mark.parametrize("name", ["", " " * 4, "a" * 101])
def test_resource_input(name: str) -> None:
    """Given 空白か長すぎる資源名 When 入力解析 Then 拒否。 [COM-03-AC] [RULE-14-AC]"""
    with pytest.raises(ValidationError):
        CreateResourceRequest(name=name)


def test_description_limit() -> None:
    """Given 1,001文字の説明 When 入力解析 Then 拒否し1,000文字は受け付ける。 [RULE-14-AC]"""
    assert CreateResourceRequest(name="会議室", description="a" * 1000).description
    with pytest.raises(ValidationError):
        CreateResourceRequest(name="会議室", description="a" * 1001)


@pytest.mark.anyio
async def test_only_admin_manages_resources() -> None:
    """Given 一般利用者と管理者 When 資源管理権限を判定 Then 管理者だけ許可する。 [SLOT-01-AC] [COM-04-AC]"""
    user = CallerIdentity(principal_id="alice", groups=())
    admin = CallerIdentity(principal_id="manager", groups=(IdentityGroup.ADMIN,))
    assert not await functions.has_resource_management_permission(user)
    assert await functions.has_resource_management_permission(admin)


@pytest.mark.anyio
async def test_save_resource_and_builders(monkeypatch: pytest.MonkeyPatch) -> None:
    """Given 登録要求 When 資源を保存し応答を組み立てる Then 有効な初期版を返し保存失敗と権限不足を区別する。 [SLOT-01-AC]"""
    recorder = QueryRecorder()
    row = queries.InsertResourcesRow(
        resource_id="resource",
        name="会議室",
        description="",
        kind=ResourceKind.ROOM,
        active=True,
        row_version=1,
    )
    recorder.install(monkeypatch, queries, "insert_resources", row)
    request = CreateResourceRequest(name="会議室")
    resource = await functions.save_resource(request, fake_session())
    assert (await functions.build_resource_response(resource)).version == 1
    assert recorder.params("insert_resources").name == "会議室"
    recorder.install(monkeypatch, queries, "insert_resources", None)
    with pytest.raises(ApiFunctionError):
        await functions.save_resource(request, fake_session())
    forbidden = await functions.build_caller_cannot_manage_resources_response(request, BOB)
    assert response_error(forbidden) == (403, "forbidden")
    error = ApiFunctionError(500, "resource_not_saved", summary="保存結果なし")
    routed = await functions.build_router_error_response(request, ADMIN, error)
    assert response_error(routed) == (500, "resource_not_saved")
