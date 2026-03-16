from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
QML_ROOT = PROJECT_ROOT / "app" / "qml"


def _resolve_bundled_qmllint_from_pyside6() -> str | None:
    try:
        import PySide6

        bundled = Path(PySide6.__file__).resolve().parent / "qmllint"
        if bundled.exists():
            return str(bundled)
    except ImportError:
        return None
    return None


def _resolve_project_venv_qmllint() -> str | None:
    bundled_candidates = sorted(PROJECT_ROOT.glob(".venv/lib/python*/site-packages/PySide6/qmllint"))
    for candidate in bundled_candidates:
        if candidate.exists():
            return str(candidate)
    return None


def _resolve_qmllint() -> str:
    bundled = _resolve_bundled_qmllint_from_pyside6()
    if bundled:
        return bundled

    bundled = _resolve_project_venv_qmllint()
    if bundled:
        return bundled

    candidates = [
        Path(sys.executable).with_name("pyside6-qmllint"),
        Path(sys.executable).with_name("qmllint"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    for name in ("pyside6-qmllint", "qmllint"):
        resolved = shutil.which(name)
        if resolved:
            return resolved

    raise SystemExit(
        "qmllint not found. Run `uv sync --extra desktop --extra dev`, then retry with this script."
    )


def _default_qml_files() -> list[str]:
    return [str(path) for path in sorted(QML_ROOT.glob("*.qml")) if path.is_file()]


def main(argv: list[str]) -> int:
    qmllint = _resolve_qmllint()
    targets = argv[1:] or _default_qml_files()
    cmd = [
        qmllint,
        "-I",
        str(QML_ROOT),
        "--unqualified",
        "disable",
        "--context-properties",
        "disable",
        "--unused-imports",
        "disable",
        *targets,
    ]
    completed = subprocess.run(cmd, cwd=PROJECT_ROOT)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
