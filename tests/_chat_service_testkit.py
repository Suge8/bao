# ruff: noqa: F401
"""Tests for ChatService state machine and message queue."""

from __future__ import annotations

import asyncio
import concurrent.futures
import importlib
import sys
from collections.abc import Coroutine
from pathlib import Path
from types import SimpleNamespace
from typing import Any, TypeVar, cast
from unittest.mock import MagicMock, call, patch

from bao.hub import HubRuntimePort, local_hub_control
from bao.hub.builder import DesktopStartupMessage
from bao.hub.directory import HubDirectory
from bao.session.manager import SessionChangeEvent

pytest = importlib.import_module("pytest")

QtCore = pytest.importorskip("PySide6.QtCore")
QtGui = pytest.importorskip("PySide6.QtGui")
QGuiApplication = QtGui.QGuiApplication
QImage = QtGui.QImage
_T = TypeVar("_T")


@pytest.fixture(scope="module", autouse=True)
def qt_app():
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    yield app


_LIVE_CHAT_SERVICES = []


@pytest.fixture(autouse=True)
def cleanup_chat_services(qt_app):
    yield
    while _LIVE_CHAT_SERVICES:
        svc = _LIVE_CHAT_SERVICES.pop()
        try:
            svc._history_sync_timer.stop()
        except Exception:
            pass
        try:
            svc.deleteLater()
        except Exception:
            pass
    qt_app.processEvents()


def make_service():
    from app.backend.chat import ChatMessageModel
    from app.backend.hub import ChatService

    _install_chat_test_compat()
    model = ChatMessageModel()

    def _submit_and_close(coro: Coroutine[Any, Any, _T]) -> concurrent.futures.Future[_T]:
        try:
            coro.close()
        except Exception:
            pass
        fut: concurrent.futures.Future[_T] = concurrent.futures.Future()
        fut.set_result(cast(_T, None))
        return fut

    runner = MagicMock()
    runner.submit = MagicMock(side_effect=_submit_and_close)
    svc = ChatService(model, runner)
    _LIVE_CHAT_SERVICES.append(svc)
    return svc, model


def _hub_local_ports(session_manager: Any) -> Any:
    if session_manager.__class__ is object:
        session_manager = MagicMock()
    workspace = getattr(session_manager, "workspace", Path("/tmp/session-root"))
    return SimpleNamespace(
        state_root=Path(str(workspace)).expanduser(),
        directory=HubDirectory(session_manager),
        control=local_hub_control(session_manager=session_manager),
        runtime=HubRuntimePort(session_manager),
    )


def _bind_chat_local_ports(service: Any, session_manager: Any) -> Any:
    ports = _hub_local_ports(session_manager)
    service.setFallbackHubPorts(ports)
    return ports


def _install_chat_test_compat() -> None:
    from app.backend.hub import ChatService

    if not hasattr(ChatService, "setSessionManager"):
        setattr(ChatService, "setSessionManager", lambda self, sm: _bind_chat_local_ports(self, sm))
    session_manager_attr = getattr(ChatService, "_session_manager", None)
    if isinstance(session_manager_attr, property):
        return

    def _get_session_manager(self: Any) -> Any:
        runtime = self._current_hub_runtime()
        return getattr(runtime, "session_manager", None) if runtime is not None else None

    def _set_session_manager(self: Any, session_manager: Any) -> None:
        if session_manager is None:
            self.setFallbackHubPorts(None)
            return
        _bind_chat_local_ports(self, session_manager)

    setattr(ChatService, "_session_manager", property(_get_session_manager, _set_session_manager))


class _SessionManagerWithListeners:
    def __init__(self, workspace: str | Path = "/tmp/session-root") -> None:
        self.listeners: list[Any] = []
        self.workspace = Path(workspace)

    def add_change_listener(self, listener: Any) -> None:
        self.listeners.append(listener)

    def remove_change_listener(self, listener: Any) -> None:
        if listener in self.listeners:
            self.listeners.remove(listener)

    def emit(self, session_key: str, kind: str) -> None:
        event = SessionChangeEvent(session_key=session_key, kind=kind)
        for listener in list(self.listeners):
            listener(event)

__all__ = [name for name in globals() if not name.startswith("__")]
