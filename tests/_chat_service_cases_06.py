# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._chat_service_testkit import *

def test_handle_history_result_applies_while_streaming_when_generation_matches():
    svc, model = make_service()
    svc._session_key = "imessage:active"
    svc._desired_session_key = "imessage:active"
    svc._processing = True
    row = model.append_assistant("", status="typing")
    svc._active_streaming_row = row
    svc._active_streaming_session_key = "imessage:active"
    svc._current_nav_id = 1

    svc._handle_history_result(
        True,
        "",
        ("imessage:active", 1, [{"role": "user", "content": "hello", "timestamp": "t"}]),
    )

    assert model.rowCount() == 1
    assert model._messages[0]["content"] == "hello"


def test_handle_history_result_rejects_stale_nav_payload():
    svc, model = make_service()
    svc._session_key = "imessage:active"
    svc._desired_session_key = "imessage:active"
    svc._current_nav_id = 2
    prepared = [
        {
            "id": 1,
            "createdat": 0,
            "role": "assistant",
            "content": "hello",
            "format": "plain",
            "status": "done",
            "entrancestyle": "none",
            "entrancepending": False,
        }
    ]
    sig = svc._history_signature(prepared)

    svc._handle_history_result(True, "", ("imessage:active", 1, sig, prepared))

    assert model.rowCount() == 0


def test_switch_while_streaming_does_not_show_old_session_content():
    svc, model = make_service()
    svc._session_key = "desktop:old"
    svc._desired_session_key = "desktop:old"
    svc._committed_session_key = "desktop:old"
    row = model.append_assistant("", status="typing")
    svc._active_streaming_row = row
    svc._active_streaming_session_key = "desktop:old"
    svc._processing = True

    svc.setSessionKey("desktop:new")
    assert model.rowCount() == 0

    svc._handle_progress_update(-1, "old-stream")
    svc._handle_send_result(row, True, "old-final")

    assert model.rowCount() == 0
    assert svc._committed_session_key == "desktop:new"


def test_set_session_key_same_key_still_loads_when_history_not_initialized():
    svc, _ = make_service()
    sm = MagicMock()
    svc._session_key = "desktop:local"
    svc._desired_session_key = "desktop:local"
    svc._committed_session_key = "desktop:local"
    svc._history_initialized = False
    svc._processing = True
    svc._session_manager = sm
    called = []
    svc._request_history_load = lambda key, *_args, **kwargs: called.append(key)

    svc.setSessionKey("desktop:local")

    assert called == ["desktop:local"]
    assert svc._current_nav_id == 1
    sm.mark_desktop_seen_ai.assert_called_once_with(
        "desktop:local",
        emit_change=False,
        metadata_updates=None,
        clear_running=False,
    )
    sm.update_metadata_only.assert_not_called()


def test_set_session_key_same_key_ignored_when_history_inflight():
    svc, _ = make_service()
    sm = MagicMock()
    svc._session_manager = sm
    svc._session_key = "desktop:local"
    svc._desired_session_key = "desktop:local"
    svc._committed_session_key = "desktop:local"
    svc._history_initialized = False
    svc._history_future = object()
    called = []
    svc._request_history_load = lambda key, *_args, **kwargs: called.append(key)

    svc.setSessionKey("desktop:local")

    assert called == []
    assert svc._current_nav_id == 0
    sm.update_metadata_only.assert_not_called()


def test_set_session_key_marks_seen_before_history_reload_for_new_session():
    svc, _ = make_service()
    sm = MagicMock()
    svc._session_manager = sm
    svc._session_key = "desktop:old"
    svc._desired_session_key = "desktop:old"
    svc._committed_session_key = "desktop:old"
    svc._history_initialized = True
    called = []
    svc._request_history_load = lambda key, *_args, **kwargs: called.append(key)

    svc.setSessionKey("desktop:new")

    assert called == ["desktop:new"]
    sm.mark_desktop_seen_ai.assert_called_once_with(
        "desktop:new",
        emit_change=False,
        metadata_updates=None,
        clear_running=False,
    )
    sm.update_metadata_only.assert_not_called()


def test_set_session_key_empty_clears_visible_history_without_reloading():
    svc, model = make_service()
    svc._session_manager = object()
    svc._session_key = "desktop:old"
    svc._desired_session_key = "desktop:old"
    svc._committed_session_key = "desktop:old"
    svc._history_initialized = True
    model.append_assistant("existing", status="done")
    called = []
    svc._request_history_load = lambda key, *_args, **kwargs: called.append(key)

    svc.setSessionKey("")

    assert svc._session_key == ""
    assert svc._desired_session_key == ""
    assert svc._committed_session_key == ""
    assert svc.historyLoading is False
    assert model.rowCount() == 0
    assert called == []


def test_set_session_key_uses_cached_snapshot_for_instant_render():
    from app.backend.chat import ChatMessageModel
    from app.backend.hub import _HistorySnapshot

    svc, model = make_service()
    cached_key = "desktop:new"
    prepared = ChatMessageModel.prepare_history(
        [{"role": "assistant", "content": "cached", "timestamp": "t"}]
    )
    svc._session_manager = object()
    svc._session_key = "desktop:old"
    svc._desired_session_key = "desktop:old"
    svc._committed_session_key = "desktop:old"
    svc._history_cache[cached_key] = _HistorySnapshot((len(prepared), "cached"), prepared, True)
    model.append_assistant("old", status="done")
    called = []
    svc._request_history_load = lambda key, *_args, **kwargs: called.append(
        (key, kwargs.get("show_loading"))
    )

    svc.setSessionKey(cached_key)

    assert model.rowCount() == 1
    assert model._messages[0]["content"] == "cached"
    assert svc.activeSessionReady is True
    assert svc.activeSessionHasMessages is True
    assert svc.historyLoading is False
    assert called == [(cached_key, False)]


def test_set_session_key_emits_session_view_applied_for_switched_cached_session():
    from app.backend.chat import ChatMessageModel
    from app.backend.hub import _HistorySnapshot

    svc, _model = make_service()
    cached_key = "desktop:new"
    prepared = ChatMessageModel.prepare_history(
        [{"role": "assistant", "content": "cached", "timestamp": "t"}]
    )
    svc._session_manager = object()
    svc._session_key = "desktop:old"
    svc._desired_session_key = "desktop:old"
    svc._committed_session_key = "desktop:old"
    svc._history_cache[cached_key] = _HistorySnapshot((len(prepared), "cached"), prepared, True)
    svc._request_history_load = lambda *_args, **_kwargs: None

    applied: list[str] = []
    svc.sessionViewApplied.connect(applied.append)

    svc.setSessionKey(cached_key)

    assert applied == [cached_key]


def test_set_session_key_same_session_does_not_emit_session_view_applied():
    svc, _model = make_service()
    sm = MagicMock()
    svc._session_manager = sm
    svc._session_key = "desktop:local"
    svc._desired_session_key = "desktop:local"
    svc._committed_session_key = "desktop:local"
    svc._history_initialized = False
    svc._request_history_load = lambda *_args, **_kwargs: None

    applied: list[str] = []
    svc.sessionViewApplied.connect(applied.append)

    svc.setSessionKey("desktop:local")

    assert applied == []
