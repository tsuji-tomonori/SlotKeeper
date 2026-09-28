from __future__ import annotations

import shutil
from pathlib import Path

from tools.check_e2e_case_evidences import check_case_evidences
from tools.check_e2e_specs import check_specs
from tools.e2e_models import (
    FLOW_STEPS,
    TARGET_CASES,
    E2eMatrixAssertion,
    build_component_variants,
    parse_variant,
    prerequisites_for_component_variant,
)
from tools.generate_e2e_case_list import rendered_outputs as case_list_outputs
from tools.generate_e2e_scenarios import rendered_outputs as scenario_outputs

FLOW_ROOT = Path("docs/spec/50.e2e/reservation_lifecycle")


def case_for(goal_variant: str) -> str:
    return next(case.case_id for case in TARGET_CASES if case.goal_variant == goal_variant)


def test_e2e_flow_steps_cover_generated_api_list() -> None:
    api_list = Path("docs/spec/40.apis/apis_list_gen.md").read_text(encoding="utf-8")
    documented_endpoints = {
        f"{method} {path}"
        for method, path in (
            (columns[2].strip(" `"), columns[3].strip(" `"))
            for line in api_list.splitlines()
            if line.startswith("| `")
            for columns in [line.split("|")]
        )
    }
    flow_endpoints = {
        f"{step.method} {step.path}".replace("${", "{")
        for step in FLOW_STEPS
        if step.path.startswith("/")
    }

    assert documented_endpoints <= flow_endpoints


def test_component_variants_follow_target_coverage_policies() -> None:
    variant_ids = {variant.variant_id for variant in build_component_variants()}

    booked = {
        variant_id
        for variant_id in variant_ids
        if variant_id.startswith("reservation_booking.book_slot.") and "booked@" in variant_id
    }
    assert len(booked) == 6
    assert "reservation_booking.book_slot.member_B.equipment_A.booked@booking_default" in booked
    assert (
        "reservation_booking.book_slot.member_B.room_A.slot_taken@booking_default"
        not in variant_ids
    )
    assert "operation_trace.trace_request.traced@trace_not_found" in variant_ids


def test_prerequisites_resolve_dependencies_recursively() -> None:
    variant = parse_variant(
        "reservation_booking.book_slot.member_A.room_A.resource_inactive@booking_default"
    )

    assert prerequisites_for_component_variant(variant) == (
        "resource_catalog.register_resource.room_A.registered@resource_default",
        "resource_control.deactivate_resource.room_A.deactivated@deactivate_default",
    )

    future = parse_variant(
        "resource_control.deactivate_resource.room_A.future_reservation_exists@deactivate_default"
    )
    assert prerequisites_for_component_variant(future) == (
        "resource_catalog.register_resource.room_A.registered@resource_default",
        "reservation_booking.book_slot.member_A.room_A.booked@booking_default",
    )


def test_target_cases_skip_embedded_goals_and_carry_matrix_assertions() -> None:
    goals = {case.goal_variant for case in TARGET_CASES}

    assert len(TARGET_CASES) == 22
    assert "resource_catalog.register_resource.room_A.registered@resource_default" not in goals
    slot_taken = next(case for case in TARGET_CASES if "slot_taken" in case.goal_variant)
    assert slot_taken.matrix_assertions == (E2eMatrixAssertion("member_A", "room_A", "rejected"),)
    assert slot_taken.filename.startswith(f"{slot_taken.case_id}_reservation_booking_book_slot")


