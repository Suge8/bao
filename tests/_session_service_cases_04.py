# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._session_service_testkit import *

def test_initialize_does_not_sync_external_family_active_key_from_desktop_focus(tmp_path, qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = SessionManager(tmp_path)
        sm.save(sm.get_or_create("telegram:chat"))
        sm.save(sm.get_or_create("telegram:chat::s2"))
        sm.set_active_session_key("desktop:local", "telegram:chat::s2")

        svc.setHubReady()
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        assert sm.get_active_session_key("telegram:chat") is None
    finally:
        runner.shutdown(grace_s=1.0)



def test_desktop_focus_external_session_does_not_write_family_active_marker(tmp_path, qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = SessionManager(tmp_path)
        sm.save(sm.get_or_create("telegram:chat"))
        sm.save(sm.get_or_create("telegram:chat::s2"))
        svc.setHubReady()
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()
        svc.selectSession("telegram:chat::s2")

        loop2 = QEventLoop()
        QTimer.singleShot(400, loop2.quit)
        loop2.exec()

        assert sm.get_active_session_key("desktop:local") == "telegram:chat::s2"
        assert sm.get_active_session_key("telegram:chat") is None
    finally:
        runner.shutdown(grace_s=1.0)



def test_external_new_session_appears_in_sidebar_realtime(tmp_path, qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = SessionManager(tmp_path)
        sm.save(sm.get_or_create("desktop:local::main"))
        sm.set_active_session_key("desktop:local", "desktop:local::main")

        svc.setHubReady()
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        assert _sessions_model(svc).rowCount() == 1
        assert svc.activeKey == "desktop:local::main"

        async def _inbound_new_session() -> None:
            session = sm.get_or_create("imessage:+86100")
            session.add_message("user", "hello from phone")
            sm.save(session)

        runner.submit(_inbound_new_session()).result(timeout=2)

        _spin_until(
            lambda: (
                _index_by_key(svc, "imessage:+86100").isValid()
                and _sessions_model(svc).rowCount() == 2
            )
        )

        idx = _index_by_key(svc, "imessage:+86100")
        assert idx.isValid()
        assert _sessions_model(svc).rowCount() == 2
        assert svc.activeKey == "desktop:local::main"
        assert _sessions_model(svc).data(idx, Qt.UserRole + 5) == "imessage"
    finally:
        runner.shutdown(grace_s=1.0)



def test_external_session_update_does_not_steal_current_active_selection(tmp_path, qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = SessionManager(tmp_path)

        desktop = sm.get_or_create("desktop:local::main")
        desktop.add_message("assistant", "desktop history")
        sm.save(desktop)
        external = sm.get_or_create("telegram:room")
        external.add_message("user", "old external")
        sm.save(external)
        sm.set_active_session_key("desktop:local", "desktop:local::main")

        svc.setHubReady()
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        assert svc.activeKey == "desktop:local::main"

        async def _inbound_existing_session() -> None:
            session = sm.get_or_create("telegram:room")
            session.add_message("user", "new external")
            sm.save(session)

        runner.submit(_inbound_existing_session()).result(timeout=2)

        _spin_until(
            lambda: (
                (idx := _index_by_key(svc, "telegram:room")).isValid()
                and bool(_sessions_model(svc).data(idx, Qt.UserRole + 4))
            )
        )

        idx = _index_by_key(svc, "telegram:room")
        assert idx.isValid()
        assert svc.activeKey == "desktop:local::main"
        top_idx = _sessions_model(svc).index(0)
        assert _sessions_model(svc).data(top_idx, Qt.UserRole + 1) == "telegram:room"
        assert _sessions_model(svc).data(idx, Qt.UserRole + 5) == "telegram"
    finally:
        runner.shutdown(grace_s=1.0)



def test_sidebar_model_groups_sessions_in_backend_projection(tmp_path, qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = SessionManager(tmp_path)

        desktop = sm.get_or_create("desktop:local::main")
        desktop.metadata["title"] = "Main"
        desktop.add_message("assistant", "desktop")
        sm.save(desktop)

        telegram = sm.get_or_create("telegram:room")
        telegram.metadata["title"] = "Room"
        telegram.metadata["desktop_last_ai_at"] = "2026-03-06T11:00:00"
        telegram.metadata["desktop_last_seen_ai_at"] = "2026-03-06T10:00:00"
        telegram.add_message("assistant", "telegram")
        sm.save(telegram)

        child = sm.get_or_create("subagent:desktop:local::child")
        child.metadata["session_kind"] = "subagent_child"
        child.metadata["read_only"] = True
        child.metadata["parent_session_key"] = "desktop:local::main"
        child.metadata["child_status"] = "running"
        child.metadata["title"] = "child"
        child.add_message("assistant", "child")
        sm.save(child)

        sm.set_active_session_key("desktop:local", "desktop:local::main")

        svc.setHubReady()
        svc.initialize(sm)

        _spin_until(lambda: _sidebar_model(svc).rowCount() == 4)

        model = _sidebar_model(svc)
        is_header_role = _sidebar_role(model, b"isHeader")
        channel_role = _sidebar_role(model, b"channel")
        item_key_role = _sidebar_role(model, b"itemKey")
        item_unread_role = _sidebar_role(model, b"itemHasUnread")
        visual_channel_role = _sidebar_role(model, b"visualChannel")
        group_running_role = _sidebar_role(model, b"groupHasRunning")

        assert model.data(model.index(0), is_header_role) is True
        assert model.data(model.index(0), channel_role) == "desktop"
        assert model.data(model.index(0), group_running_role) is True
        assert model.data(model.index(1), item_key_role) == "desktop:local::main"
        assert model.data(model.index(2), item_key_role) == "subagent:desktop:local::child"
        assert model.data(model.index(2), visual_channel_role) == "subagent"
        assert model.data(model.index(3), is_header_role) is True
        assert model.data(model.index(3), channel_role) == "telegram"
        svc.toggleSidebarGroup("telegram")
        _spin_until(lambda: _sidebar_model(svc).rowCount() == 5)
        model = _sidebar_model(svc)
        assert model.data(model.index(4), item_unread_role) is True
    finally:
        runner.shutdown(grace_s=1.0)



def test_sidebar_projection_uses_runtime_clear_for_running_state(tmp_path, qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = SessionManager(tmp_path)

        session = sm.get_or_create("imessage:chat-1::main")
        session.metadata["title"] = "Main"
        sm.save(session)
        sm.set_session_running("imessage:chat-1::main", True, emit_change=False)
        sm.set_session_running("imessage:chat-1::main", False, emit_change=False)

        svc.initialize(sm)
        svc.setHubReady()
        svc.selectSession("imessage:chat-1::main")

        _spin_until(lambda: _sidebar_model(svc).rowCount() >= 2)

        sidebar = _sidebar_model(svc)
        item_key_role = _sidebar_role(sidebar, b"itemKey")
        group_running_role = _sidebar_role(sidebar, b"groupHasRunning")
        item_running_role = _sidebar_role(sidebar, b"isRunning")

        assert sidebar.data(sidebar.index(0), group_running_role) is False
        for index in range(sidebar.rowCount()):
            if sidebar.data(sidebar.index(index), item_key_role) != "imessage:chat-1::main":
                continue
            assert sidebar.data(sidebar.index(index), item_running_role) is False
            break
        else:
            raise AssertionError("sidebar row not found")
    finally:
        runner.shutdown(grace_s=1.0)
