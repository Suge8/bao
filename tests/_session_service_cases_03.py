# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._session_service_testkit import *

def test_bootstrap_done_ignores_cancelled_future() -> None:
    import concurrent.futures

    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        fut: concurrent.futures.Future[object] = concurrent.futures.Future()
        fut.cancel()

        svc._on_bootstrap_done(fut)

        assert svc._local_hub_ports is None
    finally:
        runner.shutdown(grace_s=1.0)



def test_session_change_event_refreshes_session_list(qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(sessions=[{"key": "desktop:local", "title": "default"}])
        svc.setHubReady()
        svc.initialize(sm)
        qt_app.processEvents()

        sm.list_sessions.side_effect = lambda: [
            sm._serialize_session({"key": "desktop:local", "updated_at": "1", "metadata": {}}),
            sm._serialize_session({"key": "telegram:123", "updated_at": "2", "metadata": {}}),
        ]

        sm._emit_change("telegram:123", "messages")
        _spin_until(lambda: _sessions_model(svc).rowCount() == 2)
    finally:
        runner.shutdown(grace_s=1.0)



def test_refresh_exposes_sessions_loading_state(qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        svc._local_hub_directory = object()

        async def _slow_list(seq: int):
            await asyncio.sleep(0.05)
            return seq, [], ""

        loading_events: list[bool] = []
        svc.sessionsLoadingChanged.connect(loading_events.append)

        with patch.object(svc, "_list_sessions", side_effect=_slow_list):
            svc.refresh()
            assert svc.sessionsLoading is True

            loop = QEventLoop()
            QTimer.singleShot(200, loop.quit)
            loop.exec()

        assert svc.sessionsLoading is False
        assert loading_events[0] is True
        assert loading_events[-1] is False
    finally:
        runner.shutdown(grace_s=1.0)



def test_refresh_coalesces_repeated_requests_while_inflight(qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        svc._local_hub_directory = object()

        started: list[int] = []

        async def _slow_list(seq: int):
            started.append(seq)
            await asyncio.sleep(0.05)
            return seq, [], ""

        with patch.object(svc, "_list_sessions", side_effect=_slow_list):
            svc.refresh()
            svc.refresh()
            svc.refresh()

            _spin_until(lambda: started == [1], timeout_ms=80, tick_ms=10)
            _spin_until(lambda: started == [1, 2], timeout_ms=300, tick_ms=10)

        assert started == [1, 2]
    finally:
        runner.shutdown(grace_s=1.0)



def test_set_local_active_key_clears_unread_for_selected_session(qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        svc._model.reset_sessions(
            [
                {
                    "key": "desktop:local::default",
                    "title": "default",
                    "is_active": False,
                    "updated_at": "",
                    "channel": "desktop",
                    "has_unread": False,
                    "updated_label": "",
                },
                {
                    "key": "telegram:room1",
                    "title": "room1",
                    "is_active": False,
                    "updated_at": "",
                    "channel": "telegram",
                    "has_unread": True,
                    "updated_label": "",
                },
            ],
            "",
        )

        svc._set_local_active_key("telegram:room1")
        svc._set_local_active_key("desktop:local::default")

        unread_role = int(Qt.ItemDataRole.UserRole) + 6
        telegram_index = svc._model.index(1, 0)
        assert svc._model.data(telegram_index, unread_role) is False
    finally:
        runner.shutdown(grace_s=1.0)



def test_set_local_active_key_updates_active_projection_without_sessions_changed(qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        svc._model.reset_sessions(
            [
                {
                    "key": "desktop:local::s1",
                    "title": "s1",
                    "is_active": True,
                    "updated_at": "",
                    "channel": "desktop",
                    "has_unread": False,
                    "updated_label": "",
                    "message_count": 1,
                    "has_messages": True,
                },
                {
                    "key": "desktop:local::s2",
                    "title": "s2",
                    "is_active": False,
                    "updated_at": "",
                    "channel": "desktop",
                    "has_unread": False,
                    "updated_label": "",
                    "message_count": 3,
                    "has_messages": True,
                },
            ],
            "desktop:local::s1",
        )

        changed_events: list[bool] = []
        summaries: list[tuple[str, object, object]] = []
        svc.sessionsChanged.connect(lambda: changed_events.append(True))
        svc.activeSummaryChanged.connect(
            lambda key, count, has_messages: summaries.append((key, count, has_messages))
        )

        svc._set_local_active_key("desktop:local::s2")

        assert changed_events == []
        assert summaries[-1] == ("desktop:local::s2", 3, True)
    finally:
        runner.shutdown(grace_s=1.0)



def test_session_change_event_ignores_after_shutdown(qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(sessions=[{"key": "desktop:local", "title": "default"}])
        svc.initialize(sm)
        qt_app.processEvents()

        svc.shutdown()
        sm._emit_change("desktop:local", "messages")
        qt_app.processEvents()

        assert svc.activeKey == ""
    finally:
        runner.shutdown(grace_s=1.0)



def test_list_result_triggers_background_display_tail_backfill(qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = MagicMock()
        svc._local_hub_directory = sm.directory = MagicMock()
        sessions = [
            {
                "key": "desktop:local::s1",
                "title": "One",
                "updated_at": 1,
                "channel": "desktop",
                "needs_tail_backfill": True,
            },
            {
                "key": "desktop:local::s2",
                "title": "Two",
                "updated_at": 2,
                "channel": "desktop",
                "needs_tail_backfill": True,
            },
        ]

        svc._handle_list_result(True, "", ([dict(s) for s in sessions], "desktop:local::s1"))

        loop = QEventLoop()
        QTimer.singleShot(250, loop.quit)
        loop.exec()

        sm.backfill_display_tail_rows.assert_called_once_with(
            ["desktop:local::s1", "desktop:local::s2"], 200
        )
    finally:
        runner.shutdown(grace_s=1.0)



def test_active_summary_changed_emits_current_session_summary(qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        svc.setHubReady()
        summaries: list[tuple[str, object, object]] = []
        svc.activeSummaryChanged.connect(
            lambda key, count, has_messages: summaries.append((key, count, has_messages))
        )

        svc._handle_list_result(
            True,
            "",
            (
                [
                    {
                        "key": "desktop:local::empty",
                        "title": "Empty",
                        "updated_at": 1,
                        "channel": "desktop",
                        "message_count": 0,
                        "has_messages": False,
                    }
                ],
                "desktop:local::empty",
            ),
        )

        assert summaries[-1] == ("desktop:local::empty", 0, False)
    finally:
        runner.shutdown(grace_s=1.0)
