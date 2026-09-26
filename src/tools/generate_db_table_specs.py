from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

import sqlglot
from sqlglot import exp

from tools.generation_io import check_outputs, write_outputs


@dataclass(frozen=True)
class Column:
    name: str
    data_type: str
    nullable: bool
    primary_key: bool = False
    unique: bool = False
    references: str | None = None
    comment: str = ""
    logical_reference: bool = False

    def with_comment(self, comment: str) -> Column:
        return replace(self, comment=comment)


@dataclass
class Table:
    name: str
    columns: list[Column]
    comment: str = ""
    table_constraints: list[str] = field(default_factory=lambda: [])


def unescape_sql_comment(value: str) -> str:
    return value.replace("''", "'").replace("\n", " ").strip()


def identifier_name(expression: Any) -> str:
    return str(expression.name)


def table_name(expression: Any) -> str:
    if isinstance(expression, exp.Schema):
        return table_name(expression.this)
    if isinstance(expression, exp.Table):
        return str(expression.name)
    return str(expression.name)


def literal_value(expression: Any | None) -> str:
    if isinstance(expression, exp.Literal):
        return unescape_sql_comment(expression.this)
    return ""


def render_sql(expression: Any) -> str:
    return " ".join(expression.sql(dialect="postgres").split())


def reference_label(reference: exp.Reference) -> str:
    target = reference.this
    if isinstance(target, exp.Schema):
        name = table_name(target)
        columns = ", ".join(identifier_name(column) for column in target.expressions)
        return f"{name}({columns})" if columns else name
    return render_sql(reference)


def parse_column(definition: exp.ColumnDef) -> Column:
    primary_key = False
    not_null = False
    unique = False
    references: str | None = None

    for constraint in definition.constraints:
        kind = constraint.kind
        if isinstance(kind, exp.PrimaryKeyColumnConstraint):
            primary_key = True
        elif isinstance(kind, exp.NotNullColumnConstraint):
            not_null = True
        elif isinstance(kind, exp.UniqueColumnConstraint):
            unique = True
        elif isinstance(kind, exp.Reference):
            references = reference_label(kind)

    return Column(
        name=identifier_name(definition.this),
        data_type=render_sql(definition.kind) if definition.kind is not None else "",
        nullable=not not_null and not primary_key,
        primary_key=primary_key,
        unique=unique or primary_key,
        references=references,
    )


def parse_comments(
    expressions: list[Any],
) -> tuple[dict[str, str], dict[tuple[str, str], str]]:
    table_comments: dict[str, str] = {}
    column_comments: dict[tuple[str, str], str] = {}

    for expression in expressions:
        if not isinstance(expression, exp.Comment):
            continue

        comment = literal_value(expression.expression)
        if expression.args.get("kind") == "TABLE":
            table_comments[table_name(expression.this)] = comment
        elif expression.args.get("kind") == "COLUMN" and isinstance(expression.this, exp.Column):
            column_comments[(expression.this.table, expression.this.name)] = comment

    return table_comments, column_comments


CREATE_TABLE_RE = re.compile(
    r"^\s*CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?P<name>[\w.\"]+)", re.I
)
LOGICAL_REFERENCE_RE = re.compile(
    r"^\s*(?P<column>\w+)\s[^\n]*--\s*REFERENCES\s+(?P<table>[\w.\"]+)\s*\((?P<target>\w+)\)"
)
PRIMARY_KEY_CONSTRAINT_RE = re.compile(r"^PRIMARY KEY\s*\((?P<columns>[^)]*)\)$", re.I)


def parse_logical_references(sql: str) -> dict[tuple[str, str], str]:
    """物理FKを作れないDB向けに、列定義の `-- REFERENCES table (column)` を論理参照として読む。"""
    references: dict[tuple[str, str], str] = {}
    current_table: str | None = None
    for line in sql.splitlines():
        create = CREATE_TABLE_RE.match(line)
        if create:
            current_table = create.group("name").split(".")[-1].strip('"')
            continue
        reference = LOGICAL_REFERENCE_RE.match(line)
        if current_table is not None and reference:
            target_table = reference.group("table").split(".")[-1].strip('"')
            references[(current_table, reference.group("column"))] = (
                f"{target_table}({reference.group('target')})"
            )
    return references


def apply_table_constraints(table: Table, logical: dict[tuple[str, str], str]) -> None:
    """複合主キーと論理参照を列へ反映する。"""
    primary_columns: set[str] = set()
    for constraint in table.table_constraints:
        match = PRIMARY_KEY_CONSTRAINT_RE.match(constraint)
        if match:
            primary_columns.update(part.strip() for part in match.group("columns").split(","))
    table.columns = [
        replace(
            column,
            primary_key=column.primary_key or column.name in primary_columns,
            nullable=column.nullable and column.name not in primary_columns,
            references=column.references or logical.get((table.name, column.name)),
            logical_reference=column.references is None and (table.name, column.name) in logical,
        )
        for column in table.columns
    ]


