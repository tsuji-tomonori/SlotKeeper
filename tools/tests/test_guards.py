"""生成器と証跡変換が欠落、余剰、混入を拒否することを検査する。"""

import json
import shutil

import pytest

from tools.project import design, evidence, queries


def test_result_identity_and_unexecuted():
    """Given collectorの2件 When 片方だけ成功 Then 他方をnot-runとして残す。 [TECH-QUALITY-AC]"""
    items = evidence.match([{"id": "a"}, {"id": "b"}], {"a": {"status": "passed"}})
    assert [i["status"] for i in items] == ["passed", "not-run"]
    with pytest.raises(ValueError):
        evidence.match([{"id": "a"}], {"foreign": {"status": "passed"}})
    with pytest.raises(ValueError):
        evidence.match([{"id": "a"}, {"id": "a"}], {})


@pytest.mark.parametrize("status", ["failed", "skipped", "flaky", "missing", "not-run"])
def test_nonpassing_states_preserved(status):
    """Given 非成功状態 When 変換 Then passedへ変えない。 [TECH-QUALITY-AC]"""
    assert evidence.match([{"id": "a"}], {"a": {"status": status}})[0]["status"] == status


@pytest.mark.parametrize("change", ["missing", "extra", "type"])
def test_schema_dictionary_mutations(tmp_path, monkeypatch, change):
    """Given 列辞書欠落・余剰かDDL変更 When schema抽出 Then 不整合拒否か型変化を検出。 [TECH-DESIGN-AC]"""
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
    """Given SQLの束縛変数だけ変更 When 型生成 Then 引数不一致を拒否。 [TECH-DESIGN-AC]"""
    shutil.copytree(queries.ROOT / "backend", tmp_path / "backend")
    monkeypatch.setattr(queries, "ROOT", tmp_path)
    file = tmp_path / "backend/src/slotkeeper/operations/resources_create/sql/create.sql"
    file.write_text(file.read_text().replace("%(name)s", "%(renamed)s"))
    with pytest.raises(ValueError, match="束縛引数"):
        queries.generate()


def test_deterministic_generation():
    """Given 同一source When 2回のクリーン生成 Then byte集合が一致する。 [TECH-DESIGN-AC]"""
    first, manifest = design.generate()
    second, other = design.generate()
    assert first == second
    assert manifest == other
    assert len(first) > 50


def test_sequence_tracks_conditions():
    """Given 分岐とqueryの順序変更 When AST図生成 Then 図が変化する。 [TECH-DESIGN-AC]"""
    import ast

    one = design.sequence(
        ast.parse("if active:\n q.create(c,p)\nelse:\n raise DomainError('inactive')").body
    )
    two = design.sequence(ast.parse("if not active:\n q.create(c,p)").body)
    assert one != two
    assert "alt active" in one and "else その他" in one


@pytest.fixture(scope="module")
def baseline():
    """現在sourceからのクリーン生成物。各負例はこれとの差で検出を確かめる。"""
    files, _ = design.generate()
    return files


def write(root, files):
    for path, content in files.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(content)


def extra_route(tmp_path, monkeypatch, body):
    """一時moduleのendpointを実appへ登録し、生成器にsource解析させる。"""
    import importlib.util

    from slotkeeper.app import app

    module_file = tmp_path / "extra_endpoint.py"
    module_file.write_text(body)
    spec = importlib.util.spec_from_file_location("extra_endpoint", module_file)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    before = list(app.router.routes)
    app.add_api_route("/extra", module.endpoint, operation_id="extra_probe", tags=["system"])
    app.openapi_schema = None
    return app, before


def restore(app, before):
    app.router.routes[:] = before
    app.openapi_schema = None


def test_added_api_without_design_update(tmp_path, monkeypatch, baseline):
    """Given 生成済み設計 When API追加後に設計を更新せず検査 Then 新operationの6帳票欠落とOpenAPI変更を検出する。 [TECH-DESIGN-AC]"""
    write(tmp_path / "out", baseline)
    app, before = extra_route(
        tmp_path,
        monkeypatch,
        'def endpoint() -> dict[str, str]:\n    """追加された稼働確認。"""\n    return {}\n',
    )
    try:
        files, _ = design.generate()
    finally:
        restore(app, before)
    found = design.drift(files, tmp_path / "out")
    assert "openapi.json" in found
    assert {"api/system/extra_probe/" + k + ".md" for k in design.KINDS} <= set(found)


def test_unsupported_endpoint_syntax(tmp_path, monkeypatch):
    """Given adapterが解析しないtry構文のendpoint When 設計生成 Then 空の成功にせず未対応として拒否する。 [TECH-DESIGN-AC]"""
    app, before = extra_route(
        tmp_path,
        monkeypatch,
        'def endpoint() -> dict[str, str]:\n    """例外処理を持つ。"""\n'
        "    try:\n        return {}\n    except ValueError:\n        return {}\n",
    )
    try:
        with pytest.raises(ValueError, match="未対応endpoint構文"):
            design.generate()
    finally:
        restore(app, before)


