from __future__ import annotations

import argparse
import ast
import csv
from pathlib import Path

import pytest
from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch

from tools.generate_external_crud import (
    SERVICE_CONFIGS,
    api_name_from_functions_path,
    build_arg_parser,
    called_methods,
    collect_service_crud,
    file_operations,
    generate,
    main,
    router_dependency_names,
    service_names_for_arg,
)


def test_api_name_from_functions_path_uses_api_folder_name() -> None:
    root = Path("src/app/apis")
    path = root / "projects" / "create_project" / "functions.py"

    assert api_name_from_functions_path(path, root) == "create_project"


def test_api_name_from_functions_path_rejects_non_api_functions_path() -> None:
    with pytest.raises(ValueError, match=r"functions\.py must be under an API directory"):
        api_name_from_functions_path(
            Path("src/app/apis/projects/functions.py"),
            Path("src/app/apis"),
        )


def test_called_methods_collects_configured_variable_attribute_calls() -> None:
    tree = ast.parse(
        """
async def execute(api_gateway_control, other):
    await api_gateway_control.create_api_key()
    await api_gateway_control.get_stage()
    await other.create_api_key()
        """
    )

    assert called_methods(tree, frozenset({"api_gateway_control"})) == {
        "create_api_key",
        "get_stage",
    }


def test_file_operations_maps_service_methods_to_crud_resources(tmp_path: Path) -> None:
    functions_path = tmp_path / "functions.py"
    functions_path.write_text(
        """
async def execute(access_token_verifier, other):
    await access_token_verifier.verify_access_token()
    await other.verify_access_token()
        """,
        encoding="utf-8",
    )

    operations = file_operations(functions_path, SERVICE_CONFIGS["identity"])

    assert operations == {"jwks_signing_key": {"R"}}


def test_file_operations_ignores_unmapped_service_methods(tmp_path: Path) -> None:
    functions_path = tmp_path / "functions.py"
    functions_path.write_text(
        """
async def execute(access_token_verifier):
    await access_token_verifier.verify_access_token()
    await access_token_verifier.unmapped_operation()
        """,
        encoding="utf-8",
    )

    operations = file_operations(functions_path, SERVICE_CONFIGS["identity"])

    assert operations == {"jwks_signing_key": {"R"}}


def test_collect_service_crud_reads_router_dependencies(tmp_path: Path) -> None:
    api_root = tmp_path / "apis"
    create_reservation = api_root / "reservations" / "create_reservation"
    health = api_root / "system" / "health"
    create_reservation.mkdir(parents=True)
    health.mkdir(parents=True)
    (create_reservation / "functions.py").write_text("", encoding="utf-8")
    (create_reservation / "router.py").write_text(
        """
async def create_reservation(caller=Depends(get_caller_identity)):
    return caller
        """,
        encoding="utf-8",
    )
    (health / "functions.py").write_text("", encoding="utf-8")
    (health / "router.py").write_text(
        """
async def health():
    return {}
        """,
        encoding="utf-8",
    )

    matrix = collect_service_crud(api_root, SERVICE_CONFIGS["identity"])

    assert matrix.apis == {"create_reservation"}
    assert matrix.cells["create_reservation"]["jwks_signing_key"] == {"R"}
    assert "health" not in matrix.cells


def test_router_dependency_names_ignores_missing_router(tmp_path: Path) -> None:
    assert router_dependency_names(tmp_path / "router.py") == set()


def test_generate_writes_requested_external_crud_csvs(tmp_path: Path) -> None:
    api_root = tmp_path / "apis"
    api_dir = api_root / "reservations" / "get_reservation"
    api_dir.mkdir(parents=True)
    (api_dir / "functions.py").write_text(
        """
async def execute(access_token_verifier):
    await access_token_verifier.verify_access_token()
        """,
        encoding="utf-8",
    )
    output_dir = tmp_path / "docs" / "crud"

    written = generate(api_root, output_dir, ["identity"])

    assert [path.name for path in written] == ["identity_crud.gen.csv"]
    assert list(csv.reader((output_dir / "identity_crud.gen.csv").read_text().splitlines())) == [
        ["api", "jwks_signing_key"],
        ["get_reservation", "R"],
    ]


def test_service_names_for_arg_accepts_all_or_single_service() -> None:
    assert service_names_for_arg("all") == ["identity"]
    assert service_names_for_arg("identity") == ["identity"]

    with pytest.raises(argparse.ArgumentTypeError, match="service must be one of"):
        service_names_for_arg("db")


def test_arg_parser_defaults_and_main_output(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    default_args = build_arg_parser().parse_args([])

    assert default_args.api_root.as_posix() == "src/app/apis"
    assert default_args.output_dir.as_posix() == "docs/spec/30.crud"
    assert default_args.service == ["identity"]

    api_root = tmp_path / "apis"
    api_dir = api_root / "reservations" / "get_reservation"
    api_dir.mkdir(parents=True)
    (api_dir / "functions.py").write_text(
        """
async def execute(access_token_verifier):
    await access_token_verifier.verify_access_token()
        """,
        encoding="utf-8",
    )
    output_dir = tmp_path / "crud"
    monkeypatch.setattr(
        "sys.argv",
        [
            "generate_external_crud",
            "--api-root",
            str(api_root),
            "--output-dir",
            str(output_dir),
            "--service",
            "identity",
        ],
    )

    main()

    assert capsys.readouterr().out == (
        f"Generated {(output_dir / 'identity_crud.gen.csv').as_posix()}.\n"
    )
    assert (output_dir / "identity_crud.gen.csv").exists()
    assert main(["--api-root", str(api_root), "--output-dir", str(output_dir), "--check"]) == 0
