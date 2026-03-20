from __future__ import annotations

import importlib
import sys
from pathlib import Path

pytest = importlib.import_module("pytest")
QtCore = pytest.importorskip("PySide6.QtCore")
QtGui = pytest.importorskip("PySide6.QtGui")

QEventLoop = QtCore.QEventLoop
QTimer = QtCore.QTimer
QGuiApplication = QtGui.QGuiApplication
_QT_APP: QGuiApplication | None = None


def ensure_qt_app() -> QGuiApplication:
    global _QT_APP
    if _QT_APP is None:
        _QT_APP = QGuiApplication.instance() or QGuiApplication(sys.argv)
    return _QT_APP


def wait_until(predicate, timeout_ms: int = 2000) -> None:
    app = ensure_qt_app()
    loop = QEventLoop()

    def check() -> None:
        app.processEvents()
        if predicate():
            loop.quit()

    timer = QTimer()
    timer.setInterval(20)
    timer.timeout.connect(check)
    timer.start()
    QTimer.singleShot(timeout_ms, loop.quit)
    app.processEvents()
    check()
    loop.exec()
    timer.stop()
    app.processEvents()
    if not predicate():
        raise AssertionError("Timed out waiting for condition")


class FakeSessionService:
    def __init__(self) -> None:
        self.selected: list[str] = []

    def select_session(self, key: str) -> None:
        self.selected.append(key)

    def __getattr__(self, name: str):
        if name == "selectSession":
            return self.select_session
        raise AttributeError(name)


def start_bridge_service(monkeypatch, tmp_path: Path):
    from app.backend.asyncio_runner import AsyncioRunner
    from app.backend.cron import CronBridgeService

    monkeypatch.setattr("bao.config.paths.get_data_dir", lambda: tmp_path)
    _ = ensure_qt_app()
    runner = AsyncioRunner()
    runner.start()
    service = CronBridgeService(runner)
    return runner, service
