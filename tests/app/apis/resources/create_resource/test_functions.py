"""資源登録の入力規則と権限判定を単体で検査する。"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.apis.resources.create_resource import functions
from app.apis.resources.create_resource.schemas import CreateResourceRequest
from app.apis.sequence_types import CallerIdentity


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
    admin = CallerIdentity(principal_id="admin", groups=("admin",))
    assert not await functions.has_resource_management_permission(user)
    assert await functions.has_resource_management_permission(admin)
