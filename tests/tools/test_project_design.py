"""dev-standard設計adapterが欠落・余剰・未対応を成功扱いしないことを検査する。"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

import pytest

from tools.project import design


def test_data_capability_is_deterministic() -> None:
    """Given 同一のDDL When dataの設計を2回クリーン生成 Then byte集合が一致する。 [TECH-DESIGN-AC]"""
    first = design.rendered_files(design.CAPABILITY_BY_NAME["data"])
    second = design.rendered_files(design.CAPABILITY_BY_NAME["data"])

    assert first == second
    assert "er.gen.md" in first
    assert json.loads(first["report.json"])["unsupported_surfaces"] == []


def test_drift_reports_manual_edit_and_stale_file(tmp_path: Path) -> None:
    """Given 生成物の手編集と旧帳票の残存 When drift検査 Then 変更と余剰を報告し既存fileを書き換えない。 [TECH-DESIGN-AC]"""
    (tmp_path / "a.md").write_text("手編集\n", encoding="utf-8")
    (tmp_path / "old.md").write_text("旧帳票\n", encoding="utf-8")

    found = design.drift({"a.md": "生成\n", "b.md": "新規\n"}, tmp_path)

    assert found == ["a.md", "b.md", "old.md"]
    assert (tmp_path / "a.md").read_text(encoding="utf-8") == "手編集\n"


def test_write_owned_root_replaces_only_owned_contents(tmp_path: Path) -> None:
    """Given 旧生成物がある所有root When 再生成 Then 旧fileを残さず新しい集合だけにする。 [TECH-DESIGN-AC]"""
    (tmp_path / "stale").mkdir()
    (tmp_path / "stale/old.md").write_text("旧\n", encoding="utf-8")

    design.write_owned_root({"new/index.md": "# 新\n"}, tmp_path)

    assert sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*.md")) == [
        "new/index.md"
    ]


def test_repeat_sections_reads_profile_grammar() -> None:
    """Given profileの繰返し節 When 帳票見出しを解析 Then 実装由来の見出しを列挙する。 [TECH-DESIGN-AC]"""
    grammar: list[dict[str, Any]] = [
        {"level": 2, "title": "固定"},
        {"repeat": "items", "level": 3, "children": [{"level": 4, "title": "子"}], "min": 0},
    ]
    body = "# 題\n\n## 固定\n\n### A\n\n#### 子\n\n### B\n\n#### 子\n\n```\n### code\n```\n"

    assert design.repeat_sections(body, grammar) == {"items": ["A", "B"]}


def test_repeat_sections_rejects_unsupported_structure() -> None:
    """Given profileにない見出し When 帳票を解析 Then 空の成功にせず未対応として拒否する。 [TECH-DESIGN-AC]"""
    grammar: list[dict[str, Any]] = [{"level": 2, "title": "固定"}]

    with pytest.raises(ValueError, match="未対応の章構成"):
        design.repeat_sections("# 題\n\n## 固定\n\n## 想定外\n", grammar)
    with pytest.raises(ValueError, match="未対応の章構成"):
        design.repeat_sections("# 題\n\n## 別名\n", grammar)


def test_added_route_without_contract_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    """Given 契約のないrouteの追加 When API設計を生成 Then 実登録集合との不一致として拒否する。 [TECH-DESIGN-AC]"""
    operations = design.contract_operations()
    registered = {op.operation_id for op in operations} | set(design.PLATFORM_ROUTES)
    files = dict.fromkeys(design.PLATFORM_ROUTES.values(), "")
    monkeypatch.setattr(design, "registered_operation_ids", lambda: registered | {"extra"})

    with pytest.raises(ValueError, match="extra"):
        design.check_registered_routes(operations, files)

    monkeypatch.setattr(design, "registered_operation_ids", lambda: registered)
    with pytest.raises(ValueError, match="health"):
        design.check_registered_routes(operations, {})


def test_crud_rows_split_read_and_write_evidence() -> None:
    """Given 同じ保存先への読取りと更新 When CRUDを集約 Then 1rowでread/writeの根拠を分ける。 [TECH-DESIGN-AC]"""
    accesses = [
        design.CrudAccess("op", "slotkeeper.t", "U", "sql/002.sql", 1),
        design.CrudAccess("op", "slotkeeper.t", "R", "sql/001.sql", 1),
    ]

    assert design.crud_rows(accesses) == [
        {
            "operation": "op",
            "resource": "slotkeeper.t",
            "access": ["R", "U"],
            "evidence": [
                {"path": "sql/001.sql", "line": 1, "role": "read"},
                {"path": "sql/002.sql", "line": 1, "role": "write"},
            ],
        }
    ]


def test_crud_model_matches_common_projection() -> None:
    """Given 実装のSQLとrouter依存 When CRUD modelを生成 Then 全operationが根拠つきで射影できる。 [TECH-DESIGN-AC]"""
    model = design.crud_model()
    rendered = design.crud_renderings(model)

    assert {row["operation"] for row in model["rows"]} == set(model["operations"])
    assert ("createReservation", "slotkeeper.reservations") in {
        (row["operation"], row["resource"]) for row in model["rows"]
    }
    assert "identity.jwks_signing_key" in rendered["csv"].decode()


def test_sql_target_change_changes_crud_projection(monkeypatch: pytest.MonkeyPatch) -> None:
    """Given 生成済みCRUD When SQLの更新先が変わる Then CRUD model・表・CSVが変化する。 [TECH-DESIGN-AC]"""
    baseline = design.crud_renderings(design.crud_model())
    original = design.sql_accesses

    def moved(op: design.Operation, tables: set[str]) -> list[design.CrudAccess]:
        return [
            design.CrudAccess(a.operation_id, "slotkeeper.users", a.access, a.path, a.line)
            if a.resource == "slotkeeper.reservation_events"
            else a
            for a in original(op, tables)
        ]

    monkeypatch.setattr(design, "sql_accesses", moved)
    changed = design.crud_renderings(design.crud_model())

    assert changed["csv"] != baseline["csv"]
    assert changed["table"] != baseline["table"]


def test_database_model_marks_logical_references() -> None:
    """Given DSQL向けの論理FK When DB探索modelを生成 Then アプリ保証の参照として区別する。 [TECH-DESIGN-AC]"""
    relations = design.database_model()["relations"]

    assert {
        "from": "reservations.resource_id",
        "to": "resources.resource_id",
        "kind": "application",
        "guarantee": design.LOGICAL_REFERENCE_GUARANTEE,
    } in relations


def test_frontend_without_menu_is_unsupported(monkeypatch: pytest.MonkeyPatch) -> None:
    """Given メインメニューのない画面 When 画面設計を生成 Then 未対応として拒否する。 [TECH-DESIGN-AC]"""
    original = design.frontend_text

    def without_menu(name: str) -> str:
        return "export default function App() {}" if name == "App.tsx" else original(name)

    monkeypatch.setattr(design, "frontend_text", without_menu)

    with pytest.raises(ValueError, match="未対応の画面構造"):
        design.frontend_design()


def test_trace_rejects_missing_and_unknown_tests() -> None:
    """Given 受入条件に対応するテスト When テスト欠落・未知タグ Then 要件traceの欠落として拒否する。 [TECH-DESIGN-AC]"""
    tests = design.tagged_tests()
    assert design.trace_rows(tests)

    with pytest.raises(ValueError, match="要件にない受入条件タグ"):
        design.trace_rows(
            [*tests, {"id": "x::y", "file": "x", "narrative": "", "tags": ["NO-99-AC"]}]
        )
    with pytest.raises(ValueError, match="受入条件にテストがない"):
        design.trace_rows([case for case in tests if "SLOT-01-AC" not in case["tags"]])
    outside = {"id": "x::y", "file": "outside.py", "narrative": "", "tags": ["SLOT-01-AC"]}
    with pytest.raises(ValueError, match="要件traceにないテスト"):
        design.trace_rows([*tests, outside])


def test_verify_checks_cover_requirement_evidence() -> None:
    """Given 検査で確認する要件 When verify入口を解析 Then 参照する検査名がすべて実在する。 [TECH-DESIGN-AC]"""
    checks = design.verify_checks()

    assert {"package", "backend", "e2e", "openapi-types", "performance"} <= checks
    assert design.step_name(ast.parse('Step(name, ("x",))', mode="eval").body) is None
    assert design.step_name(ast.parse('Step("lint", ("x",))', mode="eval").body) == "lint"
