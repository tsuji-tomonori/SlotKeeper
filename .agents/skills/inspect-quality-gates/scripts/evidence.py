#!/usr/bin/env python3
"""公開用に選別した共通エビデンスを、依存なしで静的HTMLへ変換する。"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import shutil
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

CATEGORIES = ("tests", "e2e", "static", "coverage", "design")
LABELS = dict(zip(CATEGORIES, ("単体・結合テスト", "E2E", "静的解析", "カバレッジ", "設計書")))
STATES = {"passed", "failed", "skipped", "not-run", "flaky", "missing"}
ASSETS = Path(__file__).resolve().parent.parent / "assets"


class Links(HTMLParser):
    """生成HTML内の参照先を抽出する。"""

    def __init__(self):
        super().__init__()
        self.values = []

    def handle_starttag(self, tag, attrs):
        self.values.extend(value for key, value in attrs if key in ("href", "src") and value)


def verify_links(output: Path, base: str) -> None:
    """repository Pagesのbaseを考慮して内部file参照を照合する。"""
    if not base.startswith("/") or not base.endswith("/"):
        raise ValueError("siteBase must start and end with /")
    for path in output.rglob("*.html"):
        parser = Links()
        parser.feed(path.read_text(encoding="utf-8"))
        for value in parser.values:
            parsed = urlsplit(value)
            if parsed.scheme or parsed.netloc:
                if parsed.scheme not in ("http", "https", "mailto"):
                    raise ValueError(f"unsafe link scheme: {path.name}")
                continue
            name = unquote(parsed.path)
            if not name:
                continue
            if name.startswith("/"):
                if not name.startswith(base):
                    raise ValueError(f"link outside siteBase: {name}")
                target = output / name[len(base):]
            else:
                target = path.parent / name
            target = target.resolve()
            if not target.is_relative_to(output.resolve()):
                raise ValueError(f"link outside site: {name}")
            if target.is_dir():
                target /= "index.html"
            if not target.is_file():
                raise ValueError(f"broken internal link: {name}")


def text(value: object) -> str:
    return html.escape(str(value), quote=True)


def source(root: Path, name: str) -> Path:
    """公開対象はmanifest配下の明示指定された通常fileだけに限定する。"""
    relative = Path(name)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise ValueError(f"unsafe source path: {name}")
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"symlink source: {name}")
    if not current.is_file():
        raise ValueError(f"missing source: {name}")
    return current


def validate(data: dict, revision: str) -> None:
    """未接続、古い実行、架空の全件成功を公開前に検出する。"""
    if data.get("schemaVersion") != 1 or data.get("revision") != revision or not revision:
        raise ValueError("schemaVersion/revision mismatch")
    if not data.get("runId") or not data.get("generatedAt"):
        raise ValueError("runId and generatedAt are required")
    for name in CATEGORIES:
        category = data.get(name, {})
        if category.get("applicable") is False:
            if not category.get("reason", "").strip():
                raise ValueError(f"{name}: non-applicability needs a reason")
            if category.get("items"):
                raise ValueError(f"{name}: non-applicable category has items")
            continue
        if category.get("applicable") is not True or not category.get("items"):
            raise ValueError(f"{name}: adapter not connected or empty evidence")
        identities = set()
        for item in category["items"]:
            identity = item.get("id")
            if not isinstance(identity, str) or not identity or identity in identities:
                raise ValueError(f"{name}: missing or duplicate identity")
            identities.add(identity)
            hierarchy = item.get("hierarchy")
            if hierarchy is not None and (not isinstance(hierarchy, list) or not hierarchy or any(
                not isinstance(part, str) or not part.strip() for part in hierarchy
            )):
                raise ValueError(f"{name}/{identity}: hierarchy must be nonempty labels")
            if item.get("status") not in STATES or not item.get("name"):
                raise ValueError(f"{name}/{identity}: invalid status/name")
            if name in ("tests", "e2e") and not item.get("group"):
                raise ValueError(f"{name}/{identity}: group is required")
            if name == "e2e" and item["status"] == "passed":
                steps = item.get("steps", [])
                if any(not any(s.get("phase") == phase and s.get("image") and s.get("text")
                               for s in steps) for phase in ("Given", "When", "Then")):
                    raise ValueError(f"{identity}: passed E2E lacks GWT images")
            if name == "static" and not item.get("command"):
                raise ValueError(f"{identity}: command is required")
            if name == "coverage":
                numerator, denominator = item.get("covered"), item.get("total")
                if numerator is None and denominator is None and item["status"] != "passed":
                    if not item.get("detail"):
                        raise ValueError(f"{identity}: unmeasured coverage needs a reason")
                elif (type(numerator) is not int or type(denominator) is not int
                        or not 0 <= numerator <= denominator or denominator < 1
                        or item.get("metric") not in ("statements", "lines", "branches")
                        or not item.get("tool")):
                    raise ValueError(f"{identity}: invalid measured coverage")
            if name == "design" and item["status"] == "passed" and not item.get("path", "").endswith(".html"):
                raise ValueError(f"{identity}: generated HTML design entry is required")
            if name == "design" and item["status"] != "passed" and not item.get("detail"):
                raise ValueError(f"{identity}: unavailable design needs a reason")
        if name in ("tests", "e2e"):
            inventory = category.get("inventory", [])
            if len(inventory) != len(set(inventory)) or set(inventory) != identities:
                raise ValueError(f"{name}: collected inventory and results differ")


def state(category: dict) -> str:
    if category.get("applicable") is False:
        return "対象外"
    values = {item["status"] for item in category["items"]}
    return "passed" if values == {"passed"} else ", ".join(sorted(values - {"passed"}))


def render(data: dict, root: Path, output: Path) -> None:
    """静的siteを生成する。raw logや未指定fileはコピーしない。"""
    output.mkdir(parents=True)
    fingerprints = {}

    def copy(name: str, destination: str) -> None:
        path = source(root, name)
        raw = path.read_bytes()
        fingerprints[name] = hashlib.sha256(raw).hexdigest()
        target = output / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)

    declared = data.get("design", {}).get("files", [])
    if len(declared) != len(set(declared)):
        raise ValueError("duplicate design files")
    for name in declared:
        source(root, name)
        if not name.startswith("design/"):
            raise ValueError("design allowlist must be below design/")
        copy(name, name)
    nav = '<a href="index.html">品質サマリー</a>' + "".join(
        f'<a href="{key}.html">{label}</a>' for key, label in LABELS.items())

    def page(name: str, title: str, body: str, sidebar: str = "") -> None:
        provenance = f'{text(data["revision"])} / {text(data["runId"])} / {text(data["generatedAt"])}'
        (output / name).write_text(
            '<!doctype html><html lang="ja"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{text(title)}</title><link rel="stylesheet" href="evidence.css">'
            f'<header><h1>{text(title)}</h1><p>{provenance}</p><nav>{nav}</nav></header>'
            '<label class="search">このページを検索 <input id="search" type="search"></label>'
            f'<nav id="location" aria-label="現在位置">{text(title)}</nav><div class="layout"><aside>{sidebar}</aside><main>{body}</main></div>'
            '<dialog id="zoom"><button autofocus>閉じる</button><img alt="拡大エビデンス"></dialog>'
            '<script src="evidence.js"></script></html>', encoding="utf-8")

    summary = "".join(f'<article><h2><a href="{name}.html">{LABELS[name]}</a></h2>'
                      f'<p>{text(state(data[name]))}</p>'
                      f'<p>{len(data[name].get("items", []))} 件</p></article>' for name in CATEGORIES)
    page("index.html", "品質サマリー", summary)
    for name in CATEGORIES:
        category = data[name]
        body, groups = [], {}
        if category.get("applicable") is False:
            body.append(f'<p>対象外: {text(category["reason"])}</p>')
        for number, item in enumerate(category.get("items", [])):
            anchor = f"case-{number}"
            hierarchy = item.get("hierarchy", [str(item.get("group", LABELS[name]))])
            branch = groups
            for part in hierarchy:
                branch = branch.setdefault(part, {"children": {}, "links": []})["children"]
            branch.setdefault("", {"links": []})["links"].append(
                f'<li data-target="{anchor}"><a href="#{anchor}">{text(item["name"])}</a></li>')
            breadcrumb = " / ".join([*hierarchy, item["name"]])
            details = f'<p class="status">{text(item["status"])}</p>'
            for field in ("id", "command", "detail", "expected", "actual", "requirement", "factor"):
                if field in item:
                    details += f'<p><strong>{field}</strong>: {text(item[field])}</p>'
            if name == "coverage" and item.get("total") is not None:
                details += (f'<p>{text(item["tool"])} / {text(item["metric"])}: '
                            f'{item["covered"]} / {item["total"]} '
                            f'({100 * item["covered"] / item["total"]:.2f}%)</p>')
            elif name == "coverage":
                details += '<p>未測定（成功率は算出しません）</p>'
            if name == "design" and item.get("path"):
                if item["path"] not in declared:
                    raise ValueError("design entry missing from allowlist")
                details += f'<a href="{text(item["path"])}">設計HTMLを開く</a>'
            for field, suffix in (("download", ".csv"), ("diagram", ".svg")):
                if name == "design" and item.get(field):
                    target = item[field]
                    if target not in declared or not target.endswith(suffix):
                        raise ValueError(f"design {field} missing from allowlist or wrong format")
                    if field == "download":
                        details += f'<p><a download href="{text(target)}">CSV取得</a></p>'
                    else:
                        details += f'<img class="crud-diagram" src="{text(target)}" alt="APIと保存先のCRUD対応図">'

            for step in item.get("steps", []):
                if step.get("phase") not in ("Given", "When", "Then"):
                    raise ValueError("unknown GWT phase")
                details += f'<section><h3>{text(step["phase"])}</h3><p>{text(step.get("text", ""))}</p>'
                if step.get("image"):
                    path = source(root, step["image"])
                    if not path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
                        raise ValueError("GWT evidence must be PNG")
                    destination = f'images/{hashlib.sha256(step["image"].encode()).hexdigest()}.png'
                    copy(step["image"], destination)
                    details += f'<button class="image"><img src="{destination}" alt="{text(step["phase"])}"></button>'
                details += '</section>'
            body.append(f'<article id="{anchor}" data-breadcrumb="{text(breadcrumb)}"><p class="breadcrumb">{text(breadcrumb)}</p><h2>{text(item["name"])}</h2>{details}</article>')
        def tree(nodes):
            content = ""
            for label, node in nodes.items():
                if label == "":
                    content += '<ul>' + ''.join(node['links']) + '</ul>'
                else:
                    content += f'<details class="hierarchy" open><summary>{text(label)}</summary>{tree(node["children"])}</details>'
            return content
        sidebar = tree(groups)
        page(f"{name}.html", LABELS[name], "".join(body), sidebar)
    for name in ("evidence.css", "evidence.js"):
        shutil.copyfile(ASSETS / name, output / name)
    manifest = {"revision": data["revision"], "runId": data["runId"], "sources": fingerprints,
                "evidenceSha256": hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()}
    (output / "provenance.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    verify_links(output, data.get("siteBase", "/"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("init", "build", "check"))
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--revision", default="")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        if args.action == "init":
            template = {"schemaVersion": 1, "revision": "", "runId": "", "generatedAt": ""}
            template.update({name: {"applicable": True, "items": []} for name in CATEGORIES})
            args.manifest.parent.mkdir(parents=True, exist_ok=True)
            with args.manifest.open("x", encoding="utf-8") as handle:
                handle.write(json.dumps(template, ensure_ascii=False, indent=2) + "\n")
            return 0
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
        validate(data, args.revision)
        if args.output is None:
            raise ValueError("--output is required")
        if args.output.is_symlink():
            raise ValueError("output must not be a symlink")
        with tempfile.TemporaryDirectory() as temp:
            site = Path(temp) / "site"
            render(data, args.manifest.resolve().parent, site)
            expected = {p.relative_to(site): p.read_bytes() for p in site.rglob("*") if p.is_file()}
            if args.action == "check":
                actual = {p.relative_to(args.output): p.read_bytes() for p in args.output.rglob("*") if p.is_file()}
                if actual != expected:
                    raise ValueError("evidence site missing or drifted")
            else:
                if args.output.exists():
                    raise ValueError("output already exists; use a fresh run directory")
                shutil.copytree(site, args.output)
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"evidence: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
