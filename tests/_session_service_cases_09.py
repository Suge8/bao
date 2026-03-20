# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._session_service_testkit import *

def test_list_sessions_unread_uses_ai_timestamps_only():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[
                {
                    "key": "desktop:local::s1",
                    "title": "Chat 1",
                    "updated_at": "2026-01-01T00:10:00",
                    "metadata": {
                        "desktop_last_ai_at": "2026-01-01T00:09:00",
                        "desktop_last_seen_ai_at": "2026-01-01T00:08:00",
                    },
                },
                {
                    "key": "desktop:local::s2",
                    "title": "Chat 2",
                    "updated_at": "2026-01-01T00:11:00",
                    "metadata": {
                        "desktop_last_ai_at": "2026-01-01T00:07:00",
                        "desktop_last_seen_ai_at": "2026-01-01T00:07:00",
                    },
                },
                {
                    "key": "desktop:local::s3",
                    "title": "Chat 3",
                    "updated_at": "2026-01-01T00:12:00",
                    "metadata": {
                        "desktop_last_seen_ai_at": "2026-01-01T00:06:00",
                    },
                },
            ],
            active_key="desktop:local::s2",
        )
        svc.setHubReady()
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        idx_s1 = _index_by_key(svc, "desktop:local::s1")
        idx_s2 = _index_by_key(svc, "desktop:local::s2")
        idx_s3 = _index_by_key(svc, "desktop:local::s3")
        assert idx_s1.isValid()
        assert idx_s2.isValid()
        assert idx_s3.isValid()
        assert _sessions_model(svc).data(idx_s1, Qt.UserRole + 6) is True
        assert _sessions_model(svc).data(idx_s2, Qt.UserRole + 6) is False
        assert _sessions_model(svc).data(idx_s3, Qt.UserRole + 6) is False
    finally:
        runner.shutdown(grace_s=1.0)



def test_hub_ready_ignores_stored_external_active_for_desktop_startup():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[
                {
                    "key": "telegram:chat-1::s1",
                    "title": "Telegram",
                    "updated_at": "2026-01-01T00:12:00",
                },
                {
                    "key": "desktop:local::s1",
                    "title": "Desktop 1",
                    "updated_at": "2026-01-01T00:10:00",
                },
                {
                    "key": "desktop:local::s2",
                    "title": "Desktop 2",
                    "updated_at": "2026-01-01T00:11:00",
                },
            ],
            active_key="telegram:chat-1::s1",
        )
        svc.initialize(sm)
        svc.setHubReady()

        _spin_until(lambda: svc.activeKey != "")

        assert svc.activeKey == "desktop:local::s2"
    finally:
        runner.shutdown(grace_s=1.0)



def test_startup_target_ready_prefers_first_desktop_session_when_focus_is_external_before_start():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[
                {
                    "key": "desktop:local::s2",
                    "title": "Desktop 2",
                    "updated_at": "2026-01-01T00:11:00",
                },
                {
                    "key": "desktop:local::s1",
                    "title": "Desktop 1",
                    "updated_at": "2026-01-01T00:10:00",
                },
                {
                    "key": "imessage:13800138000::focus",
                    "title": "Focused iMessage",
                    "updated_at": "2026-01-01T00:12:00",
                },
            ]
        )
        targets: list[str] = []
        svc.startupTargetReady.connect(targets.append)

        svc.initialize(sm)
        _spin_until(lambda: _sessions_model(svc).rowCount() == 3)

        svc.selectSession("imessage:13800138000::focus")
        _spin_until(lambda: svc.activeKey == "imessage:13800138000::focus")

        svc.setHubReady()
        _spin_until(lambda: len(targets) > 0)

        assert svc.activeKey == "imessage:13800138000::focus"
        assert targets[-1] == "desktop:local::s2"
    finally:
        runner.shutdown(grace_s=1.0)



def test_select_session_does_not_mark_seen_ai_in_session_service():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[
                {"key": "desktop:local::s1", "title": "Chat 1"},
                {"key": "desktop:local::s2", "title": "Chat 2"},
            ],
            active_key="desktop:local::s1",
        )
        svc.setHubReady()
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        svc.selectSession("desktop:local::s2")

        loop2 = QEventLoop()
        QTimer.singleShot(300, loop2.quit)
        loop2.exec()

        assert sm.update_metadata_only.call_count == 0
    finally:
        runner.shutdown(grace_s=1.0)



def test_new_session_sets_active_key_before_list_refresh():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[{"key": "desktop:local::s1", "title": "Chat 1"}],
            active_key="desktop:local::s1",
        )
        svc.setHubReady()
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        emitted_keys: list[str] = []
        svc.activeKeyChanged.connect(emitted_keys.append)

        svc.newSession("")

        loop2 = QEventLoop()
        QTimer.singleShot(300, loop2.quit)
        loop2.exec()

        assert str(svc.activeKey).startswith("desktop:local::session-")
        assert any(key.startswith("desktop:local::session-") for key in emitted_keys)
    finally:
        runner.shutdown(grace_s=1.0)



def test_new_session_success_avoids_full_refresh(qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[{"key": "desktop:local::s1", "title": "Chat 1"}],
            active_key="desktop:local::s1",
        )
        svc.setHubReady()
        svc.initialize(sm)
        _spin_until(lambda: _sessions_model(svc).rowCount() == 1)

        refresh_calls = 0
        original_refresh = svc.refresh

        def _tracked_refresh() -> None:
            nonlocal refresh_calls
            refresh_calls += 1
            original_refresh()

        svc.refresh = _tracked_refresh  # type: ignore[method-assign]
        initial_list_calls = sm.list_sessions.call_count

        svc.newSession("")

        _spin_until(
            lambda: (
                str(svc.activeKey).startswith("desktop:local::session-")
                and svc._pending_select_key in (None, "")
                and len(svc._pending_creates) == 0
            )
        )

        assert refresh_calls == 0
        assert sm.list_sessions.call_count == initial_list_calls
        assert _sessions_model(svc).rowCount() == 2
    finally:
        runner.shutdown(grace_s=1.0)



def test_service_delete_session_updates_model():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[
                {"key": "desktop:local::s1", "title": "Chat 1"},
                {"key": "desktop:local::s2", "title": "Chat 2"},
            ],
            active_key="desktop:local::s1",
        )
        svc.setHubReady()
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        assert _sessions_model(svc).rowCount() == 2

        events = []
        svc.deleteCompleted.connect(lambda key, ok, _err: events.append((key, ok)))

        svc.deleteSession("desktop:local::s1")
        assert _sessions_model(svc).rowCount() == 1
        assert svc.activeKey == "desktop:local::s2"

        loop2 = QEventLoop()
        QTimer.singleShot(300, loop2.quit)
        loop2.exec()

        assert _sessions_model(svc).rowCount() == 1
        assert svc.activeKey == "desktop:local::s2"
        assert ("desktop:local::s1", True) in events
    finally:
        runner.shutdown(grace_s=1.0)
