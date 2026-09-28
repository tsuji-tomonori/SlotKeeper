from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

import yaml

FLOW_ID = "reservation_lifecycle"
E2E_ROOT = Path("docs/spec/50.e2e")
E2E_SPEC_ROOT = E2E_ROOT / FLOW_ID


@dataclass(frozen=True)
class E2eStep:
    step_id: str
    operation: str
    method: str
    path: str
    template: str
    captures: tuple[str, ...] = ()


@dataclass(frozen=True)
class E2eTarget:
    dimension: str
    target_id: str
    title: str
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class E2eTargetDimension:
    dimension_id: str
    title: str
    directory: str
    canonical: str
    targets: tuple[E2eTarget, ...]


@dataclass(frozen=True)
class E2eMatrixAssertion:
    row_id: str
    column_id: str
    expected: str


@dataclass(frozen=True)
class E2eTargetCase:
    case_id: str
    title: str
    coverage_group: str
    goal_component: str
    goal_variant: str
    selected_variants: tuple[str, ...]
    matrix_assertions: tuple[E2eMatrixAssertion, ...] = ()

    @property
    def filename(self) -> str:
        slug = re.sub(r"[^0-9A-Za-z]+", "_", self.goal_variant).strip("_").lower()
        return f"{self.case_id}_{slug}.gen.md"


@dataclass(frozen=True)
class E2eComponentVariant:
    component_id: str
    action_id: str
    targets: tuple[tuple[str, str], ...]
    state_id: str
    data_id: str
    continue_flow: bool

    @property
    def variant_id(self) -> str:
        return variant_id_for(
            self.component_id,
            self.action_id,
            tuple(target_id for _dimension, target_id in self.targets),
            self.state_id,
            self.data_id,
        )

    def target(self, dimension: str) -> str | None:
        for target_dimension, target_id in self.targets:
            if target_dimension == dimension:
                return target_id
        return None


def variant_id_for(
    component: str,
    action: str,
    target_ids: Sequence[str],
    state: str,
    data_id: str,
) -> str:
    return f"{'.'.join([component, action, *target_ids, state])}@{data_id}"


def as_mapping(value: object) -> Mapping[str, object]:
    return cast(Mapping[str, object], value) if isinstance(value, Mapping) else {}


def as_sequence(value: object) -> tuple[object, ...]:
    if isinstance(value, list | tuple):
        return tuple(cast(list[object] | tuple[object, ...], value))
    return ()


def scalar_text(value: object, default: str = "-") -> str:
    return value if isinstance(value, str) else default


