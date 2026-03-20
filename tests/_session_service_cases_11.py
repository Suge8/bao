# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._session_service_testkit import *

def test_service_delete_active_prefers_same_channel_neighbor():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[
                {"key": "telegram:chat::1", "title": "T1"},
                {"key": "desktop:local::s1", "title": "D1"},
                {"key": "telegram:chat::2", "title": "T2"},
                {"key": "desktop:local::s2", "title": "D2"},
            ],
            active_key="desktop:local::s1",
        )
        svc.setHubReady()
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        svc.deleteSession("desktop:local::s1")
        assert svc.activeKey == "desktop:local::s2"

        loop2 = QEventLoop()
        QTimer.singleShot(300, loop2.quit)
        loop2.exec()

        assert sm.get_active_session_key("desktop:local") == "desktop:local::s2"
    finally:
        runner.shutdown(grace_s=1.0)



def test_service_refresh_during_pending_delete_does_not_resurrect_session():
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

        original_delete = svc._delete_session

        async def _delayed_delete(key: str, new_active: str, seq: int | None) -> str:
            await asyncio.sleep(0.15)
            return await original_delete(key, new_active, seq)

        svc._delete_session = _delayed_delete

        svc.deleteSession("desktop:local::s1")
        assert _sessions_model(svc).rowCount() == 1

        svc.refresh()
        loop2 = QEventLoop()
        QTimer.singleShot(80, loop2.quit)
        loop2.exec()

        assert _sessions_model(svc).rowCount() == 1
        idx = _sessions_model(svc).index(0)
        assert _sessions_model(svc).data(idx, Qt.UserRole + 1) == "desktop:local::s2"

        loop3 = QEventLoop()
        QTimer.singleShot(300, loop3.quit)
        loop3.exec()

        assert _sessions_model(svc).rowCount() == 1
        idx2 = _sessions_model(svc).index(0)
        assert _sessions_model(svc).data(idx2, Qt.UserRole + 1) == "desktop:local::s2"
    finally:
        runner.shutdown(grace_s=1.0)



def test_local_delete_ignores_followup_deleted_change_event(qt_app):
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
        original_delete = sm.delete_session.side_effect

        def _delete_with_change(key: str) -> bool:
            assert callable(original_delete)
            result = bool(original_delete(key))
            sm._emit_change(key, "deleted")
            return result

        sm.delete_session.side_effect = _delete_with_change
        svc.setHubReady()
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        sessions_changed_count = 0

        def _count_sessions_changed() -> None:
            nonlocal sessions_changed_count
            sessions_changed_count += 1

        svc.sessionsChanged.connect(_count_sessions_changed)

        svc.deleteSession("desktop:local::s1")

        loop2 = QEventLoop()
        QTimer.singleShot(300, loop2.quit)
        loop2.exec()

        assert _sessions_model(svc).rowCount() == 1
        idx = _sessions_model(svc).index(0)
        assert _sessions_model(svc).data(idx, Qt.UserRole + 1) == "desktop:local::s2"
        assert sessions_changed_count == 1
    finally:
        runner.shutdown(grace_s=1.0)



def test_service_delete_failure_rollback_respects_other_pending_deletes():
    from app.backend.session import PendingDeleteState

    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sessions_before = [
            {"key": "desktop:local::s1", "title": "S1", "channel": "desktop"},
            {"key": "desktop:local::s2", "title": "S2", "channel": "desktop"},
            {"key": "desktop:local::s3", "title": "S3", "channel": "desktop"},
        ]
        svc._active_key = "desktop:local::s3"
        svc._model.reset_sessions([sessions_before[2]], "desktop:local::s3")
        svc._pending_deletes = {
            "desktop:local::s1": PendingDeleteState(
                sessions_before=sessions_before,
                active_before="desktop:local::s1",
                optimistic_active="desktop:local::s3",
                expanded_groups={"desktop": True},
            ),
            "desktop:local::s2": PendingDeleteState(
                sessions_before=sessions_before,
                active_before="desktop:local::s2",
                optimistic_active="desktop:local::s3",
                expanded_groups={"desktop": True},
            ),
        }

        svc._handle_delete_result("desktop:local::s1", False, "delete failed")

        keys = [
            _sessions_model(svc).data(_sessions_model(svc).index(i), Qt.UserRole + 1)
            for i in range(_sessions_model(svc).rowCount())
        ]
        assert "desktop:local::s2" not in keys
        assert "desktop:local::s1" in keys
        assert "desktop:local::s3" in keys
    finally:
        runner.shutdown(grace_s=1.0)



def test_external_deleted_change_event_still_refreshes_visible_session(qt_app):
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

        sm.list_sessions.side_effect = lambda: [
            sm._serialize_session({"key": "desktop:local::s1", "updated_at": "2", "metadata": {}}),
        ]

        svc._handle_session_change(
            SessionChangeEvent(session_key="desktop:local::s2", kind="deleted")
        )

        loop2 = QEventLoop()
        QTimer.singleShot(300, loop2.quit)
        loop2.exec()

        assert _sessions_model(svc).rowCount() == 1
        idx = _sessions_model(svc).index(0)
        assert _sessions_model(svc).data(idx, Qt.UserRole + 1) == "desktop:local::s1"
    finally:
        runner.shutdown(grace_s=1.0)



def test_external_deleted_change_updates_model_without_full_refresh(qt_app):
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
        _spin_until(lambda: _sessions_model(svc).rowCount() == 2)

        refresh_calls = 0
        original_refresh = svc.refresh

        def _tracked_refresh() -> None:
            nonlocal refresh_calls
            refresh_calls += 1
            original_refresh()

        svc.refresh = _tracked_refresh  # type: ignore[method-assign]
        initial_list_calls = sm.list_sessions.call_count

        sm._emit_change("desktop:local::s2", "deleted")

        _spin_until(lambda: _sessions_model(svc).rowCount() == 1)

        idx = _sessions_model(svc).index(0)
        assert refresh_calls == 0
        assert sm.list_sessions.call_count == initial_list_calls
        assert _sessions_model(svc).data(idx, Qt.UserRole + 1) == "desktop:local::s1"
    finally:
        runner.shutdown(grace_s=1.0)
