# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._chat_service_testkit import *

def test_set_session_key_after_failed_clear_save_keeps_previous_tail(tmp_path):
    from app.backend.chat import ChatMessageModel
    from bao.session.manager import SessionManager

    svc, model = make_service()
    sm = SessionManager(tmp_path)
    key = "desktop:local::rollback-clear"
    session = sm.get_or_create(key)
    session.add_message("assistant", "old")
    sm.save(session)
    session.clear()

    with patch.object(sm, "_write_display_tail_row", side_effect=RuntimeError("boom")):
        with pytest.raises(RuntimeError, match="boom"):
            sm.save(session)

    svc._session_manager = sm
    svc._session_key = "desktop:old"
    svc._desired_session_key = "desktop:old"
    svc._committed_session_key = "desktop:old"
    called = []
    svc._request_history_load = lambda key, *_args, **kwargs: called.append(
        (key, kwargs.get("show_loading"))
    )

    svc.setSessionKey(key)

    assert model.rowCount() == 0
    assert called == [(key, True)]

    prepared = ChatMessageModel.prepare_history(
        [{"role": "assistant", "content": "old", "timestamp": "t"}]
    )
    svc._handle_history_result(True, "", (key, svc._current_nav_id, (1, "old"), prepared, True))

    assert model.rowCount() == 1
    assert model._messages[0]["content"] == "old"


def test_handle_history_result_marks_empty_session_ready_without_messages():
    svc, _model = make_service()
    key = "desktop:local"
    svc._session_key = key
    svc._desired_session_key = key
    svc._current_nav_id = 1

    svc._handle_history_result(True, "", (key, 1, (0, ""), [], False))

    assert svc.activeSessionReady is True
    assert svc.activeSessionHasMessages is False


def test_non_active_session_message_invalidates_cached_snapshot():
    from app.backend.hub import _HistorySnapshot

    svc, _model = make_service()
    stale_key = "desktop:stale"
    active_key = "desktop:active"
    svc._desired_session_key = active_key
    svc._committed_session_key = active_key
    svc._history_cache[stale_key] = _HistorySnapshot((1, "stale"), [], False)

    svc._handle_session_change(SessionChangeEvent(session_key=stale_key, kind="messages"))

    assert stale_key not in svc._history_cache


def test_load_history_uses_display_history_for_ui_model():
    svc, _ = make_service()
    session = MagicMock()
    session.get_display_history.return_value = [
        {"role": "assistant", "content": "a1", "format": "markdown"}
    ]
    svc._session_manager = MagicMock()
    svc._session_manager.get_or_create.return_value = session

    payload = asyncio.run(svc._load_history("desktop:local", 3, 200))

    assert payload[0] == "desktop:local"
    assert payload[1] == 3
    assert payload[3] == [
        {
            "id": 1,
            "createdat": 0,
            "role": "assistant",
            "content": "a1",
            "format": "markdown",
            "status": "done",
            "entrancestyle": "none",
            "entrancepending": False,
            "dividertext": "",
            "attachments": [],
            "references": {},
        }
    ]
    assert payload[4] is True
    session.get_display_history.assert_called_once()


def test_handle_history_result_does_not_reset_when_only_entrance_differs():
    svc, model = make_service()
    svc._session_key = "desktop:local"
    svc._desired_session_key = "desktop:local"
    _ = model.append_assistant("hello", status="done", entrance_pending=True)
    prepared = [
        {
            "id": 1,
            "createdat": 0,
            "role": "assistant",
            "content": "hello",
            "format": "markdown",
            "status": "done",
            "entrancestyle": "none",
            "entrancepending": False,
        }
    ]
    sig = svc._history_signature(prepared)
    resets = []
    model.modelReset.connect(lambda: resets.append(True))
    svc._history_initialized = True
    svc._history_fingerprint = (1, "stale")
    svc._current_nav_id = 1

    svc._handle_history_result(True, "", ("desktop:local", 1, sig, prepared))

    assert resets == []


def test_handle_history_result_does_not_reset_when_only_system_entrance_differs():
    svc, model = make_service()
    svc._session_key = "desktop:local"
    svc._desired_session_key = "desktop:local"
    _ = model.append_system("hub started", entrance_style="system", entrance_pending=True)
    prepared = [
        {
            "id": 1,
            "createdat": 0,
            "role": "system",
            "content": "hub started",
            "format": "plain",
            "status": "done",
            "entrancestyle": "greeting",
            "entrancepending": False,
        }
    ]
    sig = svc._history_signature(prepared)
    resets = []
    model.modelReset.connect(lambda: resets.append(True))
    svc._history_initialized = True
    svc._history_fingerprint = (1, "stale")
    svc._current_nav_id = 1

    svc._handle_history_result(True, "", ("desktop:local", 1, sig, prepared))

    assert resets == []
    assert model._messages[0]["entrancestyle"] == "greeting"


def test_handle_history_result_preserves_transient_typing_tail_without_reset():
    svc, model = make_service()
    svc._session_key = "desktop:local"
    svc._desired_session_key = "desktop:local"
    svc._committed_session_key = "desktop:local"
    svc._active_streaming_session_key = "desktop:local"
    svc._processing = True
    svc._history_initialized = True
    svc._history_fingerprint = (1, "stale")
    svc._current_nav_id = 1

    _ = model.append_user("hello")
    typing_row = model.append_assistant("", status="typing")
    svc._active_streaming_row = typing_row

    prepared = [
        {
            "id": 1,
            "createdat": 0,
            "role": "user",
            "content": "hello",
            "format": "plain",
            "status": "done",
            "entrancestyle": "none",
            "entrancepending": False,
        }
    ]
    sig = svc._history_signature(prepared)
    resets = []
    model.modelReset.connect(lambda: resets.append(True))

    svc._handle_history_result(True, "", ("desktop:local", 1, sig, prepared))

    assert resets == []
    assert model.rowCount() == 2
    assert model._messages[0]["content"] == "hello"
    assert model._messages[1]["role"] == "assistant"
    assert model._messages[1]["status"] == "typing"