def test_sql_target_change_updates_crud(monkeypatch, baseline):
    """Given 生成済みCRUD When SQLの更新先を変更 Then CRUD model・表・CSVのdriftを検出する。 [TECH-DESIGN-AC]"""
    from pathlib import Path

    from tools.project import queries as query_module

    original = Path.read_text

    def mutated(self, *args, **kwargs):
        text = original(self, *args, **kwargs)
        if self.name == "event.sql" and "reservations_create" in self.as_posix():
            return text.replace("slotkeeper.reservation_events", "slotkeeper.users")
        return text

    monkeypatch.setattr(Path, "read_text", mutated)
    # 型付きSQLの一致検査は別の負例で扱い、ここではCRUDの追従だけを確かめる。
    monkeypatch.setattr(query_module, "generate", lambda: {})
    files, _ = design.generate()
    for name in ["crud/model.json", "crud/matrix.md", "crud/matrix.csv"]:
        assert files[name] != baseline[name]
    assert "slotkeeper.users" in files["api/reservations/reservations_create/query.md"]


def test_manual_edit_and_stale_document(tmp_path, baseline):
    """Given 生成物の手編集と旧帳票の残存 When drift検査 Then 変更と余剰を報告し既存fileを書き換えない。 [TECH-DESIGN-AC]"""
    out = tmp_path / "out"
    write(out, baseline)
    edited = out / "DATA.md"
    edited.write_text(edited.read_text() + "\n手編集\n")
    stale = out / "api/reservations/reservations_create/unit-tests.md"
    stale.write_text("旧命名の帳票")
    found = design.drift(baseline, out)
    assert found == ["DATA.md", "api/reservations/reservations_create/unit-tests.md"]
    assert edited.read_text().endswith("手編集\n")
    assert stale.exists()


def test_missing_test_for_requirement(monkeypatch):
    """Given 受入条件に対応するテスト When テスト削除・タグ欠落・未知タグ Then 要件traceの欠落として拒否する。 [TECH-DESIGN-AC]"""
    original = design.tagged_tests()
    without = [c for c in original if "SLOT-AC03" not in c["tags"]]
    monkeypatch.setattr(design, "tagged_tests", lambda: without)
    with pytest.raises(ValueError, match="SLOT-AC03"):
        design.trace()
    unknown = original + [{"id": "x::y", "file": "x", "narrative": "", "tags": ["SLOT-AC99"]}]
    monkeypatch.setattr(design, "tagged_tests", lambda: unknown)
    with pytest.raises(ValueError, match="SLOT-AC99"):
        design.trace()
    moved = [
        {**c, "file": "backend/tests/test_other.py"} if "SLOT-AC03" in c["tags"] else c
        for c in original
    ]
    monkeypatch.setattr(design, "tagged_tests", lambda: moved)
    with pytest.raises(ValueError, match="要件traceにないテスト"):
        design.trace()


def test_missing_collector_result_is_not_run():
    """Given collectorにあるが結果のないcase When 変換 Then not-runとし成功へ数えない。 [TECH-QUALITY-AC]"""
    items = evidence.match(
        [{"id": "backend/tests/test_reservations.py::test_twenty_concurrent"}], {}
    )
    assert items[0]["status"] == "not-run"


def test_foreign_run_rejected(tmp_path, monkeypatch):
    """Given 別runのcollector原本 When ポータル証跡を構築 Then 混入として拒否する。 [TECH-QUALITY-AC]"""
    art = tmp_path / "artifacts"
    art.mkdir()
    (art / "pytest-backend-results.json").write_text(
        json.dumps({"revision": "old", "runId": "1", "inventory": [], "results": {}})
    )
    monkeypatch.setattr(evidence, "ART", art)
    monkeypatch.setattr(evidence, "ROOT", tmp_path)
    with pytest.raises(ValueError, match="revision/run"):
        evidence.build("new", "2", [], "full")


@pytest.mark.parametrize("name", ["raw.log", "storage-state.txt", "dump.sql"])
def test_publication_allowlist(tmp_path, monkeypatch, name):
    """Given 公開サイトに生ログ・storage state・DB dump When 公開集合を検査 Then 公開を拒否する。 [TECH-PRIVACY-AC]"""
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("<!doctype html>")
    (site / name).write_text("secret")
    monkeypatch.setattr(evidence, "ART", tmp_path)
    with pytest.raises(ValueError, match="allowlist外"):
        evidence.verify_site()
    assert not (tmp_path / "site-ready").exists()


def test_symlink_not_published(tmp_path, monkeypatch):
    """Given 公開サイト内のsymlink When 公開集合を検査 Then 外部fileを公開しない。 [TECH-PRIVACY-AC]"""
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("<!doctype html>")
    (site / "link.json").symlink_to(tmp_path / "outside.json")
    monkeypatch.setattr(evidence, "ART", tmp_path)
    with pytest.raises(ValueError, match="symlink"):
        evidence.verify_site()
