"""API Gateway v2イベントと配布ZIPの読込を検査する。"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

import pytest

from app.lambda_handler import handler

ZIP = Path("artifacts/lambda.zip")


def event(path: str) -> dict[str, Any]:
    return {
        "version": "2.0",
        "routeKey": "GET " + path,
        "rawPath": path,
        "rawQueryString": "",
        "headers": {},
        "requestContext": {
            "http": {
                "method": "GET",
                "path": path,
                "sourceIp": "127.0.0.1",
                "protocol": "HTTP/1.1",
            },
            "requestId": "synthetic",
        },
        "isBase64Encoded": False,
    }


def test_gateway_event() -> None:
    """Given HTTP APIイベント When Mangum変換 Then health200・未認証業務401。 [TECH-LAMBDA-AC]"""
    assert handler(event("/health"), {})["statusCode"] == 200
    assert handler(event("/resources"), {})["statusCode"] == 401


@pytest.mark.skipif(not ZIP.exists(), reason="配布ZIPはverifyのpackage検査で作成する")
def test_distribution_zip() -> None:
    """Given 配布ZIP When 隔離pathからimport Then SQLと依存を含むhandlerを読める。 [TECH-LAMBDA-AC]"""
    with tempfile.TemporaryDirectory() as directory:
        with zipfile.ZipFile(ZIP) as archive:
            archive.extractall(directory)
        code = (
            "from app.lambda_handler import handler; from pathlib import Path; import app; "
            'assert list(Path(app.__file__).parent.rglob("*.sql"))'
        )
        result = subprocess.run(  # noqa: S603
            [sys.executable, "-c", code],
            cwd=directory,
            env={**os.environ, "PYTHONPATH": directory},
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
