"""資源編集の業務関数を単体で検査する。"""

from __future__ import annotations

import pytest

from app.apis.exceptions import ApiFunctionError
from app.apis.resources.update_resource import functions
from app.apis.resources.update_resource.generated import queries
from app.apis.resources.update_resource.schemas import UpdateResourceRequest
from app.apis.sequence_types import ResourceRef
from tests.app.apis.function_helpers import (
    ADMIN,
    ALICE,
    FixedClock,
    QueryRecorder,
    fake_session,
    response_error,
)

pytestmark = pytest.mark.anyio


def edit(active: bool = True, version: int = 1) -> UpdateResourceRequest:
    return UpdateResourceRequest(name="会議室", active=active, version=version)


async def test_permission_lock_version_and_future(monkeypatch: pytest.MonkeyPatch) -> None:
    """Given 将来予約のある資源 When 権限・制御版・公開版・将来予約を判定 Then 無効化時だけ将来予約を問い合わせる。 [SLOT-AC05] [SLOT-AC11] [RULE-08-AC]"""
    assert await functions.has_resource_management_permission(ADMIN)
    assert not await functions.has_resource_management_permission(ALICE)
    recorder = QueryRecorder()
    lock = queries.UpdateResourcesControlVersionRow(
        resource_id="resource", active=True, row_version=1
    )
    recorder.install(monkeypatch, queries, "update_resources_control_version", lock)
    recorder.install(
        monkeypatch,
        queries,
        "select_reservations",
        [queries.SelectReservationsRow(future_reservation_count=1)],
    )
    session = fake_session()
    resource = await functions.update_resource_control_version("resource", session)
    assert await functions.is_current_resource_version(resource, edit())
    assert not await functions.is_current_resource_version(resource, edit(version=2))
    assert not await functions.has_future_reservations(resource, edit(), FixedClock(), session)
    assert await functions.has_future_reservations(
        resource, edit(active=False), FixedClock(), session
    )
    recorder.install(monkeypatch, queries, "update_resources_control_version", None)
    with pytest.raises(ApiFunctionError):
        await functions.update_resource_control_version("missing", session)


async def test_update_resource_and_builders(monkeypatch: pytest.MonkeyPatch) -> None:
    """Given 編集要求 When 資源を更新し応答を組み立てる Then 公開版を進め拒否応答を区別する。 [SLOT-01-AC] [SLOT-AC11]"""
    recorder = QueryRecorder()
    row = queries.UpdateResourcesRow(
        resource_id="resource",
        name="会議室",
        description="",
        kind="room",
        active=False,
        row_version=2,
    )
    recorder.install(monkeypatch, queries, "update_resources", row)
    resource = ResourceRef(resource_id="resource", active=True, row_version=1)
    updated = await functions.update_resource(resource, edit(active=False), fake_session())
    assert (await functions.build_resource_response(updated)).version == 2
    recorder.install(monkeypatch, queries, "update_resources", None)
    with pytest.raises(ApiFunctionError):
        await functions.update_resource(resource, edit(), fake_session())
    cases = [
        (functions.build_caller_cannot_manage_resources_response, (403, "forbidden")),
        (functions.build_stale_resource_version_response, (409, "stale_version")),
        (functions.build_future_reservations_exist_response, (409, "future_reservations_exist")),
    ]
    for builder, expected in cases:
        assert response_error(await builder("resource", edit(), ALICE)) == expected
    error = ApiFunctionError(404, "resource_not_found", summary="資源なし")
    routed = await functions.build_router_error_response("resource", edit(), ADMIN, error)
    assert response_error(routed) == (404, "resource_not_found")
