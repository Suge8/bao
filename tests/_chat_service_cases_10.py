# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._chat_service_testkit import *

def test_send_result_after_assistant_only_history_split_uses_last_row():
    svc, model = make_service()
    svc._session_key = "desktop:local"
    svc._desired_session_key = "desktop:local"
    svc._committed_session_key = "desktop:local"
    svc._active_streaming_session_key = "desktop:local"
    svc._processing = True
    svc._history_initialized = True
    svc._history_fingerprint = (3, "stale")
    svc._current_nav_id = 1

    _ = model.append_user("hello")
    typing_row = model.append_assistant("first", status="typing")
    svc._active_streaming_row = typing_row

    from app.backend.chat import ChatMessageModel

    prepared = ChatMessageModel.prepare_history(
        [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "first", "status": "done", "format": "markdown"},
            {"role": "assistant", "content": "second", "status": "done", "format": "markdown"},
        ]
    )
    sig = svc._history_signature(prepared)
    statuses = []
    svc.statusSettled.connect(lambda row, status: statuses.append((row, status)))

    svc._handle_history_result(True, "", ("desktop:local", 1, sig, prepared))
    svc._handle_send_result(typing_row, True, "second")

    assert svc._active_streaming_row == -1
    assert statuses[-1] == (2, "done")


def test_history_materialized_split_clears_pending_split_before_send_result():
    svc, model = make_service()
    svc._session_key = "desktop:local"
    svc._desired_session_key = "desktop:local"
    svc._committed_session_key = "desktop:local"
    svc._active_streaming_session_key = "desktop:local"
    svc._processing = True
    svc._history_initialized = True
    svc._history_fingerprint = (3, "stale")
    svc._current_nav_id = 1

    _ = model.append_user("hello")
    typing_row = model.append_assistant("first", status="typing")
    svc._active_streaming_row = typing_row
    svc._active_has_content = True
    svc._pending_split = True

    from app.backend.chat import ChatMessageModel

    prepared = ChatMessageModel.prepare_history(
        [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "first", "status": "done", "format": "markdown"},
            {"role": "assistant", "content": "second", "status": "done", "format": "markdown"},
        ]
    )
    sig = svc._history_signature(prepared)
    statuses = []
    svc.statusSettled.connect(lambda row, status: statuses.append((row, status)))

    svc._handle_history_result(True, "", ("desktop:local", 1, sig, prepared))
    svc._handle_send_result(typing_row, True, "second")

    assert model.rowCount() == 3
    assert svc._active_streaming_row == -1
    assert svc._pending_split is False
    assert statuses[-1] == (2, "done")


def test_switch_back_to_streaming_session_rebinds_active_row_to_last_assistant():
    svc, model = make_service()
    svc._session_manager = object()
    svc._session_key = "desktop:old"
    svc._desired_session_key = "desktop:old"
    svc._committed_session_key = "desktop:old"
    svc._active_streaming_session_key = "desktop:old"
    svc._processing = True
    row = model.append_assistant("first", status="typing")
    svc._active_streaming_row = row

    svc.setSessionKey("desktop:new")
    svc.setSessionKey("desktop:old")

    from app.backend.chat import ChatMessageModel

    prepared = ChatMessageModel.prepare_history(
        [
            {"role": "assistant", "content": "first", "status": "done", "format": "markdown"},
            {"role": "assistant", "content": "second", "status": "done", "format": "markdown"},
        ]
    )
    sig = svc._history_signature(prepared)
    statuses = []
    svc.statusSettled.connect(lambda active_row, status: statuses.append((active_row, status)))

    svc._handle_history_result(True, "", ("desktop:old", svc._current_nav_id, sig, prepared))
    svc._handle_send_result(row, True, "second")

    assert model.rowCount() == 2
    assert model._messages[0]["content"] == "first"
    assert model._messages[1]["content"] == "second"
    assert statuses[-1] == (1, "done")


def test_switch_back_to_streaming_session_does_not_overwrite_display_only_hint():
    svc, model = make_service()
    svc._session_manager = object()
    svc._session_key = "desktop:old"
    svc._desired_session_key = "desktop:old"
    svc._committed_session_key = "desktop:old"
    svc._active_streaming_session_key = "desktop:old"
    svc._processing = True
    row = model.append_assistant("我先看一下。", status="typing")
    svc._active_streaming_row = row

    svc.setSessionKey("desktop:new")
    svc.setSessionKey("desktop:old")

    from app.backend.chat import ChatMessageModel

    prepared = ChatMessageModel.prepare_history(
        [
            {
                "role": "assistant",
                "content": "我先看一下。",
                "status": "done",
                "format": "markdown",
            },
            {
                "role": "assistant",
                "content": "🔎 搜索网页: latest ai news",
                "status": "done",
                "format": "markdown",
                "_source": "assistant-progress",
            },
        ]
    )
    sig = svc._history_signature(prepared)

    svc._handle_history_result(True, "", ("desktop:old", svc._current_nav_id, sig, prepared))
    svc._handle_send_result(row, True, "整理好了，这是结果。")

    assert model.rowCount() == 3
    assert model._messages[0]["content"] == "我先看一下。"
    assert model._messages[1]["content"] == "🔎 搜索网页: latest ai news"
    assert model._messages[1]["status"] == "done"
    assert model._messages[2]["content"] == "整理好了，这是结果。"
    assert model._messages[2]["status"] == "done"


def test_switch_back_to_streaming_session_restores_typing_placeholder_after_latest_user():
    svc, model = make_service()
    svc._session_manager = object()
    svc._session_key = "desktop:old"
    svc._desired_session_key = "desktop:old"
    svc._committed_session_key = "desktop:old"
    svc._active_streaming_session_key = "desktop:old"
    svc._processing = True
    row = model.append_assistant("first", status="typing")
    svc._active_streaming_row = row

    svc.setSessionKey("desktop:new")
    svc.setSessionKey("desktop:old")

    from app.backend.chat import ChatMessageModel

    prepared = ChatMessageModel.prepare_history(
        [
            {"role": "assistant", "content": "older", "status": "done", "format": "markdown"},
            {"role": "user", "content": "hello"},
        ]
    )
    sig = svc._history_signature(prepared)
    statuses = []
    svc.statusSettled.connect(lambda active_row, status: statuses.append((active_row, status)))

    svc._handle_history_result(True, "", ("desktop:old", svc._current_nav_id, sig, prepared))
    svc._handle_send_result(row, True, "final")

    assert model.rowCount() == 3
    assert model._messages[0]["content"] == "older"
    assert model._messages[1]["role"] == "user"
    assert model._messages[2]["role"] == "assistant"
    assert model._messages[2]["content"] == "final"
    assert statuses[-1] == (2, "done")


def test_send_result_before_switch_back_history_rebind_restores_placeholder():
    svc, model = make_service()
    svc._session_manager = object()
    svc._session_key = "desktop:old"
    svc._desired_session_key = "desktop:old"
    svc._committed_session_key = "desktop:old"
    svc._active_streaming_session_key = "desktop:old"
    svc._processing = True
    row = model.append_assistant("first", status="typing")
    svc._active_streaming_row = row

    svc.setSessionKey("desktop:new")
    svc.setSessionKey("desktop:old")

    statuses = []
    svc.statusSettled.connect(lambda active_row, status: statuses.append((active_row, status)))

    svc._handle_send_result(row, True, "final")

    assert model.rowCount() == 1
    assert model._messages[0]["role"] == "assistant"
    assert model._messages[0]["content"] == "final"
    assert statuses[-1] == (0, "done")
