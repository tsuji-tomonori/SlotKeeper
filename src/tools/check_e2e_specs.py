from __future__ import annotations

import argparse
import importlib
from collections.abc import Sequence
from pathlib import Path

import yaml

from tools.check_e2e_case_evidences import check_case_evidences
from tools.e2e_models import (
    COMPONENT_IDS,
    FLOW_ID,
    FLOW_STEPS,
    TARGET_CASES,
    TARGET_DIMENSIONS,
    as_mapping,
    as_sequence,
    build_component_variants,
    component_actions,
    flow_document,
    load_yaml,
    matrix_config,
    parse_variant,
    scalar_text,
    string_list,
)

COMPONENT_FILES = (
    "component.manual.yaml",
    "actions.manual.yaml",
    "states.manual.yaml",
    "data.manual.yaml",
    "evidences.manual.yaml",
    "bindings.manual.yaml",
)
RULE_FILES = ("renderer.manual.yaml", "matrix.manual.yaml", "pruning.manual.yaml")
REQUIRED_STRATEGIES = ("component_variant_coverage", "interaction_coverage")
REQUIRED_ASSERTION_TYPES = ("every_variant_has_case", "every_target_has_case")
SCENARIO_HEADINGS = (
    "## 1. 対象",
    "## 2. 処理概要",
    "## 3. 処理詳細",
    "### 前提条件",
    "### Step 1:",
    "#### 目的",
    "#### 操作",
    "#### 確認観点",
    "#### エビデンス",
    "## 4. 後続確認",
)


def referenced_step_files(flow_root: Path) -> set[str]:
    """bindingsとevidence collectorが参照するstep YAMLを列挙する。"""
    refs: set[str] = set()
    for component_id in COMPONENT_IDS:
        component_root = flow_root / "components" / component_id
        bindings = load_yaml(component_root / "bindings.manual.yaml")
        for binding in as_sequence(bindings.get("bindings")):
            for step in as_sequence(as_mapping(binding).get("steps")):
                refs.add(scalar_text(as_mapping(step).get("ref")))
        evidences = load_yaml(component_root / "evidences.manual.yaml")
        for evidence in as_sequence(evidences.get("evidences")):
            refs.add(scalar_text(as_mapping(as_mapping(evidence).get("collector")).get("step")))
    return {ref for ref in refs if ref.startswith("steps/")}


def required_paths(flow_root: Path) -> list[Path]:
    paths = [
        flow_root / "flow.manual.yaml",
        flow_root / "case-list_gen.md",
        flow_root / "case-variant-index_gen.md",
        flow_root / "pruned-cases_gen.csv",
        *(flow_root / "rules" / filename for filename in RULE_FILES),
        *(
            flow_root / "targets" / dimension.directory / f"{target.target_id}.target.manual.yaml"
            for dimension in TARGET_DIMENSIONS
            for target in dimension.targets
        ),
        *(flow_root / "cases" / case.filename for case in TARGET_CASES),
        *(
            flow_root / "templates" / "steps" / f"{step.template}.manual.yaml"
            for step in FLOW_STEPS
        ),
        *(
            flow_root / "components" / component_id / filename
            for component_id in COMPONENT_IDS
            for filename in COMPONENT_FILES
        ),
    ]
    if all((flow_root / "components" / component_id).exists() for component_id in COMPONENT_IDS):
        paths.extend(flow_root / ref for ref in sorted(referenced_step_files(flow_root)))
    return paths


def check_paths(flow_root: Path) -> list[str]:
    errors: list[str] = []
    for path in required_paths(flow_root):
        if not path.exists():
            errors.append(f"missing: {path.as_posix()}")
            continue
        if path.suffix == ".yaml":
            try:
                yaml.safe_load(path.read_text(encoding="utf-8"))
            except yaml.YAMLError as exc:
                errors.append(f"invalid yaml: {path.as_posix()}: {exc}")
    return errors


def check_templates(flow_root: Path) -> list[str]:
    """step templateのoperationと参照sampleが実装と一致することを確認する。"""
    errors: list[str] = []
    for step in FLOW_STEPS:
        path = flow_root / "templates" / "steps" / f"{step.template}.manual.yaml"
        if not path.exists():
            continue
        document = load_yaml(path)
        template = as_mapping(document.get("template") or document.get("step_template"))
        if template.get("method") != step.method or template.get("path") != step.path:
            errors.append(f"template endpoint mismatch: {step.template}")
        operation_id = template.get("operation_id")
        if operation_id is not None and operation_id != step.operation:
            errors.append(f"template operation mismatch: {step.template}")
        body = as_mapping(as_mapping(document.get("request")).get("body"))
        sample = as_mapping(body.get("from_sample"))
        if sample:
            module_name = scalar_text(sample.get("module"))
            object_name = scalar_text(sample.get("object"))
            try:
                module = importlib.import_module(module_name)
            except ImportError:
                errors.append(f"template sample module missing: {step.template}: {module_name}")
                continue
            if not hasattr(module, object_name):
                errors.append(f"template sample object missing: {step.template}: {object_name}")
    return errors


