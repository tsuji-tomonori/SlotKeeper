"""指定データ量と20並列でAPI別の実測値を収集する。"""

from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from random import Random
from time import monotonic, perf_counter
from typing import Any
from uuid import NAMESPACE_URL, uuid4, uuid5

import httpx

from app.core.config import Settings
from tools.project.migrate import connect

SEED = 20260925
RESOURCES = 100
USERS = 200
RESERVATIONS = 100_000
BATCH = 1000
WORKERS = 20
APIS = ("schedule", "mine", "create", "cancel")
READ_P95_LIMIT_MS = 500
WRITE_P95_LIMIT_MS = 800
PASSWORD = "Local-test-2026!"  # noqa: S105 - ローカルKeycloakの試験利用者だけに使う。


def synthetic_id(kind: str, index: int) -> str:
    return str(uuid5(NAMESPACE_URL, f"slotkeeper/perf/{kind}/{index}"))


def seed(config: Settings) -> list[str]:
    """既存データを消さず固定IDの合成資源100件と過去予約10万件を追加する。"""
    if config.environment != "local" or config.database_mode != "postgres":
        raise ValueError("性能seedはローカル専用")
    resources = [synthetic_id("resource", index) for index in range(RESOURCES)]
    base = datetime(2025, 1, 1, tzinfo=UTC)
    with connect(config) as connection:
        for index, resource_id in enumerate(resources):
            connection.execute(
                "INSERT INTO slotkeeper.resources"
                "(resource_id,name,description,kind,active,row_version,control_version) "
                "VALUES (%s,%s,%s,'room',true,1,0) ON CONFLICT(resource_id) DO NOTHING",
                (resource_id, f"性能試験 {index}", "合成データ"),
            )
        for index in range(USERS):
            connection.execute(
                "INSERT INTO slotkeeper.users(principal_id,first_seen_at) VALUES (%s,%s) "
                "ON CONFLICT(principal_id) DO NOTHING",
                (synthetic_id("user", index), base),
            )
    for batch in range(RESERVATIONS // BATCH):
        with connect(config) as connection:
            for number in range(batch * BATCH, (batch + 1) * BATCH):
                start = base + timedelta(minutes=(number // RESOURCES) * 15)
                connection.execute(
                    "INSERT INTO slotkeeper.reservations"
                    "(reservation_id,resource_id,owner_principal_id,start_at,end_at,purpose,"
                    "status,row_version) VALUES (%s,%s,%s,%s,%s,%s,'confirmed',1) "
                    "ON CONFLICT(reservation_id) DO NOTHING",
                    (
                        synthetic_id("reservation", number),
                        resources[number % RESOURCES],
                        synthetic_id("user", number % USERS),
                        start,
                        start + timedelta(minutes=15),
                        "性能用の合成予約",
                    ),
                )
    return resources


@dataclass(frozen=True)
class Call:
    api: str
    method: str
    path: str
    body: dict[str, Any] | None = None


def worker_token(client: httpx.Client, index: int) -> str:
    response = client.post(
        os.environ["SLOT_OIDC_INTERNAL"] + "/realms/slotkeeper/protocol/openid-connect/token",
        data={
            "grant_type": "password",
            "client_id": "slotkeeper",
            "username": f"perf{index}",
            "password": PASSWORD,
        },
    )
    response.raise_for_status()
    return str(response.json()["access_token"])


def next_call(random: Random, resource_id: str, day: str, start: datetime) -> Call:
    """参照80%・作成取消20%相当の操作を固定seedで選ぶ。"""
    mode = random.randrange(9)
    if mode < 4:
        return Call("schedule", "GET", f"/resources/{resource_id}/schedule?day={day}")
    if mode < 8:
        return Call("mine", "GET", "/reservations?future=false")
    return Call(
        "create",
        "POST",
        "/reservations",
        {
            "resourceId": resource_id,
            "startAt": start.isoformat(),
            "endAt": (start + timedelta(minutes=15)).isoformat(),
            "purpose": "性能測定",
        },
    )


def timed(client: httpx.Client, call: Call, headers: dict[str, str]) -> tuple[dict[str, Any], Any]:
    before = perf_counter()
    try:
        response = client.request(
            call.method,
            os.environ["SLOT_API_URL"] + call.path,
            headers={**headers, "Idempotency-Key": uuid4().hex},
            json=call.body,
        )
    except httpx.HTTPError:
        return {"api": call.api, "ms": (perf_counter() - before) * 1000, "status": 0}, None
    row = {"api": call.api, "ms": (perf_counter() - before) * 1000, "status": response.status_code}
    return row, response.json() if response.status_code == 201 else None


def worker(index: int, resources: list[str], deadline: float) -> list[dict[str, Any]]:
    """各workerが別資源を使い、競合試験と速度試験を分離する。"""
    rows: list[dict[str, Any]] = []
    with httpx.Client(timeout=15) as client:
        headers = {"Authorization": "Bearer " + worker_token(client, index)}
        day = datetime.now(UTC).date() + timedelta(days=7)
        start = datetime.combine(day, datetime.min.time(), UTC) + timedelta(hours=1)
        random = Random(SEED + index)  # noqa: S311 - 負荷の操作比率を再現する固定seed。
        while monotonic() < deadline:
            row, created = timed(
                client, next_call(random, resources[index], str(day), start), headers
            )
            rows.append(row)
            if created is not None:
                cancel = Call(
                    "cancel",
                    "POST",
                    f"/reservations/{created['reservationId']}/cancel",
                    {"version": created["version"]},
                )
                rows.append(timed(client, cancel, headers)[0])
    return rows


def measure(resources: list[str], seconds: int) -> list[dict[str, Any]]:
    deadline = monotonic() + seconds

    def run(index: int) -> list[dict[str, Any]]:
        return worker(index, resources, deadline)

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        return [row for group in pool.map(run, range(WORKERS)) for row in group]


def percentile(times: list[float], quantile: float) -> float | None:
    if not times:
        return None
    return round(times[min(len(times) - 1, int((len(times) - 1) * quantile))], 2)


def summarize(rows: list[dict[str, Any]], seconds: int) -> dict[str, Any]:
    """分位値と予期しない応答をAPI別に分ける。"""
    output: dict[str, Any] = {}
    for api in APIS:
        values = [row for row in rows if row["api"] == api]
        times = sorted(row["ms"] for row in values)
        output[api] = {
            "count": len(values),
            "p50": percentile(times, 0.5),
            "p95": percentile(times, 0.95),
            "p99": percentile(times, 0.99),
            "throughput": len(values) / seconds,
            "success": sum(200 <= row["status"] < 300 for row in values),
            "unexpected": sum(row["status"] == 0 or row["status"] >= 500 for row in values),
            "four_xx": sum(400 <= row["status"] < 500 for row in values),
        }
    return output


def integrity_violations(config: Settings, resources: list[str]) -> int | None:
    """同一資源のconfirmed予約が重なっていないことを性能run後に確認する。"""
    with connect(config) as connection:
        row = connection.execute(
            "SELECT count(*) AS count FROM slotkeeper.reservations a "
            "JOIN slotkeeper.reservations b ON a.resource_id=b.resource_id "
            "AND a.reservation_id<b.reservation_id "
            "AND a.start_at<b.end_at AND a.end_at>b.start_at "
            "WHERE a.status='confirmed' AND b.status='confirmed' AND a.resource_id=ANY(%s)",
            (resources,),
        ).fetchone()
    return int(row["count"]) if row else None


def within_limits(api: str, metrics: dict[str, Any]) -> bool:
    limit = READ_P95_LIMIT_MS if api in ("schedule", "mine") else WRITE_P95_LIMIT_MS
    return (
        metrics["p95"] is not None
        and metrics["p95"] <= limit
        and metrics["unexpected"] / max(metrics["count"], 1) < 0.001
        and metrics["four_xx"] == 0
    )


def main() -> None:
    """2分ウォームアップと5分測定を3回実行し、性能runだけを保存する。"""
    url = os.environ.get("SLOT_PERF_DATABASE_URL")
    config = Settings(database_url=url) if url else Settings()
    print("性能データを準備", flush=True)
    resources = seed(config)
    runs: list[dict[str, Any]] = []
    for index in range(3):
        measure(resources, 120)
        runs.append({"index": index + 1, "metrics": summarize(measure(resources, 300), 300)})
        print(f"性能測定 {index + 1} / 3 完了", flush=True)
    violations = integrity_violations(config, resources)
    output = {
        "revision": os.environ.get("SLOT_REVISION", "local-worktree"),
        "runId": os.environ.get("SLOT_RUN_ID", "local"),
        "generatedAt": datetime.now(UTC).isoformat(),
        "status": "measured",
        "scope": "performance-only",
        "seed": SEED,
        "resources": RESOURCES,
        "users": USERS,
        "reservations": RESERVATIONS,
        "concurrency": WORKERS,
        "limits": {"api_cpu": 1, "db_cpu": 1, "api_memory_gib": 2, "db_memory_gib": 2},
        "runtime_resource_measurement": "not-run: cgroupを跨ぐCPU・memory実測は未接続",
        "runs": runs,
        "integrity_violations": violations,
    }
    folder = Path("artifacts")
    folder.mkdir(exist_ok=True)
    (folder / "performance.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n"
    )
    passed = violations == 0 and all(
        within_limits(api, metrics) for run in runs for api, metrics in run["metrics"].items()
    )
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
