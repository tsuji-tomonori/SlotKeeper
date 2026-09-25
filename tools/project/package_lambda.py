"""Linux/x86_64用の依存を含むLambda配布ZIPを作る。"""

import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def package() -> None:
    """固定lockからruntime依存だけを出力し、SQLを含めて梱包する。"""
    (ROOT / "artifacts").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as name:
        stage = Path(name)
        requirements = stage / "requirements.txt"
        subprocess.run(
            [
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
        subprocess.run(
            [
                "uv",
                "pip",
                "install",
                "--python-platform",
                "x86_64-manylinux2014",
                "--python-version",
                "3.12",
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
            ROOT / "backend/src/slotkeeper",
            target / "slotkeeper",
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        with zipfile.ZipFile(
            ROOT / "artifacts/lambda.zip", "w", compression=zipfile.ZIP_DEFLATED
        ) as archive:
            for path in sorted(target.rglob("*")):
                if path.is_file():
                    entry = zipfile.ZipInfo(
                        path.relative_to(target).as_posix(), date_time=(2026, 1, 1, 0, 0, 0)
                    )
                    entry.compress_type = zipfile.ZIP_DEFLATED
                    archive.writestr(entry, path.read_bytes())


if __name__ == "__main__":
    package()
