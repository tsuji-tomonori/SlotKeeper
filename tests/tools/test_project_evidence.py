"""証跡変換が未実行・別run混入・公開外fileを成功扱いしないことを検査する。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.project import evidence


def test_result_identity_and_unexecuted() -> None:
    """Given collectorの2件 When 片方だけ成功 Then 他方をnot-runとして残す。 [TECH-QUALITY-AC]"""
    inventory = [{"id": "a"}, {"id": "b"}]

    matched = evidence.match(inventory, {"a": {"status": "passed"}})

    assert [case["status"] for case in matched] == ["passed", "not-run"]


@pytest.mark.parametrize("status", ["failed", "skipped", "flaky"])
def test_nonpassing_states_preserved(status: str) -> None:
    """Given 非成功状態 When 変換 Then passedへ変えない。 [TECH-QUALITY-AC]"""
    matched = evidence.match([{"id": "a"}], {"a": {"status": status}})

    assert matched[0]["status"] == status


def test_result_outside_collector_is_rejected() -> None:
    """Given collector外の結果 When 変換 Then 混入として拒否する。 [TECH-QUALITY-AC]"""
    with pytest.raises(ValueError, match="collector"):
        evidence.match([{"id": "a"}], {"b": {"status": "passed"}})


def test_foreign_run_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Given 別runのcollector原本 When ポータル証跡を構築 Then 混入として拒否する。 [TECH-QUALITY-AC]"""
    monkeypatch.setattr(evidence, "ART", tmp_path)
    (tmp_path / "pytest-backend-results.json").write_text(
        json.dumps({"revision": "r1", "runId": "old", "inventory": [], "results": {}}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="異なるrevision/run"):
        evidence.pytest_tests("r1", "new")


def test_backend_coverage_below_goal_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Given 目標未満の業務コードcoverage When 証跡へ変換 Then 計測済みではなく失敗として示す。 [TECH-QUALITY-AC]"""
    monkeypatch.setattr(evidence, "ART", tmp_path)
    totals = {"covered_lines": 50, "num_statements": 100, "covered_branches": 9, "num_branches": 10}
    (tmp_path / "backend-coverage.json").write_text(json.dumps({"totals": totals}), "utf-8")

    rows = evidence.python_coverage("backend")

    assert [row["status"] for row in rows] == ["failed", "passed"]
    assert evidence.python_coverage("infra")[0]["status"] == "missing"


@pytest.mark.parametrize("name", ["api.log", "storage-state.txt", "dump.sql"])
def test_publication_allowlist(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str) -> None:
    """Given 公開サイトに生ログ・storage state・DB dump When 公開集合を検査 Then 公開を拒否する。 [TECH-PRIVACY-AC]"""
    monkeypatch.setattr(evidence, "ART", tmp_path)
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("<html></html>", encoding="utf-8")
    (site / name).write_text("secret", encoding="utf-8")

    with pytest.raises(ValueError, match="allowlist外"):
        evidence.verify_site()
    assert not (tmp_path / "site-ready").exists()


def test_symlink_not_published(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Given 公開サイト内のsymlink When 公開集合を検査 Then 外部fileを公開しない。 [TECH-PRIVACY-AC]"""
    monkeypatch.setattr(evidence, "ART", tmp_path)
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("<html></html>", encoding="utf-8")
    (tmp_path / "outside.json").write_text("{}", encoding="utf-8")
    (site / "link.json").symlink_to(tmp_path / "outside.json")

    with pytest.raises(ValueError, match="symlink"):
        evidence.verify_site()


def test_allowed_site_records_provenance(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Given allowlist内だけの公開サイト When 公開集合を検査 Then hashを記録して公開可能にする。 [TECH-PRIVACY-AC]"""
    monkeypatch.setattr(evidence, "ART", tmp_path)
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("<html></html>", encoding="utf-8")

    evidence.verify_site()

    assert "index.html" in json.loads((site / "provenance.json").read_text(encoding="utf-8"))
    assert (tmp_path / "site-ready").read_text(encoding="utf-8") == "ready\n"


def test_design_search_covers_lazunex_documents() -> None:
    """Given lazunex形式の設計Markdown When 検索索引を作る Then API帳票とE2E仕様を含める。 [TECH-DESIGN-AC]"""
    paths = {row["path"] for row in evidence.design_search_index()}

    assert "/design/40.apis/reservations/create_reservation/sequence_gen/" in paths
    assert "/design/50.e2e/reservation_lifecycle/case-list_gen/" in paths
