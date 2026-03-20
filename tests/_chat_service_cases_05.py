# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from types import SimpleNamespace

from tests._chat_service_testkit import *

def test_tool_hint_during_pending_split_keeps_hint_separate_from_next_turn():
    svc, model = make_service()
    row0 = model.append_assistant("working", status="typing")
    svc._active_streaming_row = row0
    svc._active_has_content = True
    svc._pending_split = True

    svc._handle_tool_hint_update("🤖 Delegate Task: run subagent")

    assert model.rowCount() == 3
    assert model._messages[0]["status"] == "done"
    assert model._messages[1]["content"] == "🤖 Delegate Task: run subagent"
    assert model._messages[1]["status"] == "done"
    assert model._messages[2]["status"] == "typing"
    assert svc._active_streaming_row == 2
    assert svc._pending_split is False


def test_send_result_pending_split_with_final_content_creates_new_final_bubble():
    svc, model = make_service()
    row0 = model.append_assistant("first", status="typing")
    svc._active_streaming_row = row0
    svc._active_has_content = True
    svc._pending_split = True

    svc._handle_send_result(row0, True, "final")

    assert model.rowCount() == 2
    assert model._messages[0]["content"] == "first"
    assert model._messages[0]["status"] == "done"
    assert model._messages[1]["content"] == "final"
    assert model._messages[1]["status"] == "done"


def test_send_result_pending_split_without_final_content_no_empty_done_bubble():
    svc, model = make_service()
    row0 = model.append_assistant("first", status="typing")
    svc._active_streaming_row = row0
    svc._active_has_content = True
    svc._pending_split = True

    svc._handle_send_result(row0, True, "")

    assert model.rowCount() == 1
    assert model._messages[0]["content"] == "first"
    assert model._messages[0]["status"] == "done"


def test_send_result_provider_error_switches_active_bubble_to_plain_text():
    svc, model = make_service()
    row = model.append_assistant("", status="typing")
    svc._active_streaming_row = row

    svc._handle_send_result(row, True, "Error calling LLM: <b>forbidden</b>")

    assert model._messages[0]["format"] == "plain"
    assert model._messages[0]["status"] == "error"
    assert model._messages[0]["content"] == "Error calling LLM: <b>forbidden</b>"


def test_send_result_transport_error_switches_active_bubble_to_plain_text():
    svc, model = make_service()
    row = model.append_assistant("", status="typing")
    svc._active_streaming_row = row

    svc._handle_send_result(row, False, "Error: network down")

    assert model._messages[0]["format"] == "plain"
    assert model._messages[0]["status"] == "error"
    assert model._messages[0]["content"] == "Error: network down"


def test_send_result_does_not_mark_seen_for_background_session():
    svc, model = make_service()
    svc._session_manager = object()
    svc._committed_session_key = "desktop:new"
    row = model.append_assistant("", status="typing")
    svc._active_streaming_row = row
    svc._active_streaming_session_key = "desktop:old"

    svc._handle_send_result(row, True, "ok")

    cast(MagicMock, svc._runner.submit).assert_not_called()


def test_send_result_marks_seen_for_active_session():
    svc, model = make_service()
    sm = MagicMock()
    svc._session_manager = sm
    svc._committed_session_key = "desktop:active"
    row = model.append_assistant("", status="typing")
    svc._active_streaming_row = row
    svc._active_streaming_session_key = "desktop:active"
    svc._active_send_future = MagicMock()

    svc._handle_send_result(row, True, "ok")

    assert svc._active_send_future is None
    sm.mark_desktop_turn_completed.assert_called_once_with(
        "desktop:active",
        emit_change=True,
        metadata_updates=None,
    )
    assert sm.method_calls[-1] == call.mark_desktop_turn_completed(
        "desktop:active",
        emit_change=True,
        metadata_updates=None,
    )
    sm.mark_desktop_seen_ai.assert_not_called()
    sm.set_session_running.assert_not_called()
    sm.update_metadata_only.assert_not_called()


def test_handle_session_deleted_keeps_streaming_key_for_cancel_cleanup() -> None:
    svc, _model = make_service()
    active_future = MagicMock()
    svc._active_streaming_session_key = "desktop:local::s1"
    svc._active_send_future = active_future

    svc.handle_session_deleted("desktop:local::s1", True, "")

    active_future.cancel.assert_called_once()
    assert svc._active_streaming_session_key == "desktop:local::s1"


def test_set_session_manager_registers_change_listener():
    svc, _model = make_service()
    sm = _SessionManagerWithListeners()

    svc.setSessionManager(sm)

    assert svc._on_session_change in sm.listeners


