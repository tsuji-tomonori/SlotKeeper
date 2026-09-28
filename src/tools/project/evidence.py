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
DESIGN_ROOT = ROOT / "docs/spec"
PLAYWRIGHT_STATUS = {
    "expected": "passed",
    "unexpected": "failed",
    "skipped": "skipped",
    "flaky": "flaky",
}
VITEST_STATUS = {"pending": "skipped", "todo": "not-run"}
GWT_PHASES = ("Given", "When", "Then")
COVERAGE_SCOPES = {
    "backend": (
        "手書き業務コード src/app。除外: 生成した型付きSQL（apis/*/*/generated）とテストコード"
    ),
    "infra": "CDK定義 infra。除外: テストコード",
    "adapter": "lazunex由来の生成器・検査器と証跡変換 src/tools。除外: テストコード",
    "frontend": "画面の業務ロジック frontend/src/logic.ts。除外: 生成したOpenAPI型、"
    "React描画（E2Eで検証）",
}
# 目標値は手書き業務コードだけに適用し、infra・adapterは計測値を別表示する。
COVERAGE_GOALS = {"lines": 0.95, "statements": 0.95, "branches": 0.90}
PYTHON_COVERAGE_METRICS = (
    ("lines", "covered_lines", "num_statements"),
    ("branches", "covered_branches", "num_branches"),
)
NOT_RUN_PERFORMANCE = {"status": "not-run", "reason": "性能profileは今回のrunでは実行していない。"}
NOT_RUN_CLOUD = {
    "status": "not-run",
    "reason": "AWS account・role未指定。synthと実AWS検証を区別する。",
}


