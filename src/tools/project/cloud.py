"""明示指定された実AWSだけを検査し、ローカル成功と区別した証跡を残す。"""

from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from threading import Barrier
from time import perf_counter
from typing import Any
from uuid import uuid4

import httpx

JST_OFFSET = timedelta(hours=9)


def timed(client: httpx.Client, method: str, url: str, **kwargs: Any) -> tuple[int, float]:
    """応答statusと所要時間だけを記録し、本文やtokenを残さない。"""
    before = perf_counter()
    response = client.request(method, url, **kwargs)
    return response.status_code, round((perf_counter() - before) * 1000, 2)


def concurrent_booking(url: str, token: str, resource: str) -> dict[str, Any]:
    """DSQL上で同じ枠へ20要求を同時送信し、OCCと重複拒否を確かめる。"""
    headers = {"Authorization": "Bearer " + token}
    # 30日以内・15分刻み・日本時間の同日内になる将来枠を選ぶ。
    day = (datetime.now(UTC) + JST_OFFSET).date() + timedelta(days=20)
    start = datetime(day.year, day.month, day.day, 1, tzinfo=UTC) + timedelta(
        minutes=15 * (uuid4().int % 20)
    )
    body = {
        "resourceId": resource,
        "startAt": start.isoformat(),
        "endAt": (start + timedelta(minutes=15)).isoformat(),
        "purpose": "実AWS競合検証",
    }
    barrier = Barrier(20)

    def send(_: int) -> httpx.Response:
        with httpx.Client(timeout=30) as client:
            barrier.wait(timeout=30)
            return client.post(
                url + "/reservations",
                json=body,
                headers={**headers, "Idempotency-Key": str(uuid4())},
            )

    with ThreadPoolExecutor(max_workers=20) as pool:
        responses = list(pool.map(send, range(20)))
    statuses = sorted(r.status_code for r in responses)
    created = [r.json() for r in responses if r.status_code == 201]
    with httpx.Client(timeout=30) as client:
        for row in created:
            client.post(
                url + "/reservations/" + row["reservationId"] + "/cancel",
                headers=headers,
                json={"version": row["version"]},
            )
    return {
        "status": "passed" if statuses == [201] + [409] * 19 else "failed",
        "statuses": statuses,
    }


def passed(condition: bool) -> str:
    return "passed" if condition else "failed"


def endpoint_cases(url: str, token: str) -> dict[str, Any]:
    """health、JWT境界、cold/warm応答を確認する。"""
    auth = {"Authorization": "Bearer " + token}
    with httpx.Client(timeout=30) as client:
        # 最初の業務要求はLambdaとDSQL接続が冷えている可能性があるため、以後と分けて記録する。
        first = timed(client, "GET", url + "/resources", headers=auth)
        warm = [timed(client, "GET", url + "/resources", headers=auth) for _ in range(10)]
        health = timed(client, "GET", url + "/health")
        anonymous = timed(client, "GET", url + "/resources")
    return {
        "health": {"status": passed(health[0] == 200), "http": health[0]},
        "anonymous-denied": {"status": passed(anonymous[0] == 401), "http": anonymous[0]},
        "authenticated-read": {
            "status": passed(first[0] == 200 and all(status == 200 for status, _ in warm)),
            "first_ms": first[1],
            "warm_ms": sorted(ms for _, ms in warm),
        },
    }


def main() -> None:
    """health、JWT境界、cold/warm応答、任意でDSQLの同時予約を実AWSで確認する。"""
    url = os.environ.get("SLOT_CLOUD_API", "").rstrip("/")
    token = os.environ.get("SLOT_CLOUD_TOKEN", "")
    resource = os.environ.get("SLOT_CLOUD_RESOURCE_ID", "")
    if not url.startswith("https://") or not token:
        raise SystemExit("実AWS URLとaccess tokenの明示指定が必要")
    cases = endpoint_cases(url, token)
    cases["dsql-concurrent-booking"] = (
        concurrent_booking(url, token, resource)
        if resource
        else {"status": "not-run", "reason": "SLOT_CLOUD_RESOURCE_IDの合成資源が未指定"}
    )
    results = {
        "revision": os.environ.get("SLOT_REVISION", "local-worktree"),
        "runId": os.environ.get("SLOT_RUN_ID", "local"),
        "generatedAt": datetime.now(UTC).isoformat(),
        "status": "measured",
        "scope": "cloud",
        "note": "coldは直前の利用状況に依存する最初の要求。DSQL接続はIAM認証の公式connector。",
        "cases": cases,
    }
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/cloud.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n"
    )
    if any(case["status"] == "failed" for case in cases.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
