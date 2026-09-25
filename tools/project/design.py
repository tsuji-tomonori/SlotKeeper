"""OpenAPI、Python AST、SQL AST、画面sourceとCDK合成物から設計を生成する。"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import inspect
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, cast

import sqlglot
from sqlglot import exp

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "backend/src"), str(ROOT)]
OUT = ROOT / "docs/design/generated"
KINDS = ["detail-design", "interface", "messages", "query", "sequence", "unit-test"]


def dump(value: object) -> str:
    """キー順を固定してUTF-8 JSONを作る。"""
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def table(headers: list[str], rows: list[list[object]]) -> str:
    """改行と区切り文字を安全に表へ変換する。"""
    return (
        "\n".join(
            ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
            + [
                "| "
                + " | ".join(str(v).replace("|", "&#124;").replace("\n", " ") for v in row)
                + " |"
                for row in rows
            ]
        )
        + "\n"
    )


def schema() -> dict[str, Any]:
    """DDLの実在列と和名辞書を照合し物理FKを推測しない。"""
    labels = json.loads((ROOT / "backend/schema-labels.json").read_text())
    tables: list[dict[str, Any]] = []
    for statement in sqlglot.parse((ROOT / "backend/schema.sql").read_text(), read="postgres"):
        if not isinstance(statement, exp.Create) or statement.args.get("kind") != "TABLE":
            continue
        item = statement.this
        if not isinstance(item, exp.Schema):
            raise ValueError("未対応DDL: " + statement.sql())
        name = item.this.name
        columns: list[dict[str, Any]] = []
        for column in item.expressions:
            if not isinstance(column, exp.ColumnDef):
                continue
            constraints = column.args.get("constraints", [])
            columns.append(
                {
                    "name": column.name,
                    "label": labels[name]["columns"][column.name],
                    "type": column.args["kind"].sql(dialect="postgres"),
                    "nullable": not any(
                        isinstance(
                            c.kind, (exp.NotNullColumnConstraint, exp.PrimaryKeyColumnConstraint)
                        )
                        for c in constraints
                    ),
                    "primary": any(
                        isinstance(c.kind, exp.PrimaryKeyColumnConstraint) for c in constraints
                    ),
                    "ddl": column.sql(dialect="postgres"),
                }
            )
        if set(labels[name]["columns"]) != {c["name"] for c in columns}:
            raise ValueError("列辞書不一致: " + name)
        tables.append(
            {
                "name": name,
                "label": labels[name]["name"],
                "columns": columns,
                "ddl": statement.sql(dialect="postgres", pretty=True),
            }
        )
    if set(labels) != {t["name"] for t in tables}:
        raise ValueError("テーブル辞書不一致")
    return {
        "tables": tables,
        "relations": json.loads((ROOT / "backend/logical-relations.json").read_text()),
    }


def test_cases() -> list[dict[str, str]]:
    """実在するpytest関数と自然言語の受入説明を取得する。"""
    cases: list[dict[str, str]] = []
    for file in sorted((ROOT / "backend/tests").glob("test_*.py")):
        for node in ast.walk(ast.parse(file.read_text())):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                narrative = ast.get_docstring(node)
                if not narrative or any(
                    word not in narrative for word in ["Given", "When", "Then"]
                ):
                    raise ValueError("GWT欠落: " + str(file) + ":" + node.name)
                cases.append(
                    {
                        "id": file.relative_to(ROOT).as_posix() + "::" + node.name,
                        "narrative": narrative,
                    }
                )
    return cases


def sequence(nodes: list[ast.stmt]) -> str:
    """endpointの実分岐とquery呼出しを順序どおりに図へ変換する。"""
    lines = [
        "sequenceDiagram",
        "participant E as endpoint",
        "participant Q as query",
        "participant D as transaction",
    ]

    functions = {
        n.name: n.body for n in nodes if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

    def visit(body: list[ast.stmt]) -> None:
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            elif isinstance(node, ast.If):
                condition = ast.unparse(node.test).replace("\n", " ").replace(";", ",")
                lines.append("alt " + condition)
                visit(node.body)
                if node.orelse:
                    lines.append("else その他")
                    visit(node.orelse)
                lines.append("end")
            elif isinstance(node, (ast.For, ast.While)):
                lines.append("loop " + ast.unparse(node).splitlines()[0])
                visit(node.body)
                lines.append("end")
            elif isinstance(node, ast.Raise):
                lines.append("E-->>E: " + ast.unparse(node).replace(";", ","))
            else:
                for call in ast.walk(node):
                    if not isinstance(call, ast.Call):
                        continue
                    name = ast.unparse(call.func)
                    if name.startswith("q.") and not name.endswith("Params"):
                        lines.append("E->>Q: " + name[2:])
                    elif name in ("require_admin", "require_owner", "validate_booking"):
                        lines.append("E->>E: " + name)
                    elif name == "transaction":
                        lines.append("E->>D: transaction開始")
                        lines.append("loop 上限付きOCC retry / 新snapshot")
                        if (
                            not call.args
                            or not isinstance(call.args[0], ast.Name)
                            or call.args[0].id not in functions
                        ):
                            raise ValueError("未対応transaction callback")
                        visit(functions[call.args[0].id])
                        lines.append("D-->>E: commit成功時のみ応答")
                        lines.append("end")

    visit(nodes)
    return "\n".join(lines) + "\n"


def generate() -> tuple[dict[str, str], dict[str, Any]]:
    """現在のsource集合を解析し、所有root内の全生成物を返す。"""
    from fastapi.routing import APIRoute
    from slotkeeper.app import app

    from tools.project.queries import generate as query_outputs

    for path, content in query_outputs().items():
        if not path.exists() or path.read_text() != content:
            raise ValueError("型付きSQL drift: " + str(path))
    openapi = app.openapi()
    files = {"openapi.json": dump(openapi)}
    db = schema()
    files["database.json"] = dump(db)
    files["DATA.md"] = (
        "# データ設計\n\n"
        + "\n".join(
            "## "
            + t["label"]
            + " / "
            + t["name"]
            + "\n\n"
            + table(
                ["和名", "物理名", "型", "NULL", "PK"],
                [
                    [c["label"], c["name"], c["type"], c["nullable"], c["primary"]]
                    for c in t["columns"]
                ],
            )
            + "\n```sql\n"
            + t["ddl"]
            + ";\n```\n"
            for t in db["tables"]
        )
        + "\n論理参照はbackend/logical-relations.jsonに宣言。物理FKは使用しない。\n"
    )
    cases = test_cases()
    files["TESTS.md"] = "# テスト設計\n\n" + table(
        ["実在テスト", "Given / When / Then"], [[c["id"], c["narrative"]] for c in cases]
    )
    operations: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    no_access: dict[str, str] = {}
    groups: dict[str, list[str]] = {}
    routes: list[APIRoute] = []

    def collect_routes(items: Any) -> None:
        for route in items:
            if isinstance(route, APIRoute):
                routes.append(route)
            elif hasattr(route, "original_router"):
                collect_routes(route.original_router.routes)

    collect_routes(app.routes)
    actual_ids = {route.operation_id for route in routes}
    contract_ids: set[str] = {
        str(cast(Any, value)["operationId"])
        for path in openapi["paths"].values()
        for value in path.values()
        if isinstance(value, dict) and "operationId" in value
    }
    if actual_ids != contract_ids:
        raise ValueError("実登録operationとOpenAPIの集合不一致")
    for route in sorted(routes, key=lambda r: r.operation_id or ""):
        operation = route.operation_id
        if not operation:
            raise ValueError("operation IDなし")
        group = str(route.tags[0])
        groups.setdefault(group, []).append(operation)
        source_file = Path(inspect.getfile(route.endpoint))
        source = source_file.read_text()
        tree = ast.parse(source)
        endpoint = next(
            n
            for n in tree.body
            if isinstance(n, ast.FunctionDef) and n.name == route.endpoint.__name__
        )
        if any(
            isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute)
            and n.func.attr in ("execute", "executemany", "commit", "rollback")
            for n in ast.walk(endpoint)
        ):
            raise ValueError("endpoint直接DB I/O: " + operation)
        for node in ast.walk(endpoint):
            if isinstance(node, (ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef, ast.Try)):
                raise ValueError("未対応endpoint構文: " + operation + ":" + type(node).__name__)
        prefix = "api/" + group + "/" + operation + "/"
        description = ast.get_docstring(endpoint) or ""
        if not description.strip():
            raise ValueError("処理説明なし: " + operation)
        contract = openapi["paths"][route.path][next(iter(route.methods or {"GET"})).lower()]
        queries: list[dict[str, Any]] = []
        for path in sorted(source_file.with_name("sql").glob("*.sql")):
            sql = path.read_text()
            sql_ast = sqlglot.parse_one(re.sub(r"%\((\w+)\)s", r":\1", sql), read="postgres")
            bindings = re.findall(r"q\.(\w+)\(", source)
            if path.stem not in bindings:
                raise ValueError("未接続SQL: " + str(path))
            changes = {exp.Insert: "C", exp.Update: "U", exp.Delete: "D"}
            access = next((v for cls, v in changes.items() if isinstance(sql_ast, cls)), None)
            target = sql_ast.this if access else None
            if isinstance(target, exp.Schema):
                target = target.this
            for t in sql_ast.find_all(exp.Table):
                table_name = t.db + "." + t.name if t.db else t.name
                mode = access if target is t else "R"
                existing = next(
                    (
                        r
                        for r in rows
                        if r["operation"] == operation and r["resource"] == table_name
                    ),
                    None,
                )
                evidence = {
                    "path": path.relative_to(ROOT).as_posix(),
                    "line": 4,
                    "role": "read" if mode == "R" else "write",
                }
                if existing:
                    existing["access"] = sorted(set(existing["access"] + [mode]))
                    existing["evidence"].append(evidence)
                else:
                    rows.append(
                        {
                            "operation": operation,
                            "resource": table_name,
                            "access": [mode],
                            "evidence": [evidence],
                        }
                    )
            queries.append(
                {
                    "id": path.stem,
                    "sql": sql,
                    "kind": sql_ast.key,
                    "tables": sorted({t.name for t in sql_ast.find_all(exp.Table)}),
                }
            )
        if not queries:
            no_access[operation] = "外部保存先にアクセスしないhealth"
        query_names = [q["id"] for q in queries]
        relevant = [
            c
            for c in cases
            if (
                "auth" in c["id"]
                or ("resource" in operation and "resource" in c["id"])
                or ("reservation" in operation and "test_reservations" in c["id"])
                or operation == "health"
                and "health" in c["id"]
            )
        ]
        if not relevant:
            relevant = [c for c in cases if "anonymous" in c["id"]]
        sections = {
            "responses": list(contract["responses"]),
            "samples": ["公開契約"],
            "messages": ["request_result"],
            "queries": query_names,
            "factors": ["入力・権限・状態・競合"],
            "cases": [c["id"] for c in relevant],
        }
        documents = {kind: "docs/design/generated/" + prefix + kind + ".md" for kind in KINDS}
        operation_info = {
            "id": operation,
            "group": group,
            "api": operation,
            "documents": documents,
            "sections": sections,
        }
        if not queries:
            operation_info["non_applicable"] = {"queries": "DBアクセスがない"}
        operations.append(operation_info)
        files[prefix + "index.md"] = (
            "# "
            + operation
            + "\n\n"
            + description
            + "\n\n"
            + "\n".join("- [" + k + "](" + k + ".md)" for k in KINDS)
            + "\n"
        )
        files[prefix + "detail-design.md"] = (
            "# "
            + operation
            + " / Detail Design\n\n## 1. 正常系入力\n\n"
            + dump(contract.get("requestBody", contract.get("parameters", [])))
            + "\n## 2. 正常系前提\n\n"
            + description
            + "\n\n## 3. 正常系リソース変更\n\n"
            + table(
                ["query", "操作", "対象"],
                [[q["id"], q["kind"], ", ".join(q["tables"])] for q in queries],
            )
            + "\n## 4. 正常系レスポンス\n\n```json\n"
            + dump(contract["responses"])
            + "```\n"
        )
        interface = "# " + operation + " / Interface\n"
        for title, value in [
            ("Headers", [p for p in contract.get("parameters", []) if p["in"] == "header"]),
            ("Path Parameters", [p for p in contract.get("parameters", []) if p["in"] == "path"]),
            ("Query Parameters", [p for p in contract.get("parameters", []) if p["in"] == "query"]),
            ("Data", contract.get("requestBody", {})),
        ]:
            interface += "\n## " + title + "\n\n```json\n" + dump(value) + "```\n"
        interface += "\n## Responses\n"
        for status, response in contract["responses"].items():
            interface += "\n##### " + status + "\n\n```json\n" + dump(response) + "```\n"
        interface += (
            "\n## Samples\n\n### 公開契約\n\n#### Request\n\n`"
            + next(iter(route.methods or {"GET"}))
            + " "
            + route.path
            + "`。入力例と型はOpenAPIを参照。\n\n#### Response\n\nOpenAPIのresponse schemaに従う。実応答はテスト証跡に記録する。\n"
        )
        files[prefix + "interface.md"] = interface
        files[prefix + "messages.md"] = (
            "# "
            + operation
            + " / Message\n\n## API\n\n"
            + operation
            + "\n\n## 生成・検証方針\n\napp.pyのHTTP middlewareとDomainError境界が所有。\n\n## メッセージ一覧\n\nrequest_result: 全HTTP結果。\n\n## ログ詳細\n\n### request_result\n\n#### 出力項目\n\nrequest_id:string / operation:string / status:int / elapsed_ms:number。目的、token、生例外は出力しない。\n\n## strict検証で要求する項目\n\n401認証、403権限、404存在、409業務・版、422入力、503再試行上限。ログと応答の要求IDを照合する。\n"
        )
        query_doc = "# " + operation + " / Query\n"
        for q in queries:
            headers = q["sql"].splitlines()
            query_doc += (
                "\n## "
                + q["id"]
                + "\n\n### SQL種別\n\n"
                + q["kind"]
                + "\n\n### SQLの概要\n\n"
                + headers[0][3:]
                + "\n\n### 利用するテーブル\n\n"
                + ", ".join(q["tables"])
                + "\n\n### 引数\n\n"
                + headers[1][3:]
                + "\n\n### 戻り値\n\n"
                + headers[2][3:]
                + "\n\n### 条件\n\n```sql\n"
                + q["sql"]
                + "```\n"
            )
        if not queries:
            query_doc += "\n該当なし（理由: DBアクセスがない）\n"
        files[prefix + "query.md"] = query_doc
        files[prefix + "sequence.md"] = (
            "# " + operation + " / Sequence\n\n```mermaid\n" + sequence(endpoint.body) + "```\n"
        )
        files[prefix + "unit-test.md"] = (
            "# "
            + operation
            + " / Unit Test\n\n## 0. endpoint層の暗黙処理\n\nFastAPI入力解析と認証依存を適用。\n\n## 1. 要因ごとの要素\n\n### 入力・権限・状態・競合\n\n実在ケースだけを列挙する。全組合せの網羅を意味しない。\n\n## 2. 組合せたテストケース一覧\n\n"
            + table(["ID", "受入説明"], [[c["id"], c["narrative"]] for c in relevant])
            + "\n## 3. テスト詳細\n"
            + "".join("\n### " + c["id"] + "\n\n" + c["narrative"] + "\n" for c in relevant)
        )
    files["operations.json"] = dump([op["id"] for op in operations])
    files["api/index.md"] = (
        "# API設計\n\n"
        + "\n".join("- [" + g + "](" + g + "/index.md)" for g in sorted(groups))
        + "\n"
    )
    for group, ids in groups.items():
        files["api/" + group + "/index.md"] = (
            "# "
            + group
            + "\n\n"
            + "\n".join("- [" + id + "](" + id + "/index.md)" for id in ids)
            + "\n"
        )
    model = {
        "schema_version": 1,
        "operations": sorted([op["id"] for op in operations]),
        "rows": sorted(rows, key=lambda r: (r["operation"], r["resource"])),
        "no_access": no_access,
        "unresolved": [],
    }
    spec = importlib.util.spec_from_file_location(
        "check_design",
        ROOT / ".agents/skills/generate-implementation-design/scripts/check_design.py",
    )
    if not spec or not spec.loader:
        raise RuntimeError("標準検査器がない")
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_design"] = module
    spec.loader.exec_module(module)
    files["crud/model.json"] = dump(model)
    renderings = module.crud_renderings(model)
    for kind, content in renderings.items():
        files[
            "crud/"
            + {
                "csv": "matrix.csv",
                "table": "matrix.md",
                "diagram": "diagram.md",
                "evidence": "evidence.json",
            }[kind]
        ] = content.decode()
    frontend: list[list[object]] = []
    for file in sorted((ROOT / "frontend/src").rglob("*")):
        if file.suffix not in (".tsx", ".ts", ".astro", ".css") or "generated" in file.parts:
            continue
        text = file.read_text()
        frontend.append(
            [
                file.relative_to(ROOT).as_posix(),
                ", ".join(re.findall(r"useState[^;]+", text)),
                ", ".join(re.findall(r'client\.(?:GET|POST|PUT)\(\s*["\']([^"\']+)', text)),
            ]
        )
    files["FRONTEND.md"] = "# 画面・状態・呼出API\n\n" + table(
        ["source", "状態宣言", "API"], frontend
    )
    with tempfile.TemporaryDirectory() as folder:
        import aws_cdk as cdk
        from aws_cdk.assertions import Template

        from infra.stack import SlotKeeperStack

        cdk_app = cdk.App(outdir=folder)
        stack = SlotKeeperStack(cdk_app, "SlotKeeper")
        template = Template.from_stack(stack).to_json()
    files["infra.json"] = dump(template)
    files["INFRA.md"] = "# 合成インフラ\n\n" + table(
        ["論理ID", "種別", "設定"],
        [
            [k, v["Type"], json.dumps(v.get("Properties", {}), ensure_ascii=False, sort_keys=True)]
            for k, v in sorted(template["Resources"].items())
        ],
    )
    files["OVERVIEW.md"] = (
        "# 全体構成\n\n静的Astro → HTTP API → FastAPI / Mangum → Aurora DSQL。ローカルはPostgreSQL Repeatable ReadとKeycloak。\n\n[API](api/index.md) · [DB](DATA.md) · [CRUD](crud/matrix.md) · [画面](FRONTEND.md) · [インフラ](INFRA.md) · [テスト](TESTS.md)\n"
    )
    sources: list[Path] = []
    for root in ["backend", "frontend/src", "infra", "tools/project", "tools/tests", "e2e"]:
        sources += [
            p
            for p in (ROOT / root).rglob("*")
            if p.is_file()
            and p.suffix in (".py", ".sql", ".json", ".ts", ".tsx", ".astro", ".css")
            and "__pycache__" not in p.parts
        ]
    sources += [ROOT / "compose.yaml", ROOT / "pyproject.toml", ROOT / "package.json"]
    files["sources.json"] = dump(
        {
            p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(set(sources))
        }
    )
    files["report.json"] = dump(
        {
            "configuration": "pass",
            "design_drift": "pass",
            "execution_tests": "not-run",
            "unsupported_surfaces": [],
        }
    )
    req_ids = ["TECH-DESIGN"]
    manifest = {
        "schema_version": 2,
        "requirements": "spec/requirements/requirements.json",
        "applicable_requirement_ids": req_ids,
        "reference_inventories": [".dev-standard/reference-adoption.json"],
        "surfaces": {
            s: {"status": "required", "capabilities": ["implementation"]}
            for s in ("api", "data", "frontend", "infra")
        },
        "capabilities": {
            "implementation": {
                "status": "required",
                "requirement_ids": req_ids,
                "sources": sorted(p.relative_to(ROOT).as_posix() for p in set(sources)),
                "generate": ["python", "tools/project/design.py"],
                "check": ["python", "tools/project/design.py", "--check"],
                "output_root": "docs/design/generated",
                "outputs": ["docs/design/generated/" + k for k in sorted(files)],
                "report": "docs/design/generated/report.json",
            }
        },
        "api": {
            "profile": ".agents/skills/generate-implementation-design/assets/api-document-profile-v1.json",
            "operation_inventory": "docs/design/generated/operations.json",
            "root": "docs/design/generated/api",
            "index": "docs/design/generated/api/index.md",
            "group_indexes": {g: "docs/design/generated/api/" + g + "/index.md" for g in groups},
            "api_indexes": {
                op["id"]: "docs/design/generated/api/" + op["group"] + "/" + op["id"] + "/index.md"
                for op in operations
            },
            "operations": operations,
        },
        "crud": {
            "model": "docs/design/generated/crud/model.json",
            **{
                k: "docs/design/generated/crud/" + v
                for k, v in {
                    "csv": "matrix.csv",
                    "table": "matrix.md",
                    "diagram": "diagram.md",
                    "evidence": "evidence.json",
                }.items()
            },
        },
    }
    return files, manifest


def main() -> None:
    """欠落・余剰・変更を非破壊checkし、明示更新だけで書き換える。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--manifest", action="store_true")
    args = parser.parse_args()
    files, manifest = generate()
    existing: set[str] = (
        {p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file()}
        if OUT.exists()
        else set()
    )
    if args.check:
        changed = [
            p for p, s in files.items() if not (OUT / p).exists() or (OUT / p).read_text() != s
        ]
        if changed or existing - set(files):
            raise SystemExit("設計drift: " + str(changed + sorted(existing - set(files))))
    else:
        if OUT.exists():
            shutil.rmtree(OUT)
        for p, s in files.items():
            (OUT / p).parent.mkdir(parents=True, exist_ok=True)
            (OUT / p).write_text(s)
        if args.manifest:
            (ROOT / ".dev-standard/design.json").write_text(dump(manifest))


if __name__ == "__main__":
    main()
