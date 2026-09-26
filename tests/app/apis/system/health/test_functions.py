"""稼働確認の業務関数を単体で検査する。"""

from __future__ import annotations

import pytest

from app.apis.exceptions import ApiFunctionError
from app.apis.system.health import functions
from tests.app.apis.function_helpers import response_error

pytestmark = pytest.mark.anyio


async def test_build_health_response_returns_ok_only() -> None:
    """Given 稼働中のAPI When 稼働状態を組み立てる Then 秘密やDB情報を含まずokだけを返す。 [TECH-PRIVACY-AC]"""
    response = await functions.build_health_response()
    assert response.model_dump(by_alias=True) == {"status": "ok"}


async def test_router_error_response() -> None:
    """Given 稼働確認中の業務例外 When Router例外を変換 Then 500と理由コードを返す。 [COM-07-AC]"""
    error = ApiFunctionError(500, "forced router error", summary="稼働確認失敗")
    routed = await functions.build_router_error_response(error)
    assert response_error(routed) == (500, "forced router error")
