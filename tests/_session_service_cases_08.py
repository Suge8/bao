# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._session_service_testkit import *

def test_runtime_refresh_ignores_stored_child_active_when_local_parent_is_valid():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        svc.setHubReady()
        sessions = [
            {
                "key": "desktop:local::main",
                "title": "Main",
                "updated_at": 1,
                "channel": "desktop",
            },
            {
                "key": "subagent:desktop:local::main::child-1",
                "title": "Child",
                "updated_at": 2,
                "channel": "desktop",
                "session_kind": "subagent_child",
                "is_read_only": True,
                "parent_session_key": "desktop:local::main",
                "child_status": "running",
                "is_running": True,
            },
        ]
        svc._active_key = "desktop:local::main"
        svc._last_emitted_active_key = "desktop:local::main"
        svc._model.reset_sessions([dict(s) for s in sessions], "desktop:local::main")

        svc._handle_list_result(
            True,
            "",
            ([dict(s) for s in sessions], "subagent:desktop:local::main::child-1"),
        )

        assert svc.activeKey == "desktop:local::main"
    finally:
        runner.shutdown(grace_s=1.0)



def test_list_refresh_updates_visible_time_fields_even_when_keys_match():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        svc.setHubReady()

        sessions = [
            {
                "key": "desktop:local::s1",
                "title": "Chat 1",
                "updated_at": 1,
                "updated_label": "<1m",
                "channel": "desktop",
                "has_unread": False,
            },
            {
                "key": "desktop:local::s2",
                "title": "Chat 2",
                "updated_at": 2,
                "updated_label": "2m",
                "channel": "desktop",
                "has_unread": False,
            },
        ]

        svc._active_key = "desktop:local::s1"
        svc._last_emitted_active_key = "desktop:local::s1"
        svc._model.reset_sessions([dict(s) for s in sessions], "desktop:local::s1")
        changed_events: list[bool] = []
        svc.sessionsChanged.connect(lambda: changed_events.append(True))

        svc._handle_list_result(True, "", ([dict(s) for s in sessions], "desktop:local::s1"))

        refreshed = [dict(s) for s in sessions]
        refreshed[0]["updated_at"] = 3
        refreshed[0]["updated_label"] = "3m"
        svc._handle_list_result(True, "", (refreshed, "desktop:local::s1"))

        idx = _sessions_model(svc).index(0)
        assert len(changed_events) == 2
        assert _sessions_model(svc).data(idx, Qt.UserRole + 7) == "3m"
    finally:
        runner.shutdown(grace_s=1.0)



def test_list_refresh_uses_incoming_order_when_keys_unchanged():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        svc.setHubReady()

        initial = [
            {
                "key": "desktop:local::s1",
                "title": "Chat 1",
                "updated_at": 10,
                "channel": "desktop",
                "has_unread": False,
            },
            {
                "key": "desktop:local::s2",
                "title": "Chat 2",
                "updated_at": 9,
                "channel": "desktop",
                "has_unread": False,
            },
        ]
        svc._handle_list_result(True, "", ([dict(s) for s in initial], "desktop:local::s1"))

        reordered = [
            {
                "key": "desktop:local::s2",
                "title": "Chat 2",
                "updated_at": 20,
                "channel": "desktop",
                "has_unread": False,
            },
            {
                "key": "desktop:local::s1",
                "title": "Chat 1",
                "updated_at": 10,
                "channel": "desktop",
                "has_unread": False,
            },
        ]
        svc._handle_list_result(True, "", ([dict(s) for s in reordered], "desktop:local::s1"))

        assert (
            _sessions_model(svc).data(_sessions_model(svc).index(0), Qt.UserRole + 1)
            == "desktop:local::s2"
        )
        assert (
            _sessions_model(svc).data(_sessions_model(svc).index(1), Qt.UserRole + 1)
            == "desktop:local::s1"
        )
    finally:
        runner.shutdown(grace_s=1.0)



def test_list_refresh_emits_active_cleared_when_sessions_empty():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        svc.setHubReady()

        sessions = [
            {"key": "desktop:local::s1", "title": "Chat 1", "updated_at": 1, "channel": "desktop"},
        ]
        active_keys: list[str] = []
        svc.activeKeyChanged.connect(active_keys.append)

        svc._handle_list_result(True, "", ([dict(s) for s in sessions], "desktop:local::s1"))
        assert svc.activeKey == "desktop:local::s1"

        svc._handle_list_result(True, "", ([], "desktop:local::s1"))
        assert _sessions_model(svc).rowCount() == 0
        assert svc.activeKey == ""
        assert active_keys[-1] == ""
    finally:
        runner.shutdown(grace_s=1.0)



def test_list_refresh_autocreates_session_when_empty_and_manager_present():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(sessions=[], active_key="")
        svc.setHubReady()
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        assert _sessions_model(svc).rowCount() == 1
        assert str(svc.activeKey).startswith("desktop:local::session-")
    finally:
        runner.shutdown(grace_s=1.0)



def test_unread_reappears_after_new_update_even_if_previously_cleared():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        svc.setHubReady()

        sessions = [
            {
                "key": "desktop:local::s1",
                "title": "Chat 1",
                "updated_at": "2026-01-01T00:00:00",
                "channel": "desktop",
            },
            {
                "key": "desktop:local::s2",
                "title": "Chat 2",
                "updated_at": "2026-01-01T00:00:00",
                "channel": "desktop",
            },
        ]

        svc._model.reset_sessions([dict(s) for s in sessions], "desktop:local::s1")
        svc._active_key = "desktop:local::s1"

        refreshed: list[dict[str, Any]] = [dict(s) for s in sessions]
        refreshed[1]["has_unread"] = True
        svc._handle_list_result(
            True,
            "",
            (refreshed, "desktop:local::s1"),
        )

        idx_s2 = _sessions_model(svc).index(1)
        assert _sessions_model(svc).data(idx_s2, Qt.UserRole + 6) is True
    finally:
        runner.shutdown(grace_s=1.0)
