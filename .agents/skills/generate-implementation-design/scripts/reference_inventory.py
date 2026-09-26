#!/usr/bin/env python3
"""参照実装の固定版・全件一覧を検査し、人向け一覧を決定的に生成する。"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "assets"


def confined(root: Path, value: str) -> Path:
    """相対pathと全祖先のsymlinkを検査する。"""
    if not isinstance(value, str) or not value or "\\" in value or any(p in {"", ".", ".."} for p in value.split("/")):
        raise ValueError(f"invalid relative path: {value!r}")
    path = root
    for part in value.split("/"):
        path /= part
        if path.is_symlink():
            raise ValueError(f"symlink is not allowed: {value}")
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"path escapes repository: {value}")
    return path


def read_json(path: Path):
    """重複keyを黙って上書きせず読む。"""
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs)


def validate_schema(value, schema: dict, label: str = "$", document: dict | None = None) -> None:
    """配布schemaで使用するJSON Schemaの部分集合を外部依存なしで検査する。"""
    document = schema if document is None else document
    if "oneOf" in schema:
        matches = 0
        for alternative in schema["oneOf"]:
            try:
                validate_schema(value, alternative, label, document)
                matches += 1
            except ValueError:
                pass
        if matches != 1:
            raise ValueError(f"{label}: expected exactly one schema alternative")
    if "$ref" in schema:
        target = document
        for part in schema["$ref"].removeprefix("#/").split("/"):
            target = target[part]
        return validate_schema(value, target, label, document)
    types = {"object": dict, "array": list, "string": str, "integer": int, "boolean": bool}
    if "type" in schema and (not isinstance(value, types[schema["type"]]) or (schema["type"] == "integer" and isinstance(value, bool))):
        raise ValueError(f"{label}: expected {schema['type']}")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"{label}: invalid value {value!r}")
    if "const" in schema and (type(value) is not type(schema["const"]) or value != schema["const"]):
        raise ValueError(f"{label}: expected {schema['const']!r}")
    if isinstance(value, str):
        if len(value.strip()) < schema.get("minLength", 0) or ("pattern" in schema and re.search(schema["pattern"], value) is None):
            raise ValueError(f"{label}: invalid string")
    if isinstance(value, int) and value < schema.get("minimum", value):
        raise ValueError(f"{label}: below minimum")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            raise ValueError(f"{label}: missing entries")
        if schema.get("uniqueItems") and len({json.dumps(x, sort_keys=True) for x in value}) != len(value):
            raise ValueError(f"{label}: duplicate entries")
        for index, item in enumerate(value):
            validate_schema(item, schema.get("items", {}), f"{label}[{index}]", document)
    if isinstance(value, dict):
        if set(schema.get("required", [])) - value.keys():
            raise ValueError(f"{label}: missing fields {sorted(set(schema['required']) - value.keys())}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False and value.keys() - properties.keys():
            raise ValueError(f"{label}: unknown fields {sorted(value.keys() - properties.keys())}")
        for key, item in value.items():
            rule = properties.get(key, schema.get("additionalProperties", {}))
            if isinstance(rule, dict):
                validate_schema(item, rule, f"{label}.{key}", document)


def tree_digest(files: list[dict]) -> str:
    """パスとGit blob IDの組から全件集合のdigestを計算する。"""
    content = "".join(f"{x['path']}\t{x['blob_sha']}\n" for x in sorted(files, key=lambda x: x['path']))
    return hashlib.sha256(content.encode()).hexdigest()


def validate_inventory(data: dict, active_ids: set[str], reference_root: Path | None = None, target_root: Path | None = None) -> None:
    """構造・集合・要件coverageと、任意で固定commitの実blobを照合する。"""
    validate_schema(data, read_json(ASSETS / "reference-inventory.schema.json"))
    files = data["files"]
    paths = [x["path"] for x in files]
    if len(paths) != data["file_count"] or len(set(paths)) != len(paths):
        raise ValueError("inventory missing, excess or duplicate paths")
    if tree_digest(files) != data["tree_sha256"]:
        raise ValueError("inventory path/blob SHA mismatch")
    required = set(data["requirement_ids"])
    covered = {r for x in files for r in x["requirement_ids"]} | {x["requirement_id"] for x in data["gaps"]}
    if required != covered or not required <= active_ids:
        raise ValueError("inventory requirement coverage mismatch or unknown/inactive requirement")
    for item in files:
        confined(Path('/reference'), item['path'])
        if not item['path'].startswith(data['source_root'].rstrip('/') + '/'):
            raise ValueError('inventory file outside source_root')
        if item['adoption'] != 'not-adopted' and not item['connections']:
            raise ValueError('adopted tool requires connection')
        if data['scope'] == 'target-adoption' and item['adoption'] != 'not-adopted':
            if target_root is None:
                raise ValueError('target inventory requires target_root')
            for connection in item['connections']:
                if not confined(target_root, connection).is_file():
                    raise ValueError(f'missing inventory connection: {connection}')
    if reference_root is not None:
        lines = subprocess.check_output(['git', '-C', str(reference_root), 'ls-tree', '-r', data['revision'], '--', data['source_root']], text=True).splitlines()
        actual = {}
        for line in lines:
            mode, kind, blob, path = line.replace('\t', ' ', 1).split(' ', 3)
            if kind != 'blob' or mode not in {'100644', '100755'}:
                raise ValueError('reference tree contains unsupported entry')
            actual[path] = blob
        if actual != {x['path']: x['blob_sha'] for x in files}:
            raise ValueError('reference has missing/excess paths or mismatching blob SHA')


def render(data: dict) -> str:
    """JSONだけから一覧を生成する。"""
    def cell(value):
        return str(value).replace('|', '&#124;').replace('\n', '<br>')
    lines = ['# 参照tools全件対応表（自動生成）', '', '直接編集せず reference_inventory.py で再生成する。', '',
             f"参照: {data['repository']} / `{data['revision']}` / {data['file_count']} files", '',
             '採用区分は導入先での実装方針。reference-blueprintは導入先への実接続済みを意味しない。', '',
             '| パス / blob SHA | 用途 / 分類 | 要件ID | 採用区分 / 理由 | 固有前提 | 接続先 |', '|---|---|---|---|---|---|']
    for x in sorted(data['files'], key=lambda x: x['path']):
        row = [f"{x['path']}<br>{x['blob_sha']}", x['purpose']+'<br>'+x['classification'], ', '.join(x['requirement_ids']),
               x['adoption']+'<br>'+x['reason'], ', '.join(x['language_assumptions']) or 'なし', ', '.join(x['connections']) or '非採用']
        lines.append('| '+' | '.join(cell(v) for v in row)+' |')
    lines += ['', '## 参照toolsだけでは満たせない要件', '', '| 要件ID | 不足と導入先で必要な実装 |', '|---|---|']
    for gap in data['gaps']:
        lines.append(f"| {gap['requirement_id']} | {cell(gap['reason'])} |")
    return '\n'.join(lines)+'\n'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inventory', type=Path)
    parser.add_argument('--requirements', type=Path, default=Path('spec/requirements/requirements.json'))
    parser.add_argument('--reference-root', type=Path)
    parser.add_argument('--target-root', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        data = read_json(args.inventory)
        active = {x['id'] for x in read_json(args.requirements)['requirements'] if x['status'] == 'active'}
        validate_inventory(data, active, args.reference_root, args.target_root)
        if args.out:
            expected = render(data).encode()
            if args.check:
                if args.out.read_bytes() != expected:
                    raise ValueError('inventory Markdown drift')
            else:
                if args.out.is_symlink():
                    raise ValueError('symlink output')
                args.out.write_bytes(expected)
        print(f"reference inventory passed: {len(data['files'])} files")
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(1, f'inventory incomplete: {exc}\n')


if __name__ == '__main__':
    main()
