"""Compose内で全検査を収集し、失敗ポータルを作ってから非0で終了する。"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from tools.project import evidence

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts"


def run(name: str, command: list[str], checks: list[dict[str, Any]], timeout: int = 600) -> bool:
    """個々の失敗やtimeoutを保存し後続の検査を止めない。"""
    print("検査: " + name, flush=True)
    with (ART / (name + ".log")).open("w") as output:
        try:
            result = subprocess.run(
                command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT, timeout=timeout
            )
            status = "passed" if result.returncode == 0 else "failed"
        except (subprocess.TimeoutExpired, OSError) as exc:
            output.write(str(exc))
            status = "failed"
    checks.append({"name": name, "command": " ".join(command), "status": status})
    print(name + ": " + status, flush=True)
    if status == "failed":
        print((ART / (name + ".log")).read_text()[-3000:], flush=True)
    return status == "passed"


def main() -> None:
    """生成更新と検査を分け、既存設計のdriftを先に検査する。"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--suite", choices=["backend", "frontend", "infra", "e2e", "design", "portal"]
    )
    parser.add_argument("--generate-design", action="store_true")
    parser.add_argument("--performance", action="store_true")
    parser.add_argument(
        "--performance-only",
        action="store_true",
        help="性能だけを測定し、同じrunの結果でポータルを更新する",
    )
    args = parser.parse_args()
    if args.generate_design:
        for command in [
            [sys.executable, "tools/quintflow.py", "generate"],
            [sys.executable, "tools/project/queries.py"],
            [sys.executable, "-m", "tools.project.package_lambda"],
            [sys.executable, "tools/project/design.py", "--manifest"],
            ["npm", "run", "types"],
        ]:
            subprocess.run(command, cwd=ROOT, check=True)
        return
    ART.mkdir(exist_ok=True)
    # 過去runの原本を今回の成功として取り込まない。
    for pattern in [
        "pytest-*-results.json",
        "*-coverage.json",
        "vitest.json",
        "playwright.json",
        "portal.json",
        "site-ready",
        "performance.json",
        "cloud.json",
    ]:
        for path in ART.glob(pattern):
            path.unlink()
    for folder in ["frontend-coverage", "site", "public", "e2e"]:
        if (ART / folder).exists():
            shutil.rmtree(ART / folder)
    revision = os.environ.get("SLOT_REVISION", "local-worktree")
    run_id = os.environ.get("SLOT_RUN_ID", "local")
    checks: list[dict[str, Any]] = []

    def selected(s: str) -> bool:
        return not args.performance_only and (args.suite is None or args.suite == s)

    if not args.performance_only:
        run("package", [sys.executable, "-m", "tools.project.package_lambda"], checks)
    if selected("design"):
        run("quint", [sys.executable, "tools/quintflow.py", "check"], checks)
        run("queries", [sys.executable, "tools/project/queries.py", "--check"], checks)
        run("design", [sys.executable, "tools/project/design.py", "--check"], checks)
        run(
            "design-contract",
            [
                sys.executable,
                ".agents/skills/generate-implementation-design/scripts/check_design.py",
                "--root",
                ".",
            ],
            checks,
        )
        os.environ["SLOT_COLLECTOR"] = "artifacts/pytest-adapter-results.json"
        run(
            "adapter",
            [
                "pytest",
                "tools/tests",
                "-q",
                "--junitxml=artifacts/adapter.xml",
                "--cov=tools/project",
                "--cov-report=json:artifacts/adapter-coverage.json",
                "-p",
                "tools.project.collector",
            ],
            checks,
        )
    if selected("backend"):
        run("ruff", ["ruff", "check", "backend", "infra", "tools/project", "tools/tests"], checks)
        run("mypy", ["mypy"], checks)
        run("pyright", ["pyright"], checks)
        os.environ["SLOT_COLLECTOR"] = "artifacts/pytest-backend-results.json"
        run(
            "backend",
            [
                "pytest",
                "backend/tests",
                "-q",
                "--junitxml=artifacts/backend.xml",
                "--cov=slotkeeper",
                "--cov-report=json:artifacts/backend-coverage.json",
                "-p",
                "tools.project.collector",
            ],
            checks,
        )
    if selected("infra"):
        os.environ["SLOT_COLLECTOR"] = "artifacts/pytest-infra-results.json"
        run(
            "infra",
            [
                "pytest",
                "infra/tests",
                "-q",
                "--junitxml=artifacts/infra.xml",
                "--cov=infra",
                "--cov-report=json:artifacts/infra-coverage.json",
                "-p",
                "tools.project.collector",
            ],
            checks,
        )
        for env in ["dev", "prod"]:
            run(
                "synth-" + env,
                [
                    "npx",
                    "cdk",
                    "synth",
                    "--strict",
                    "-c",
                    "env=" + env,
                    "--output",
                    "artifacts/cdk.out/" + env,
                ],
                checks,
            )
    if selected("frontend"):
        for name, command in [
            ("astro", ["npm", "run", "check"]),
            ("portal-types", ["npx", "astro", "check", "--root", "portal"]),
            ("openapi-types", ["node", "tools/frontend.mjs"]),
            ("eslint", ["npm", "run", "lint"]),
            ("format", ["npm", "run", "format"]),
            ("frontend-build", ["npm", "run", "build"]),
            (
                "vitest",
                [
                    "npx",
                    "vitest",
                    "run",
                    "--coverage",
                    "--reporter=json",
                    "--outputFile=artifacts/vitest.json",
                ],
            ),
        ]:
            run(name, command, checks)
    if selected("e2e"):
        run("e2e", ["npx", "playwright", "test", "--config=e2e/playwright.config.ts"], checks)
    if args.performance or args.performance_only:
        run("performance", [sys.executable, "-m", "tools.project.perf"], checks, timeout=1800)
    scope = (
        "performance-only"
        if args.performance_only
        else "full"
        if args.suite is None
        else "partial: " + args.suite
    )
    evidence.build(revision, run_id, checks, scope)
    ready = run("portal-build", ["npm", "run", "portal"], checks)
    if ready and selected("portal"):
        run("portal-e2e", ["npx", "playwright", "test", "--config=e2e/portal.config.ts"], checks)
        # テスト対象のbuild hashを保存。追記後はリンクと公開集合だけを確認する。
        evidence.verify_site()
        tested_hash = (ART / "site/provenance.json").read_text()
        (ART / "tested-build-hashes.json").write_text(tested_hash)
        evidence.build(revision, run_id, checks, scope)
        ready = run("portal-final", ["npm", "run", "portal"], checks)
    if ready:
        evidence.verify_site()
    (ART / "checks.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2) + "\n")
    raise SystemExit(1 if any(c["status"] != "passed" for c in checks) else 0)


if __name__ == "__main__":
    main()