def string_list(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    return tuple(item for item in as_sequence(value) if isinstance(item, str))


def string_set(value: object) -> set[str]:
    return set(string_list(value))


def load_yaml(path: Path) -> Mapping[str, object]:
    return as_mapping(yaml.safe_load(path.read_text(encoding="utf-8")))


@cache
def flow_document() -> Mapping[str, object]:
    return load_yaml(E2E_SPEC_ROOT / "flow.manual.yaml")


def flow_section(key: str) -> Mapping[str, object]:
    return as_mapping(flow_document().get(key))


def flow_title() -> str:
    return scalar_text(flow_section("flow").get("title"), FLOW_ID)


def build_flow_steps() -> tuple[E2eStep, ...]:
    steps: list[E2eStep] = []
    for item in as_sequence(flow_document().get("steps")):
        step = as_mapping(item)
        steps.append(
            E2eStep(
                scalar_text(step.get("id")),
                scalar_text(step.get("operation_id")),
                scalar_text(step.get("method")),
                scalar_text(step.get("path")),
                scalar_text(step.get("template")),
                string_list(step.get("captures")),
            )
        )
    return tuple(steps)


def target_yaml(directory: str, target_id: str) -> Mapping[str, object]:
    return load_yaml(E2E_SPEC_ROOT / "targets" / directory / f"{target_id}.target.manual.yaml")


def build_target_dimensions() -> tuple[E2eTargetDimension, ...]:
    dimensions: list[E2eTargetDimension] = []
    for item in as_sequence(flow_document().get("target_dimensions")):
        dimension = as_mapping(item)
        dimension_id = scalar_text(dimension.get("id"))
        directory = scalar_text(dimension.get("directory"))
        targets: list[E2eTarget] = []
        for target_id in string_list(dimension.get("targets")):
            target = as_mapping(target_yaml(directory, target_id).get("target"))
            targets.append(
                E2eTarget(
                    dimension_id,
                    target_id,
                    scalar_text(target.get("title"), target_id),
                    string_list(target.get("tags")),
                )
            )
        dimensions.append(
            E2eTargetDimension(
                dimension_id,
                scalar_text(dimension.get("title"), dimension_id),
                directory,
                scalar_text(dimension.get("canonical")),
                tuple(targets),
            )
        )
    return tuple(dimensions)


def component_ids() -> tuple[str, ...]:
    return string_list(flow_document().get("component_sequence"))


FLOW_STEPS = build_flow_steps()
TARGET_DIMENSIONS = build_target_dimensions()
COMPONENT_IDS = component_ids()
DIMENSIONS_BY_ID = {dimension.dimension_id: dimension for dimension in TARGET_DIMENSIONS}
TARGETS_BY_ID = {
    target.target_id: target for dimension in TARGET_DIMENSIONS for target in dimension.targets
}


def target_title(target_id: str | None) -> str:
    if target_id is None:
        return "-"
    target = TARGETS_BY_ID.get(target_id)
    return target.title if target is not None else target_id


def target_defaults(target_id: str | None) -> Mapping[str, object]:
    target = TARGETS_BY_ID.get(target_id or "")
    if target is None:
        return {}
    directory = DIMENSIONS_BY_ID[target.dimension].directory
    return as_mapping(target_yaml(directory, target.target_id).get("defaults"))


def load_component_yaml(component_id: str, filename: str) -> Mapping[str, object]:
    return load_yaml(E2E_SPEC_ROOT / "components" / component_id / filename)


def component_items(component_id: str, filename: str, key: str) -> tuple[Mapping[str, object], ...]:
    return tuple(
        as_mapping(item)
        for item in as_sequence(load_component_yaml(component_id, filename).get(key))
    )


def component_actions(component_id: str) -> tuple[Mapping[str, object], ...]:
    return component_items(component_id, "actions.manual.yaml", "actions")


def component_states(component_id: str) -> tuple[Mapping[str, object], ...]:
    return component_items(component_id, "states.manual.yaml", "states")


def component_data_profiles(component_id: str) -> tuple[Mapping[str, object], ...]:
    return component_items(component_id, "data.manual.yaml", "data_profiles")


def item_by_id(items: Sequence[Mapping[str, object]], item_id: str) -> Mapping[str, object]:
    for item in items:
        if item.get("id") == item_id:
            return item
    return {}


def target_allowed(target_id: str, policy: str, dimension_id: str) -> bool:
    if policy == "all":
        return True
    canonical = DIMENSIONS_BY_ID[dimension_id].canonical
    if policy == "canonical_pair":
        return target_id == canonical
    if policy == f"canonical_{dimension_id}":
        return target_id == canonical
    return True


def target_coverage_policy(
    action: Mapping[str, object],
    state: Mapping[str, object],
    data_profile: Mapping[str, object],
) -> str:
    state_value = state.get("target_coverage")
    if isinstance(state_value, str):
        return state_value
    if state.get("continue_flow") is False:
        return "canonical_pair"
    for source in (data_profile, action):
        value = source.get("target_coverage")
        if isinstance(value, str):
            return value
    return "all"


def action_dimensions(action: Mapping[str, object]) -> tuple[str, ...]:
    requested = string_set(action.get("target"))
    return tuple(
        dimension.dimension_id
        for dimension in TARGET_DIMENSIONS
        if dimension.dimension_id in requested
    )


def action_targets(
    action: Mapping[str, object],
    policy: str = "all",
) -> tuple[tuple[tuple[str, str], ...], ...]:
    combinations: list[tuple[tuple[str, str], ...]] = [()]
    for dimension_id in action_dimensions(action):
        dimension = DIMENSIONS_BY_ID[dimension_id]
        combinations = [
            (*combination, (dimension_id, target.target_id))
            for combination in combinations
            for target in dimension.targets
            if target_allowed(target.target_id, policy, dimension_id)
        ]
    return tuple(combinations)


def compatible_with(value: str, allowed: object) -> bool:
    allowed_values = string_set(allowed)
    return not allowed_values or value in allowed_values


def action_state_compatible(action: Mapping[str, object], state: Mapping[str, object]) -> bool:
    action_id = scalar_text(action.get("id"))
    state_id = scalar_text(state.get("id"))
    return compatible_with(state_id, action.get("compatible_states")) and compatible_with(
        action_id, state.get("compatible_actions")
    )


def data_compatible(
    action: Mapping[str, object],
    state: Mapping[str, object],
    data_profile: Mapping[str, object],
) -> bool:
    action_id = scalar_text(action.get("id"))
    state_id = scalar_text(state.get("id"))
    data_tags = string_set(data_profile.get("tags"))
    required_tags = string_set(state.get("requires_data_tags"))
    return (
        compatible_with(action_id, data_profile.get("compatible_actions"))
        and compatible_with(state_id, data_profile.get("compatible_states"))
        and required_tags <= data_tags
    )


def standalone_case_enabled(
    action: Mapping[str, object],
    state: Mapping[str, object],
    data_profile: Mapping[str, object],
) -> bool:
    case_generation = as_mapping(action.get("case_generation"))
    for case in as_sequence(case_generation.get("standalone_cases")):
        case_mapping = as_mapping(case)
        if scalar_text(case_mapping.get("state")) == scalar_text(state.get("id")) and scalar_text(
            case_mapping.get("data")
        ) == scalar_text(data_profile.get("id")):
            return True
    return False


def action_goal_enabled(
    action: Mapping[str, object],
    state: Mapping[str, object],
    data_profile: Mapping[str, object],
) -> bool:
    case_generation = as_mapping(action.get("case_generation"))
    as_goal = case_generation.get("as_goal")
    if isinstance(as_goal, bool):
        return as_goal or standalone_case_enabled(action, state, data_profile)
    if isinstance(as_goal, Mapping):
        states = string_set(cast(Mapping[str, object], as_goal).get("states"))
        return scalar_text(state.get("id")) in states
    operation_type = scalar_text(action.get("operation_type"))
    if operation_type in {"query", "evidence"}:
        return standalone_case_enabled(action, state, data_profile)
    return True


def should_generate_variant(
    action: Mapping[str, object],
    state: Mapping[str, object],
    data_profile: Mapping[str, object],
) -> bool:
    coverage_role = scalar_text(data_profile.get("coverage_role"))
    if coverage_role == "evidence_probe" and not standalone_case_enabled(
        action, state, data_profile
    ):
        return False
    return action_goal_enabled(action, state, data_profile)


@cache
def build_component_variants() -> tuple[E2eComponentVariant, ...]:
    variants: list[E2eComponentVariant] = []
    for component_id in COMPONENT_IDS:
        states = component_states(component_id)
        data_profiles = component_data_profiles(component_id)
        for action in component_actions(component_id):
            action_id = scalar_text(action.get("id"))
            for state in states:
                if not action_state_compatible(action, state):
                    continue
                state_id = scalar_text(state.get("id"))
                continue_flow = state.get("continue_flow")
                for data_profile in data_profiles:
                    if not data_compatible(action, state, data_profile):
                        continue
                    if not should_generate_variant(action, state, data_profile):
                        continue
                    policy = target_coverage_policy(action, state, data_profile)
                    for targets in action_targets(action, policy):
                        variants.append(
                            E2eComponentVariant(
                                component_id,
                                action_id,
                                targets,
                                state_id,
                                scalar_text(data_profile.get("id")),
                                continue_flow if isinstance(continue_flow, bool) else False,
                            )
                        )
    return tuple(variants)


def parse_variant(variant_id: str) -> E2eComponentVariant:
    raw, data_id = variant_id.split("@", maxsplit=1) if "@" in variant_id else (variant_id, "-")
    parts = raw.split(".")
    component_id = parts[0] if parts else "-"
    action_id = parts[1] if len(parts) > 1 else "-"
    state_id = parts[-1] if len(parts) > 2 else "-"
    targets = tuple(
        (TARGETS_BY_ID[target_id].dimension, target_id)
        for target_id in parts[2:-1]
        if target_id in TARGETS_BY_ID
    )
    return E2eComponentVariant(component_id, action_id, targets, state_id, data_id, True)


def default_variant_spec(component_id: str) -> Mapping[str, object]:
    return as_mapping(flow_section("default_variants").get(component_id))


def required_variant(
    variant: E2eComponentVariant,
    requirement: Mapping[str, object],
) -> E2eComponentVariant:
    component_id = scalar_text(requirement.get("component"))
    defaults = default_variant_spec(component_id)
    action_id = scalar_text(requirement.get("action"), scalar_text(defaults.get("action")))
    state_id = scalar_text(requirement.get("state"), scalar_text(defaults.get("state")))
    data_id = scalar_text(requirement.get("data"), scalar_text(defaults.get("data")))
    action = item_by_id(component_actions(component_id), action_id)
    same_dimensions = string_set(requirement.get("same"))
    targets = tuple(
        (
            dimension_id,
            (variant.target(dimension_id) if dimension_id in same_dimensions else None)
            or DIMENSIONS_BY_ID[dimension_id].canonical,
        )
        for dimension_id in action_dimensions(action)
    )
    return E2eComponentVariant(component_id, action_id, targets, state_id, data_id, True)


def dependency_applies(dependency: Mapping[str, object], variant: E2eComponentVariant) -> bool:
    source = as_mapping(dependency.get("from"))
    return (
        source.get("component") == variant.component_id
        and source.get("action") in (None, variant.action_id)
        and compatible_with(variant.state_id, source.get("state"))
    )


def prerequisite_variants(variant: E2eComponentVariant) -> tuple[E2eComponentVariant, ...]:
    ordered: list[E2eComponentVariant] = []
    for item in as_sequence(flow_document().get("component_dependencies")):
        dependency = as_mapping(item)
        if not dependency_applies(dependency, variant):
            continue
        for requirement in as_sequence(dependency.get("requires")):
            required = required_variant(variant, as_mapping(requirement))
            ordered.extend(prerequisite_variants(required))
            ordered.append(required)
    return tuple(ordered)


def prerequisites_for_component_variant(variant: E2eComponentVariant) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            prerequisite.variant_id
            for prerequisite in prerequisite_variants(variant)
            if prerequisite.variant_id != variant.variant_id
        )
    )


