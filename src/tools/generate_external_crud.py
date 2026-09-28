from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from tools.generate_db_crud import CrudMatrix, render_csv, write_crud_csv
from tools.generation_io import check_outputs, write_outputs

ServiceName = Literal["identity"]


@dataclass(frozen=True)
class MethodCrud:
    resource: str
    operation: str


@dataclass(frozen=True)
class ServiceCrudConfig:
    output_name: str
    variable_names: frozenset[str]
    methods: dict[str, MethodCrud]
    router_dependencies: dict[str, MethodCrud] = field(default_factory=lambda: {})

    @property
    def resources(self) -> list[str]:
        return sorted(
            {
                method.resource
                for method in [*self.methods.values(), *self.router_dependencies.values()]
            }
        )


SERVICE_CONFIGS: dict[ServiceName, ServiceCrudConfig] = {
    "identity": ServiceCrudConfig(
        output_name="identity_crud.gen.csv",
        variable_names=frozenset({"access_token_verifier"}),
        methods={
            "verify_access_token": MethodCrud("jwks_signing_key", "R"),
        },
        router_dependencies={
            "get_caller_identity": MethodCrud("jwks_signing_key", "R"),
        },
    ),
}


def api_name_from_functions_path(functions_path: Path, api_root: Path) -> str:
    relative = functions_path.relative_to(api_root)
    if relative.name != "functions.py" or len(relative.parts) < 3:
        raise ValueError(f"functions.py must be under an API directory: {functions_path}")
    return relative.parts[-2]


def called_methods(tree: ast.AST, variable_names: frozenset[str]) -> set[str]:
    methods: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if (
            isinstance(function, ast.Attribute)
            and isinstance(function.value, ast.Name)
            and function.value.id in variable_names
        ):
            methods.add(function.attr)
    return methods


def file_operations(functions_path: Path, config: ServiceCrudConfig) -> dict[str, set[str]]:
    tree = ast.parse(functions_path.read_text(encoding="utf-8"), filename=functions_path.as_posix())
    operations: dict[str, set[str]] = {}
    for method_name in called_methods(tree, config.variable_names):
        method_crud = config.methods.get(method_name)
        if method_crud is None:
            continue
        operations.setdefault(method_crud.resource, set()).add(method_crud.operation)
    return operations


def router_dependency_names(router_path: Path) -> set[str]:
    """routerの`Depends(...)`で注入する依存関数名を取得する。"""
    if not router_path.exists():
        return set()
    tree = ast.parse(router_path.read_text(encoding="utf-8"), filename=router_path.as_posix())
    names: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "Depends"
            and node.args
            and isinstance(node.args[0], ast.Name)
        ):
            names.add(node.args[0].id)
    return names


def router_operations(router_path: Path, config: ServiceCrudConfig) -> dict[str, set[str]]:
    operations: dict[str, set[str]] = {}
    for dependency in router_dependency_names(router_path):
        method_crud = config.router_dependencies.get(dependency)
        if method_crud is not None:
            operations.setdefault(method_crud.resource, set()).add(method_crud.operation)
    return operations


def collect_service_crud(api_root: Path, config: ServiceCrudConfig) -> CrudMatrix:
    matrix = CrudMatrix(tables=set(config.resources))
    for functions_path in sorted(api_root.rglob("functions.py")):
        api = api_name_from_functions_path(functions_path, api_root)
        operations = file_operations(functions_path, config)
        for resource, resource_operations in router_operations(
            functions_path.with_name("router.py"), config
        ).items():
            operations.setdefault(resource, set()).update(resource_operations)
        if not operations:
            continue
        matrix.apis.add(api)
        for resource, resource_operations in operations.items():
            for operation in resource_operations:
                matrix.add(api, resource, operation)
    return matrix


def generate_service(api_root: Path, output_dir: Path, service_name: ServiceName) -> Path:
    config = SERVICE_CONFIGS[service_name]
    matrix = collect_service_crud(api_root, config)
    return write_crud_csv(matrix, config.resources, output_dir / config.output_name)


def generate(api_root: Path, output_dir: Path, service_names: list[ServiceName]) -> list[Path]:
    rendered = render_outputs(api_root, output_dir, service_names)
    write_outputs(rendered)
    return list(rendered)


def render_outputs(
    api_root: Path,
    output_dir: Path,
    service_names: list[ServiceName],
) -> dict[Path, str]:
    rendered: dict[Path, str] = {}
    for service_name in service_names:
        config = SERVICE_CONFIGS[service_name]
        matrix = collect_service_crud(api_root, config)
        rendered[output_dir / config.output_name] = render_csv(matrix, config.resources)
    return rendered


def service_names_for_arg(value: str) -> list[ServiceName]:
    if value == "all":
        return list(SERVICE_CONFIGS)
    if value not in SERVICE_CONFIGS:
        expected = ", ".join(("all", *SERVICE_CONFIGS))
        raise argparse.ArgumentTypeError(f"service must be one of: {expected}")
    return [value]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate API x external service resource CRUD CSV files."
    )
    parser.add_argument("--api-root", type=Path, default=Path("src/app/apis"))
    parser.add_argument("--output-dir", type=Path, default=Path("docs/spec/30.crud"))
    parser.add_argument(
        "--service",
        type=service_names_for_arg,
        default=service_names_for_arg("all"),
    )
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    rendered = render_outputs(args.api_root, args.output_dir, args.service)
    if args.check:
        return check_outputs(rendered)
    write_outputs(rendered)
    output_paths = list(rendered)
    for output_path in output_paths:
        print(f"Generated {output_path.as_posix()}.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
