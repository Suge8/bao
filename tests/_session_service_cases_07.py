# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._session_service_testkit import *

def test_service_hub_ready_prefers_persisted_active_key_over_latest_session():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[
                {"key": "desktop:local::s1", "title": "Chat 1", "updated_at": 1},
                {"key": "desktop:local::s2", "title": "Chat 2", "updated_at": 2},
            ],
            active_key="desktop:local::s1",
        )

        svc.setHubReady()
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        assert svc.activeKey == "desktop:local::s1"
        assert _sessions_model(svc).data(_sessions_model(svc).index(0), Qt.UserRole + 3) is True
        assert _sessions_model(svc).data(_sessions_model(svc).index(1), Qt.UserRole + 3) is False
    finally:
        runner.shutdown(grace_s=1.0)



def test_service_hub_ready_autopick_persists_selected_session():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[
                {"key": "desktop:local::s1", "title": "Chat 1", "updated_at": 1},
                {"key": "desktop:local::s2", "title": "Chat 2", "updated_at": 2},
            ],
            active_key="",
        )

        svc.setHubReady()
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        assert svc.activeKey == "desktop:local::s2"
        assert sm.get_active_session_key("desktop:local") == "desktop:local::s2"
    finally:
        runner.shutdown(grace_s=1.0)



def test_list_refresh_prefers_valid_persisted_active_when_local_active_is_stale():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        svc.setHubReady()
        svc._active_key = "desktop:local::stale"
        svc._last_emitted_active_key = "desktop:local::stale"

        sessions = [
            {"key": "desktop:local::s1", "title": "Chat 1", "updated_at": 1, "channel": "desktop"},
            {"key": "desktop:local::s2", "title": "Chat 2", "updated_at": 2, "channel": "desktop"},
        ]

        active_keys: list[str] = []
        svc.activeKeyChanged.connect(active_keys.append)

        svc._handle_list_result(True, "", ([dict(s) for s in sessions], "desktop:local::s1"))

        assert svc.activeKey == "desktop:local::s1"
        assert active_keys == ["desktop:local::s1"]
        assert _sessions_model(svc).data(_sessions_model(svc).index(0), Qt.UserRole + 3) is True
        assert _sessions_model(svc).data(_sessions_model(svc).index(1), Qt.UserRole + 3) is False
    finally:
        runner.shutdown(grace_s=1.0)



def test_service_hub_ready_repairs_invalid_active_key():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[
                {"key": "desktop:local::s1", "title": "Chat 1"},
                {"key": "desktop:local::s2", "title": "Chat 2"},
            ],
            active_key="desktop:local::missing",
        )

        svc.setHubReady()
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        assert svc.activeKey == "desktop:local::s1"
    finally:
        runner.shutdown(grace_s=1.0)



def test_service_select_session_updates_active_key():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[
                {"key": "desktop:local::s1"},
                {"key": "desktop:local::s2"},
            ],
            active_key="desktop:local::s1",
        )
        svc.initialize(sm)

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

        svc.refresh()
        loop3 = QEventLoop()
        QTimer.singleShot(300, loop3.quit)
        loop3.exec()

        assert svc.activeKey == "desktop:local::s2"
    finally:
        runner.shutdown(grace_s=1.0)



def test_list_refresh_does_not_override_pending_selection():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        svc.setHubReady()

        sessions = [
            {"key": "desktop:local::s1", "title": "Chat 1", "updated_at": 1, "channel": "desktop"},
            {"key": "desktop:local::s2", "title": "Chat 2", "updated_at": 2, "channel": "desktop"},
        ]
        svc._active_key = "desktop:local::s1"
        svc._pending_select_key = "desktop:local::s2"

        svc._handle_list_result(True, "", (sessions, "desktop:local::s1"))

        assert svc.activeKey == "desktop:local::s2"
        idx = _sessions_model(svc).index(1)
        assert _sessions_model(svc).data(idx, Qt.UserRole + 3) is True
    finally:
        runner.shutdown(grace_s=1.0)



def test_list_refresh_active_only_change_keeps_local_active_source_of_truth():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        svc.setHubReady()

        sessions = [
            {"key": "desktop:local::s1", "title": "Chat 1", "updated_at": 1, "channel": "desktop"},
            {"key": "desktop:local::s2", "title": "Chat 2", "updated_at": 2, "channel": "desktop"},
        ]

        svc._active_key = "desktop:local::s1"
        svc._last_emitted_active_key = "desktop:local::s1"
        svc._model.reset_sessions([dict(s) for s in sessions], "desktop:local::s1")

        changed_events: list[bool] = []
        active_keys: list[str] = []
        svc.sessionsChanged.connect(lambda: changed_events.append(True))
        svc.activeKeyChanged.connect(active_keys.append)

        svc._handle_list_result(True, "", ([dict(s) for s in sessions], "desktop:local::s1"))
        assert len(changed_events) == 1

        svc._pending_select_key = "desktop:local::s2"
        svc._handle_list_result(True, "", ([dict(s) for s in sessions], "desktop:local::s2"))
        assert len(changed_events) == 2
        assert svc.activeKey == "desktop:local::s2"
        assert active_keys == ["desktop:local::s2"]
        assert _sessions_model(svc).data(_sessions_model(svc).index(0), Qt.UserRole + 3) is False
        assert _sessions_model(svc).data(_sessions_model(svc).index(1), Qt.UserRole + 3) is True
    finally:
        runner.shutdown(grace_s=1.0)



def test_stale_select_result_does_not_override_current_active_key():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        svc.setHubReady()
        sessions = [
            {"key": "desktop:local::s1", "title": "Chat 1", "updated_at": 1, "channel": "desktop"},
            {"key": "desktop:local::s2", "title": "Chat 2", "updated_at": 2, "channel": "desktop"},
        ]
        svc._active_key = "desktop:local::s2"
        svc._last_emitted_active_key = "desktop:local::s2"
        svc._model.reset_sessions([dict(s) for s in sessions], "desktop:local::s2")

        svc._pending_select_key = None
        svc._handle_select_result(True, "", "desktop:local::s1")

        assert svc.activeKey == "desktop:local::s2"
        assert _sessions_model(svc).data(_sessions_model(svc).index(0), Qt.UserRole + 3) is False
        assert _sessions_model(svc).data(_sessions_model(svc).index(1), Qt.UserRole + 3) is True
    finally:
        runner.shutdown(grace_s=1.0)



def test_child_session_refresh_keeps_parent_active_selection(tmp_path, qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = SessionManager(tmp_path)
        parent = sm.get_or_create("desktop:local::main")
        parent.metadata["title"] = "Main"
        sm.save(parent)
        other = sm.get_or_create("desktop:local::other")
        other.metadata["title"] = "Other"
        sm.save(other)
        sm.set_active_session_key("desktop:local", "desktop:local::main")

        svc.setHubReady()
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        child = sm.get_or_create("subagent:desktop:local::main::child-1")
        child.metadata.update(
            {
                "title": "Child",
                "session_kind": "subagent_child",
                "read_only": True,
                "parent_session_key": "desktop:local::main",
                "child_status": "running",
            }
        )
        sm.save(child)

        loop2 = QEventLoop()
        QTimer.singleShot(300, loop2.quit)
        loop2.exec()

        assert svc.activeKey == "desktop:local::main"
    finally:
        runner.shutdown(grace_s=1.0)
