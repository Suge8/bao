# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._chat_service_testkit import *

def test_set_session_key_same_session_cold_open_emits_session_viewport_ready():
    from app.backend.chat import ChatMessageModel
    from app.backend.hub import _HistorySnapshot

    svc, _model = make_service()
    key = "desktop:local"
    prepared = ChatMessageModel.prepare_history(
        [{"role": "assistant", "content": "cached", "timestamp": "t"}]
    )
    svc._session_manager = object()
    svc._session_key = key
    svc._desired_session_key = key
    svc._committed_session_key = key
    svc._history_initialized = False
    svc._history_cache[key] = _HistorySnapshot((len(prepared), "cached"), prepared, True)
    svc._request_history_load = lambda *_args, **_kwargs: None

    ready: list[str] = []
    svc.historyReady.connect(ready.append)

    svc.setSessionKey(key)

    assert ready == [key]


def test_handle_history_result_emits_session_viewport_ready_after_apply():
    svc, _model = make_service()
    key = "desktop:local"
    svc._session_key = key
    svc._desired_session_key = key
    svc._committed_session_key = key
    svc._current_nav_id = 1

    ready: list[str] = []
    svc.historyReady.connect(ready.append)

    svc._handle_history_result(
        True,
        "",
        (key, 1, (1, "sig"), [{"role": "assistant", "content": "hello", "timestamp": "t"}], True),
    )

    assert ready == [key]


def test_set_session_key_uses_manager_tail_snapshot_before_async_reload():
    svc, model = make_service()
    raw_tail = [{"role": "assistant", "content": "from-manager", "timestamp": "t"}]
    sm = MagicMock()
    sm.peek_tail_messages.return_value = raw_tail
    svc._session_manager = sm
    svc._session_key = "desktop:old"
    svc._desired_session_key = "desktop:old"
    svc._committed_session_key = "desktop:old"
    model.append_assistant("old", status="done")
    called = []

    def _capture_request(*args, **kwargs) -> None:
        _ = args[1]
        called.append((args[0], kwargs.get("show_loading"), kwargs.get("raw_messages_override")))

    svc._request_history_load = _capture_request

    with patch(
        "app.backend.hub.ChatMessageModel.prepare_history",
        side_effect=AssertionError("sync prepare"),
    ):
        svc.setSessionKey("desktop:new")

    assert model.rowCount() == 0
    assert svc.activeSessionReady is False
    assert svc.activeSessionHasMessages is False
    assert svc.historyLoading is False
    assert called == [("desktop:new", False, raw_tail)]


def test_set_session_key_without_memory_snapshot_uses_async_load_path():
    svc, model = make_service()
    sm = MagicMock()
    sm.peek_tail_messages.return_value = None
    svc._session_manager = sm
    svc._session_key = "desktop:old"
    svc._desired_session_key = "desktop:old"
    svc._committed_session_key = "desktop:old"
    model.append_assistant("old", status="done")
    called = []
    svc._request_history_load = lambda key, *_args, **kwargs: called.append(
        (key, kwargs.get("show_loading"))
    )

    svc.setSessionKey("desktop:new")

    assert model.rowCount() == 0
    assert svc.activeSessionReady is False
    assert svc.activeSessionHasMessages is False
    assert called == [("desktop:new", True)]


def test_set_session_key_uses_empty_manager_tail_snapshot_without_loading():
    svc, model = make_service()
    sm = MagicMock()
    sm.peek_tail_messages.return_value = []
    svc._session_manager = sm
    svc._session_key = "desktop:old"
    svc._desired_session_key = "desktop:old"
    svc._committed_session_key = "desktop:old"
    model.append_assistant("old", status="done")
    called = []
    svc._request_history_load = lambda key, *_args, **kwargs: called.append(
        (key, kwargs.get("show_loading"))
    )

    svc.setSessionKey("desktop:empty")

    assert model.rowCount() == 0
    assert svc.activeSessionReady is True
    assert svc.activeSessionHasMessages is False
    assert svc.historyLoading is False
    assert called == [("desktop:empty", False)]


def test_set_session_key_uses_empty_session_summary_without_tail_read():
    svc, model = make_service()
    sm = MagicMock()
    svc._session_manager = sm
    svc._session_key = "desktop:old"
    svc._desired_session_key = "desktop:old"
    svc._committed_session_key = "desktop:old"
    svc.setSessionSummary("desktop:empty", 0, False)
    model.append_assistant("old", status="done")
    called = []
    svc._request_history_load = lambda key, *_args, **kwargs: called.append(
        (key, kwargs.get("show_loading"))
    )

    svc.setSessionKey("desktop:empty")

    sm.peek_tail_messages.assert_not_called()
    assert model.rowCount() == 0
    assert svc.activeSessionReady is True
    assert svc.activeSessionHasMessages is False
    assert svc.historyLoading is False
    assert called == [("desktop:empty", False)]


def test_empty_session_summary_still_allows_silent_history_correction():
    from app.backend.chat import ChatMessageModel

    svc, model = make_service()
    sm = MagicMock()
    svc._session_manager = sm
    svc._session_key = "desktop:old"
    svc._desired_session_key = "desktop:old"
    svc._committed_session_key = "desktop:old"
    svc._current_nav_id = 1
    svc.setSessionSummary("desktop:empty", 0, False)
    called = []
    svc._request_history_load = lambda key, *_args, **kwargs: called.append(
        (key, kwargs.get("show_loading"))
    )

    svc.setSessionKey("desktop:empty")
    assert called == [("desktop:empty", False)]

    prepared = ChatMessageModel.prepare_history(
        [{"role": "assistant", "content": "arrived", "timestamp": "t"}]
    )
    svc._handle_history_result(
        True,
        "",
        ("desktop:empty", svc._current_nav_id, (1, "arrived"), prepared, True),
    )

    assert model.rowCount() == 1
    assert model._messages[0]["content"] == "arrived"
    assert svc.activeSessionHasMessages is True


def test_set_session_key_does_not_render_uncommitted_tail_after_failed_save(tmp_path):
    from app.backend.chat import ChatMessageModel
    from bao.session.manager import SessionManager

    svc, model = make_service()
    sm = SessionManager(tmp_path)
    key = "desktop:local::rollback-tail"
    session = sm.get_or_create(key)
    session.add_message("assistant", "old")
    sm.save(session)
    session.add_message("assistant", "new")

    with patch.object(sm._msg_table(), "add", side_effect=RuntimeError("boom")):
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