def uncomment_comment_on_statements(sql: str) -> str:
    return re.sub(r"^\s*--\s+(COMMENT ON .*)$", r"\1", sql, flags=re.MULTILINE)


def table_like_source(expressions: list[Any]) -> str | None:
    for expression in expressions:
        if isinstance(expression, exp.LikeProperty):
            return table_name(expression.this)
    return None


def parse_create_table(statement: exp.Create) -> tuple[str, list[Column], list[str], str | None]:
    properties = statement.args.get("properties")
    if isinstance(statement.this, exp.Table) and isinstance(properties, exp.Properties):
        like_source = table_like_source(properties.expressions)
        if like_source:
            return table_name(statement.this), [], [], like_source

    if not isinstance(statement.this, exp.Schema):
        raise ValueError(f"CREATE TABLE statement has no schema: {statement.sql()}")

    schema = statement.this
    name = table_name(schema)
    like_source = table_like_source(schema.expressions)
    if like_source:
        return name, [], [], like_source

    columns: list[Column] = []
    constraints: list[str] = []
    for expression in schema.expressions:
        if isinstance(expression, exp.ColumnDef):
            columns.append(parse_column(expression))
        else:
            constraints.append(render_sql(expression))

    return name, columns, constraints, None


def parse_tables(sql: str) -> dict[str, Table]:
    expressions = [expression for expression in sqlglot.parse(sql, read="postgres") if expression]
    comment_expressions = [
        expression
        for expression in sqlglot.parse(uncomment_comment_on_statements(sql), read="postgres")
        if expression
    ]
    table_comments, column_comments = parse_comments(comment_expressions)
    tables: dict[str, Table] = {}

    for statement in expressions:
        if not isinstance(statement, exp.Create) or statement.kind != "TABLE":
            continue

        table_name, columns, constraints, like_source = parse_create_table(statement)
        if like_source:
            source = tables.get(like_source)
            if source is None:
                raise ValueError(f"LIKE source table is not defined: {like_source}")
            tables[table_name] = Table(
                name=table_name,
                columns=list(source.columns),
                table_constraints=list(source.table_constraints),
            )
        else:
            tables[table_name] = Table(
                name=table_name,
                columns=columns,
                table_constraints=constraints,
            )

    logical = parse_logical_references(sql)
    for table in tables.values():
        apply_table_constraints(table, logical)
        table.comment = table_comments.get(table.name, "")
        table.columns = [
            column.with_comment(column_comments.get((table.name, column.name), column.comment))
            for column in table.columns
        ]

    return tables


def key_label(column: Column) -> str:
    labels: list[str] = []
    if column.primary_key:
        labels.append("PK")
    if column.unique and not column.primary_key:
        labels.append("UNIQUE")
    if column.references and column.logical_reference:
        labels.append(f"論理FK -> {column.references}")
    elif column.references:
        labels.append(f"FK -> {column.references}")
    return ", ".join(labels)


def markdown_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def render_table_markdown(table: Table) -> str:
    lines = [
        f"# {table.name}",
        "",
        table.comment or "説明未設定。",
        "",
        "| カラム | 型 | NULL許可 | キー | 説明 |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]

    for column in table.columns:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{column.name}`",
                    f"`{column.data_type}`",
                    "YES" if column.nullable else "NO",
                    markdown_escape(key_label(column)),
                    markdown_escape(column.comment),
                ]
            )
            + " |"
        )

    if table.table_constraints:
        lines.extend(["", "## テーブル制約", ""])
        lines.extend(f"- `{markdown_escape(constraint)}`" for constraint in table.table_constraints)

    lines.append("")
    return "\n".join(lines)


def render_table_specs(tables: dict[str, Table], output_dir: Path) -> dict[Path, str]:
    return {
        output_dir / f"{table_name}.gen.md": render_table_markdown(tables[table_name])
        for table_name in sorted(tables)
    }


def write_table_specs(tables: dict[str, Table], output_dir: Path) -> list[Path]:
    rendered = render_table_specs(tables, output_dir)
    write_outputs(rendered)
    return list(rendered)


def generate(ddl_path: Path, output_dir: Path) -> list[Path]:
    sql = ddl_path.read_text(encoding="utf-8")
    tables = parse_tables(sql)
    return write_table_specs(tables, output_dir)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate Markdown table specs from DDL.")
    parser.add_argument("--ddl", type=Path, default=Path("src/db/ddl.sql"))
    parser.add_argument("--output-dir", type=Path, default=Path("docs/spec/20.db/tables"))
    parser.add_argument("--check", action="store_true")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    tables = parse_tables(args.ddl.read_text(encoding="utf-8"))
    rendered = render_table_specs(tables, args.output_dir)
    if args.check:
        return check_outputs(rendered)
    write_outputs(rendered)
    print(f"Generated {len(rendered)} table spec files.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
