# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._chat_service_testkit import *

def test_send_message_emits_signal():
    svc, model = make_service()
    emitted = []
    svc.appendAtBottom.connect(emitted.append)
    svc.sendMessage("test")
    assert len(emitted) == 1
    assert emitted[0] == 0  # row 0


def test_send_message_marks_session_running_when_queue_starts() -> None:
    svc, model = make_service()
    sm = MagicMock()
    svc._session_manager = sm
    svc._state = "running"
    svc._session_key = "desktop:local::s1"

    svc.sendMessage("test")

    assert model.rowCount() == 2
    assert model._messages[0]["status"] == "pending"
    assert sm.set_session_running.call_args_list[0].args == ("desktop:local::s1", True)
    assert sm.set_session_running.call_args_list[0].kwargs == {"emit_change": True}


def test_send_message_while_starting_keeps_single_pending_user_path() -> None:
    svc, model = make_service()
    svc._state = "starting"
    svc._set_history_loading(True)
    emitted: list[int] = []
    svc.appendAtBottom.connect(emitted.append)

    svc.sendMessage("hello")

    assert model.rowCount() == 1
    assert emitted == [0]
    assert model._messages[0]["role"] == "user"
    assert model._messages[0]["status"] == "pending"


def test_on_send_done_emits_cancelled_result() -> None:
    svc, _model = make_service()
    results: list[tuple[int, bool, str]] = []
    svc._sendResult.connect(lambda row, ok, content: results.append((row, ok, content)))
    future: concurrent.futures.Future[str] = concurrent.futures.Future()
    future.cancel()

    svc._on_send_done(future, 3)

    assert results == [(3, False, "Cancelled.")]


def test_handle_send_result_marks_active_user_done_and_persists_status() -> None:
    svc, model = make_service()
    session = MagicMock()
    session.messages = [
        {"role": "user", "content": "hello", "_pre_saved_token": "tok", "status": "pending"}
    ]
    sm = MagicMock()
    sm.get_or_create.return_value = session
    svc._session_manager = sm
    svc._committed_session_key = "desktop:local::s1"
    user_row = model.append_user("hello", status="pending", client_token="tok")
    typing_row = model.append_assistant("", status="typing")
    svc._active_user = type(svc._active_user)(
        row=user_row,
        session_key="desktop:local::s1",
        token="tok",
    )
    svc._active_streaming_row = typing_row
    svc._active_streaming_session_key = "desktop:local::s1"

    svc._handle_send_result(typing_row, True, "final")

    assert model._messages[user_row]["status"] == "done"
    assert session.messages[0]["status"] == "done"
    sm.save.assert_called_with(session, emit_change=False)


def test_handle_send_result_marks_active_user_error_and_persists_status() -> None:
    svc, model = make_service()
    session = MagicMock()
    session.messages = [
        {"role": "user", "content": "hello", "_pre_saved_token": "tok", "status": "pending"}
    ]
    sm = MagicMock()
    sm.get_or_create.return_value = session
    svc._session_manager = sm
    svc._committed_session_key = "desktop:local::s1"
    user_row = model.append_user("hello", status="pending", client_token="tok")
    typing_row = model.append_assistant("", status="typing")
    svc._active_user = type(svc._active_user)(
        row=user_row,
        session_key="desktop:local::s1",
        token="tok",
    )
    svc._active_streaming_row = typing_row
    svc._active_streaming_session_key = "desktop:local::s1"

    svc._handle_send_result(typing_row, False, "Error: boom")

    assert model._messages[user_row]["status"] == "error"
    assert session.messages[0]["status"] == "error"
    sm.save.assert_called_with(session, emit_change=False)


def test_stop_from_idle_is_noop():
    svc, _ = make_service()
    svc.stop()  # should not raise
    assert svc.state == "stopped"


def test_state_transitions_to_starting_on_start():
    svc, _ = make_service()
    states = []
    svc.stateChanged.connect(states.append)
    pending_init: concurrent.futures.Future[object] = concurrent.futures.Future()

    def _submit(coro: Coroutine[Any, Any, object]) -> concurrent.futures.Future[object]:
        coro.close()
        return pending_init

    svc._runner.submit = MagicMock(side_effect=_submit)
    svc.start()

    assert "starting" in states


