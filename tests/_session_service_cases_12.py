# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._session_service_testkit import *

def test_metadata_change_updates_session_without_full_refresh(qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[
                {"key": "desktop:local::s1", "title": "Chat 1", "updated_at": 10},
                {"key": "desktop:local::s2", "title": "Chat 2", "updated_at": 9},
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
        initial_list_calls = sm.list_sessions_with_active_key.call_count

        sm._update_session(
            "desktop:local::s2",
            metadata={"title": "Renamed Chat 2"},
        )
        sm._emit_change("desktop:local::s2", "metadata")

        _spin_until(
            lambda: _sessions_model(svc).data(
                _index_by_key(svc, "desktop:local::s2"), Qt.UserRole + 2
            )
            == "Renamed Chat 2"
        )

        assert refresh_calls == 0
        assert sm.list_sessions_with_active_key.call_count == initial_list_calls
        assert sm.get_session_list_entry.call_count >= 1
    finally:
        runner.shutdown(grace_s=1.0)



def test_message_change_updates_session_without_full_refresh(qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[
                {"key": "desktop:local::s1", "title": "Chat 1", "updated_at": 10},
                {"key": "desktop:local::s2", "title": "Chat 2", "updated_at": 9},
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
        initial_list_calls = sm.list_sessions_with_active_key.call_count

        sm._update_session(
            "desktop:local::s2",
            updated_at=20,
            message_count=3,
            has_messages=True,
            metadata={
                "title": "Chat 2",
                "desktop_last_ai_at": "2026-03-14T10:00:00",
                "desktop_last_seen_ai_at": "2026-03-14T09:00:00",
            },
        )
        sm._emit_change("desktop:local::s2", "messages")

        _spin_until(
            lambda: _sessions_model(svc).data(_sessions_model(svc).index(0), Qt.UserRole + 1)
            == "desktop:local::s2"
        )

        idx = _sessions_model(svc).index(0)
        assert refresh_calls == 0
        assert sm.list_sessions_with_active_key.call_count == initial_list_calls
        assert sm.get_session_list_entry.call_count >= 1
        assert _sessions_model(svc).data(idx, Qt.UserRole + 8) == 3
        assert _sessions_model(svc).data(idx, Qt.UserRole + 6) is True
    finally:
        runner.shutdown(grace_s=1.0)



def test_stale_incremental_session_entry_result_does_not_override_newer_state():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[
                {"key": "desktop:local::s1", "title": "Chat 1", "updated_at": 10},
                {"key": "desktop:local::s2", "title": "Current", "updated_at": 9},
            ],
            active_key="desktop:local::s1",
        )
        svc.setHubReady()
        svc.initialize(sm)
        _spin_until(lambda: _sessions_model(svc).rowCount() == 2)

        generation = svc._session_entry_generation
        svc._session_entry_request_seq["desktop:local::s2"] = 2

        svc._handle_session_entry_result(
            True,
            "",
            (
                "desktop:local::s2",
                1,
                generation,
                {
                    "key": "desktop:local::s2",
                    "updated_at": 8,
                    "metadata": {"title": "Stale"},
                },
            ),
        )

        idx = _index_by_key(svc, "desktop:local::s2")
        assert _sessions_model(svc).data(idx, Qt.UserRole + 2) == "Current"

        svc._handle_session_entry_result(
            True,
            "",
            (
                "desktop:local::s2",
                2,
                generation - 1,
                {
                    "key": "desktop:local::s2",
                    "updated_at": 8,
                    "metadata": {"title": "Older Generation"},
                },
            ),
        )

        assert _sessions_model(svc).data(idx, Qt.UserRole + 2) == "Current"
    finally:
        runner.shutdown(grace_s=1.0)



def test_incremental_message_change_backfills_only_updated_session(qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[
                {
                    "key": "desktop:local::s1",
                    "title": "Chat 1",
                    "updated_at": 10,
                    "needs_tail_backfill": True,
                },
                {"key": "desktop:local::s2", "title": "Chat 2", "updated_at": 9},
            ],
            active_key="desktop:local::s1",
        )
        svc.setHubReady()
        svc.initialize(sm)
        _spin_until(lambda: _sessions_model(svc).rowCount() == 2)
        sm.backfill_display_tail_rows.reset_mock()

        sm._update_session(
            "desktop:local::s2",
            updated_at=20,
            needs_tail_backfill=True,
            message_count=2,
            has_messages=True,
            metadata={"title": "Chat 2"},
        )
        sm._emit_change("desktop:local::s2", "messages")

        _spin_until(lambda: sm.backfill_display_tail_rows.call_count >= 1)

        sm.backfill_display_tail_rows.assert_called_once_with(["desktop:local::s2"], 200)
    finally:
        runner.shutdown(grace_s=1.0)



def test_incremental_message_change_uses_row_upsert_not_full_sync(qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[
                {"key": "desktop:local::s1", "title": "Chat 1", "updated_at": 10},
                {"key": "desktop:local::s2", "title": "Chat 2", "updated_at": 9},
            ],
            active_key="desktop:local::s1",
        )
        svc.setHubReady()
        svc.initialize(sm)
        _spin_until(lambda: _sessions_model(svc).rowCount() == 2)

        original_upsert = svc._model.upsert_sessions
        upsert_calls = 0

        def _tracked_upsert(sessions: list[dict[str, Any]], active_key: str) -> None:
            nonlocal upsert_calls
            upsert_calls += 1
            original_upsert(sessions, active_key)

        def _unexpected_sync(_sessions: list[dict[str, Any]], _active_key: str) -> None:
            raise AssertionError("incremental path should not call sync_sessions")

        svc._model.upsert_sessions = _tracked_upsert  # type: ignore[method-assign]
        svc._model.sync_sessions = _unexpected_sync  # type: ignore[method-assign]

        sm._update_session(
            "desktop:local::s2",
            updated_at=20,
            message_count=1,
            has_messages=True,
            metadata={"title": "Chat 2"},
        )
        sm._emit_change("desktop:local::s2", "messages")

        _spin_until(lambda: upsert_calls == 1)
        assert upsert_calls == 1
    finally:
        runner.shutdown(grace_s=1.0)



def test_delete_success_with_active_sync_failure_keeps_deleted_session_gone(qt_app):
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
            fail_set_active=True,
        )
        events = []
        svc.deleteCompleted.connect(lambda key, ok, _err: events.append((key, ok)))
        svc.setHubReady()
        svc.initialize(sm)

        _spin_until(lambda: _sessions_model(svc).rowCount() == 2)

        svc.deleteSession("desktop:local::s1")

        _spin_until(lambda: _sessions_model(svc).rowCount() == 1)
        _spin_until(lambda: svc.activeKey == "desktop:local::s2")
        _spin_until(lambda: ("desktop:local::s1", True) in events)
        idx = _sessions_model(svc).index(0)
        assert _sessions_model(svc).data(idx, Qt.UserRole + 1) == "desktop:local::s2"
    finally:
        runner.shutdown(grace_s=1.0)