def component_variant_title(variant: E2eComponentVariant) -> str:
    targets = " / ".join(target_id for _dimension, target_id in variant.targets)
    target_label = f"{targets} " if targets else ""
    return (
        f"{target_label}{variant.component_id}.{variant.action_id} "
        f"{variant.state_id}@{variant.data_id} を主役にする"
    )


def embedded_goal_variant(variant: E2eComponentVariant) -> bool:
    for item in as_sequence(flow_document().get("embedded_goals")):
        goal = as_mapping(item)
        if (
            goal.get("component") == variant.component_id
            and goal.get("action") == variant.action_id
            and goal.get("state") == variant.state_id
            and goal.get("data") == variant.data_id
        ):
            return True
    return False


def matrix_config() -> Mapping[str, object]:
    return flow_section("matrix")


def matrix_dimensions() -> tuple[str, str]:
    matrix = matrix_config()
    return scalar_text(matrix.get("rows")), scalar_text(matrix.get("columns"))


def matrix_expectation(variant: E2eComponentVariant) -> str | None:
    assertion = as_mapping(matrix_config().get("assertion"))
    if assertion.get("component") != variant.component_id:
        return None
    expected = as_mapping(assertion.get("expected_by_state")).get(variant.state_id)
    return expected if isinstance(expected, str) else None


def matrix_expectation_label(expected: str) -> str:
    assertion = as_mapping(matrix_config().get("assertion"))
    return scalar_text(as_mapping(assertion.get("labels")).get(expected), expected)


def matrix_assertions_for(variant: E2eComponentVariant) -> tuple[E2eMatrixAssertion, ...]:
    expected = matrix_expectation(variant)
    row_dimension, column_dimension = matrix_dimensions()
    row_id = variant.target(row_dimension)
    column_id = variant.target(column_dimension)
    if expected is None or row_id is None or column_id is None:
        return ()
    return (E2eMatrixAssertion(row_id, column_id, expected),)


@cache
def build_target_cases() -> tuple[E2eTargetCase, ...]:
    cases: list[E2eTargetCase] = []
    for variant in build_component_variants():
        if embedded_goal_variant(variant):
            continue
        cases.append(
            E2eTargetCase(
                f"TC_TARGET_{len(cases) + 1:03d}",
                component_variant_title(variant),
                "component_variant",
                variant.component_id,
                variant.variant_id,
                (*prerequisites_for_component_variant(variant), variant.variant_id),
                matrix_assertions_for(variant),
            )
        )
    return tuple(cases)


TARGET_CASES = build_target_cases()


def markdown_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()
