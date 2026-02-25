"""Tests for SessionService and SessionListModel."""

from __future__ import annotations

import sys
import pytest
from unittest.mock import MagicMock, patch

from PySide6.QtCore import QCoreApplication


@pytest.fixture(scope="module", autouse=True)
def qt_app():
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    yield app


from app.backend.session import SessionListModel, SessionService
from app.backend.asyncio_runner import AsyncioRunner


# ── SessionListModel tests ────────────────────────────────────────────────────


def test_model_empty_initially():
    m = SessionListModel()
    assert m.rowCount() == 0


def test_model_reset_sessions():
    m = SessionListModel()
    sessions = [
        {"key": "desktop:local::s1", "title": "Session 1", "updated_at": 100},
        {"key": "desktop:local::s2", "title": "Session 2", "updated_at": 200},
    ]
    m.reset_sessions(sessions, "desktop:local::s1")
    assert m.rowCount() == 2


def test_model_data_roles():
    from PySide6.QtCore import Qt, QModelIndex

    m = SessionListModel()
    sessions = [{"key": "k1", "title": "T1", "updated_at": 42}]
    m.reset_sessions(sessions, "k1")
    idx = m.index(0)
    assert m.data(idx, Qt.UserRole + 1) == "k1"  # key
    assert m.data(idx, Qt.UserRole + 2) == "T1"  # title
    assert m.data(idx, Qt.UserRole + 3) is True  # isActive
    assert m.data(idx, Qt.UserRole + 4) == 42  # updatedAt


def test_model_inactive_session():
    from PySide6.QtCore import Qt

    m = SessionListModel()
    sessions = [{"key": "k1", "title": "T1", "updated_at": 0}]
    m.reset_sessions(sessions, "k2")  # k2 is active, not k1
    idx = m.index(0)
    assert m.data(idx, Qt.UserRole + 3) is False


def test_model_set_active():
    from PySide6.QtCore import Qt

    m = SessionListModel()
    sessions = [
        {"key": "k1", "title": "T1", "updated_at": 0},
        {"key": "k2", "title": "T2", "updated_at": 0},
    ]
    m.reset_sessions(sessions, "k1")
    m.set_active("k2")
    assert m.data(m.index(0), Qt.UserRole + 3) is False
    assert m.data(m.index(1), Qt.UserRole + 3) is True


def test_model_invalid_index_returns_none():
    from PySide6.QtCore import Qt

    m = SessionListModel()
    idx = m.index(99)
    assert m.data(idx, Qt.UserRole + 1) is None


# ── SessionService tests ──────────────────────────────────────────────────────


def _make_mock_session_manager(sessions=None, active_key=""):
    sm = MagicMock()
    if sessions is None:
        sessions = []
    # list_sessions() returns list of dicts (not Session objects)
    mock_sessions = []
    for s in sessions:
        mock_sessions.append(
            {
                "key": s["key"],
                "updated_at": s.get("updated_at", 0),
                "metadata": {"title": s.get("title", s["key"])},
            }
        )
    sm.list_sessions.return_value = mock_sessions
    sm.get_active_session_key.return_value = active_key
    return sm


def test_service_initial_active_key():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = SessionService(runner)
        assert svc.activeKey == ""
    finally:
        runner.shutdown(grace_s=1.0)


def test_service_refresh_populates_model():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = SessionService(runner)
        sm = _make_mock_session_manager(
            sessions=[{"key": "desktop:local::s1", "title": "Chat 1"}],
            active_key="desktop:local::s1",
        )
        svc.initialize(sm)

        # Wait for async refresh to complete
        from PySide6.QtCore import QEventLoop, QTimer

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        assert svc.sessionsModel.rowCount() == 1
    finally:
        runner.shutdown(grace_s=1.0)


def test_service_select_session_updates_active_key():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = SessionService(runner)
        sm = _make_mock_session_manager(
            sessions=[
                {"key": "desktop:local::s1"},
                {"key": "desktop:local::s2"},
            ],
            active_key="desktop:local::s1",
        )
        svc.initialize(sm)

        from PySide6.QtCore import QEventLoop, QTimer

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        keys = []
        svc.activeKeyChanged.connect(keys.append)
        svc.selectSession("desktop:local::s2")

        loop2 = QEventLoop()
        QTimer.singleShot(300, loop2.quit)
        loop2.exec()

        assert "desktop:local::s2" in keys
    finally:
        runner.shutdown(grace_s=1.0)


def test_service_refresh_without_manager_is_noop():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = SessionService(runner)
        svc.refresh()  # should not raise
        assert svc.sessionsModel.rowCount() == 0
    finally:
        runner.shutdown(grace_s=1.0)
