"""API Gateway v2イベントと配布ZIPの読込を検査する。"""

import os
import subprocess
import sys
import tempfile
import zipfile

from slotkeeper.app import handler


def event(path):
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


def test_gateway_event():
    """Given HTTP APIイベント When Mangum変換 Then health200・未認証業務401。 [TECH-LAMBDA-AC]"""
    assert handler(event("/health"), {})["statusCode"] == 200
    assert handler(event("/resources"), {})["statusCode"] == 401


def test_distribution_zip():
    """Given 配布ZIP When 隔離pathからimport Then SQLと依存を含むhandlerを読める。 [TECH-LAMBDA-AC]"""
    with tempfile.TemporaryDirectory() as directory:
        with zipfile.ZipFile("artifacts/lambda.zip") as archive:
            archive.extractall(directory)
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                'from slotkeeper.app import handler; from pathlib import Path; import slotkeeper; assert list(Path(slotkeeper.__file__).parent.rglob("*.sql"))',
            ],
            cwd=directory,
            env={**os.environ, "PYTHONPATH": directory},
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
