"""生成器と証跡変換が欠落、余剰、混入を拒否することを検査する。"""

import json
import shutil

import pytest

from tools.project import design, evidence, queries


def test_result_identity_and_unexecuted():
    """Given collectorの2件 When 片方だけ成功 Then 他方をnot-runとして残す。"""
    items = evidence.match([{"id": "a"}, {"id": "b"}], {"a": {"status": "passed"}})
    assert [i["status"] for i in items] == ["passed", "not-run"]
    with pytest.raises(ValueError):
        evidence.match([{"id": "a"}], {"foreign": {"status": "passed"}})
    with pytest.raises(ValueError):
        evidence.match([{"id": "a"}, {"id": "a"}], {})


@pytest.mark.parametrize("status", ["failed", "skipped", "flaky", "missing", "not-run"])
def test_nonpassing_states_preserved(status):
    """Given 非成功状態 When 変換 Then passedへ変えない。"""
    assert evidence.match([{"id": "a"}], {"a": {"status": status}})[0]["status"] == status


@pytest.mark.parametrize("change", ["missing", "extra", "type"])
def test_schema_dictionary_mutations(tmp_path, monkeypatch, change):
    """Given 列辞書欠落・余剰かDDL変更 When schema抽出 Then 不整合拒否か型変化を検出。"""
    shutil.copytree(design.ROOT / "backend", tmp_path / "backend")
    monkeypatch.setattr(design, "ROOT", tmp_path)
    file = tmp_path / "backend/schema-labels.json"
    data = json.loads(file.read_text())
    if change == "missing":
        del data["resources"]["columns"]["name"]
    elif change == "extra":
        data["resources"]["columns"]["ghost"] = "存在しない"
    else:
        original = design.schema()
        ddl = tmp_path / "backend/schema.sql"
        ddl.write_text(ddl.read_text().replace("name varchar(100)", "name varchar(90)"))
        assert design.schema() != original
        return
    file.write_text(json.dumps(data))
    with pytest.raises((ValueError, KeyError)):
        design.schema()


def test_sql_parameter_mutation(tmp_path, monkeypatch):
    """Given SQLの束縛変数だけ変更 When 型生成 Then 引数不一致を拒否。"""
    shutil.copytree(queries.ROOT / "backend/src", tmp_path / "backend/src")
    monkeypatch.setattr(queries, "ROOT", tmp_path)
    file = tmp_path / "backend/src/slotkeeper/operations/resources_create/sql/create.sql"
    file.write_text(file.read_text().replace("%(name)s", "%(renamed)s"))
    with pytest.raises(ValueError, match="束縛引数"):
        queries.generate()


def test_deterministic_generation():
    """Given 同一source When 2回のクリーン生成 Then byte集合が一致する。"""
    first, manifest = design.generate()
    second, other = design.generate()
    assert first == second
    assert manifest == other
    assert len(first) > 50


def test_sequence_tracks_conditions():
    """Given 分岐とqueryの順序変更 When AST図生成 Then 図が変化する。"""
    import ast

    one = design.sequence(
        ast.parse("if active:\n q.create(c,p)\nelse:\n raise DomainError('inactive')").body
    )
    two = design.sequence(ast.parse("if not active:\n q.create(c,p)").body)
    assert one != two
    assert "alt active" in one and "else その他" in one