def test_e2e_case_list_links_scenarios(tmp_path: Path) -> None:
    rendered = case_list_outputs(tmp_path)
    content = rendered[tmp_path / "reservation_lifecycle/case-list_gen.md"]
    variant_index = rendered[tmp_path / "reservation_lifecycle/case-variant-index_gen.md"]
    pruned_csv = rendered[tmp_path / "reservation_lifecycle/pruned-cases_gen.csv"]

    for heading in (
        "## 0. 読み方",
        "## 1. 対象フロー",
        "## 2. Coverage summary",
        "## 3. コンポーネントごとの要素",
        "## 4. 枝刈り規則",
        "## 5. Component coverage summary",
        "## 6. Member x Resource matrix",
        "## 7. Cases by component",
        "## 8. Appendix",
    ):
        assert heading in content
    assert "| `reservation_booking` | 10 | 10 | 10 | 100.0% |" in content
    assert "| `resource_catalog` | 4 | 4 | 1 | 100.0% |" in content
    assert (
        "| 操作 | `book_slot` | 予約枠を予約する | 操作種別=コマンド, 既定状態=booked |" in content
    )
    assert "| 状態 | `slot_taken` | 重複枠の予約拒否 | 後続継続=いいえ |" in content
    assert (
        "| データ | `resource_default` | Room A / Room B / Equipment A | valid_resource, admin |"
    ) in content
    assert "| Member \\ Resource | Room A | Room B | Equipment A |" in content
    assert (
        f"| Member B | `{case_for('reservation_booking.book_slot.member_B.room_A.booked@booking_default')}` |"
        in content
    )
    assert "Member A x Room Aで予約枠を予約し、重複枠の予約拒否を確認する" in content
    assert "Room A rejected" in content
    assert "Goal Variant | Selected Variants | Matrix期待 |" in variant_index
    assert "`member_A` / `room_A`: `confirmed`" in variant_index
    assert pruned_csv.startswith(
        "case_id,resource_catalog[データ],resource_catalog[操作],resource_catalog[状態],"
    )
    assert pruned_csv.splitlines()[0].endswith("operation_trace[状態]")
    assert pruned_csv.count("\nTC_TARGET_") == len(TARGET_CASES)
    for step in FLOW_STEPS:
        assert f"`{step.operation}`" in content
    for target_case in TARGET_CASES:
        assert f"cases/{target_case.filename}" in content
        assert f"cases/{target_case.filename}" in variant_index


def test_e2e_scenarios_render_steps_settings_and_failure_triggers(tmp_path: Path) -> None:
    rendered = scenario_outputs(tmp_path)
    assert {path.name for path in rendered} == {case.filename for case in TARGET_CASES}

    slot_taken = next(case for case in TARGET_CASES if "slot_taken" in case.goal_variant)
    content = rendered[tmp_path / "reservation_lifecycle/cases" / slot_taken.filename]
    assert "${admin_token}" in content
    assert "${member_token}" in content
    assert slot_taken.goal_variant not in content
    assert "### Step 1: 資源を登録する" in content
    assert "### Step 3: 予約枠を予約する" in content
    assert f"| `request.body.name` | `E2E 会議室A {slot_taken.case_id}` |" in content
    assert f"| `request.headers.Idempotency-Key` | `{slot_taken.case_id}-member_A-room_A` |" in (
        content
    )
    assert "失敗を発生させるため、前の Step で予約済みの Room A 10:00-11:00枠" in content
    assert "| `error.precondition` | `Room A の10:00-11:00にconfirmed予約が存在する` |" in content
    assert "保存名は `" + slot_taken.case_id + "_E_slot_taken_member_A_room_A.json`" in content
    assert "Member A による Room A の予約は「予約が拒否される」として扱う。" in content

    trace = next(case for case in TARGET_CASES if case.goal_component == "operation_trace")
    trace_content = rendered[tmp_path / "reservation_lifecycle/cases" / trace.filename]
    assert "実行条件として、存在しない予約IDを指定して" in trace_content
    assert "取得方法は運用ログをtraceIdで検索する。" in trace_content
    assert "このケースでは予約確定の期待は設定しない。" in trace_content


def test_check_e2e_specs_accepts_repository_tree() -> None:
    assert check_specs() == []
    assert check_case_evidences() == []


def test_check_e2e_specs_reports_missing_generated_case(tmp_path: Path) -> None:
    shutil.copytree(FLOW_ROOT, tmp_path / "reservation_lifecycle")
    (tmp_path / "reservation_lifecycle" / "cases" / TARGET_CASES[0].filename).unlink()

    errors = check_specs(tmp_path)

    assert errors == [
        f"missing: {(tmp_path / 'reservation_lifecycle/cases' / TARGET_CASES[0].filename).as_posix()}"
    ]
