"""dev-standard adapter: lazunex形式の設計生成物を能力ごとの所有rootへ集約する。

各能力は `docs/spec/<NN>.<name>` を完全所有する。lazunex由来の生成器は `src/` の一時コピーで
実行し、所有rootの内容だけを取り出すため、生成・検査とも所有出力以外へ書き込まない。
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
for _path in (str(ROOT), str(SRC)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

REQUIREMENT_IDS = ["TECH-DESIGN"]
MANIFEST = ROOT / ".dev-standard/design.json"
PROFILE = ".dev-standard/api-document-profile.json"
SKILL_SCRIPTS = ROOT / ".agents/skills/generate-implementation-design/scripts"
COMMAND = ["python", "-B", "src/tools/project/design.py"]
REPORT = {
    "configuration": "pass",
    "design_drift": "pass",
    "execution_tests": "not-run",
    "unsupported_surfaces": [],
}
API_ROOT = "docs/spec/40.apis"
CRUD_ROOT = "docs/spec/30.crud"
CRUD_MODEL_DIR = "dev-standard"
API_KINDS = ("detail-design", "interface", "messages", "query", "sequence", "unit-test")
EMPTY_REASONS = {
    "request_bodies": "Request body はありません。",
    "resource_changes": "正常系で作成/更新/削除するリソースはありません。",
    "queries": "このAPIが実行するSQLはありません。",
}
TAG = re.compile(r"\[([A-Z]+-[A-Z0-9]+(?:-AC)?)\]")


def dump(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def table(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> str:
    def cell(value: object) -> str:
        return str(value).replace("|", "\\|").replace("\n", "<br>")

    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
        *("| " + " | ".join(cell(value) for value in row) + " |" for row in rows),
    ]
    return "\n".join(lines) + "\n"


def run_lazunex_generators(modules: Sequence[str], output_root: str) -> dict[str, str]:
    """`src/`の一時コピーで生成器を実行し、所有root配下の生成物を相対pathで返す。"""
    with tempfile.TemporaryDirectory(prefix="slotkeeper-design-") as temporary:
        work = Path(temporary)
        shutil.copytree(SRC, work / "src", ignore=shutil.ignore_patterns("__pycache__"))
        env = {
            **os.environ,
            "PYTHONPATH": f"{work / 'src'}{os.pathsep}{work}",
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        for module in modules:
            subprocess.run(  # noqa: S603
                [sys.executable, "-B", "-m", f"tools.{module}"],
                cwd=work,
                env=env,
                check=True,
                stdout=subprocess.DEVNULL,
            )
        root = work / output_root
        return {
            path.relative_to(root).as_posix(): path.read_text(encoding="utf-8")
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }


# data ---------------------------------------------------------------------


def render_data() -> dict[str, str]:
    return run_lazunex_generators(
        ("generate_db_table_specs", "generate_db_er_diagram"), "docs/spec/20.db"
    )


# api ----------------------------------------------------------------------


@dataclass(frozen=True)
class Operation:
    operation_id: str
    group: str
    api: str
    summary: str


def contract_operations() -> list[Operation]:
    """contract.pyのCONTRACTから、実装されたoperationと所有directoryを列挙する。"""
    from tools.check_api_contracts import contract_metadata

    operations: list[Operation] = []
    for path in sorted((SRC / "app/apis").glob("*/*/contract.py")):
        metadata = contract_metadata(path)
        if not hasattr(metadata, "operation_id"):
            raise ValueError(f"未対応のcontract: {path.relative_to(ROOT)}")
        group, api = path.parent.relative_to(SRC / "app/apis").parts
        operations.append(
            Operation(
                metadata.operation_id,  # type: ignore[union-attr]
                group,
                api,
                metadata.business_summary,  # type: ignore[union-attr]
            )
        )
    return sorted(operations, key=lambda op: op.operation_id)


def registered_operation_ids() -> set[str]:
    from app.main import create_app

    schema = create_app().openapi()
    return {
        operation["operationId"]
        for path_item in schema["paths"].values()
        for operation in path_item.values()
    }


def headings(body: str) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    fenced = False
    for line in body.splitlines():
        if line.startswith("```"):
            fenced = not fenced
            continue
        match = re.match(r"^(#{1,6}) (.+?)\s*$", line)
        if match and not fenced:
            found.append((len(match.group(1)), match.group(2)))
    return found


def repeat_sections(body: str, grammar: Sequence[Mapping[str, Any]]) -> dict[str, list[str]]:
    """profileの文法に沿って見出しを読み、繰返し節の実見出しを列挙する。"""
    found = headings(body)[1:]
    index = 0
    sections: dict[str, list[str]] = {}
    for item in grammar:
        if "repeat" not in item:
            if index >= len(found) or found[index] != (item["level"], item["title"]):
                raise ValueError(f"未対応の章構成: {item['title']}")
            index += 1
            continue
        values: list[str] = []
        children = [(child["level"], child["title"]) for child in item["children"]]
        while index < len(found) and found[index][0] == item["level"]:
            values.append(found[index][1])
            index += 1 + len(children)
        sections[item["repeat"]] = values
    if index != len(found):
        raise ValueError("未対応の章構成: 余剰の見出し")
    return sections


def api_manifest_operations(
    operations: Sequence[Operation], files: Mapping[str, str]
) -> list[dict[str, Any]]:
    profile = json.loads((ROOT / PROFILE).read_text(encoding="utf-8"))
    result: list[dict[str, Any]] = []
    for op in operations:
        documents = {kind: f"{API_ROOT}/{op.group}/{op.api}/{kind}_gen.md" for kind in API_KINDS}
        sections: dict[str, list[str]] = {}
        for kind in API_KINDS:
            body = files[f"{op.group}/{op.api}/{kind}_gen.md"]
            sections.update(repeat_sections(body, profile["headings"][kind]))
        entry: dict[str, Any] = {
            "id": op.operation_id,
            "group": op.group,
            "api": op.api,
            "documents": documents,
            "sections": sections,
        }
        non_applicable = {key: EMPTY_REASONS[key] for key, values in sections.items() if not values}
        if non_applicable:
            entry["non_applicable"] = non_applicable
        result.append(entry)
    return result


def render_api() -> dict[str, str]:
    files = run_lazunex_generators(
        (
            "generate_openapi_if_specs",
            "generate_api_list",
            "generate_api_sequences",
            "generate_query_specs",
            "generate_api_detail_design",
            "generate_api_unit_test_factors",
            "generate_api_message_catalog",
        ),
        API_ROOT,
    )
    operations = contract_operations()
    registered = registered_operation_ids()
    if registered != {op.operation_id for op in operations}:
        raise ValueError(
            "未登録または契約のないoperation: "
            + ", ".join(sorted(registered ^ {op.operation_id for op in operations}))
        )
    from app.main import create_app

    files["openapi.json"] = dump(create_app().openapi())
    files["operations.json"] = dump([op.operation_id for op in operations])
    groups = sorted({op.group for op in operations})
    files["index.md"] = (
        "# API設計\n\n"
        "lazunex形式のAPI帳票。各APIの6帳票はgroup/API単位のindexから辿る。\n\n"
        "- [API一覧](apis_list_gen.md)\n"
        "- [運用ログmessage一覧](messages_index_gen.md)\n"
        "- [OpenAPI](openapi.json)\n\n"
        "## Group\n\n" + "".join(f"- [{group}]({group}/index.md)\n" for group in groups)
    )
    for group in groups:
        members = [op for op in operations if op.group == group]
        files[f"{group}/index.md"] = f"# {group}\n\n" + table(
            ["API", "operationId", "業務概要"],
            [
                [f"[{op.api}]({op.api}/index.md)", f"`{op.operation_id}`", op.summary]
                for op in members
            ],
        )
    for op in operations:
        files[f"{op.group}/{op.api}/index.md"] = (
            f"# {op.api}\n\n- operationId: `{op.operation_id}`\n- 業務概要: {op.summary}\n\n"
            + "".join(f"- [{kind}]({kind}_gen.md)\n" for kind in API_KINDS)
        )
    return files


# crud ---------------------------------------------------------------------


def crud_model() -> dict[str, Any]:
    """SQLとrouter依存からAPI×保存先のCRUDを根拠行つきで組み立てる。"""
    from tools.generate_db_crud import sql_operations
    from tools.generate_db_table_specs import parse_tables
    from tools.generate_external_crud import SERVICE_CONFIGS, router_dependency_names

    tables = set(parse_tables((SRC / "db/ddl.sql").read_text(encoding="utf-8")))
    operations = contract_operations()
    rows: dict[tuple[str, str], dict[str, Any]] = {}

    def add(op: str, resource: str, access: str, path: Path, line: int) -> None:
        row = rows.setdefault(
            (op, resource),
            {"operation": op, "resource": resource, "access": [], "evidence": []},
        )
        if access not in row["access"]:
            row["access"].append(access)
        evidence = {
            "path": path.relative_to(ROOT).as_posix(),
            "line": line,
            "role": "read" if access == "R" else "write",
        }
        if evidence not in row["evidence"]:
            row["evidence"].append(evidence)

    identity = SERVICE_CONFIGS["identity"]
    for op in operations:
        api_dir = SRC / "app/apis" / op.group / op.api
        for sql_path in sorted((api_dir / "sql").glob("*.sql")):
            for table_name, accesses in sql_operations(
                sql_path.read_text(encoding="utf-8")
            ).items():
                if table_name in tables:
                    for access in sorted(accesses):
                        add(op.operation_id, f"slotkeeper.{table_name}", access, sql_path, 1)
        router_path = api_dir / "router.py"
        for dependency in sorted(router_dependency_names(router_path)):
            method = identity.router_dependencies.get(dependency)
            if method is None:
                continue
            lines = router_path.read_text(encoding="utf-8").splitlines()
            line = next(i for i, text in enumerate(lines, 1) if f"Depends({dependency})" in text)
            add(op.operation_id, f"identity.{method.resource}", method.operation, router_path, line)
    for row in rows.values():
        row["access"] = [access for access in "CRUD" if access in row["access"]]
        row["evidence"].sort(key=lambda item: (item["path"], item["line"], item["role"]))
    accessed = {op for op, _resource in rows}
    return {
        "schema_version": 1,
        "operations": [op.operation_id for op in operations],
        "rows": [rows[key] for key in sorted(rows)],
        "no_access": {
            op.operation_id: "DBと外部サービスへアクセスせず稼働状態だけを返す"
            for op in operations
            if op.operation_id not in accessed
        },
        "unresolved": [],
    }


def crud_renderings(model: dict[str, Any]) -> dict[str, bytes]:
    sys.path.insert(0, str(SKILL_SCRIPTS))
    try:
        import check_design  # type: ignore[import-not-found]
    finally:
        sys.path.remove(str(SKILL_SCRIPTS))
    return cast(dict[str, bytes], check_design.crud_renderings(model))


CRUD_FILES = {
    "model": "model.json",
    "csv": "matrix.csv",
    "table": "matrix.md",
    "diagram": "diagram.md",
    "evidence": "evidence.json",
}


def render_crud() -> dict[str, str]:
    files = run_lazunex_generators(("generate_db_crud", "generate_external_crud"), CRUD_ROOT)
    model = crud_model()
    rendered = crud_renderings(model)
    files[f"{CRUD_MODEL_DIR}/{CRUD_FILES['model']}"] = dump(model)
    for kind in ("csv", "table", "diagram", "evidence"):
        files[f"{CRUD_MODEL_DIR}/{CRUD_FILES[kind]}"] = rendered[kind].decode()
    files["index.md"] = (
        "# CRUD設計\n\n"
        "- [API×DB CRUD（lazunex形式）](db_crud.gen.csv)\n"
        "- [API×identity CRUD（lazunex形式）](identity_crud.gen.csv)\n"
        f"- [API×保存先 CRUD（dev-standard射影）]({CRUD_MODEL_DIR}/matrix.md)\n"
        f"- [CRUD図]({CRUD_MODEL_DIR}/diagram.md)\n"
    )
    return files


# tools --------------------------------------------------------------------


def render_tools() -> dict[str, str]:
    from app_tool.docs.generate_tool_docs import rendered_outputs

    output_dir = Path("docs/spec/tools")
    return {
        path.relative_to(output_dir).as_posix(): content
        for path, content in rendered_outputs(output_dir).items()
    }


# frontend -----------------------------------------------------------------


def frontend_design() -> str:
    """App.tsxの画面区画・入力・呼出API・権限と、logic.tsの例外表示を抽出する。"""
    app = (ROOT / "frontend/src/App.tsx").read_text(encoding="utf-8")
    logic = (ROOT / "frontend/src/logic.ts").read_text(encoding="utf-8")
    auth = (ROOT / "frontend/src/auth.ts").read_text(encoding="utf-8")
    nav = re.search(r'<nav aria-label="メインメニュー">(.*?)</nav>', app, re.S)
    if not nav:
        raise ValueError("未対応の画面構造: frontend/src/App.tsx にメインメニューがない")
    tabs = re.findall(r'\["(\w+)", "([^"]+)"\]', nav.group(1))
    admin_only = set(re.findall(r'admin \? \[\["(\w+)"', nav.group(1)))
    functions: dict[str, list[str]] = {}
    for match in re.finditer(r"async function (\w+)\(", app):
        body = app[match.end() : app.find("\n  }\n", match.end())]
        calls = re.findall(r'client\.(GET|POST|PUT)\(\s*"([^"]+)"', body)
        functions[match.group(1)] = [method + " " + path for method, path in calls]

    def section(start: int, end: int) -> list[str]:
        text = app[start:end]
        titles = [h.strip() for h in re.findall(r"<h2>([^<{]+)", text)]
        labels = [
            re.sub(r"\s+", " ", label).strip()
            for label in re.findall(r"<label[^>]*>\s*([^<{]+)", text)
            if label.strip()
        ]
        handlers = sorted(set(re.findall(r"void (\w+)\(", text)) & set(functions))
        apis = sorted({api for name in handlers for api in functions[name]})
        return [
            " / ".join(titles) or "—",
            ", ".join(labels) or "—",
            ", ".join(handlers) or "—",
            ", ".join(apis) or "—",
        ]

    starts = [(m.start(), m.group(1)) for m in re.finditer(r'\{tab === "(\w+)"', app)]
    detail = app.find('aria-label="予約詳細"')
    if not tabs or len(starts) != len(tabs) or detail < 0:
        raise ValueError("未対応の画面構造: タブと画面区画の対応を抽出できない")
    labels = dict(tabs)
    rows: list[list[str]] = []
    for index, (start, tab) in enumerate(starts):
        end = starts[index + 1][0] if index + 1 < len(starts) else detail
        rows.append(
            [labels[tab] + "（" + tab + "）", "管理者" if tab in admin_only else "認証済み利用者"]
            + section(start, end)
        )
    rows.append(
        ["予約詳細・履歴（?reservation=ID）", "本人・管理者（APIで判定）"]
        + section(detail, len(app))
    )
    effects = [
        [re.sub(r"\s+", " ", condition).strip(), name, ", ".join(functions[name]) or "—", deps]
        for condition, name, deps in re.findall(
            r"useEffect\(\(\) => \{\s*(?:const [^;]+;\s*)?if \(([^)]*)\) void (\w+)\([^)]*\);"
            r"\s*\}, \[([^\]]*)\]\)",
            app,
        )
        if name in functions
    ]
    catalog = re.search(r"const codes[^{]*\{(.*?)\};", logic, re.S)
    if not catalog:
        raise ValueError("未対応の例外表示: frontend/src/logic.ts に業務コード表がない")
    codes = re.findall(r"(\w+):\s*\n?\s*\"([^\"]+)\"", catalog.group(1))
    statuses = re.findall(r"(\d{3}): \"([^\"]+)\"", logic)
    storage = [
        name
        for name, found in (
            ("tokenはInMemoryWebStorage（メモリ）", "InMemoryWebStorage" in auth),
            ("PKCE stateはsessionStorage", "sessionStorage" in auth),
            ("localStorage不使用", "localStorage" not in auth + app),
        )
        if found
    ]
    sources = [
        [
            file.relative_to(ROOT).as_posix(),
            ", ".join(re.findall(r"useState[^;]+", file.read_text(encoding="utf-8"))) or "—",
            ", ".join(
                re.findall(
                    r'client\.(?:GET|POST|PUT)\(\s*["\']([^"\']+)', file.read_text(encoding="utf-8")
                )
            )
            or "—",
        ]
        for file in sorted((ROOT / "frontend/src").rglob("*"))
        if file.suffix in (".tsx", ".ts", ".astro", ".css") and "generated" not in file.parts
    ]
    return (
        "# 画面・状態・呼出API\n\n"
        "静的Astroページ1枚にReact islandを載せ、画面区画はメニューとURLのreservation引数で"
        "切り替える。権限はUI表示に加え、APIの403で最終判定する。\n\n## 画面一覧\n\n"
        + table(["画面", "表示権限", "見出し", "入力", "操作関数", "呼出API"], rows)
        + "\n## 状態変化による取得\n\n"
        + table(["条件", "関数", "呼出API", "再実行の依存"], effects)
        + "\n## 例外表示（業務コード）\n\n"
        + table(["コード", "表示"], codes)
        + "\n## 例外表示（HTTP status）\n\n"
        + table(["status", "表示"], [*statuses, ("通信失敗", "入力を保持して再送を案内")])
        + "\n## 認証情報の保持\n\n"
        + "".join("- " + item + "\n" for item in storage)
        + "\n## source別の状態宣言\n\n"
        + table(["source", "状態宣言", "API"], sources)
    )


def render_frontend() -> dict[str, str]:
    return {"frontend.gen.md": frontend_design()}


# infra --------------------------------------------------------------------


def render_infra() -> dict[str, str]:
    import aws_cdk as cdk
    from aws_cdk.assertions import Template

    from infra.stack import SlotKeeperStack

    with tempfile.TemporaryDirectory() as folder:
        app = cdk.App(outdir=folder)
        template = Template.from_stack(SlotKeeperStack(app, "SlotKeeper-dev")).to_json()
    return {
        "template.json": dump(template),
        "infra.gen.md": "# 合成インフラ\n\n"
        + table(
            ["論理ID", "種別", "設定"],
            [
                [
                    logical_id,
                    resource["Type"],
                    json.dumps(resource.get("Properties", {}), ensure_ascii=False, sort_keys=True),
                ]
                for logical_id, resource in sorted(template["Resources"].items())
            ],
        ),
    }


# trace --------------------------------------------------------------------


def tagged_tests() -> list[dict[str, Any]]:
    """pytest・Vitest・Playwrightの実在テストと受入条件タグを収集する。"""
    found: list[dict[str, Any]] = []
    for file in sorted((ROOT / "tests").rglob("test_*.py")):
        relative = file.relative_to(ROOT).as_posix()
        for node in ast.walk(ast.parse(file.read_text(encoding="utf-8"))):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.name.startswith(
                "test_"
            ):
                narrative = ast.get_docstring(node) or ""
                found.append(
                    {
                        "id": relative + "::" + node.name,
                        "file": relative,
                        "narrative": TAG.sub("", narrative).strip(),
                        "tags": TAG.findall(narrative),
                    }
                )
    scripts = [("vitest", path) for path in sorted((ROOT / "frontend/tests").glob("*.test.ts"))]
    scripts += [("playwright", path) for path in sorted((ROOT / "e2e").glob("*.spec.ts"))]
    for kind, file in scripts:
        pattern = r'describe\(\s*"([^"]+)"' if kind == "vitest" else r'\btest\(\s*"([^"]+)"'
        for title in re.findall(pattern, file.read_text(encoding="utf-8")):
            found.append(
                {
                    "id": kind + "::" + title,
                    "file": file.relative_to(ROOT).as_posix(),
                    "narrative": TAG.sub("", title).strip(),
                    "tags": TAG.findall(title),
                }
            )
    return found


def verify_checks() -> set[str]:
    """verify入口が実行する検査名をASTから取得する。"""
    names: set[str] = set()
    tree = ast.parse((SRC / "tools/project/verify.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and ast.unparse(node.func) == "run" and node.args:
            first = node.args[0]
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                names.add(first.value)
        if isinstance(node, ast.Tuple) and len(node.elts) == 2:
            first = node.elts[0]
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                names.add(first.value)
    return names


def trace_rows(tests: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """要件→受入条件→実在テストID・検査名を照合し、欠落と未知タグを拒否する。"""
    catalog = json.loads((ROOT / "spec/requirements/requirements.json").read_text("utf-8"))
    active = [item for item in catalog["requirements"] if item["status"] == "active"]
    criteria = {criterion["id"] for item in active for criterion in item["acceptance_criteria"]}
    unknown = sorted({tag for case in tests for tag in case["tags"]} - criteria)
    if unknown:
        raise ValueError("要件にない受入条件タグ: " + ", ".join(unknown))
    checks = verify_checks()
    rows: list[dict[str, Any]] = []
    for item in active:
        method = item["verification"]["method"]
        for criterion in item["acceptance_criteria"]:
            linked = [case for case in tests if criterion["id"] in case["tags"]]
            evidence: list[str] = []
            if method == "check":
                evidence = re.findall(r"verify:([\w-]+)", item["verification"]["evidence"])
                missing = sorted(set(evidence) - checks)
                if not evidence or missing:
                    raise ValueError("検査名の欠落: " + criterion["id"] + " " + ", ".join(missing))
            elif not linked:
                raise ValueError("受入条件にテストがない: " + criterion["id"])
            outside = sorted({case["file"] for case in linked} - set(item["traces"]["tests"]))
            if outside:
                raise ValueError(
                    "要件traceにないテスト: " + criterion["id"] + " " + ", ".join(outside)
                )
            rows.append(
                {
                    "requirement": item["id"],
                    "criterion": criterion["id"],
                    "gwt": (
                        f"Given {criterion['given']} When {criterion['when']} "
                        f"Then {criterion['then']}"
                    ),
                    "tests": [case["id"] for case in linked],
                    "checks": evidence,
                }
            )
    return rows


def render_trace() -> dict[str, str]:
    tests = tagged_tests()
    rows = trace_rows(tests)
    return {
        "trace.json": dump(rows),
        "trace.gen.md": "# 要件トレーサビリティ\n\n"
        + table(
            ["要件", "受入条件", "Given / When / Then", "実在テストID", "検査"],
            [
                [
                    row["requirement"],
                    row["criterion"],
                    row["gwt"],
                    "<br>".join(row["tests"]) or "—",
                    ", ".join(row["checks"]) or "—",
                ]
                for row in rows
            ],
        ),
        "tests.gen.md": "# テスト設計\n\n"
        + table(
            ["テストID", "説明", "受入条件"],
            [
                [case["id"], case["narrative"] or "—", ", ".join(case["tags"]) or "—"]
                for case in tests
            ],
        ),
        "index.md": "# 要件・テスト追跡\n\n"
        "- [要件トレーサビリティ](trace.gen.md)\n- [テスト設計](tests.gen.md)\n",
    }


# capabilities -------------------------------------------------------------


@dataclass(frozen=True)
class Capability:
    name: str
    output_root: str
    render: Callable[[], dict[str, str]]
    sources: tuple[str, ...]
    surfaces: tuple[str, ...]


CAPABILITIES = (
    Capability(
        "data",
        "docs/spec/20.db",
        render_data,
        (
            "src/db/ddl.sql",
            "src/tools/generate_db_table_specs.py",
            "src/tools/generate_db_er_diagram.py",
        ),
        ("data",),
    ),
    Capability(
        "crud",
        CRUD_ROOT,
        render_crud,
        (
            "src/app/apis",
            "src/db/ddl.sql",
            "src/tools/generate_db_crud.py",
            "src/tools/generate_external_crud.py",
        ),
        ("data",),
    ),
    Capability(
        "api",
        API_ROOT,
        render_api,
        ("src/app", "src/db/ddl.sql", "src/tools", PROFILE),
        ("api",),
    ),
    Capability(
        "tools",
        "docs/spec/tools",
        render_tools,
        ("src/app_tool", "src/tools"),
        ("tooling",),
    ),
    Capability(
        "frontend",
        "docs/spec/60.frontend",
        render_frontend,
        ("frontend/src",),
        ("frontend",),
    ),
    Capability(
        "infra",
        "docs/spec/70.infra",
        render_infra,
        ("infra", "artifacts/lambda.zip"),
        ("infra",),
    ),
    Capability(
        "trace",
        "docs/spec/80.trace",
        render_trace,
        (
            "spec/requirements/requirements.json",
            "tests",
            "frontend/tests",
            "e2e",
            "src/tools/project/verify.py",
        ),
        ("trace",),
    ),
)
CAPABILITY_BY_NAME = {capability.name: capability for capability in CAPABILITIES}


def rendered_files(capability: Capability) -> dict[str, str]:
    files = capability.render()
    files["report.json"] = dump(REPORT)
    return dict(sorted(files.items()))


def drift(files: Mapping[str, str], out: Path) -> list[str]:
    """欠落・変更・余剰（旧帳票を含む）を検出し、既存fileは書き換えない。"""
    existing = (
        {path.relative_to(out).as_posix() for path in out.rglob("*") if path.is_file()}
        if out.exists()
        else set()
    )
    changed = [
        path
        for path, content in files.items()
        if not (out / path).is_file() or (out / path).read_text(encoding="utf-8") != content
    ]
    return sorted(changed) + sorted(existing - set(files))


def write_owned_root(files: Mapping[str, str], out: Path) -> None:
    """所有rootの中身を入れ替える。root自体はbind mount先になりうるため残す。"""
    out.mkdir(parents=True, exist_ok=True)
    for child in list(out.iterdir()):
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()
    for path, content in files.items():
        (out / path).parent.mkdir(parents=True, exist_ok=True)
        (out / path).write_text(content, encoding="utf-8")


def manifest(outputs: Mapping[str, Mapping[str, str]]) -> dict[str, Any]:
    api_files = outputs["api"]
    operations = contract_operations()
    api_operations = api_manifest_operations(operations, api_files)
    groups = sorted({op.group for op in operations})
    surfaces: dict[str, dict[str, Any]] = {}
    for capability in CAPABILITIES:
        for surface in capability.surfaces:
            surfaces.setdefault(surface, {"status": "required", "capabilities": []})
            surfaces[surface]["capabilities"].append(capability.name)
    return {
        "schema_version": 2,
        "requirements": "spec/requirements/requirements.json",
        "applicable_requirement_ids": REQUIREMENT_IDS,
        "reference_inventories": [".dev-standard/reference-adoption.json"],
        "surfaces": surfaces,
        "capabilities": {
            capability.name: {
                "status": "required",
                "requirement_ids": REQUIREMENT_IDS,
                "sources": list(capability.sources),
                "generate": [*COMMAND, "--target", capability.name],
                "check": [*COMMAND, "--target", capability.name, "--check"],
                "output_root": capability.output_root,
                "outputs": [
                    f"{capability.output_root}/{path}" for path in outputs[capability.name]
                ],
                "report": f"{capability.output_root}/report.json",
            }
            for capability in CAPABILITIES
        },
        "api": {
            "profile": PROFILE,
            "operation_inventory": f"{API_ROOT}/operations.json",
            "root": API_ROOT,
            "index": f"{API_ROOT}/index.md",
            "group_indexes": {group: f"{API_ROOT}/{group}/index.md" for group in groups},
            "api_indexes": {
                op.operation_id: f"{API_ROOT}/{op.group}/{op.api}/index.md" for op in operations
            },
            "operations": api_operations,
        },
        "crud": {
            kind: f"{CRUD_ROOT}/{CRUD_MODEL_DIR}/{filename}"
            for kind, filename in CRUD_FILES.items()
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    """能力単位で非破壊checkまたは所有rootの再生成を行う。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=[*CAPABILITY_BY_NAME, "all"], default="all")
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--manifest", action="store_true", help=".dev-standard/design.jsonも再生成する"
    )
    args = parser.parse_args(argv)
    names = list(CAPABILITY_BY_NAME) if args.target == "all" else [args.target]
    outputs = {name: rendered_files(CAPABILITY_BY_NAME[name]) for name in names}
    failed = False
    for name, files in outputs.items():
        out = ROOT / CAPABILITY_BY_NAME[name].output_root
        if args.check:
            found = drift(files, out)
            if found:
                print(f"設計drift {name}: " + ", ".join(found[:20]), file=sys.stderr)
                failed = True
        else:
            write_owned_root(files, out)
    if args.manifest:
        if set(outputs) != set(CAPABILITY_BY_NAME):
            raise SystemExit("--manifest は --target all と併用する")
        expected = dump(manifest(outputs))
        if args.check:
            if not MANIFEST.exists() or MANIFEST.read_text(encoding="utf-8") != expected:
                print("設計drift: .dev-standard/design.json", file=sys.stderr)
                failed = True
        else:
            MANIFEST.write_text(expected, encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
