# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._session_service_testkit import *

def test_service_initial_active_key():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        assert svc.activeKey == ""
    finally:
        runner.shutdown(grace_s=1.0)



def test_service_shutdown_clears_runtime_state():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[{"key": "desktop:local::s1", "title": "Chat 1"}],
            active_key="desktop:local::s1",
        )
        svc.initialize(sm)
        svc.setHubReady()
        svc.selectSession("desktop:local::main")

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        svc.shutdown()
        assert svc._disposed is True
        assert svc._local_hub_ports is None
        svc.refresh()
    finally:
        runner.shutdown(grace_s=1.0)



def test_service_projects_child_session_metadata(qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[
                {
                    "key": "desktop:local::main",
                    "title": "Main",
                    "updated_at": datetime.now().isoformat(),
                },
                {
                    "key": "subagent:desktop:local::child-1",
                    "title": "Research",
                    "updated_at": datetime.now().isoformat(),
                    "metadata": {
                        "session_kind": "subagent_child",
                        "read_only": True,
                        "parent_session_key": "desktop:local::main",
                        "task_label": "Research",
                        "child_status": "running",
                    },
                },
            ],
            active_key="desktop:local::main",
        )
        svc.initialize(sm)
        svc.setHubReady()
        svc.selectSession("desktop:local::main")

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        idx = _index_by_key(svc, "subagent:desktop:local::child-1")
        assert idx.isValid()
        model = _sessions_model(svc)
        assert model.data(idx, Qt.UserRole + 10) == "subagent_child"
        assert model.data(idx, Qt.UserRole + 11) is True
        assert model.data(idx, Qt.UserRole + 13) == "Main"
        assert svc.property("activeSessionReadOnly") is False
    finally:
        runner.shutdown(grace_s=1.0)



def test_service_marks_parent_running_when_child_running(qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[
                {
                    "key": "imessage:chat-1::main",
                    "title": "Main",
                    "updated_at": datetime.now().isoformat(),
                    "metadata": {"session_running": False},
                },
                {
                    "key": "subagent:imessage:chat-1::child-1",
                    "title": "Worker",
                    "updated_at": datetime.now().isoformat(),
                    "metadata": {
                        "session_kind": "subagent_child",
                        "read_only": True,
                        "parent_session_key": "imessage:chat-1::main",
                        "child_status": "running",
                    },
                },
            ],
            active_key="imessage:chat-1::main",
        )
        svc.initialize(sm)
        svc.setHubReady()
        svc.selectSession("imessage:chat-1::main")

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        model = _sessions_model(svc)
        parent_idx = _index_by_key(svc, "imessage:chat-1::main")
        child_idx = _index_by_key(svc, "subagent:imessage:chat-1::child-1")
        assert model.data(parent_idx, Qt.UserRole + 5) == "imessage"
        assert model.data(child_idx, Qt.UserRole + 5) == "imessage"
        assert model.data(parent_idx, Qt.UserRole + 15) is True
        assert model.data(child_idx, Qt.UserRole + 15) is True
    finally:
        runner.shutdown(grace_s=1.0)



def test_delete_session_ignores_read_only_child(qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[
                {
                    "key": "subagent:desktop:local::child-1",
                    "title": "Research",
                    "updated_at": datetime.now().isoformat(),
                    "metadata": {
                        "session_kind": "subagent_child",
                        "read_only": True,
                        "parent_session_key": "desktop:local::main",
                        "child_status": "running",
                    },
                }
            ],
            active_key="subagent:desktop:local::child-1",
        )
        svc.initialize(sm)
        svc.setHubReady()
        svc.selectSession("subagent:desktop:local::child-1")

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        svc.deleteSession("subagent:desktop:local::child-1")
        assert sm.delete_session.call_count == 0
        assert sm.delete_session_tree.call_count == 0
    finally:
        runner.shutdown(grace_s=1.0)



def test_done_callbacks_ignore_cancelled_future():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        future = concurrent.futures.Future()
        future.cancel()

        svc._on_list_done(future)
        svc._on_select_done(future)
        svc._on_create_done("desktop:local::new", future)
        svc._on_delete_done("desktop:local::old", future)
    finally:
        runner.shutdown(grace_s=1.0)



def test_initialize_registers_and_shutdown_removes_change_listener():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager()

        svc.initialize(sm)

        assert svc._on_session_change in sm._listeners

        svc.shutdown()

        assert svc._on_session_change not in sm._listeners
    finally:
        runner.shutdown(grace_s=1.0)



def test_initialize_with_same_session_manager_is_noop():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager()

        with patch.object(svc, "refresh") as refresh:
            svc.initialize(sm)
            assert refresh.call_count == 1

            svc.initialize(sm)
            assert refresh.call_count == 1
    finally:
        runner.shutdown(grace_s=1.0)



def test_bootstrap_workspace_initializes_session_manager_async(qt_app, tmp_path):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager()
        sm.workspace = tmp_path / "workspace"
        ready: list[Any] = []
        svc.hubLocalPortsReady.connect(ready.append)

        with patch("bao.hub.open_local_hub_ports", return_value=_hub_local_ports(sm)):
            svc.bootstrapWorkspace(str(tmp_path / "workspace"))
            assert svc.sessionsLoading is True
            loop = QEventLoop()
            QTimer.singleShot(300, loop.quit)
            loop.exec()

        assert svc._local_hub_ports is ready[0]
        assert svc.sessionsLoading is False
    finally:
        runner.shutdown(grace_s=1.0)



def test_bootstrap_result_does_not_override_existing_session_manager(qt_app):
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        current = _make_mock_session_manager()
        late = _make_mock_session_manager()
        current.workspace = "/tmp/current"
        late.workspace = "/tmp/late"
        ready: list[Any] = []
        svc.hubLocalPortsReady.connect(ready.append)

        svc.initialize(current)
        svc._handle_bootstrap_result(True, "", _hub_local_ports(late))
        qt_app.processEvents()

        assert svc._local_hub_ports is current
        assert ready == []
    finally:
        runner.shutdown(grace_s=1.0)
