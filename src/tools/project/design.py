"""dev-standard adapter: lazunex形式の設計生成物を能力ごとの所有rootへ集約する。

各能力は `docs/spec/<NN>.<name>` を完全所有する。lazunex由来の生成器は `src/` の一時コピーで
実行し、所有rootの内容だけを取り出すため、生成・検査とも所有出力以外へ書き込まない。
"""

from __future__ import annotations

import argparse
import ast
import importlib
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
from typing import Any

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
REPORT: dict[str, object] = {
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
}
# lazunexのENTRYPOINT-DO-002でmain.pyが所有する稼働確認route。業務operationの6帳票対象外とし、
# lazunexと同じくIF帳票だけを生成する。
PLATFORM_ROUTES = {"health": "system/health/interface_gen.md"}
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


LOGICAL_REFERENCE_GUARANTEE = (
    "DSQLに物理FKがないため、参照先の存在と整合はアプリが同一transactionで保証する"
)


def create_table_ddl(sql: str) -> dict[str, str]:
    """DDL正本のCREATE TABLE文をテーブル名ごとに整形して返す。"""
    import sqlglot
    from sqlglot import exp

    statements: dict[str, str] = {}
    for statement in sqlglot.parse(sql, read="postgres"):
        if isinstance(statement, exp.Create) and statement.kind == "TABLE":
            table = statement.find(exp.Table)
            if table is not None:
                statements[table.name] = statement.sql(
                    dialect="postgres", pretty=True, comments=False
                )
    return statements


def label_of(comment: str, fallback: str) -> str:
    return comment.split("。", 1)[0] or fallback


def database_model() -> dict[str, Any]:
    """ポータルのDB探索用に、テーブル・列・論理参照をDDL正本から組み立てる。"""
    from tools.generate_db_table_specs import parse_tables

    sql = (SRC / "db/ddl.sql").read_text(encoding="utf-8")
    tables = parse_tables(sql)
    ddl = create_table_ddl(sql)
    return {
        "tables": [
            {
                "name": table.name,
                "label": label_of(table.comment, table.name),
                "ddl": ddl.get(table.name, ""),
                "columns": [
                    {
                        "name": column.name,
                        "label": label_of(column.comment, column.name),
                        "type": column.data_type,
                        "nullable": column.nullable,
                        "primary": column.primary_key,
                        "ddl": f"{column.name} {column.data_type}"
                        + ("" if column.nullable else " NOT NULL"),
                    }
                    for column in table.columns
                ],
            }
            for table in (tables[name] for name in sorted(tables))
        ],
        "relations": [
            {
                "from": f"{table.name}.{column.name}",
                "to": column.references.replace("(", ".").rstrip(")"),
                "kind": "application" if column.logical_reference else "database",
                "guarantee": LOGICAL_REFERENCE_GUARANTEE if column.logical_reference else "物理FK",
            }
            for table in (tables[name] for name in sorted(tables))
            for column in table.columns
            if column.references
        ],
    }


def render_data() -> dict[str, str]:
    files = run_lazunex_generators(
        ("generate_db_table_specs", "generate_db_er_diagram"), "docs/spec/20.db"
    )
    files["database.json"] = dump(database_model())
    return files


# api ----------------------------------------------------------------------


@dataclass(frozen=True)
class Operation:
    operation_id: str
    group: str
    api: str
    summary: str


def contract_operations() -> list[Operation]:
    """contract.pyのCONTRACTから、実装されたoperationと所有directoryを列挙する。"""
    from tools.check_api_contracts import ContractIssue, contract_metadata

    operations: list[Operation] = []
    for path in sorted((SRC / "app/apis").glob("*/*/contract.py")):
        metadata = contract_metadata(path)
        if isinstance(metadata, ContractIssue):
            raise ValueError(f"未対応のcontract: {metadata.path}: {metadata.message}")
        group, api = path.parent.relative_to(SRC / "app/apis").parts
        operations.append(Operation(metadata.operation_id, group, api, metadata.business_summary))
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


