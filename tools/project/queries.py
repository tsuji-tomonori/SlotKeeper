"""SQL正本から束縛引数型と投影結果を検査するquery関数を生成する。"""

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def generate() -> dict[Path, str]:
    """所有operation単位でSQLと型の対応を生成する。"""
    outputs: dict[Path, str] = {}
    for folder in sorted((ROOT / "backend/src/slotkeeper/operations").iterdir()):
        if not (folder / "sql").is_dir():
            continue
        lines = [
            '"""SQL正本から自動生成した型付きquery。直接編集しない。"""',
            "from datetime import datetime",
            "from pathlib import Path",
            "from pydantic import BaseModel, ConfigDict",
            "from psycopg import sql",
            "from slotkeeper.db import Connection",
            "from slotkeeper.domain import Resource, Reservation, Event",
            "from slotkeeper.query_models import Count, Record",
            "",
        ]
        for path in sorted((folder / "sql").glob("*.sql")):
            source = path.read_text()
            header = source.splitlines()
            params = header[1].removeprefix("-- params: ").split(", ")
            result = header[2].removeprefix("-- result: ")
            if {p.split(":")[0] for p in params} != set(re.findall(r"%\((\w+)\)s", source)):
                raise ValueError(f"束縛引数不一致: {path}")
            cls = "".join(p.title() for p in path.stem.split("_")) + "Params"
            lines += [
                f"class {cls}(BaseModel):",
                '    model_config = ConfigDict(extra="forbid", strict=True)',
            ]
            lines += ["    " + p.replace(":", ": ") for p in params]
            lines += [
                "",
                f"def {path.stem}(connection: Connection, params: {cls}) -> "
                + ("None:" if result == "none" else f"list[{result}]:"),
                '    """' + header[0].removeprefix("-- ") + '"""',
                f'    statement = Path(__file__).with_name("sql").joinpath("{path.name}").read_text()',
                (
                    "    connection.execute(statement.encode(), params.model_dump())"
                    if result == "none"
                    else "    cursor = connection.execute(statement.encode(), params.model_dump())"
                ),
            ]
            lines += [
                "    return None"
                if result == "none"
                else f"    return [{result}.model_validate(row) for row in cursor.fetchall()]",
                "",
            ]
        # import整理も決定的な生成工程に含む。
        import subprocess

        source_text = "\n".join(lines)
        result_process = subprocess.run(
            [
                "ruff",
                "check",
                "--select",
                "I,F401",
                "--fix",
                "--stdin-filename",
                str(folder / "queries.py"),
                "-",
            ],
            input=source_text,
            text=True,
            capture_output=True,
            check=True,
        )
        formatted = subprocess.run(
            ["ruff", "format", "--stdin-filename", str(folder / "queries.py"), "-"],
            input=result_process.stdout,
            text=True,
            capture_output=True,
            check=True,
        )
        outputs[folder / "queries.py"] = formatted.stdout
    return outputs


def main() -> None:
    """checkでは既存ファイルを変更しない。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for path, content in generate().items():
        if args.check:
            if not path.exists() or path.read_text() != content:
                raise SystemExit(f"型付きSQLのdrift: {path.relative_to(ROOT)}")
        else:
            path.write_text(content)


if __name__ == "__main__":
    main()
