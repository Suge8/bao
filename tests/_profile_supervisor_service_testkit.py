# ruff: noqa: E402, N802, N815
from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass
from pathlib import Path

pytest = importlib.import_module("pytest")
pytestmark = [pytest.mark.integration, pytest.mark.gui]

QtCore = pytest.importorskip("PySide6.QtCore")
QtGui = pytest.importorskip("PySide6.QtGui")
QEventLoop = QtCore.QEventLoop
QTimer = QtCore.QTimer
QObject = QtCore.QObject
Signal = QtCore.Signal
QGuiApplication = QtGui.QGuiApplication


@pytest.fixture(scope="module", autouse=True)
def qt_app():
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    yield app


@pytest.fixture()
def fake_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path))
    monkeypatch.setenv("HOME", str(tmp_path))
    return tmp_path


def wait_until(predicate, timeout_ms: int = 4000) -> None:
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


def spin(ms: int) -> None:
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def model_items(model: object) -> list[dict[str, object]]:
    items = getattr(model, "_items", [])
    return [dict(item) for item in items if isinstance(item, dict)]


def profile_items(supervisor: object) -> list[dict[str, object]]:
    return model_items(getattr(supervisor, "profilesModel"))


class _SessionModel:
    def __init__(self, sessions: list[dict[str, object]]) -> None:
        self._sessions = [dict(item) for item in sessions]


class DummySessionService(QObject):
    sessionsChanged = Signal()
    hubLocalPortsReady = Signal(object)

    def __init__(self, sessions: list[dict[str, object]]) -> None:
        super().__init__()
        self._model = _SessionModel(sessions)
        self.selected: list[str] = []

    def selectSession(self, key: str) -> None:
        self.selected.append(key)

    def supervisorSessionsSnapshot(self) -> list[dict[str, object]]:
        return [dict(item) for item in self._model._sessions]


class DummyChatService(QObject):
    stateChanged = Signal(str)
    errorChanged = Signal(str)
    hubChannelsChanged = Signal()
    hubDetailChanged = Signal()
    startupActivityChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.state = "running"
        self.hubState = "running"
        self.hubDetail = ""
        self.lastError = ""
        self.hubDetailIsError = False
        self.hubChannels = ["desktop", "telegram"]
        self.startupActivity: dict[str, object] = {}
        self.start_calls = 0
        self.stop_calls = 0

    def start(self) -> None:
        self.start_calls += 1

    def stop(self) -> None:
        self.stop_calls += 1

    def supervisorHubSnapshot(self) -> dict[str, object]:
        return {
            "state": self.hubState,
            "detail": self.hubDetail,
            "error": self.lastError,
            "detail_is_error": self.hubDetailIsError,
            "channels": list(self.hubChannels),
            "startup_activity": dict(self.startupActivity),
        }


class DummyCronService(QObject):
    tasksChanged = Signal()
    profileChanged = Signal()

    def __init__(self, tasks: list[dict[str, object]]) -> None:
        super().__init__()
        self._all_tasks = [dict(item) for item in tasks]
        self._selected_task: dict[str, object] = {}
        self.selected: list[str] = []
        self.toggle_calls: list[bool] = []

    @property
    def selectedTask(self) -> dict[str, object]:
        return dict(self._selected_task)

    def selectTask(self, task_id: str) -> None:
        self.selected.append(task_id)
        self._selected_task = next(
            (dict(item) for item in self._all_tasks if str(item.get("id", "")) == task_id),
            {},
        )

    def toggleEnabled(self, enabled: bool) -> None:
        self.toggle_calls.append(bool(enabled))

    def supervisorTasksSnapshot(self) -> list[dict[str, object]]:
        return [dict(item) for item in self._all_tasks]


class DummyLiveHeartbeat:
    def __init__(self, running: bool) -> None:
        self._running = running

    def status(self) -> dict[str, object]:
        return {"running": self._running}


class DummyHeartbeatService(QObject):
    stateChanged = Signal()
    profileChanged = Signal()

    def __init__(self, heartbeat_file: Path, *, running: bool = True) -> None:
        super().__init__()
        self.enabled = True
        self.heartbeatFilePath = str(heartbeat_file)
        self.heartbeatFileExists = heartbeat_file.exists()
        self.lastDecisionLabel = ""
        self.lastError = ""
        self._snapshot = {
            "last_checked_at_ms": 1_710_000_000_000,
            "last_run_at_ms": 1_710_000_060_000,
        }
        self._live = DummyLiveHeartbeat(running)
        self.run_now_calls = 0

    def _effective_live(self) -> DummyLiveHeartbeat:
        return self._live

    def runNow(self) -> None:
        self.run_now_calls += 1

    def supervisorSnapshot(self) -> dict[str, object]:
        return {
            "enabled": self.enabled,
            "heartbeat_file": self.heartbeatFilePath,
            "heartbeat_file_exists": self.heartbeatFileExists,
            "last_checked_at_ms": self._snapshot.get("last_checked_at_ms"),
            "last_run_at_ms": self._snapshot.get("last_run_at_ms"),
            "last_decision": self.lastDecisionLabel,
            "last_error": self.lastError,
            "running": self._live.status().get("running", False),
        }


def write_workspace(shared_workspace: Path) -> None:
    shared_workspace.mkdir(parents=True, exist_ok=True)
    for filename, content in (
        ("INSTRUCTIONS.md", "# Instructions\n"),
        ("PERSONA.md", "# Persona\n"),
        ("HEARTBEAT.md", "- review inbox\n"),
    ):
        (shared_workspace / filename).write_text(content, encoding="utf-8")


@dataclass(frozen=True)
class SessionItemRequest:
    key: str
    title: str
    updated_at: str
    channel: str
    visual_channel: str
    is_child_session: bool
    parent_session_key: str = ""


def session_item(request: SessionItemRequest) -> dict[str, object]:
    return {
        "key": request.key,
        "title": request.title,
        "updated_at": request.updated_at,
        "updated_label": "刚刚",
        "channel": request.channel,
        "visual_channel": request.visual_channel,
        "child_status": "running" if request.is_child_session else "",
        "is_running": True,
        "is_child_session": request.is_child_session,
        "parent_session_key": request.parent_session_key,
    }


def cron_item(task_id: str, *, title: str = "Daily Review") -> dict[str, object]:
    return {
        "id": task_id,
        "name": title,
        "enabled": True,
        "schedule_summary": "每 30 分钟",
        "status_key": "scheduled",
        "status_label": "已调度",
        "session_key": f"cron:{task_id}",
        "next_run_text": "2026-03-14 12:00",
        "last_result_text": "成功 · 2026-03-14 11:30",
        "updated_at_ms": 1_710_000_000_000,
        "last_error": "",
    }
