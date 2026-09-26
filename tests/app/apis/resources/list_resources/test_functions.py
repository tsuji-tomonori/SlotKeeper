"""資源一覧の業務関数を単体で検査する。"""

from __future__ import annotations

import pytest

from app.apis.exceptions import ApiFunctionError
from app.apis.resources.list_resources import functions
from app.apis.resources.list_resources.generated import queries
from app.apis.resources.list_resources.schemas import ListResourcesQuery
from tests.app.apis.function_helpers import ALICE, QueryRecorder, fake_session, response_error

pytestmark = pytest.mark.anyio


def row(name: str, resource_id: str) -> queries.SelectResourcesRow:
    return queries.SelectResourcesRow(
        resource_id=resource_id,
        name=name,
        description="",
        kind="room",
        active=True,
        row_version=1,
    )


async def test_resources_are_paged_by_name_and_id(monkeypatch: pytest.MonkeyPatch) -> None:
    """Given 同名を含む3件の資源と上限2件 When 一覧を取得 Then 名前とIDの継続tokenで次ページを問い合わせる。 [SLOT-01-AC] [RULE-14-AC]"""
    recorder = QueryRecorder()
    rows = [row("A", "1"), row("A", "2"), row("B", "3")]
    recorder.install(monkeypatch, queries, "select_resources", rows)
    query = ListResourcesQuery(limit=2)
    resources = await functions.get_resources(query, fake_session())
    page = await functions.apply_pagination(resources, query)
    response = await functions.build_resource_list_response(page)
    assert [item.resource_id for item in response.items] == ["1", "2"]
    assert response.next_token is not None
    await functions.get_resources(
        ListResourcesQuery(next_token=response.next_token), fake_session()
    )
    params = recorder.calls[-1][1]
    assert (params.after_name, params.after_resource_id) == ("A", "2")
    with pytest.raises(ApiFunctionError):
        await functions.get_resources(ListResourcesQuery(next_token="%%%"), fake_session())


async def test_router_error_response() -> None:
    """Given 不正な継続token When Router例外を変換 Then 422と理由コードを返す。 [COM-03-AC]"""
    error = ApiFunctionError(422, "invalid_page_token", summary="token不正")
    routed = await functions.build_router_error_response(ListResourcesQuery(), ALICE, error)
    assert response_error(routed) == (422, "invalid_page_token")
