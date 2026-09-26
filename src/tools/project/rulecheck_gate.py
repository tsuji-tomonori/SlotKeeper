"""lazunexのrulecheckを実行し、既知の継承負債を超える違反だけを失敗にする。"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASELINE = ROOT / "config/rulecheck_baseline.json"
FAIL_LINE = re.compile(
    r"^\[FAIL\] (?P<checker>\S+) (?P<rule>\S+) (?P<target>\S+) - (?P<message>.+)$"
)


def failures(output: str) -> set[str]:
    """行番号を除いたchecker・rule・path・内容をkeyにする。"""
    keys: set[str] = set()
    for line in output.splitlines():
        match = FAIL_LINE.match(line)
        if match is None:
            continue
        path = match.group("target").split(":", 1)[0]
        keys.add(
            " ".join((match.group("checker"), match.group("rule"), path, match.group("message")))
        )
    return keys


def run_rulecheck() -> str:
    """lazunexと同じ引数でMUST規約を検査する。"""
    completed = subprocess.run(  # noqa: S603
        [
            sys.executable,
            "-m",
            "tools.rulecheck",
            "check",
            "--repo-root",
            ".",
            "--rules-dir",
            "docs/rule/coding",
            "--config",
            "config/rulecheck_config.example.json",
            "--must-only",
        ],
        cwd=ROOT,
        env={"PYTHONPATH": str(ROOT / "src")},
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.stdout + completed.stderr


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--update-baseline", action="store_true")
    args = parser.parse_args()
    current = failures(run_rulecheck())
    if args.update_baseline:
        BASELINE.write_text(
            json.dumps(
                {
                    "description": (
                        "lazunex rulecheckのMUST違反のうち、lazunexから継承したtoolsと、"
                        "router.pyへ処理順を明示する規約と数値閾値が衝突する既知の違反。"
                        "新規違反は許可しない。解消した項目は削除する。"
                    ),
                    "failures": sorted(current),
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return 0
    baseline = set(json.loads(BASELINE.read_text(encoding="utf-8"))["failures"])
    new = sorted(current - baseline)
    fixed = sorted(baseline - current)
    for key in new:
        print("NEW " + key)
    for key in fixed:
        print("FIXED(baselineから削除する) " + key)
    print(f"rulecheck: current={len(current)} baseline={len(baseline)} new={len(new)}")
    return 1 if new or fixed else 0


if __name__ == "__main__":
    raise SystemExit(main())
