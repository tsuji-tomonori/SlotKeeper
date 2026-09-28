"""router testで使う実DB harnessと認証headerのfixtureです。"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import Any

import pytest

from tests.helpers import Signer

from .helpers import assert_sample_request_emits_router_error_log, capture_operational_log_events
from .router_db import (
    RouterDbHarness,
    count_rows,
    create_router_db_harness,
    fetch_one,
    seed_reservation,
    seed_resource,
)


@pytest.fixture
async def router_db_harness(database: None) -> AsyncIterator[RouterDbHarness]:
    _ = database
    async for harness in create_router_db_harness():
        yield harness


@pytest.fixture
def router_auth_headers(signed: Signer) -> Callable[..., dict[str, str]]:
    """署名済みaccess tokenのAuthorization headerを作る。"""

    def make(principal_id: str = "alice", admin: bool = False) -> dict[str, str]:
        return signed(principal_id, admin)

    return make


@pytest.fixture
def router_fetch_one() -> Callable[..., Any]:
    return fetch_one


@pytest.fixture
def router_count_rows() -> Callable[..., Any]:
    return count_rows


@pytest.fixture
def assert_router_error_log() -> Callable[..., Any]:
    return assert_sample_request_emits_router_error_log


@pytest.fixture
def capture_router_logs() -> Callable[..., Any]:
    return capture_operational_log_events


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def router_seed_resource() -> Callable[..., Any]:
    return seed_resource


@pytest.fixture
def router_seed_reservation() -> Callable[..., Any]:
    return seed_reservation
