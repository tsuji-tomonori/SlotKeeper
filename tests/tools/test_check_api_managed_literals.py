from __future__ import annotations

from pathlib import Path

import pytest

from tools.check_api_managed_literals import (
    ManagedLiteralIssue,
    build_arg_parser,
    check_api_managed_literal_roots,
    check_api_managed_literals,
    main,
    render_issues,
)


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_check_api_managed_literals_reports_disallowed_literals(tmp_path: Path) -> None:
    api_root = tmp_path / "apis"
    write_file(
        api_root / "reservations" / "get_reservation" / "functions.py",
        '''
async def get_reservation_detail() -> object:
    """confirmed in docstring is allowed."""
    return "confirmed", "cancelled", "admin", "room", "equipment", "created"
''',
    )
    write_file(
        api_root / "common.py",
        """
from enum import StrEnum


class IdentityGroup(StrEnum):
    ADMIN = "admin"
""",
    )
    write_file(
        api_root / "resources" / "common.py",
        """
ROOM = "room"
EQUIPMENT = "equipment"
""",
    )
    write_file(
        api_root / "reservations" / "common.py",
        """
CONFIRMED = "confirmed"
CANCELLED = "cancelled"
CREATED = "created"
""",
    )
    write_file(
        api_root / "resources" / "create_resource" / "contract.py",
        """PERMISSIONS = ("admin",)\n""",
    )

    issues = check_api_managed_literals(api_root)

    assert [(issue.literal, issue.line) for issue in issues] == [
        ("admin", 4),
        ("cancelled", 4),
        ("confirmed", 4),
        ("created", 4),
        ("equipment", 4),
        ("room", 4),
    ]


def test_check_api_managed_literals_accepts_repository_usage() -> None:
    assert check_api_managed_literal_roots([Path("src/app/apis"), Path("tests/app/apis")]) == []


def test_render_issues_and_main(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    issue = ManagedLiteralIssue(
        path=Path("src/app/apis/reservations/get_reservation/functions.py"),
        line=10,
        literal="confirmed",
        message="managed literal must be referenced through a shared constant or enum",
    )
    assert "confirmed" in render_issues([issue])

    api_root = tmp_path / "apis"
    write_file(
        api_root / "reservations" / "get_reservation" / "functions.py",
        'VALUE = "confirmed"\n',
    )

    assert main(["--api-root", str(api_root)]) == 1
    assert "confirmed" in capsys.readouterr().out


def test_build_arg_parser_defaults() -> None:
    args = build_arg_parser().parse_args([])

    assert args.api_roots is None