def check_flow() -> list[str]:
    errors: list[str] = []
    flow = flow_document()
    known_components = set(COMPONENT_IDS)
    for component_id in COMPONENT_IDS:
        if not component_actions(component_id):
            errors.append(f"component has no actions: {component_id}")
    for item in as_sequence(flow.get("component_dependencies")):
        dependency = as_mapping(item)
        dependency_id = scalar_text(dependency.get("id"))
        source = scalar_text(as_mapping(dependency.get("from")).get("component"))
        if source not in known_components:
            errors.append(f"dependency {dependency_id} has unknown component: {source}")
        for requirement in as_sequence(dependency.get("requires")):
            required = scalar_text(as_mapping(requirement).get("component"))
            if required not in known_components:
                errors.append(f"dependency {dependency_id} requires unknown component: {required}")
    for component_id, spec in as_mapping(flow.get("default_variants")).items():
        if component_id not in known_components:
            errors.append(f"default variant has unknown component: {component_id}")
        if not as_mapping(spec).get("state"):
            errors.append(f"default variant missing state: {component_id}")
    for component_id in string_list(matrix_config().get("components")):
        if component_id not in known_components:
            errors.append(f"matrix has unknown component: {component_id}")
    for dimension in TARGET_DIMENSIONS:
        if dimension.canonical not in {target.target_id for target in dimension.targets}:
            errors.append(f"canonical target is not declared: {dimension.canonical}")
    return errors


def check_matrix_rules(flow_root: Path) -> list[str]:
    matrix_path = flow_root / "rules" / "matrix.manual.yaml"
    if not matrix_path.exists():
        return []
    errors: list[str] = []
    matrix = load_yaml(matrix_path)
    dimensions = as_mapping(
        as_mapping(matrix.get("component_variant_generation")).get("dimensions")
    )
    for component_id in COMPONENT_IDS:
        if component_id not in dimensions:
            errors.append(f"matrix missing component dimension: {component_id}")
    strategies = {
        as_mapping(strategy).get("id")
        for strategy in as_sequence(
            as_mapping(matrix.get("component_case_generation")).get("strategies")
        )
    }
    for strategy_id in REQUIRED_STRATEGIES:
        if strategy_id not in strategies:
            errors.append(f"matrix missing component case strategy: {strategy_id}")
    assertion_types = {
        as_mapping(assertion).get("type")
        for assertion in as_sequence(matrix.get("coverage_assertions"))
    }
    for assertion_type in REQUIRED_ASSERTION_TYPES:
        if assertion_type not in assertion_types:
            errors.append(f"matrix missing coverage assertion: {assertion_type}")
    return errors


def check_coverage() -> list[str]:
    errors: list[str] = []
    variant_ids = {variant.variant_id for variant in build_component_variants()}
    covered_goal_variants = {target_case.goal_variant for target_case in TARGET_CASES}
    covered_selected_variants = {
        variant_id for target_case in TARGET_CASES for variant_id in target_case.selected_variants
    }
    errors.extend(
        f"component variant missing target case: {variant_id}"
        for variant_id in sorted(variant_ids - covered_selected_variants)
    )
    errors.extend(
        f"target case has unknown component variant: {variant_id}"
        for variant_id in sorted(covered_goal_variants - variant_ids)
    )
    errors.extend(
        f"target case has unknown prerequisite variant: {target_case.case_id}: {variant_id}"
        for target_case in TARGET_CASES
        for variant_id in target_case.selected_variants
        if variant_id not in variant_ids
    )
    goal_targets = {
        target_id
        for target_case in TARGET_CASES
        for _dimension, target_id in parse_variant(target_case.goal_variant).targets
    }
    errors.extend(
        f"target {dimension.dimension_id} missing target case: {target.target_id}"
        for dimension in TARGET_DIMENSIONS
        for target in dimension.targets
        if target.target_id not in goal_targets
    )
    assertion = as_mapping(matrix_config().get("assertion"))
    assertion_component = scalar_text(assertion.get("component"))
    covered_states = {
        parse_variant(target_case.goal_variant).state_id
        for target_case in TARGET_CASES
        if target_case.goal_component == assertion_component
    }
    errors.extend(
        f"{assertion_component} state missing target case: {state_id}"
        for state_id in as_mapping(assertion.get("expected_by_state"))
        if state_id not in covered_states
    )
    return errors


def check_rendered_cases(flow_root: Path) -> list[str]:
    errors: list[str] = []
    case_list_path = flow_root / "case-list_gen.md"
    if case_list_path.exists():
        case_list = case_list_path.read_text(encoding="utf-8")
        errors.extend(
            f"case-list missing link: cases/{case.filename}"
            for case in TARGET_CASES
            if f"cases/{case.filename}" not in case_list
        )
    placeholders = string_list(flow_document().get("required_placeholders"))
    for case in TARGET_CASES:
        scenario_path = flow_root / "cases" / case.filename
        if not scenario_path.exists():
            continue
        scenario = scenario_path.read_text(encoding="utf-8")
        errors.extend(
            f"{case.case_id}: scenario does not keep {placeholder} placeholder"
            for placeholder in placeholders
            if placeholder not in scenario
        )
        if case.case_id not in scenario:
            errors.append(f"{case.case_id}: scenario title does not include case id")
        errors.extend(
            f"{case.case_id}: scenario missing heading {heading}"
            for heading in SCENARIO_HEADINGS
            if heading not in scenario
        )
    return errors


def check_specs(root: Path = Path("docs/spec/50.e2e")) -> list[str]:
    flow_root = root / FLOW_ID
    errors = check_paths(flow_root)
    errors.extend(check_templates(flow_root))
    errors.extend(check_flow())
    errors.extend(check_matrix_rules(flow_root))
    errors.extend(check_coverage())
    errors.extend(check_rendered_cases(flow_root))
    errors.extend(check_case_evidences(root))
    return errors


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.parse_args(argv)
    errors = check_specs()
    if errors:
        print("\n".join(errors))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
