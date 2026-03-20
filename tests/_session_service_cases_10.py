# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._session_service_testkit import *

def test_service_delete_session_persists_in_storage(tmp_path):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = SessionManager(tmp_path)
        s1 = sm.get_or_create("desktop:local::s1")
        s1.add_message("user", "hello")
        sm.save(s1)
        s2 = sm.get_or_create("desktop:local::s2")
        s2.add_message("user", "world")
        sm.save(s2)
        sm.set_active_session_key("desktop:local", "desktop:local::s1")

        svc.setHubReady()
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(400, loop.quit)
        loop.exec()

        assert _sessions_model(svc).rowCount() == 2

        svc.deleteSession("desktop:local::s1")

        loop2 = QEventLoop()
        QTimer.singleShot(400, loop2.quit)
        loop2.exec()

        keys = [row["key"] for row in sm.list_sessions()]
        assert "desktop:local::s1" not in keys
        assert "desktop:local::s2" in keys
    finally:
        runner.shutdown(grace_s=1.0)



def test_service_delete_failure_restores_model():
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
            fail_delete=True,
        )
        svc.setHubReady()
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        events = []
        svc.deleteCompleted.connect(lambda key, ok, _err: events.append((key, ok)))

        svc.deleteSession("desktop:local::s1")
        assert _sessions_model(svc).rowCount() == 1

        loop2 = QEventLoop()
        QTimer.singleShot(300, loop2.quit)
        loop2.exec()

        assert _sessions_model(svc).rowCount() == 2
        assert svc.activeKey == "desktop:local::s1"
        assert ("desktop:local::s1", False) in events
    finally:
        runner.shutdown(grace_s=1.0)



def test_service_delete_false_result_restores_model():
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
            delete_returns_false=True,
        )
        svc.setHubReady()
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        events = []
        svc.deleteCompleted.connect(lambda key, ok, _err: events.append((key, ok)))

        svc.deleteSession("desktop:local::s1")
        assert _sessions_model(svc).rowCount() == 1

        loop2 = QEventLoop()
        QTimer.singleShot(300, loop2.quit)
        loop2.exec()

        assert _sessions_model(svc).rowCount() == 2
        assert svc.activeKey == "desktop:local::s1"
        assert ("desktop:local::s1", False) in events
    finally:
        runner.shutdown(grace_s=1.0)



def test_delete_failure_restores_collapsed_group_state_when_group_temporarily_disappears(
    qt_app,
):
    from app.backend.session import PendingDeleteState

    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sessions_before = [
            {"key": "desktop:local::main", "title": "Desktop", "channel": "desktop"},
            {"key": "imessage:chat::main", "title": "Main", "channel": "imessage"},
        ]
        svc._active_key = "desktop:local::main"
        svc._sidebar_expanded_groups = {"desktop": True}
        svc._model.reset_sessions([sessions_before[0]], "desktop:local::main")
        svc._pending_deletes = {
            "imessage:chat::main": PendingDeleteState(
                sessions_before=sessions_before,
                active_before="imessage:chat::main",
                optimistic_active="desktop:local::main",
                expanded_groups={"desktop": True, "imessage": False},
            )
        }

        svc._handle_delete_result("imessage:chat::main", False, "delete failed")

        model = _sidebar_model(svc)
        item_key_role = _sidebar_role(model, b"itemKey")
        is_header_role = _sidebar_role(model, b"isHeader")
        channel_role = _sidebar_role(model, b"channel")
        expanded_role = _sidebar_role(model, b"expanded")

        keys = [
            model.data(model.index(i), item_key_role)
            for i in range(model.rowCount())
            if not model.data(model.index(i), is_header_role)
        ]
        header_collapsed = any(
            model.data(model.index(i), is_header_role)
            and model.data(model.index(i), channel_role) == "imessage"
            and model.data(model.index(i), expanded_role) is False
            for i in range(model.rowCount())
        )

        assert svc.activeKey == "imessage:chat::main"
        assert svc._sidebar_expanded_groups.get("imessage") is False
        assert header_collapsed is True
        assert keys.count("imessage:chat::main") == 1
    finally:
        runner.shutdown(grace_s=1.0)