API_GENERATORS = (
    "generate_openapi_if_specs",
    "generate_api_list",
    "generate_api_sequences",
    "generate_query_specs",
    "generate_api_detail_design",
    "generate_api_unit_test_factors",
    "generate_api_message_catalog",
)


def check_registered_routes(operations: Sequence[Operation], files: Mapping[str, str]) -> None:
    """FastAPIの実登録集合が、契約付きoperationと宣言済みplatform routeに一致するか検査する。"""
    registered = registered_operation_ids()
    expected = {op.operation_id for op in operations} | set(PLATFORM_ROUTES)
    if registered != expected:
        raise ValueError(
            "未登録または契約のないoperation: " + ", ".join(sorted(registered ^ expected))
        )
    missing = [route for route, document in PLATFORM_ROUTES.items() if document not in files]
    if missing:
        raise ValueError("platform routeのIF帳票がない: " + ", ".join(missing))


def api_root_index(groups: Sequence[str]) -> str:
    return (
        "# API設計\n\n"
        "lazunex形式のAPI帳票。各APIの6帳票はgroup/API単位のindexから辿る。"
        "OpenAPIは`openapi.json`、operation一覧は`operations.json`に出力する。\n\n"
        "- [API一覧](apis_list_gen.md)\n"
        "- [運用ログmessage一覧](messages_index_gen.md)\n\n"
        "## Group\n\n"
        + "".join(f"- [{group}]({group}/index.md)\n" for group in groups)
        + "\n## Platform route\n\n"
        "`src/app/main.py`が所有する業務外routeは、lazunexと同じくIF帳票だけを持つ。\n\n"
        + "".join(f"- [{route}]({document})\n" for route, document in PLATFORM_ROUTES.items())
    )


def api_group_index(group: str, operations: Sequence[Operation]) -> str:
    return f"# {group}\n\n" + table(
        ["API", "operationId", "業務概要"],
        [
            [f"[{op.api}]({op.api}/index.md)", f"`{op.operation_id}`", op.summary]
            for op in operations
            if op.group == group
        ],
    )


def api_operation_index(op: Operation) -> str:
    return (
        f"# {op.api}\n\n- operationId: `{op.operation_id}`\n- 業務概要: {op.summary}\n\n"
        + "".join(f"- [{kind}]({kind}_gen.md)\n" for kind in API_KINDS)
    )


def render_api() -> dict[str, str]:
    from app.main import create_app

    files = run_lazunex_generators(API_GENERATORS, API_ROOT)
    operations = contract_operations()
    check_registered_routes(operations, files)
    groups = sorted({op.group for op in operations})
    files["openapi.json"] = dump(create_app().openapi())
    files["operations.json"] = dump([op.operation_id for op in operations])
    files["index.md"] = api_root_index(groups)
    files.update({f"{group}/index.md": api_group_index(group, operations) for group in groups})
    files.update({f"{op.group}/{op.api}/index.md": api_operation_index(op) for op in operations})
    return files


# crud ---------------------------------------------------------------------


@dataclass(frozen=True)
class CrudAccess:
    operation_id: str
    resource: str
    access: str
    path: str
    line: int


def sql_accesses(op: Operation, tables: set[str]) -> list[CrudAccess]:
    """operationのSQL fileごとに、DDLにあるテーブルへのCRUDを根拠行つきで返す。"""
    from tools.generate_db_crud import sql_operations

    accesses: list[CrudAccess] = []
    for sql_path in sorted((SRC / "app/apis" / op.group / op.api / "sql").glob("*.sql")):
        relative = sql_path.relative_to(ROOT).as_posix()
        operations = sql_operations(sql_path.read_text(encoding="utf-8"))
        accesses += [
            CrudAccess(op.operation_id, f"slotkeeper.{table_name}", access, relative, 1)
            for table_name, table_accesses in operations.items()
            if table_name in tables
            for access in sorted(table_accesses)
        ]
    return accesses


