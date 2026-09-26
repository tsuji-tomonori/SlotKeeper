#!/usr/bin/env python3
"""JUnit/Vitestの実行結果をcollector一覧と照合して共通test区分へ変換する。"""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path


def convert(format_name: str, raw: str, inventory: list[dict]) -> dict:
    """runner名に依存するID規約を保持し、消えたtestをnot-runにする。"""
    records = {}
    if format_name == "junit":
        if "<!DOCTYPE" in raw.upper() or "<!ENTITY" in raw.upper():
            raise ValueError("DTD/entities are not accepted")
        for case in ET.fromstring(raw).iter("testcase"):
            group = case.get("classname") or case.get("file") or "suite"
            name = case.get("name", "")
            identity = f"{group}::{name}"
            status = "passed"
            if case.find("failure") is not None or case.find("error") is not None:
                status = "failed"
            elif case.find("skipped") is not None:
                status = "skipped"
            elif case.find("flakyFailure") is not None or case.find("rerunFailure") is not None:
                status = "flaky"
            if identity in records:
                raise ValueError(f"duplicate result: {identity}")
            records[identity] = {"id": identity, "name": name, "group": group, "status": status}
    elif format_name == "vitest":
        for suite in json.loads(raw)["testResults"]:
            for case in suite["assertionResults"]:
                name = case["fullName"]
                identity = f'{suite["name"]}::{name}'
                status = {"passed": "passed", "failed": "failed", "pending": "skipped",
                          "skipped": "skipped", "todo": "not-run"}.get(case["status"], "missing")
                if identity in records:
                    raise ValueError(f"duplicate result: {identity}")
                records[identity] = {"id": identity, "name": name, "group": suite["name"], "status": status}
    else:
        raise ValueError("unsupported format")
    ids = [item["id"] for item in inventory]
    if len(ids) != len(set(ids)) or set(records) - set(ids):
        raise ValueError("collector/result identity mismatch")
    items = []
    for item in inventory:
        # descriptionと要件・要因対応は公開用collector metadataから取得する。
        record = {**item, "status": records.get(item["id"], {}).get("status", "not-run")}
        items.append(record)
    return {"applicable": True, "inventory": ids, "items": items}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("format", choices=("junit", "vitest"))
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    args = parser.parse_args()
    result = convert(args.format, args.input.read_text(), json.loads(args.inventory.read_text()))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