def match(
    inventory: list[dict[str, Any]], results: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """結果がないcaseは未実行、collector外の結果は混入として拒否する。"""
    ids = [item["id"] for item in inventory]
    if len(ids) != len(set(ids)) or set(results) - set(ids):
        raise ValueError("collectorのID集合不一致")
    return [{**item, **results.get(item["id"], {"status": "not-run"})} for item in inventory]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def pytest_tests(revision: str, run_id: str) -> list[dict[str, Any]]:
    tests: list[dict[str, Any]] = []
    for path in sorted(ART.glob("pytest-*-results.json")):
        data = read_json(path)
        if data["revision"] != revision or data["runId"] != run_id:
            raise ValueError("異なるrevision/runの結果: " + path.name)
        tests += match(data["inventory"], data["results"])
    return tests


def vitest_tests() -> list[dict[str, Any]]:
    path = ART / "vitest.json"
    if not path.exists():
        return []
    return [
        {
            "id": "vitest::" + case["fullName"],
            "status": VITEST_STATUS.get(case["status"], case["status"]),
            "duration": (case.get("duration") or 0) / 1000,
        }
        for suite in read_json(path).get("testResults", [])
        for case in suite.get("assertionResults", [])
    ]


def publish_screenshot(attachment: dict[str, Any], public: Path) -> str | None:
    """Given/When/ThenのPNGだけを内容hash名で公開rootへ複製する。"""
    source = Path(attachment.get("path", ""))
    if attachment.get("name") not in GWT_PHASES:
        return None
    if not source.is_file() or source.suffix != ".png":
        return None
    destination = "screenshots/" + hashlib.sha256(source.read_bytes()).hexdigest() + ".png"
    (public / "screenshots").mkdir(exist_ok=True)
    shutil.copyfile(source, public / destination)
    return destination


def playwright_case(
    kind: str, spec: dict[str, Any], test: dict[str, Any], public: Path
) -> dict[str, Any]:
    results = test.get("results", [])
    steps = [
        {"phase": attachment["name"], "text": spec["title"], "image": image}
        for result in results
        for attachment in result.get("attachments", [])
        for image in [publish_screenshot(attachment, public)]
        if image is not None
    ]
    return {
        "id": f"{kind}::{test.get('projectName', '')}::{spec['title']}",
        "status": PLAYWRIGHT_STATUS.get(test.get("status", "not-run"), "not-run"),
        "duration": sum(result.get("duration", 0) for result in results) / 1000,
        "steps": steps,
    }


def playwright_suite_cases(
    kind: str, suites: list[dict[str, Any]], public: Path
) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for suite in suites:
        cases += [
            playwright_case(kind, spec, test, public)
            for spec in suite.get("specs", [])
            for test in spec.get("tests", [])
        ]
        cases += playwright_suite_cases(kind, suite.get("suites", []), public)
    return cases


def playwright_tests(public: Path) -> list[dict[str, Any]]:
    tests: list[dict[str, Any]] = []
    for kind in ("playwright", "portal"):
        path = ART / (kind + ".json")
        if path.exists():
            tests += playwright_suite_cases(kind, read_json(path).get("suites", []), public)
    return tests


def python_coverage(name: str) -> list[dict[str, Any]]:
    path = ART / (name + "-coverage.json")
    if not path.exists():
        return [{"name": name, "status": "missing", "scope": COVERAGE_SCOPES[name]}]
    totals = read_json(path)["totals"]
    rows: list[dict[str, Any]] = []
    for label, covered_key, total_key in PYTHON_COVERAGE_METRICS:
        covered, total = totals.get(covered_key, 0), totals.get(total_key, 0)
        if name != "backend":
            status = "measured" if total > 0 else "missing"
        else:
            status = (
                "passed" if total > 0 and covered / total >= COVERAGE_GOALS[label] else "failed"
            )
        rows.append(
            {
                "name": f"{name} / {label}",
                "scope": COVERAGE_SCOPES[name],
                "status": status,
                "covered": covered,
                "total": total,
            }
        )
    return rows


def frontend_coverage() -> list[dict[str, Any]]:
    summary = ART / "frontend-coverage/coverage-summary.json"
    if not summary.exists():
        return [{"name": "frontend", "status": "missing", "scope": COVERAGE_SCOPES["frontend"]}]
    data = read_json(summary)["total"]
    rows: list[dict[str, Any]] = []
    for metric in ("statements", "branches", "lines"):
        covered, total = data[metric]["covered"], data[metric]["total"]
        passed = total > 0 and covered / total >= COVERAGE_GOALS[metric]
        rows.append(
            {
                "name": "frontend / " + metric,
                "scope": COVERAGE_SCOPES["frontend"],
                "status": "passed" if passed else "failed",
                "covered": covered,
                "total": total,
            }
        )
    return rows


def same_run_result(
    name: str, revision: str, run_id: str, default: dict[str, Any]
) -> dict[str, Any]:
    """性能・実AWSの結果は同じrevision・runのものだけを採用する。"""
    path = ART / name
    if not path.exists():
        return default
    measured: dict[str, Any] = read_json(path)
    if measured.get("revision") != revision or measured.get("runId") != run_id:
        raise ValueError(f"{name}のrevision/run不一致")
    return measured


def design_search_index() -> list[dict[str, str]]:
    """lazunex形式の設計Markdownをポータル検索用に列挙する。"""
    return [
        {
            "title": relative.replace("/", " → "),
            "path": "/design/" + relative + "/",
            "text": file.read_text(encoding="utf-8"),
        }
        for file in sorted(DESIGN_ROOT.rglob("*.md"))
        for relative in [file.relative_to(DESIGN_ROOT).with_suffix("").as_posix()]
    ]


def build(revision: str, run_id: str, checks: list[dict[str, Any]], scope: str) -> None:
    """新しい公開rootへ同一runの結果と許可した画像だけを書き出す。"""
    public = ART / "public"
    if public.exists():
        shutil.rmtree(public)
    public.mkdir(parents=True)
    tests = pytest_tests(revision, run_id) + vitest_tests() + playwright_tests(public)
    coverage = [
        *(row for name in ("backend", "infra", "adapter") for row in python_coverage(name)),
        *frontend_coverage(),
    ]
    evidence = {
        "revision": revision,
        "runId": run_id,
        "scope": scope,
        "generatedAt": datetime.now(UTC).isoformat(),
        "checks": checks,
        "tests": tests,
        "coverage": coverage,
        "performance": same_run_result("performance.json", revision, run_id, NOT_RUN_PERFORMANCE),
        "cloud": same_run_result("cloud.json", revision, run_id, NOT_RUN_CLOUD),
    }
    (public / "evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    portal_public = ROOT / "portal/public"
    if portal_public.exists():
        shutil.rmtree(portal_public)
    shutil.copytree(public, portal_public)
    (portal_public / "search.json").write_text(
        json.dumps(design_search_index(), ensure_ascii=False) + "\n"
    )


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
