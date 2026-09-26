"""同一runの原本だけを公開用に変換し、allowlistを組み立てる。"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "artifacts"


def match(
    inventory: list[dict[str, Any]], results: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """結果がないcaseは未実行、collector外の結果は混入として拒否する。"""
    ids = [i["id"] for i in inventory]
    if len(ids) != len(set(ids)) or set(results) - set(ids):
        raise ValueError("collectorのID集合不一致")
    return [{**i, **results.get(i["id"], {"status": "not-run"})} for i in inventory]


def build(revision: str, run_id: str, checks: list[dict[str, Any]], scope: str) -> None:
    """新しい公開rootへ同一runの結果と許可した画像だけを書き出す。"""
    public = ART / "public"
    if public.exists():
        shutil.rmtree(public)
    public.mkdir(parents=True)
    tests: list[dict[str, Any]] = []
    for path in sorted(ART.glob("pytest-*-results.json")):
        data = json.loads(path.read_text())
        if data["revision"] != revision or data["runId"] != run_id:
            raise ValueError("異なるrevision/runの結果: " + path.name)
        tests += match(data["inventory"], data["results"])
    vitest = ART / "vitest.json"
    if vitest.exists():
        data = json.loads(vitest.read_text())
        for suite in data.get("testResults", []):
            for case in suite.get("assertionResults", []):
                tests.append(
                    {
                        "id": "vitest::" + case["fullName"],
                        "status": {"pending": "skipped", "todo": "not-run"}.get(
                            case["status"], case["status"]
                        ),
                        "duration": (case.get("duration") or 0) / 1000,
                    }
                )
    for name in ["playwright", "portal"]:
        path = ART / (name + ".json")
        if not path.exists():
            continue
        data = json.loads(path.read_text())

        def visit(suites: list[dict[str, Any]], name: str = name) -> None:
            for suite in suites:
                for spec in suite.get("specs", []):
                    for test in spec.get("tests", []):
                        results = test.get("results", [])
                        status = test.get("status", "not-run")
                        status = {
                            "expected": "passed",
                            "unexpected": "failed",
                            "skipped": "skipped",
                            "flaky": "flaky",
                        }.get(status, "not-run")
                        steps: list[dict[str, str]] = []
                        for result in results:
                            for attachment in result.get("attachments", []):
                                source = Path(attachment.get("path", ""))
                                if (
                                    attachment.get("name") in ("Given", "When", "Then")
                                    and source.is_file()
                                    and source.suffix == ".png"
                                ):
                                    destination = (
                                        "screenshots/"
                                        + hashlib.sha256(source.read_bytes()).hexdigest()
                                        + ".png"
                                    )
                                    (public / "screenshots").mkdir(exist_ok=True)
                                    shutil.copyfile(source, public / destination)
                                    steps.append(
                                        {
                                            "phase": attachment["name"],
                                            "text": spec["title"],
                                            "image": destination,
                                        }
                                    )
                        tests.append(
                            {
                                "id": name
                                + "::"
                                + test.get("projectName", "")
                                + "::"
                                + spec["title"],
                                "status": status,
                                "duration": sum(r.get("duration", 0) for r in results) / 1000,
                                "steps": steps,
                            }
                        )
                visit(suite.get("suites", []))

        visit(data.get("suites", []))
    coverage: list[dict[str, Any]] = []
    scopes = {
        "backend": "手書き業務コード backend/src/slotkeeper。除外: 生成した型付きSQL"
        "（operations/*/queries.py）とテストコード",
        "infra": "CDK定義 infra。除外: テストコード",
        "adapter": "設計生成・証跡変換 tools/project。除外: テストコード",
        "frontend": "画面の業務ロジック frontend/src/logic.ts。除外: 生成したOpenAPI型、"
        "React描画（E2Eで検証）",
    }
    for name in ["backend", "infra", "adapter"]:
        file = ART / (name + "-coverage.json")
        if file.exists():
            totals = json.loads(file.read_text())["totals"]
            for label, covered, total in [
                ("lines", "covered_lines", "num_statements"),
                ("branches", "covered_branches", "num_branches"),
            ]:
                # 目標値は手書き業務コードだけに適用し、infra・adapterは計測値を別表示する。
                goal = 0.90 if label == "branches" else 0.95
                measured = totals.get(total, 0) > 0
                coverage.append(
                    {
                        "name": name + " / " + label,
                        "scope": scopes[name],
                        "status": ("measured" if measured else "missing")
                        if name != "backend"
                        else "passed"
                        if measured and totals.get(covered, 0) / totals[total] >= goal
                        else "failed",
                        "covered": totals.get(covered, 0),
                        "total": totals.get(total, 0),
                    }
                )
        else:
            coverage.append({"name": name, "status": "missing", "scope": scopes[name]})
    summary = ART / "frontend-coverage/coverage-summary.json"
    if summary.exists():
        data = json.loads(summary.read_text())["total"]
        for metric in ["statements", "branches", "lines"]:
            covered, total = data[metric]["covered"], data[metric]["total"]
            coverage.append(
                {
                    "name": "frontend / " + metric,
                    "scope": scopes["frontend"],
                    "status": "passed"
                    if total > 0 and covered / total >= (0.90 if metric == "branches" else 0.95)
                    else "failed",
                    "covered": data[metric]["covered"],
                    "total": data[metric]["total"],
                }
            )
    else:
        coverage.append({"name": "frontend", "status": "missing", "scope": scopes["frontend"]})
    performance = {"status": "not-run", "reason": "性能profileは今回のrunでは実行していない。"}
    perf_file = ART / "performance.json"
    if perf_file.exists():
        measured = json.loads(perf_file.read_text())
        if measured["revision"] != revision or measured["runId"] != run_id:
            raise ValueError("性能結果のrevision/run不一致")
        performance = measured
    cloud: dict[str, Any] = {
        "status": "not-run",
        "reason": "AWS account・role未指定。synthと実AWS検証を区別する。",
    }
    cloud_file = ART / "cloud.json"
    if cloud_file.exists():
        measured = json.loads(cloud_file.read_text())
        if measured.get("revision") != revision or measured.get("runId") != run_id:
            raise ValueError("実AWS結果のrevision/run不一致")
        cloud = measured
    evidence = {
        "revision": revision,
        "runId": run_id,
        "scope": scope,
        "generatedAt": datetime.now(UTC).isoformat(),
        "checks": checks,
        "tests": tests,
        "coverage": coverage,
        "performance": performance,
        "cloud": cloud,
    }
    (public / "evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    search: list[dict[str, str]] = []
    for file in sorted((ROOT / "docs/design/generated").rglob("*.md")):
        relative = file.relative_to(ROOT / "docs/design/generated").with_suffix("").as_posix()
        search.append(
            {
                "title": relative.replace("/", " → "),
                "path": "/design/" + relative + "/",
                "text": file.read_text(),
            }
        )
    portal_public = ROOT / "portal/public"
    if portal_public.exists():
        shutil.rmtree(portal_public)
    shutil.copytree(public, portal_public)
    (portal_public / "search.json").write_text(json.dumps(search, ensure_ascii=False) + "\n")


def verify_site() -> None:
    """公開ファイル集合とhashを記録し、生ログやtoken保存物を拒否する。"""
    site = ART / "site"
    if not (site / "index.html").exists():
        raise ValueError("ポータル未生成")
    allowed = {".html", ".css", ".js", ".json", ".png", ".svg", ".woff2"}
    files: dict[str, str] = {}
    for path in sorted(site.rglob("*")):
        if path.is_symlink():
            raise ValueError("symlinkは公開しない")
        if not path.is_file():
            continue
        if path.suffix not in allowed:
            raise ValueError("allowlist外: " + path.name)
        files[path.relative_to(site).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    (site / "provenance.json").write_text(json.dumps(files, indent=2) + "\n")
    (ART / "site-ready").write_text("ready\n")