def identity_accesses(op: Operation) -> list[CrudAccess]:
    """routerの`Depends(...)`で注入するidentity依存を、宣言行つきで返す。"""
    from tools.generate_external_crud import SERVICE_CONFIGS

    router_path = SRC / "app/apis" / op.group / op.api / "router.py"
    lines = router_path.read_text(encoding="utf-8").splitlines()
    return [
        CrudAccess(
            op.operation_id,
            f"identity.{method.resource}",
            method.operation,
            router_path.relative_to(ROOT).as_posix(),
            line_number,
        )
        for dependency, method in sorted(SERVICE_CONFIGS["identity"].router_dependencies.items())
        for line_number, text in enumerate(lines, start=1)
        if f"Depends({dependency})" in text
    ]


def crud_rows(accesses: Iterable[CrudAccess]) -> list[dict[str, Any]]:
    """operation×resourceごとに1rowへまとめ、read/writeの根拠を分けて持つ。"""
    grouped: dict[tuple[str, str], list[CrudAccess]] = {}
    for access in accesses:
        grouped.setdefault((access.operation_id, access.resource), []).append(access)
    rows: list[dict[str, Any]] = []
    for (operation_id, resource), items in sorted(grouped.items()):
        evidence = {
            (item.path, item.line, "read" if item.access == "R" else "write") for item in items
        }
        rows.append(
            {
                "operation": operation_id,
                "resource": resource,
                "access": [letter for letter in "CRUD" if letter in {i.access for i in items}],
                "evidence": [
                    {"path": path, "line": line, "role": role}
                    for path, line, role in sorted(evidence)
                ],
            }
        )
    return rows


def crud_model() -> dict[str, Any]:
    """SQLとrouter依存からAPI×保存先のCRUDを根拠行つきで組み立てる。"""
    from tools.generate_db_table_specs import parse_tables

    tables = set(parse_tables((SRC / "db/ddl.sql").read_text(encoding="utf-8")))
    operations = contract_operations()
    rows = crud_rows(
        access
        for op in operations
        for access in [*sql_accesses(op, tables), *identity_accesses(op)]
    )
    missing = sorted({op.operation_id for op in operations} - {row["operation"] for row in rows})
    if missing:
        # lazunexの規約では全operationがSQLを持つため、アクセスなしは未解決として拒否する。
        raise ValueError("CRUDを解決できないoperation: " + ", ".join(missing))
    return {
        "schema_version": 1,
        "operations": [op.operation_id for op in operations],
        "rows": rows,
        "no_access": {},
        "unresolved": [],
    }