def test_set_session_manager_replaces_previous_change_listener():
    svc, _model = make_service()
    old_sm = _SessionManagerWithListeners()
    new_sm = _SessionManagerWithListeners()

    svc.setSessionManager(old_sm)
    svc.setSessionManager(new_sm)

    assert svc._on_session_change not in old_sm.listeners
    assert svc._on_session_change in new_sm.listeners


def test_set_session_manager_caches_previous_root_for_future_reuse(tmp_path):
    svc, _model = make_service()
    first_root = tmp_path / "profile-a"
    second_root = tmp_path / "profile-b"
    first_sm = _SessionManagerWithListeners(first_root)
    second_sm = _SessionManagerWithListeners(second_root)

    svc.setSessionManager(first_sm)
    svc.setSessionManager(second_sm)

    config = type("Config", (), {"workspace_path": str(first_root)})()
    reused = svc._reusable_session_manager(config, None)

    assert reused is first_sm
    assert str(first_root) not in svc._hot_session_managers


def test_set_session_manager_same_root_does_not_cache_stale_manager(tmp_path):
    svc, _model = make_service()
    root = tmp_path / "same-root"
    old_sm = _SessionManagerWithListeners(root)
    new_sm = _SessionManagerWithListeners(root)

    svc.setSessionManager(old_sm)
    svc.setSessionManager(new_sm)

    assert svc._hot_session_managers == {}


def test_session_change_reloads_active_history_for_message_commit():
    svc, _model = make_service()
    sm = _SessionManagerWithListeners()
    svc.setSessionManager(sm)
    svc._desired_session_key = "desktop:local"
    svc._committed_session_key = "desktop:local"
    svc._current_nav_id = 7

    called = []
    svc._cancel_history_future = lambda: called.append(("cancel",))
    svc._request_history_load = (
        lambda key, nav_id, *, show_loading=None, raw_messages_override=None: called.append(
            (key, nav_id, show_loading)
        )
    )

    sm.emit("desktop:local", "messages")

    assert called == [("cancel",), ("desktop:local", 7, False)]


def test_session_change_ignores_metadata_commit_for_active_history():
    svc, _model = make_service()
    sm = _SessionManagerWithListeners()
    svc.setSessionManager(sm)
    svc._desired_session_key = "desktop:local"
    svc._committed_session_key = "desktop:local"

    called = []
    svc._request_history_load = lambda *args, **kwargs: called.append((args, kwargs))

    sm.emit("desktop:local", "metadata")

    assert called == []


def test_handle_init_result_registers_actual_session_manager_listener():
    svc, _model = make_service()
    early_sm = _SessionManagerWithListeners()
    actual_sm = _SessionManagerWithListeners()
    svc.setSessionManager(early_sm)
    actual_ports = _hub_local_ports(actual_sm)
    svc._dispatcher = SimpleNamespace(
        runtime_port=actual_ports.runtime,
        directory=actual_ports.directory,
        agent=None,
        cron=None,
        heartbeat=None,
    )

    svc._lifecycle_request_id = 1
    svc._handle_init_result(1, True, "", actual_sm, [])

    assert svc._on_session_change not in early_sm.listeners
    assert svc._on_session_change in actual_sm.listeners


def test_handle_history_result_ignores_stale_session_payload():
    svc, model = make_service()
    svc._session_key = "imessage:active"
    svc._desired_session_key = "imessage:active"

    svc._handle_history_result(
        True,
        "",
        ("imessage:other", [{"role": "user", "content": "hello", "timestamp": "t"}]),
    )

    assert model.rowCount() == 0


def test_handle_history_result_skips_reload_when_signature_unchanged():
    svc, model = make_service()
    svc._session_key = "imessage:active"
    svc._desired_session_key = "imessage:active"
    payload = ("imessage:active", [{"role": "user", "content": "hello", "timestamp": "t"}])

    with patch.object(model, "load_history", wraps=model.load_history) as mocked:
        svc._handle_history_result(True, "", payload)
        svc._handle_history_result(True, "", payload)

    assert mocked.call_count == 1


def test_set_session_key_switches_immediately_while_processing():
    svc, model = make_service()
    svc._session_manager = object()
    svc._processing = True
    row = model.append_assistant("", status="typing")
    svc._active_streaming_row = row
    svc._active_streaming_session_key = "imessage:active"
    called = []
    svc._request_history_load = lambda key, *_args, **kwargs: called.append(key)

    svc.setSessionKey("imessage:new")

    assert svc._desired_session_key == "imessage:new"
    assert svc._committed_session_key == "imessage:new"
    assert svc._current_nav_id == 1
    assert svc._active_streaming_row == -1
    assert model.rowCount() == 0
    assert called == ["imessage:new"]
