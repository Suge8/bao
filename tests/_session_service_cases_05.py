# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._session_service_testkit import *


def _persist_stale_running_child(meta_table, child) -> None:
    meta_table.delete("session_key = 'subagent:imessage:chat-1::child'")
    meta_table.add(
        [
            {
                "session_key": "subagent:imessage:chat-1::child",
                "created_at": child.created_at.isoformat(),
                "updated_at": child.updated_at.isoformat(),
                "metadata_json": json.dumps(
                    {
                        "title": "Child",
                        "session_kind": "subagent_child",
                        "read_only": True,
                        "parent_session_key": "imessage:chat-1::main",
                        "child_status": "running",
                        "active_task_id": "task-1",
                    },
                    ensure_ascii=False,
                ),
                "last_consolidated": 0,
            }
        ]
    )


def _assert_child_sidebar_not_running(svc) -> None:
    sidebar = _sidebar_model(svc)
    item_key_role = _sidebar_role(sidebar, b"itemKey")
    group_running_role = _sidebar_role(sidebar, b"groupHasRunning")
    item_running_role = _sidebar_role(sidebar, b"isRunning")
    assert sidebar.data(sidebar.index(0), group_running_role) is False
    for index in range(sidebar.rowCount()):
        if sidebar.data(sidebar.index(index), item_key_role) != "subagent:imessage:chat-1::child":
            continue
        assert sidebar.data(sidebar.index(index), item_running_role) is False
        return
    raise AssertionError("child sidebar row not found")


def test_sidebar_projection_ignores_stale_persisted_running_child_after_restart(tmp_path, qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = SessionManager(tmp_path)

        parent = sm.get_or_create("imessage:chat-1::main")
        parent.metadata["title"] = "Main"
        sm.save(parent)

        child = sm.get_or_create("subagent:imessage:chat-1::child")
        child.metadata.update(
            {
                "title": "Child",
                "session_kind": "subagent_child",
                "read_only": True,
                "parent_session_key": "imessage:chat-1::main",
            }
        )
        sm.save(child)

        _persist_stale_running_child(sm._meta_table(), child)
        reloaded = SessionManager(tmp_path)
        svc.initialize(reloaded)
        svc.setHubReady()
        svc.selectSession("imessage:chat-1::main")
        _spin_until(lambda: _sidebar_model(svc).rowCount() >= 2)
        _assert_child_sidebar_not_running(svc)
    finally:
        runner.shutdown(grace_s=1.0)



def test_toggle_sidebar_group_updates_backend_row_visibility(tmp_path, qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = SessionManager(tmp_path)

        desktop = sm.get_or_create("desktop:local::main")
        desktop.add_message("assistant", "desktop")
        sm.save(desktop)

        telegram = sm.get_or_create("telegram:room")
        telegram.add_message("assistant", "telegram")
        sm.save(telegram)

        svc.setHubReady()
        svc.initialize(sm)

        _spin_until(lambda: _sidebar_model(svc).rowCount() >= 3)

        model = _sidebar_model(svc)
        item_key_role = _sidebar_role(model, b"itemKey")
        assert all(
            model.data(model.index(i), item_key_role) != "telegram:room"
            for i in range(model.rowCount())
        )

        svc.toggleSidebarGroup("telegram")

        _spin_until(
            lambda: any(
                _sidebar_model(svc).data(_sidebar_model(svc).index(i), item_key_role)
                == "telegram:room"
                for i in range(_sidebar_model(svc).rowCount())
            )
        )
        model = _sidebar_model(svc)

        assert any(
            model.data(model.index(i), item_key_role) == "telegram:room"
            for i in range(model.rowCount())
        )
    finally:
        runner.shutdown(grace_s=1.0)



def test_collapsed_active_group_keeps_only_active_row_visible(tmp_path, qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = SessionManager(tmp_path)

        active = sm.get_or_create("desktop:local::main")
        active.add_message("assistant", "main")
        sm.save(active)

        sibling = sm.get_or_create("desktop:local::scratch")
        sibling.add_message("assistant", "scratch")
        sm.save(sibling)

        other = sm.get_or_create("telegram:room")
        other.add_message("assistant", "telegram")
        sm.save(other)

        sm.set_active_session_key("desktop:local", "desktop:local::main")

        svc.setHubReady()
        svc.initialize(sm)

        _spin_until(lambda: _sidebar_model(svc).rowCount() >= 3)
        svc.toggleSidebarGroup("desktop")

        model = _sidebar_model(svc)
        item_key_role = _sidebar_role(model, b"itemKey")
        is_header_role = _sidebar_role(model, b"isHeader")
        channel_role = _sidebar_role(model, b"channel")
        expanded_role = _sidebar_role(model, b"expanded")

        def _desktop_collapsed_with_active_only() -> bool:
            keys = [
                model.data(model.index(i), item_key_role)
                for i in range(model.rowCount())
                if not model.data(model.index(i), is_header_role)
            ]
            desktop_headers = [
                model.data(model.index(i), expanded_role)
                for i in range(model.rowCount())
                if model.data(model.index(i), is_header_role)
                and model.data(model.index(i), channel_role) == "desktop"
            ]
            return (
                desktop_headers == [False]
                and "desktop:local::main" in keys
                and "desktop:local::scratch" not in keys
            )

        _spin_until(_desktop_collapsed_with_active_only)
    finally:
        runner.shutdown(grace_s=1.0)



def test_select_session_keeps_target_group_collapsed_when_user_never_expanded_it(tmp_path, qt_app):
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

        desktop = sm.get_or_create("desktop:local::main")
        desktop.add_message("assistant", "desktop")
        sm.save(desktop)

        sm.set_active_session_key("desktop:local", "desktop:local::main")

        svc.setHubReady()
        svc.initialize(sm)

        _spin_until(lambda: _sidebar_model(svc).rowCount() >= 3)
        svc.selectSession("imessage:chat::main")
        _spin_until(lambda: svc.activeKey == "imessage:chat::main")

        model = _sidebar_model(svc)
        item_key_role = _sidebar_role(model, b"itemKey")
        is_header_role = _sidebar_role(model, b"isHeader")
        channel_role = _sidebar_role(model, b"channel")
        expanded_role = _sidebar_role(model, b"expanded")

        def _target_group_stays_collapsed() -> bool:
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

        _spin_until(_target_group_stays_collapsed)
    finally:
        runner.shutdown(grace_s=1.0)
