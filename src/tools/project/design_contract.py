"""共通設計契約のCRUD図に、repository所有の和名マトリクスを接続する。"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from tools.project import design


def common_projection(
    root: Path, data: dict[str, Any], output: dict[str, bytes]
) -> dict[str, bytes]:
    """実マトリクスを検査後、共通検査器へ渡す図だけを同一モデルの標準射影にする。

    共通検査器はMermaidのbyte一致を要求するため、図の表示契約だけをここで適応する。
    fileは変更せず、モデル検証・他帳票の照合・根拠検査・二重生成は共通検査器に委ねる。
    summaryは検査対象rootのOpenAPIを使い、生成drift検査で実sourceとの一致を保証する。
    """
    config = data["crud"]
    model = json.loads(output[config["model"]])
    rendered = design.common_crud_renderings(model)
    openapi_path = f"{data['api']['root']}/openapi.json"
    if openapi_path not in output:
        raise ValueError("CRUDのAPI和名には所有出力のOpenAPIが必要")
    summaries = design.crud_summaries(json.loads(output[openapi_path]))
    expected = design.crud_diagram(model, summaries).encode()
    if output[config["diagram"]] != expected:
        raise ValueError(f"CRUD diagram differs from API/table matrix: {root / config['diagram']}")
    return {**output, config["diagram"]: rendered["diagram"]}


def check(root: Path, contract: str) -> dict[str, Any]:
    """図の形式だけを適応し、共通契約の全検査を実行する。"""
    module = design.load_design_checker()
    validate: Callable[[Path, dict[str, Any], dict[str, bytes]], None] = module.__dict__[
        "validate_outputs"
    ]

    def validate_outputs(work: Path, data: dict[str, Any], output: dict[str, bytes]) -> None:
        validate(work, data, common_projection(work, data, output))

    module.__dict__["validate_outputs"] = validate_outputs
    run: Callable[[Path, str], dict[str, Any]] = module.__dict__["check"]
    return run(root, contract)


def main(argv: Sequence[str] | None = None) -> int:
    """repositoryのdesign-contract検査入口。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--contract", default=".dev-standard/design.json")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(check(args.root, args.contract), ensure_ascii=False, sort_keys=True))
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"as-built incomplete: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
