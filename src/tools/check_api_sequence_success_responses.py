from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

SUCCESS_RESPONSE_PATTERN = re.compile(r"API-->>User:\s+HTTP\s+2\d\d\b")
NORMAL_ACTION_PATTERN = re.compile(r"API->>(?:API|DB|R_[A-Za-z0-9_]+):")
ERROR_RESPONSE_PATTERN = re.compile(r"API-->>User:\s+HTTP\s+[45]\d\d\b")
ALT_START_PATTERN = re.compile(r"^\s*alt\b")
BLOCK_END_PATTERN = re.compile(r"^\s*end\s*$")


def error_branch_lines(lines: list[str]) -> set[int]:
    """エラー応答だけで終わるalt block内の行番号を返す。"""
    stack: list[int] = []
    error_lines: set[int] = set()
    for index, line in enumerate(lines, start=1):
        if ALT_START_PATTERN.match(line):
            stack.append(index)
        elif BLOCK_END_PATTERN.match(line) and stack:
            start = stack.pop()
            block = lines[start - 1 : index]
            if any(ERROR_RESPONSE_PATTERN.search(item) for item in block) and not any(
                SUCCESS_RESPONSE_PATTERN.search(item) for item in block
            ):
                error_lines.update(range(start, index + 1))
    return error_lines


@dataclass(frozen=True, order=True)
class ApiSequenceSuccessResponseIssue:
    path: Path
    message: str


def check_api_sequence_success_responses(
    docs_root: Path = Path("docs/spec/40.apis"),
) -> list[ApiSequenceSuccessResponseIssue]:
    issues: list[ApiSequenceSuccessResponseIssue] = []
    for path in sorted(docs_root.glob("*/*/sequence_gen.md")):
        lines = path.read_text(encoding="utf-8").splitlines()
        success_lines = [
            index
            for index, line in enumerate(lines, start=1)
            if SUCCESS_RESPONSE_PATTERN.search(line)
        ]
        if not success_lines:
            issues.append(
                ApiSequenceSuccessResponseIssue(
                    path=path,
                    message="sequence must include a successful 2xx response",
                )
            )
            continue
        excluded = error_branch_lines(lines)
        action_lines = [
            index
            for index, line in enumerate(lines, start=1)
            if NORMAL_ACTION_PATTERN.search(line) and index not in excluded
        ]
        if action_lines and max(success_lines) <= max(action_lines):
            issues.append(
                ApiSequenceSuccessResponseIssue(
                    path=path,
                    message="successful 2xx response must be rendered after normal processing",
                )
            )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check generated API sequences include successful 2xx responses."
    )
    parser.add_argument("--docs-root", type=Path, default=Path("docs/spec/40.apis"))
    args = parser.parse_args()

    issues = check_api_sequence_success_responses(args.docs_root)
    if not issues:
        print("All generated API sequences include successful 2xx responses.")
        return 0

    for issue in issues:
        print(f"{issue.path}: {issue.message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
