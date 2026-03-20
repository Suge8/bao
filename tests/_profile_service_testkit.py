# ruff: noqa: E402, F401
from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest

QtCore = pytest.importorskip("PySide6.QtCore")
QCoreApplication = QtCore.QCoreApplication
QEventLoop = QtCore.QEventLoop
QTimer = QtCore.QTimer

from app.backend.asyncio_runner import AsyncioRunner
from app.backend.profile import ProfileService
from bao.profile import CreateProfileOptions, RenameProfileOptions, create_profile, rename_profile


@pytest.fixture(scope="module", autouse=True)
def qt_app():
    app = QCoreApplication.instance() or QCoreApplication([])
    yield app


@pytest.fixture()
def fake_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path))
    monkeypatch.setenv("HOME", str(tmp_path))
    return tmp_path


def _wait_until(predicate, timeout_ms: int = 4000) -> None:
    loop = QEventLoop()

    def check() -> None:
        if predicate():
            loop.quit()

    timer = QTimer()
    timer.setInterval(20)
    timer.timeout.connect(check)
    timer.start()
    QTimer.singleShot(timeout_ms, loop.quit)
    check()
    loop.exec()
    timer.stop()
    if not predicate():
        raise AssertionError("Timed out waiting for condition")


def _spin(ms: int) -> None:
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def _write_workspace(shared_workspace: Path) -> None:
    shared_workspace.mkdir(parents=True, exist_ok=True)
    for filename, content in (
        ("INSTRUCTIONS.md", "instructions"),
        ("PERSONA.md", "persona"),
        ("HEARTBEAT.md", "heartbeat"),
    ):
        (shared_workspace / filename).write_text(content, encoding="utf-8")


__all__ = [name for name in globals() if not (name.startswith("__") and name.endswith("__"))]
