"""Compose内で全検査を収集し、失敗ポータルを作ってから非0で終了する。"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.project import evidence

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "artifacts"
PY = sys.executable
CHECK_DESIGN = ".agents/skills/generate-implementation-design/scripts/check_design.py"
RULECHECK_ARGS = [
    "--repo-root",
    ".",
    "--rules-dir",
    "docs/rule/coding",
    "--checklist",
    "docs/rule/coding/12_review_checklist.generated.md",
    "--config",
    "config/rulecheck_config.example.json",
]
STALE_ARTIFACTS = (
    "pytest-*-results.json",
    "*-coverage.json",
    "vitest.json",
    "playwright.json",
    "portal.json",
    "site-ready",
    "performance.json",
    "cloud.json",
)
STALE_FOLDERS = ("frontend-coverage", "site", "public", "e2e")
GENERATE_DESIGN = (
    [PY, "tools/quintflow.py", "generate"],
    ["app-codegen", "all"],
    [PY, "-m", "tools.project.package_lambda"],
    ["app-docs", "generate"],
    [PY, "-B", "src/tools/project/design.py", "--target", "all", "--manifest"],
    ["npm", "run", "types"],
)


@dataclass(frozen=True)
class Step:
    """1つの検査。collectorを持つpytestは同じrunの結果原本を残す。"""

    name: str
    command: tuple[str, ...]
    collector: str | None = None
    timeout: int = 600


def pytest_step(name: str, paths: Sequence[str], cov: str, *extra: str) -> Step:
    return Step(
        name,
        (
            "pytest",
            *paths,
            *extra,
            "-q",
            f"--junitxml=artifacts/{name}.xml",
            f"--cov={cov}",
            f"--cov-report=json:artifacts/{name}-coverage.json",
            "-p",
            "tools.project.collector",
        ),
        collector=f"artifacts/pytest-{name}-results.json",
    )


SUITES: dict[str, tuple[Step, ...]] = {
    "design": (
        Step("quint", (PY, "tools/quintflow.py", "check")),
        Step("codegen", ("app-codegen", "all", "--check")),
        Step("docs", ("app-docs", "generate", "--check")),
        Step("archlint", ("app-archlint", "all")),
        Step("rulecheck-checklist", (PY, "-m", "tools.rulecheck", "verify", *RULECHECK_ARGS)),
        Step("rulecheck", (PY, "-m", "tools.project.rulecheck_gate")),
        Step("design", (PY, "-B", "src/tools/project/design.py", "--manifest", "--check")),
        Step("design-contract", (PY, CHECK_DESIGN, "--root", ".")),
        pytest_step("adapter", ["tests/tools"], "src/tools"),
    ),
    "backend": (
        Step("ruff-format", ("ruff", "format", "--check", "src", "tests", "infra")),
        Step("ruff", ("ruff", "check", "src", "tests", "infra")),
        Step("mypy", ("mypy",)),
        Step("pyright", ("pyright",)),
        pytest_step(
            "backend", ["tests"], "src/app", "--ignore=tests/tools", "--ignore=tests/infra"
        ),
    ),
    "infra": (
        pytest_step("infra", ["tests/infra"], "infra"),
        *(
            Step(
                "synth-" + env,
                (
                    "npx",
                    "cdk",
                    "synth",
                    "--strict",
                    "-c",
                    "env=" + env,
                    "--output",
                    "artifacts/cdk.out/" + env,
                ),
            )
            for env in ("dev", "prod")
        ),
    ),
    "frontend": (
        Step("astro", ("npm", "run", "check")),
        Step("portal-types", ("npx", "astro", "check", "--root", "portal")),
        Step("openapi-types", ("node", "src/tools/frontend.mjs")),
        Step("eslint", ("npm", "run", "lint")),
        Step("format", ("npm", "run", "format")),
        Step("frontend-build", ("npm", "run", "build")),
        Step(
            "vitest",
            (
                "npx",
                "vitest",
                "run",
                "--coverage",
                "--reporter=json",
                "--outputFile=artifacts/vitest.json",
            ),
        ),
    ),
    "e2e": (Step("e2e", ("npx", "playwright", "test", "--config=e2e/playwright.config.ts")),),
}
PACKAGE = Step("package", (PY, "-m", "tools.project.package_lambda"))
PERFORMANCE = Step("performance", (PY, "-m", "tools.project.perf"), timeout=1800)


def run(step: Step, checks: list[dict[str, Any]]) -> bool:
    """個々の失敗やtimeoutを保存し後続の検査を止めない。"""
    print("検査: " + step.name, flush=True)
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    if step.collector is not None:
        env["SLOT_COLLECTOR"] = step.collector
    log = ART / (step.name + ".log")
    with log.open("w") as output:
        try:
            result = subprocess.run(  # noqa: S603
                step.command,
                cwd=ROOT,
                env=env,
                stdout=output,
                stderr=subprocess.STDOUT,
                timeout=step.timeout,
                check=False,
            )
            status = "passed" if result.returncode == 0 else "failed"
        except (subprocess.TimeoutExpired, OSError) as exc:
            output.write(str(exc))
            status = "failed"
    checks.append({"name": step.name, "command": " ".join(step.command), "status": status})
    print(step.name + ": " + status, flush=True)
    if status == "failed":
        print(log.read_text()[-3000:], flush=True)
    return status == "passed"


def reset_artifacts() -> None:
    """過去runの原本を今回の成功として取り込まない。"""
    ART.mkdir(exist_ok=True)
    for pattern in STALE_ARTIFACTS:
        for path in ART.glob(pattern):
            path.unlink()
    for folder in STALE_FOLDERS:
        if (ART / folder).exists():
            shutil.rmtree(ART / folder)


def run_scope(args: argparse.Namespace) -> str:
    if args.performance_only:
        return "performance-only"
    return "full" if args.suite is None else "partial: " + args.suite


def build_portal(args: argparse.Namespace, checks: list[dict[str, Any]], scope: str) -> None:
    """同一runの結果から公開ポータルを作り、portal suite選択時はE2E後に再構築する。"""
    revision = os.environ.get("SLOT_REVISION", "local-worktree")
    run_id = os.environ.get("SLOT_RUN_ID", "local")
    evidence.build(revision, run_id, checks, scope)
    portal = Step("portal-build", ("npm", "run", "portal"))
    ready = run(portal, checks)
    if ready and not args.performance_only and args.suite in (None, "portal"):
        run(
            Step("portal-e2e", ("npx", "playwright", "test", "--config=e2e/portal.config.ts")),
            checks,
        )
        # テスト対象のbuild hashを保存。追記後はリンクと公開集合だけを確認する。
        evidence.verify_site()
        (ART / "tested-build-hashes.json").write_text((ART / "site/provenance.json").read_text())
        evidence.build(revision, run_id, checks, scope)
        ready = run(Step("portal-final", ("npm", "run", "portal")), checks)
    if ready:
        evidence.verify_site()


def main(argv: Sequence[str] | None = None) -> None:
    """生成更新と検査を分け、既存設計のdriftを先に検査する。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=[*SUITES, "portal"])
    parser.add_argument("--generate-design", action="store_true")
    parser.add_argument("--performance", action="store_true")
    parser.add_argument(
        "--performance-only",
        action="store_true",
        help="性能だけを測定し、同じrunの結果でポータルを更新する",
    )
    args = parser.parse_args(argv)
    if args.generate_design:
        for command in GENERATE_DESIGN:
            subprocess.run(command, cwd=ROOT, check=True)  # noqa: S603
        return
    reset_artifacts()
    checks: list[dict[str, Any]] = []
    if not args.performance_only:
        run(PACKAGE, checks)
        for suite, steps in SUITES.items():
            if args.suite in (None, suite):
                for step in steps:
                    run(step, checks)
    if args.performance or args.performance_only:
        run(PERFORMANCE, checks)
    build_portal(args, checks, run_scope(args))
    (ART / "checks.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2) + "\n")
    raise SystemExit(1 if any(check["status"] != "passed" for check in checks) else 0)


if __name__ == "__main__":
    main()
