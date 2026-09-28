"""開発標準とアプリのtoolsが同じプロセスで読み込めることを検査する。"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("paths", [("src", "."), (".", "src")])
def test_tools_package_imports_both_roots(paths: tuple[str, str]) -> None:
    """Given 2箇所のtools配置 When 順序を変えて探索 Then Quintとverifyの依存を読み込める。"""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import tools.project.verify; import tools.safe_io; import runpy; "
            "runpy.run_path('.agents/skills/maintain-canonical-requirements/scripts/specflow.py')",
        ],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": os.pathsep.join(str(ROOT / path) for path in paths)},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