def test_service_delete_false_after_delete_treated_as_success():
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
            delete_returns_false_after_delete=True,
        )
        svc.setHubReady()
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        events = []
        svc.deleteCompleted.connect(lambda key, ok, _err: events.append((key, ok)))

        svc.deleteSession("desktop:local::s1")
        assert _sessions_model(svc).rowCount() == 1

        loop2 = QEventLoop()
        QTimer.singleShot(300, loop2.quit)
        loop2.exec()

        assert _sessions_model(svc).rowCount() == 1
        assert svc.activeKey == "desktop:local::s2"
        assert ("desktop:local::s1", True) in events
    finally:
        runner.shutdown(grace_s=1.0)



def test_service_delete_active_picks_adjacent_session_and_persists_active():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[
                {"key": "desktop:local::s1", "title": "Chat 1"},
                {"key": "desktop:local::s2", "title": "Chat 2"},
                {"key": "desktop:local::s3", "title": "Chat 3"},
            ],
            active_key="desktop:local::s2",
        )
        svc.setHubReady()
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        svc.deleteSession("desktop:local::s2")
        assert _sessions_model(svc).rowCount() == 2
        assert svc.activeKey == "desktop:local::s1"

        loop2 = QEventLoop()
        QTimer.singleShot(300, loop2.quit)
        loop2.exec()

        assert svc.activeKey == "desktop:local::s1"
        assert sm.get_active_session_key("desktop:local") == "desktop:local::s1"
    finally:
        runner.shutdown(grace_s=1.0)


def test_service_delete_prefers_hub_dispatcher_provider(tmp_path):
    from types import SimpleNamespace

    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = SessionManager(tmp_path)
        s1 = sm.get_or_create("desktop:local::s1")
        s1.add_message("user", "hello")
        sm.save(s1)
        s2 = sm.get_or_create("desktop:local::s2")
        s2.add_message("user", "world")
        sm.save(s2)
        sm.set_active_session_key("desktop:local", "desktop:local::s1")

        class _FakeDispatcher:
            def __init__(self, session_manager):
                self.unbound_keys = []
                self.agent = SimpleNamespace(
                    sessions=session_manager,
                    _session_runs=None,
                    subagents=None,
                    _clear_interactive_state=lambda _session: False,
                )
                self.runtime = SimpleNamespace(agent=self.agent, session_manager=session_manager)

            def resolve_profile_id_for(self, explicit_profile_id, _session_key):
                return str(explicit_profile_id or "default").strip() or "default"

            def ensure_runtime(self, _profile_id):
                return self.runtime

            def unbind_route(self, key):
                self.unbound_keys.append(key)

        dispatcher = _FakeDispatcher(sm)
        svc.setHubDispatcherProvider(lambda: dispatcher)
        svc.setHubReady()
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(400, loop.quit)
        loop.exec()

        svc.deleteSession("desktop:local::s1")

        loop2 = QEventLoop()
        QTimer.singleShot(400, loop2.quit)
        loop2.exec()

        keys = [row["key"] for row in sm.list_sessions()]
        assert "desktop:local::s1" not in keys
        assert dispatcher.unbound_keys == ["desktop:local::s1"]
    finally:
        runner.shutdown(grace_s=1.0)



def test_service_delete_non_active_keeps_active_stable():
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

        svc.deleteSession("desktop:local::s2")
        _spin_until(lambda: _sessions_model(svc).rowCount() == 1)
        assert svc.activeKey == "desktop:local::s1"

        _spin_until(lambda: sm.get_active_session_key("desktop:local") == "desktop:local::s1")

        assert svc.activeKey == "desktop:local::s1"
        assert sm.get_active_session_key("desktop:local") == "desktop:local::s1"
    finally:
        runner.shutdown(grace_s=1.0)
