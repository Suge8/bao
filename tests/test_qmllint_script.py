from __future__ import annotations

import builtins
import importlib
import importlib.util
import subprocess
import sys
from pathlib import Path

pytest = importlib.import_module("pytest")
pytestmark = [pytest.mark.desktop_ui_smoke]

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "app" / "scripts" / "run_qmllint.py"


def _load_script_module():
    spec = importlib.util.spec_from_file_location("run_qmllint_test_module", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_resolve_qmllint_prefers_project_bundled_binary_over_wrapper(tmp_path, monkeypatch) -> None:
    module = _load_script_module()
    fake_root = tmp_path / "repo"
    bundled = fake_root / ".venv" / "lib" / "python3.11" / "site-packages" / "PySide6" / "qmllint"
    wrapper = fake_root / ".venv" / "bin" / "pyside6-qmllint"
    bundled.parent.mkdir(parents=True, exist_ok=True)
    wrapper.parent.mkdir(parents=True, exist_ok=True)
    bundled.write_text("", encoding="utf-8")
    wrapper.write_text("", encoding="utf-8")

    original_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "PySide6":
            raise ImportError("simulated missing import")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(module, "PROJECT_ROOT", fake_root)
    monkeypatch.setattr(module.sys, "executable", str(fake_root / ".venv" / "bin" / "python3"))
    monkeypatch.setattr(module.shutil, "which", lambda name: str(wrapper))
    monkeypatch.setattr(builtins, "__import__", fake_import)

    assert module._resolve_qmllint() == str(bundled)


def test_run_qmllint_script_on_sidebar_brand_dock() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "app/qml/SidebarBrandDock.qml",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout
