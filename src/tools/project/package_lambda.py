"""Linux/x86_64用の依存を含むLambda配布ZIPを作る。"""

import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def package() -> None:
    """固定lockからruntime依存だけを出力し、SQLを含めて梱包する。"""
    (ROOT / "artifacts").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as name:
        stage = Path(name)
        requirements = stage / "requirements.txt"
        subprocess.run(  # noqa: S603 - 固定引数のuvだけを実行する。
            [  # noqa: S607
                "uv",
                "export",
                "--frozen",
                "--no-dev",
                "--no-emit-project",
                "--output-file",
                str(requirements),
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
        target = stage / "package"
        subprocess.run(  # noqa: S603 - 固定引数のuvだけを実行する。
            [  # noqa: S607
                "uv",
                "pip",
                "install",
                "--python-platform",
                "x86_64-manylinux_2_28",
                "--python-version",
                "3.14",
                "--only-binary",
                ":all:",
                "--target",
                str(target),
                "-r",
                str(requirements),
            ],
            check=True,
        )
        shutil.copytree(
            ROOT / "src/app",
            target / "app",
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        with zipfile.ZipFile(
            ROOT / "artifacts/lambda.zip", "w", compression=zipfile.ZIP_DEFLATED
        ) as archive:
            for path in sorted(target.rglob("*")):
                if packaged(path, target):
                    entry = zipfile.ZipInfo(
                        path.relative_to(target).as_posix(), date_time=(2026, 1, 1, 0, 0, 0)
                    )
                    entry.compress_type = zipfile.ZIP_DEFLATED
                    archive.writestr(entry, path.read_bytes())


def packaged(path: Path, target: Path) -> bool:
    """実行時に不要なconsole scriptとwheel記録をZIPから除く。"""
    if not path.is_file() or path.name == "RECORD":
        return False
    return path.relative_to(target).parts[0] != "bin"


if __name__ == "__main__":
    package()
