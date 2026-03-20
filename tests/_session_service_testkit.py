# ruff: noqa: F401
"""Tests for SessionService and SessionListModel."""

from __future__ import annotations

import asyncio
import concurrent.futures
import importlib
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

from app.backend.asyncio_runner import AsyncioRunner
from bao.hub import HubRuntimePort, local_hub_control
from bao.hub.directory import HubDirectory
from bao.session.manager import SessionChangeEvent, SessionManager
from tests._session_service_mockkit import _MockSessionManagerOptions, make_mock_session_manager

pytest = importlib.import_module("pytest")
pytestmark = [pytest.mark.integration, pytest.mark.gui]

QtCore = pytest.importorskip("PySide6.QtCore")
QCoreApplication = QtCore.QCoreApplication
Qt = QtCore.Qt
QModelIndex = QtCore.QModelIndex
QEventLoop = QtCore.QEventLoop
QTimer = QtCore.QTimer


@pytest.fixture(scope="module", autouse=True)
def qt_app():
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    yield app


_LIVE_SESSION_SERVICES: list[Any] = []


@pytest.fixture(autouse=True)
def cleanup_session_services(qt_app):
    yield
    while _LIVE_SESSION_SERVICES:
        svc = _LIVE_SESSION_SERVICES.pop()
        try:
            svc.shutdown()
        except Exception:
            pass
        try:
            svc.deleteLater()
        except Exception:
            pass
    qt_app.processEvents()


# ── SessionListModel tests ────────────────────────────────────────────────────


def _session_classes():
    from app.backend.session import SessionListModel, SessionService

    return SessionListModel, SessionService


def _new_session_model():
    session_list_model_cls, _ = _session_classes()
    return session_list_model_cls()


def _new_session_service(runner: AsyncioRunner):
    _, session_service_cls = _session_classes()
    svc = session_service_cls(runner)
    _LIVE_SESSION_SERVICES.append(svc)
    return svc


def _sessions_model(svc: Any) -> Any:
    return svc.sessionsModel


def _sidebar_model(svc: Any) -> Any:
    return svc.sidebarModel


def _index_by_key(svc: Any, key: str) -> Any:
    model = _sessions_model(svc)
    for i in range(model.rowCount()):
        idx = model.index(i)
        if model.data(idx, Qt.UserRole + 1) == key:
            return idx
    return QModelIndex()


def _spin_until(predicate: Any, *, timeout_ms: int = 1000, tick_ms: int = 50) -> None:
    deadline = datetime.now() + timedelta(milliseconds=timeout_ms)
    while datetime.now() < deadline:
        if bool(predicate()):
            return
        loop = QEventLoop()
        QTimer.singleShot(tick_ms, loop.quit)
        loop.exec()
    assert bool(predicate())


def _sidebar_role(model: Any, name: bytes) -> int:
    for role, role_name in model.roleNames().items():
        if bytes(role_name) == name:
            return int(role)
    raise AssertionError(f"sidebar role not found: {name!r}")


def _make_mock_session_manager(
    sessions: list[dict[str, Any]] | None = None,
    *,
    options: _MockSessionManagerOptions | None = None,
    **option_overrides: Any,
):
    resolved = options or _MockSessionManagerOptions(**option_overrides)
    return make_mock_session_manager(sessions, options=resolved)


def _hub_local_ports(session_manager: Any) -> Any:
    workspace = getattr(session_manager, "workspace", Path("/tmp/mock-session-root"))
    return SimpleNamespace(
        state_root=Path(str(workspace)).expanduser(),
        directory=HubDirectory(session_manager),
        control=local_hub_control(session_manager=session_manager),
        runtime=HubRuntimePort(session_manager),
    )


__all__ = [
    "asyncio",
    "concurrent",
    "json",
    "sys",
    "datetime",
    "timedelta",
    "Any",
    "MagicMock",
    "patch",
    "pytest",
    "pytestmark",
    "AsyncioRunner",
    "SessionChangeEvent",
    "SessionManager",
    "QCoreApplication",
    "Qt",
    "QModelIndex",
    "QEventLoop",
    "QTimer",
    "qt_app",
    "cleanup_session_services",
    "_new_session_model",
    "_new_session_service",
    "_sessions_model",
    "_sidebar_model",
    "_index_by_key",
    "_spin_until",
    "_sidebar_role",
    "_make_mock_session_manager",
    "_hub_local_ports",
]