def test_init_hub_keeps_subagent_system_callback_unbound():
    from types import SimpleNamespace

    svc, _model = make_service()

    fake_agent = SimpleNamespace(on_system_response=None)

    async def _noop(*args: Any, **kwargs: Any) -> None:
        del args, kwargs
        return None

    fake_agent.run = _noop
    fake_channels = SimpleNamespace(enabled_channels=["desktop"], start_all=_noop)
    fake_cron = SimpleNamespace(start=_noop, status=lambda: {"jobs": 0})
    fake_heartbeat = SimpleNamespace(start=_noop)
    fake_stack = SimpleNamespace(
        agent=fake_agent,
        channels=fake_channels,
        cron=fake_cron,
        heartbeat=fake_heartbeat,
        session_manager=MagicMock(),
        bus=MagicMock(),
        config=SimpleNamespace(),
    )
    fake_config = SimpleNamespace(workspace_path="/tmp/bao-test")

    with (
        patch("bao.config.loader.ensure_first_run"),
        patch("bao.config.loader.get_config_path", return_value="/tmp/config.jsonc"),
        patch("bao.config.loader.load_config", return_value=fake_config),
        patch("bao.providers.make_provider", return_value=MagicMock()),
        patch("bao.hub.builder.build_hub_stack", return_value=fake_stack),
        patch("bao.hub.builder.send_startup_greeting", new=_noop),
    ):
        asyncio.run(svc._init_hub())

    assert fake_agent.on_system_response is None


def test_init_hub_uses_injected_config_snapshot() -> None:
    from types import SimpleNamespace

    svc, _model = make_service()
    svc.setConfigData({"agents": {"defaults": {"model": "openai/gpt-4o"}}, "providers": {}})

    async def _noop(*args: Any, **kwargs: Any) -> None:
        del args, kwargs
        return None

    fake_stack = SimpleNamespace(
        agent=SimpleNamespace(run=_noop, on_system_response=None),
        channels=SimpleNamespace(enabled_channels=["desktop"], start_all=_noop),
        cron=SimpleNamespace(start=_noop, status=lambda: {"jobs": 0}),
        heartbeat=SimpleNamespace(start=_noop),
        session_manager=MagicMock(),
        bus=MagicMock(),
        config=SimpleNamespace(),
    )
    fake_config = SimpleNamespace(
        workspace_path="/tmp/bao-test",
        agents=SimpleNamespace(defaults=SimpleNamespace(model="openai/gpt-4o")),
    )

    with (
        patch("bao.config.loader.ensure_first_run"),
        patch("bao.config.loader.get_config_path", return_value="/tmp/config.jsonc"),
        patch(
            "bao.config.loader.load_config", side_effect=AssertionError("should not reload config")
        ),
        patch("bao.config.schema.Config.model_validate", return_value=fake_config),
        patch("bao.providers.make_provider", return_value=MagicMock()),
        patch("bao.hub.builder.build_hub_stack", return_value=fake_stack),
        patch("bao.hub.builder.send_startup_greeting", new=_noop),
    ):
        asyncio.run(svc._init_hub())


def test_init_hub_surfaces_config_path_when_loader_exits() -> None:
    svc, _model = make_service()

    with (
        patch("bao.config.loader.ensure_first_run"),
        patch("bao.config.loader.get_config_path", return_value="/tmp/config.jsonc"),
        patch("bao.config.loader.load_config", side_effect=SystemExit(0)),
    ):
        with pytest.raises(RuntimeError, match="/tmp/config.jsonc"):
            asyncio.run(svc._init_hub())


def test_stop_invalidates_inflight_init_result() -> None:
    svc, _model = make_service()
    pending_init: concurrent.futures.Future[object] = concurrent.futures.Future()

    def _submit(coro: Coroutine[Any, Any, object]) -> concurrent.futures.Future[object]:
        coro.close()
        return pending_init

    svc._runner.submit = MagicMock(side_effect=_submit)
    svc.start()

    request_id = svc._lifecycle_request_id - 1
    svc.stop()
    svc._handle_init_result(request_id, True, "", MagicMock(), ["telegram"])

    assert svc.state == "stopped"
    assert svc.property("hubDetail") == ""


def test_double_start_is_noop():
    svc, _ = make_service()
    states = []
    svc.stateChanged.connect(states.append)
    pending_init: concurrent.futures.Future[object] = concurrent.futures.Future()

    def _submit(coro: Coroutine[Any, Any, object]) -> concurrent.futures.Future[object]:
        coro.close()
        return pending_init

    svc._runner.submit = MagicMock(side_effect=_submit)
    svc.start()
    svc.start()  # second call should be ignored

    assert states.count("starting") == 1