def crud_renderings(model: dict[str, Any]) -> dict[str, bytes]:
    """dev-standardの共通検査器と同じ射影でCSV・表・図・根拠を作る。"""
    sys.path.insert(0, str(SKILL_SCRIPTS))
    try:
        module = importlib.import_module("check_design")
    finally:
        sys.path.remove(str(SKILL_SCRIPTS))
    render: Callable[[dict[str, Any]], dict[str, bytes]] = module.__dict__["crud_renderings"]
    return render(model)


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
    files[f"{CRUD_MODEL_DIR}/operation-documents.json"] = dump(
        {op.operation_id: f"{op.group}/{op.api}" for op in contract_operations()}
    )
    for kind in ("csv", "table", "diagram", "evidence"):
        files[f"{CRUD_MODEL_DIR}/{CRUD_FILES[kind]}"] = rendered[kind].decode()
    files["index.md"] = (
        "# CRUD設計\n\n"
        "lazunex形式のAPI×DB CRUD表は`db_crud.gen.csv`、API×identity CRUD表は"
        "`identity_crud.gen.csv`に出力する。\n\n"
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


FRONTEND_API_CALL = re.compile(r'client\.(GET|POST|PUT)\(\s*"([^"]+)"')
FRONTEND_EFFECT = re.compile(
    r"useEffect\(\(\) => \{\s*(?:const [^;]+;\s*)?if \(([^)]*)\) void (\w+)\([^)]*\);"
    r"\s*\}, \[([^\]]*)\]\)"
)
DETAIL_SCREEN = ("予約詳細・履歴（?reservation=ID）", "本人・管理者（APIで判定）")


def frontend_text(name: str) -> str:
    return (ROOT / "frontend/src" / name).read_text(encoding="utf-8")


def api_calls_by_function(app: str) -> dict[str, list[str]]:
    """App.tsxのasync関数ごとに、openapi-fetchで呼ぶAPIを列挙する。"""
    functions: dict[str, list[str]] = {}
    for match in re.finditer(r"async function (\w+)\(", app):
        body = app[match.end() : app.find("\n  }\n", match.end())]
        functions[match.group(1)] = [
            method + " " + path for method, path in FRONTEND_API_CALL.findall(body)
        ]
    return functions


def screen_section(text: str, functions: Mapping[str, list[str]]) -> list[str]:
    """画面区画の見出し・入力・操作関数・呼出APIを抽出する。"""
    titles = [title.strip() for title in re.findall(r"<h2>([^<{]+)", text)]
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


def screen_rows(app: str, functions: Mapping[str, list[str]]) -> list[list[str]]:
    nav = re.search(r'<nav aria-label="メインメニュー">(.*?)</nav>', app, re.S)
    if not nav:
        raise ValueError("未対応の画面構造: frontend/src/App.tsx にメインメニューがない")
    tabs = dict(re.findall(r'\["(\w+)", "([^"]+)"\]', nav.group(1)))
    admin_only = set(re.findall(r'admin \? \[\["(\w+)"', nav.group(1)))
    starts = [(m.start(), m.group(1)) for m in re.finditer(r'\{tab === "(\w+)"', app)]
    detail = app.find('aria-label="予約詳細"')
    if not tabs or len(starts) != len(tabs) or detail < 0:
        raise ValueError("未対応の画面構造: タブと画面区画の対応を抽出できない")
    ends = [start for start, _tab in starts[1:]] + [detail]
    rows = [
        [
            f"{tabs[tab]}（{tab}）",
            "管理者" if tab in admin_only else "認証済み利用者",
            *screen_section(app[start:end], functions),
        ]
        for (start, tab), end in zip(starts, ends, strict=True)
    ]
    rows.append([*DETAIL_SCREEN, *screen_section(app[detail:], functions)])
    return rows


def effect_rows(app: str, functions: Mapping[str, list[str]]) -> list[list[str]]:
    return [
        [re.sub(r"\s+", " ", condition).strip(), name, ", ".join(functions[name]) or "—", deps]
        for condition, name, deps in FRONTEND_EFFECT.findall(app)
        if name in functions
    ]


def error_rows(logic: str) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    catalog = re.search(r"const codes[^{]*\{(.*?)\};", logic, re.S)
    if not catalog:
        raise ValueError("未対応の例外表示: frontend/src/logic.ts に業務コード表がない")
    codes = re.findall(r"(\w+):\s*\n?\s*\"([^\"]+)\"", catalog.group(1))
    statuses = re.findall(r"(\d{3}): \"([^\"]+)\"", logic)
    return codes, [*statuses, ("通信失敗", "入力を保持して再送を案内")]


def storage_notes(auth: str, app: str) -> list[str]:
    notes = (
        ("tokenはInMemoryWebStorage（メモリ）", "InMemoryWebStorage" in auth),
        ("PKCE stateはsessionStorage", "sessionStorage" in auth),
        ("localStorage不使用", "localStorage" not in auth + app),
    )
    return [name for name, found in notes if found]


def source_rows() -> list[list[str]]:
    rows: list[list[str]] = []
    for file in sorted((ROOT / "frontend/src").rglob("*")):
        if file.suffix not in (".tsx", ".ts", ".astro", ".css") or "generated" in file.parts:
            continue
        text = file.read_text(encoding="utf-8")
        calls = re.findall(r'client\.(?:GET|POST|PUT)\(\s*["\']([^"\']+)', text)
        rows.append(
            [
                file.relative_to(ROOT).as_posix(),
                ", ".join(re.findall(r"useState[^;]+", text)) or "—",
                ", ".join(calls) or "—",
            ]
        )
    return rows


def frontend_design() -> str:
    """App.tsxの画面区画・入力・呼出API・権限と、logic.tsの例外表示を抽出する。"""
    app = frontend_text("App.tsx")
    functions = api_calls_by_function(app)
    codes, statuses = error_rows(frontend_text("logic.ts"))
    return (
        "# 画面・状態・呼出API\n\n"
        "静的Astroページ1枚にReact islandを載せ、画面区画はメニューとURLのreservation引数で"
        "切り替える。権限はUI表示に加え、APIの403で最終判定する。\n\n## 画面一覧\n\n"
        + table(
            ["画面", "表示権限", "見出し", "入力", "操作関数", "呼出API"],
            screen_rows(app, functions),
        )
        + "\n## 状態変化による取得\n\n"
        + table(["条件", "関数", "呼出API", "再実行の依存"], effect_rows(app, functions))
        + "\n## 例外表示（業務コード）\n\n"
        + table(["コード", "表示"], codes)
        + "\n## 例外表示（HTTP status）\n\n"
        + table(["status", "表示"], statuses)
        + "\n## 認証情報の保持\n\n"
        + "".join("- " + item + "\n" for item in storage_notes(frontend_text("auth.ts"), app))
        + "\n## source別の状態宣言\n\n"
        + table(["source", "状態宣言", "API"], source_rows())
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


def step_name(node: ast.AST) -> str | None:
    """`Step("name", ...)`/`pytest_step("name", ...)`の検査名を返す。"""
    if not isinstance(node, ast.Call) or ast.unparse(node.func) not in {"Step", "pytest_step"}:
        return None
    first = node.args[0] if node.args else None
    if isinstance(first, ast.Constant) and isinstance(first.value, str):
        return first.value
    return None


def verify_checks() -> set[str]:
    """verify入口のStep定義から検査名をASTで取得する。"""
    tree = ast.parse((SRC / "tools/project/verify.py").read_text(encoding="utf-8"))
    return {name for node in ast.walk(tree) for name in [step_name(node)] if name is not None}


def criterion_checks(item: Mapping[str, Any], criterion_id: str, checks: set[str]) -> list[str]:
    """検査で確認する要件は、verify入口に実在する検査名を持つことを確認する。"""
    evidence = re.findall(r"verify:([\w-]+)", item["verification"]["evidence"])
    missing = sorted(set(evidence) - checks)
    if not evidence or missing:
        raise ValueError("検査名の欠落: " + criterion_id + " " + ", ".join(missing))
    return evidence


def trace_row(
    item: Mapping[str, Any],
    criterion: Mapping[str, Any],
    tests: Sequence[Mapping[str, Any]],
    checks: set[str],
) -> dict[str, Any]:
    linked = [case for case in tests if criterion["id"] in case["tags"]]
    evidence: list[str] = []
    if item["verification"]["method"] == "check":
        evidence = criterion_checks(item, criterion["id"], checks)
    elif not linked:
        raise ValueError("受入条件にテストがない: " + criterion["id"])
    outside = sorted({case["file"] for case in linked} - set(item["traces"]["tests"]))
    if outside:
        raise ValueError("要件traceにないテスト: " + criterion["id"] + " " + ", ".join(outside))
    return {
        "requirement": item["id"],
        "criterion": criterion["id"],
        "gwt": f"Given {criterion['given']} When {criterion['when']} Then {criterion['then']}",
        "tests": [case["id"] for case in linked],
        "checks": evidence,
    }


def trace_rows(tests: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """要件→受入条件→実在テストID・検査名を照合し、欠落と未知タグを拒否する。"""
    catalog = json.loads((ROOT / "spec/requirements/requirements.json").read_text("utf-8"))
    active = [item for item in catalog["requirements"] if item["status"] == "active"]
    criteria = {criterion["id"] for item in active for criterion in item["acceptance_criteria"]}
    unknown = sorted({tag for case in tests for tag in case["tags"]} - criteria)
    if unknown:
        raise ValueError("要件にない受入条件タグ: " + ", ".join(unknown))
    checks = verify_checks()
    return [
        trace_row(item, criterion, tests, checks)
        for item in active
        for criterion in item["acceptance_criteria"]
    ]


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
    existing: set[str] = set()
    if out.exists():
        existing = {path.relative_to(out).as_posix() for path in out.rglob("*") if path.is_file()}
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
