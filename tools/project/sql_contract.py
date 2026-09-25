"""SQL投影と結果型をDDLに照合し、未対応式を拒否する。"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, cast, get_args, get_origin

import sqlglot
from pydantic import AwareDatetime
from slotkeeper import domain, query_models
from sqlglot import exp


def validate(path: Path, root: Path) -> None:
    """列名・型・NULLと返却モデルの集合を比較する。"""
    source = path.read_text()
    model_name = source.splitlines()[2].removeprefix("-- result: ")
    parsed = sqlglot.parse_one(re.sub(r"%\((\w+)\)s", r":\1", source), read="postgres")
    schema: dict[str, dict[str, tuple[type[Any], bool]]] = {}
    for stmt in sqlglot.parse((root / "backend/schema.sql").read_text(), read="postgres"):
        if (
            isinstance(stmt, exp.Create)
            and stmt.args.get("kind") == "TABLE"
            and isinstance(stmt.this, exp.Schema)
        ):
            columns: dict[str, tuple[type[Any], bool]] = {}
            for column in stmt.this.expressions:
                if not isinstance(column, exp.ColumnDef):
                    continue
                kind = column.args["kind"].sql(dialect="postgres").lower()
                python_type = (
                    str
                    if kind.startswith(("varchar", "text"))
                    else bool
                    if kind == "boolean"
                    else datetime
                    if kind.startswith("timestamp")
                    else int
                    if kind in ("integer", "bigint", "int")
                    else None
                )
                if python_type is None:
                    raise ValueError("未対応列型: " + kind)
                nullable = not any(
                    isinstance(
                        c.kind, (exp.NotNullColumnConstraint, exp.PrimaryKeyColumnConstraint)
                    )
                    for c in column.args.get("constraints", [])
                )
                columns[column.name] = (python_type, nullable)
            schema[stmt.this.this.name] = columns
    tables = {t.alias_or_name: t.name for t in parsed.find_all(exp.Table)}
    if set(tables.values()) - set(schema):
        raise ValueError("未定義テーブル: " + str(path))
    if model_name == "none":
        if isinstance(parsed, exp.Select) or parsed.args.get("returning"):
            raise ValueError("結果破棄: " + str(path))
        return
    model = getattr(domain, model_name, None) or getattr(query_models, model_name, None)
    if model is None:
        raise ValueError("未知の結果型: " + model_name)
    fields: dict[str, Any] = model.model_fields
    projection = (
        parsed.expressions
        if isinstance(parsed, exp.Select)
        else parsed.args["returning"].expressions
    )
    if {p.alias_or_name for p in projection} != set(fields):
        raise ValueError("投影と結果型の列集合が不一致: " + str(path))
    for expression in projection:
        node = expression.this if isinstance(expression, exp.Alias) else expression
        if isinstance(node, exp.Count):
            actual_type, nullable = int, False
        elif isinstance(node, exp.Column):
            if node.name == "*":
                raise ValueError("SELECT * は型正本にできない")
            candidates = [
                cols[node.name]
                for table, cols in schema.items()
                if table in tables.values() and node.name in cols
            ]
            if not candidates or len(set(candidates)) != 1:
                raise ValueError("列型を一意に解決できない: " + node.name)
            actual_type, nullable = candidates[0]
        else:
            raise ValueError("未対応投影式: " + node.sql())
        annotation = fields[expression.alias_or_name].annotation
        expected_type: Any = (
            cast(Any, type(get_args(annotation)[0]))
            if get_origin(annotation) is Literal
            else annotation
        )
        if expected_type is AwareDatetime:
            expected_type = datetime
        expected_nullable = type(None) in get_args(expected_type)
        if expected_nullable:
            expected_type = next(t for t in get_args(expected_type) if t is not type(None))
        if expected_type is not actual_type or nullable != expected_nullable:
            raise ValueError("列型/NULL不一致: " + str(path) + ":" + expression.alias_or_name)
