# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._session_service_testkit import *

def test_session_refresh_keeps_active_group_collapsed(tmp_path, qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = SessionManager(tmp_path)

        active = sm.get_or_create("imessage:chat::main")
        active.add_message("assistant", "main")
        sm.save(active)

        sibling = sm.get_or_create("imessage:chat::other")
        sibling.add_message("assistant", "other")
        sm.save(sibling)

        sm.set_active_session_key("desktop:local", "imessage:chat::main")

        svc.setHubReady()
        svc.initialize(sm)

        _spin_until(lambda: _sidebar_model(svc).rowCount() >= 3)
        svc.selectSession("imessage:chat::main")
        _spin_until(lambda: svc.activeKey == "imessage:chat::main")
        svc.toggleSidebarGroup("imessage")

        model = _sidebar_model(svc)
        item_key_role = _sidebar_role(model, b"itemKey")
        is_header_role = _sidebar_role(model, b"isHeader")
        channel_role = _sidebar_role(model, b"channel")
        expanded_role = _sidebar_role(model, b"expanded")

        _spin_until(
            lambda: any(
                model.data(model.index(i), is_header_role)
                and model.data(model.index(i), channel_role) == "imessage"
                and model.data(model.index(i), expanded_role) is False
                for i in range(model.rowCount())
            )
        )

        refreshed = sm.get_or_create("imessage:chat::main")
        refreshed.add_message("assistant", "reply")
        sm.save(refreshed)

        def _collapsed_after_refresh() -> bool:
            header_collapsed = any(
                model.data(model.index(i), is_header_role)
                and model.data(model.index(i), channel_role) == "imessage"
                and model.data(model.index(i), expanded_role) is False
                for i in range(model.rowCount())
            )
            keys = [
                model.data(model.index(i), item_key_role)
                for i in range(model.rowCount())
                if not model.data(model.index(i), is_header_role)
            ]
            return (
                header_collapsed
                and "imessage:chat::main" in keys
                and "imessage:chat::other" not in keys
            )

        _spin_until(_collapsed_after_refresh)
    finally:
        runner.shutdown(grace_s=1.0)



def test_active_sidebar_row_stays_within_its_group_when_rows_above_change(tmp_path, qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = SessionManager(tmp_path)

        sm.save(sm.get_or_create("desktop:local::main"))
        sm.save(sm.get_or_create("desktop:local::scratch"))
        sm.save(sm.get_or_create("telegram:room1"))
        sm.save(sm.get_or_create("telegram:room2"))

        svc.setHubReady()
        svc.initialize(sm)

        item_key_role = _sidebar_role(_sidebar_model(svc), b"itemKey")
        channel_role = _sidebar_role(_sidebar_model(svc), b"channel")
        is_header_role = _sidebar_role(_sidebar_model(svc), b"isHeader")

        def _has_telegram_header() -> bool:
            model = _sidebar_model(svc)
            for i in range(model.rowCount()):
                index = model.index(i)
                if (
                    model.data(index, is_header_role) is True
                    and model.data(index, channel_role) == "telegram"
                ):
                    return True
            return False

        def _telegram_sidebar_ready() -> bool:
            model = _sidebar_model(svc)
            header_index = -1
            active_index = -1
            for i in range(model.rowCount()):
                index = model.index(i)
                if (
                    model.data(index, is_header_role) is True
                    and model.data(index, channel_role) == "telegram"
                ):
                    header_index = i
                if model.data(index, item_key_role) == "telegram:room2":
                    active_index = i
            return header_index >= 0 and active_index > header_index

        _spin_until(_has_telegram_header)
        svc.selectSession("telegram:room2")
        _spin_until(lambda: svc.activeKey == "telegram:room2")
        _spin_until(_telegram_sidebar_ready)

        extra = sm.get_or_create("desktop:local::newer")
        extra.add_message("assistant", "desktop update")
        sm.save(extra)

        _spin_until(_telegram_sidebar_ready)
    finally:
        runner.shutdown(grace_s=1.0)



def test_rapid_same_family_selection_only_updates_desktop_active_key(tmp_path, qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = SessionManager(tmp_path)
        sm.save(sm.get_or_create("telegram:chat::s1"))
        sm.save(sm.get_or_create("telegram:chat::s2"))

        svc.setHubReady()
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        svc.selectSession("telegram:chat::s1")
        svc.selectSession("telegram:chat::s2")

        loop2 = QEventLoop()
        QTimer.singleShot(400, loop2.quit)
        loop2.exec()

        assert sm.get_active_session_key("desktop:local") == "telegram:chat::s2"
        assert sm.get_active_session_key("telegram:chat") is None
    finally:
        runner.shutdown(grace_s=1.0)



def test_metadata_change_event_refreshes_session_list_for_plan_updates(qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(sessions=[{"key": "desktop:local", "title": "default"}])
        svc.setHubReady()
        svc.initialize(sm)
        qt_app.processEvents()

        sm.list_sessions.side_effect = lambda: [
            sm._serialize_session(
                {
                    "key": "desktop:local",
                    "updated_at": "2",
                    "metadata": {"title": "default", "_plan_state": {"goal": "ship"}},
                }
            )
        ]

        sm._emit_change("desktop:local", "metadata")
        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        assert _sessions_model(svc).rowCount() == 1
        idx = _sessions_model(svc).index(0)
        assert _sessions_model(svc).data(idx, Qt.UserRole + 1) == "desktop:local"
    finally:
        runner.shutdown(grace_s=1.0)



def test_session_service_labels_cron_and_heartbeat_channels(qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[
                {"key": "heartbeat", "title": "heartbeat", "updated_at": "1"},
                {"key": "cron:job-1", "title": "cron", "updated_at": "2"},
            ]
        )
        svc.setHubReady()
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        heartbeat_idx = _index_by_key(svc, "heartbeat")
        cron_idx = _index_by_key(svc, "cron:job-1")
        assert _sessions_model(svc).data(heartbeat_idx, Qt.UserRole + 5) == "heartbeat"
        assert _sessions_model(svc).data(cron_idx, Qt.UserRole + 5) == "cron"
    finally:
        runner.shutdown(grace_s=1.0)



def test_service_refresh_populates_model():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[{"key": "desktop:local::s1", "title": "Chat 1"}],
            active_key="desktop:local::s1",
        )
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        assert _sessions_model(svc).rowCount() == 1
        assert svc.activeKey == "desktop:local::s1"
        idx = _sessions_model(svc).index(0)
        assert _sessions_model(svc).data(idx, Qt.UserRole + 3) is True
    finally:
        runner.shutdown(grace_s=1.0)



def test_service_refresh_exposes_active_key_before_hub_ready():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[{"key": "desktop:local::s1", "title": "Chat 1"}],
            active_key="desktop:local::s1",
        )

        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        assert svc.activeKey == "desktop:local::s1"
        idx = _sessions_model(svc).index(0)
        assert _sessions_model(svc).data(idx, Qt.UserRole + 3) is True
    finally:
        runner.shutdown(grace_s=1.0)
