"""pytestの収集集合と実結果を同じrunに結び付ける。"""

import json
import os
from pathlib import Path
from typing import Any

import pytest

INVENTORY: dict[str, dict[str, Any]] = {}
RESULTS: dict[str, dict[str, Any]] = {}


def pytest_collection_finish(session: pytest.Session) -> None:
    """実collectorからパラメータ化caseを分けて取得する。"""
    for item in session.items:
        obj = getattr(item, "obj", None)
        INVENTORY[item.nodeid] = {"id": item.nodeid, "narrative": getattr(obj, "__doc__", "") or ""}
    save()


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """setup/teardown失敗とskipも実行結果へ残す。"""
    if report.when == "call" or report.failed or report.skipped:
        status = "failed" if report.failed else "skipped" if report.skipped else "passed"
        RESULTS[report.nodeid] = {"status": status, "duration": report.duration}
    save()


def save() -> None:
    """collector原本には公開可能な固定情報だけを書く。"""
    target = Path(os.environ.get("SLOT_COLLECTOR", "artifacts/pytest-results.json"))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            {
                "revision": os.environ.get("SLOT_REVISION", "local-worktree"),
                "runId": os.environ.get("SLOT_RUN_ID", "local"),
                "inventory": list(INVENTORY.values()),
                "results": RESULTS,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )
