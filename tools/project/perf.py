"""指定データ量と20並列でAPI別の実測値を収集する。"""

from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from random import Random
from time import monotonic, perf_counter
from typing import Any
from uuid import NAMESPACE_URL, uuid4, uuid5

import httpx
from slotkeeper.db import connect
from slotkeeper.settings import settings


def seed() -> list[str]:
    """既存データを消さず固定IDの合成資源100件と過去予約10万件を追加する。"""
    if settings().environment != "local" or settings().database_mode != "postgres":
        raise ValueError("性能seedはローカル専用")
    resources = [
        str(uuid5(NAMESPACE_URL, "slotkeeper/perf/resource/" + str(i))) for i in range(100)
    ]
    base = datetime(2025, 1, 1, tzinfo=UTC)
    with connect() as connection:
        for i, id in enumerate(resources):
            connection.execute(
                "INSERT INTO slotkeeper.resources(id,name,description,kind,active,version,control_version) VALUES (%s,%s,%s,%s,true,1,0) ON CONFLICT(id) DO NOTHING",
                (id, "性能試験 " + str(i), "合成データ", "room"),
            )
        for i in range(200):
            connection.execute(
                "INSERT INTO slotkeeper.users(subject,first_seen) VALUES (%s,%s) ON CONFLICT(subject) DO NOTHING",
                (str(uuid5(NAMESPACE_URL, "slotkeeper/perf/user/" + str(i))), base),
            )
    for batch in range(100):
        with connect() as connection:
            for n in range(batch * 1000, (batch + 1) * 1000):
                start = base + timedelta(minutes=(n // 100) * 15)
                connection.execute(
                    "INSERT INTO slotkeeper.reservations(id,resource_id,subject,start_at,end_at,purpose,status,version) VALUES (%s,%s,%s,%s,%s,%s,'confirmed',1) ON CONFLICT(id) DO NOTHING",
                    (
                        str(uuid5(NAMESPACE_URL, "slotkeeper/perf/reservation/" + str(n))),
                        resources[n % 100],
                        str(uuid5(NAMESPACE_URL, "slotkeeper/perf/user/" + str(n % 200))),
                        start,
                        start + timedelta(minutes=15),
                        "性能用の合成予約",
                    ),
                )
    return resources


def measure(resources: list[str], seconds: int) -> list[dict[str, Any]]:
    """各workerが別資源を使い、競合試験と速度試験を分離する。"""
    origin = os.environ["SLOT_API_URL"]
    oidc = os.environ["SLOT_OIDC_INTERNAL"]
    deadline = monotonic() + seconds

    def worker(index: int) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        with httpx.Client(timeout=15) as client:
            token_response = client.post(
                oidc + "/realms/slotkeeper/protocol/openid-connect/token",
                data={
                    "grant_type": "password",
                    "client_id": "slotkeeper",
                    "username": "perf" + str(index),
                    "password": "Local-test-2026!",
                },
            )
            token_response.raise_for_status()
            token = token_response.json()["access_token"]
            headers = {"Authorization": "Bearer " + token}
            day = datetime.now(UTC).date() + timedelta(days=7)
            start = datetime.combine(day, datetime.min.time(), UTC) + timedelta(hours=1)
            random = Random(20260925 + index)
            while monotonic() < deadline:
                mode = random.randrange(9)
                calls = (
                    [("schedule", "GET", f"/resources/{resources[index]}/schedule?day={day}", None)]
                    if mode < 4
                    else [("mine", "GET", "/reservations?future=false", None)]
                    if mode < 8
                    else [
                        (
                            "create",
                            "POST",
                            "/reservations",
                            {
                                "resource_id": resources[index],
                                "start_at": start.isoformat(),
                                "end_at": (start + timedelta(minutes=15)).isoformat(),
                                "purpose": "性能測定",
                            },
                        )
                    ]
                )
                for name, method, path, body in calls:
                    before = perf_counter()
                    try:
                        response = client.request(
                            method,
                            origin + path,
                            headers={**headers, "Idempotency-Key": str(uuid4())},
                            json=body,
                        )
                        rows.append(
                            {
                                "api": name,
                                "ms": (perf_counter() - before) * 1000,
                                "status": response.status_code,
                            }
                        )
                        if name == "create" and response.status_code == 201:
                            reservation = response.json()
                            before = perf_counter()
                            cancel = client.post(
                                origin + "/reservations/" + reservation["id"] + "/cancel",
                                headers=headers,
                                json={"version": 1},
                            )
                            rows.append(
                                {
                                    "api": "cancel",
                                    "ms": (perf_counter() - before) * 1000,
                                    "status": cancel.status_code,
                                }
                            )
                    except httpx.HTTPError:
                        rows.append(
                            {"api": name, "ms": (perf_counter() - before) * 1000, "status": 0}
                        )
        return rows

    with ThreadPoolExecutor(max_workers=20) as pool:
        return [row for group in pool.map(worker, range(20)) for row in group]


def summarize(rows: list[dict[str, Any]], seconds: int) -> dict[str, Any]:
    """分位値と予期しない応答をAPI別に分ける。"""
    output: dict[str, Any] = {}
    for api in ["schedule", "mine", "create", "cancel"]:
        values = [r for r in rows if r["api"] == api]
        times = sorted(r["ms"] for r in values)

        def percentile(q: float, times: list[float] = times) -> float | None:
            return (
                round(times[min(len(times) - 1, int((len(times) - 1) * q))], 2) if times else None
            )

        output[api] = {
            "count": len(values),
            "p50": percentile(0.5),
            "p95": percentile(0.95),
            "p99": percentile(0.99),
            "throughput": len(values) / seconds,
            "success": sum(200 <= r["status"] < 300 for r in values),
            "unexpected": sum(r["status"] == 0 or r["status"] >= 500 for r in values),
            "four_xx": sum(400 <= r["status"] < 500 for r in values),
        }
    return output


def main() -> None:
    """2分ウォームアップと5分測定を3回実行し、性能runだけを保存する。"""
    if os.environ.get("SLOT_PERF_DATABASE_URL"):
        os.environ["SLOT_DATABASE_URL"] = os.environ["SLOT_PERF_DATABASE_URL"]
        settings.cache_clear()
    print("性能データを準備", flush=True)
    resources = seed()
    runs: list[dict[str, Any]] = []
    for i in range(3):
        measure(resources, 120)
        results = measure(resources, 300)
        runs.append({"index": i + 1, "metrics": summarize(results, 300)})
        print("性能測定 " + str(i + 1) + " / 3 完了", flush=True)
    with connect() as connection:
        violation = connection.execute(
            "SELECT count(*) AS count FROM slotkeeper.reservations a JOIN slotkeeper.reservations b ON a.resource_id=b.resource_id AND a.id<b.id AND a.start_at<b.end_at AND a.end_at>b.start_at WHERE a.status='confirmed' AND b.status='confirmed' AND a.resource_id=ANY(%s)",
            (resources,),
        ).fetchone()
    output = {
        "revision": os.environ.get("SLOT_REVISION", "local-worktree"),
        "runId": os.environ.get("SLOT_RUN_ID", "local"),
        "generatedAt": datetime.now(UTC).isoformat(),
        "status": "measured",
        "scope": "performance-only",
        "seed": 20260925,
        "resources": 100,
        "users": 200,
        "reservations": 100000,
        "concurrency": 20,
        "limits": {"api_cpu": 1, "db_cpu": 1, "api_memory_gib": 2, "db_memory_gib": 2},
        "runtime_resource_measurement": "not-run: cgroupを跨ぐCPU・memory実測は未接続",
        "runs": runs,
        "integrity_violations": violation["count"] if violation else None,
    }
    folder = Path("artifacts")
    folder.mkdir(exist_ok=True)
    (folder / "performance.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n"
    )
    if not violation or violation["count"] != 0:
        raise SystemExit(1)
    for run in runs:
        for api, metrics in run["metrics"].items():
            if (
                metrics["p95"] is None
                or metrics["p95"] > (500 if api in ("schedule", "mine") else 800)
                or metrics["unexpected"] / max(metrics["count"], 1) >= 0.001
                or metrics["four_xx"] > 0
            ):
                raise SystemExit(1)


if __name__ == "__main__":
    main()
