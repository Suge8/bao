# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._chat_service_testkit import *

def test_handle_history_result_updates_active_assistant_without_reset_on_finalize_race():
    svc, model = make_service()
    svc._session_key = "desktop:local"
    svc._desired_session_key = "desktop:local"
    svc._committed_session_key = "desktop:local"
    svc._active_streaming_session_key = "desktop:local"
    svc._processing = True
    svc._history_initialized = True
    svc._history_fingerprint = (2, "stale")
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
        },
        {
            "id": 2,
            "createdat": 0,
            "role": "assistant",
            "content": "world",
            "format": "markdown",
            "status": "done",
            "entrancestyle": "none",
            "entrancepending": False,
        },
    ]
    sig = svc._history_signature(prepared)
    resets = []
    model.modelReset.connect(lambda: resets.append(True))

    svc._handle_history_result(True, "", ("desktop:local", 1, sig, prepared))

    assert resets == []
    assert model.rowCount() == 2
    assert model._messages[1]["content"] == "world"
    assert model._messages[1]["status"] == "done"


def test_prepare_history_preserves_assistant_progress_source() -> None:
    from app.backend.chat import ChatMessageModel

    prepared = ChatMessageModel.prepare_history(
        [
            {
                "role": "assistant",
                "content": "🔎 搜索网页: latest ai news",
                "status": "done",
                "format": "markdown",
                "_source": "assistant-progress",
            }
        ]
    )

    assert prepared[0]["_source"] == "assistant-progress"


def test_prepare_history_preserves_assistant_greeting_entrance_style() -> None:
    from app.backend.chat import ChatMessageModel

    prepared = ChatMessageModel.prepare_history(
        [
            {
                "role": "assistant",
                "content": "早安杰哥",
                "status": "done",
                "format": "markdown",
                "entrance_style": "greeting",
            }
        ]
    )

    assert prepared[0]["role"] == "assistant"
    assert prepared[0]["entrancestyle"] == "greeting"


def test_handle_history_result_preserves_transient_tail_after_tool_row_without_reset():
    svc, model = make_service()
    svc._session_key = "desktop:local"
    svc._desired_session_key = "desktop:local"
    svc._committed_session_key = "desktop:local"
    svc._active_streaming_session_key = "desktop:local"
    svc._processing = True
    svc._history_initialized = True
    svc._history_fingerprint = (2, "stale")
    svc._current_nav_id = 1

    _ = model.append_user("hello")
    _ = model.append_assistant("working", status="done")
    typing_row = model.append_assistant("", status="typing")
    svc._active_streaming_row = typing_row

    from app.backend.chat import ChatMessageModel

    prepared = ChatMessageModel.prepare_history(
        [{"role": "user", "content": "hello"}, {"role": "tool", "content": "running tool"}]
    )
    sig = svc._history_signature(prepared)
    resets = []
    model.modelReset.connect(lambda: resets.append(True))

    svc._handle_history_result(True, "", ("desktop:local", 1, sig, prepared))

    assert resets == []
    assert model.rowCount() == 4
    assert model._messages[1]["role"] == "system"
    assert model._messages[2]["content"] == "working"
    assert model._messages[3]["status"] == "typing"
    assert svc._active_streaming_row == 3


def test_handle_history_result_reconciles_tool_row_and_final_assistant_without_reset():
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
    _ = model.append_assistant("working", status="done")
    typing_row = model.append_assistant("", status="typing")
    svc._active_streaming_row = typing_row

    from app.backend.chat import ChatMessageModel

    prepared = ChatMessageModel.prepare_history(
        [
            {"role": "user", "content": "hello"},
            {"role": "tool", "content": "running tool"},
            {"role": "assistant", "content": "final", "status": "done", "format": "markdown"},
        ]
    )
    sig = svc._history_signature(prepared)
    resets = []
    model.modelReset.connect(lambda: resets.append(True))

    svc._handle_history_result(True, "", ("desktop:local", 1, sig, prepared))

    assert resets == []
    assert model.rowCount() == 3
    assert model._messages[1]["role"] == "system"
    assert model._messages[2]["content"] == "final"
    assert model._messages[2]["status"] == "done"
    assert svc._active_streaming_row == 2


def test_handle_history_result_reconciles_after_send_result_wins_race():
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
    _ = model.append_assistant("working", status="done")
    typing_row = model.append_assistant("", status="typing")
    svc._active_streaming_row = typing_row
    svc._handle_send_result(typing_row, True, "final")

    from app.backend.chat import ChatMessageModel

    prepared = ChatMessageModel.prepare_history(
        [
            {"role": "user", "content": "hello"},
            {"role": "tool", "content": "running tool"},
            {"role": "assistant", "content": "final", "status": "done", "format": "markdown"},
        ]
    )
    sig = svc._history_signature(prepared)
    resets = []
    model.modelReset.connect(lambda: resets.append(True))

    svc._handle_history_result(True, "", ("desktop:local", 1, sig, prepared))

    assert resets == []
    assert model.rowCount() == 3
    assert model._messages[1]["role"] == "system"
    assert model._messages[2]["content"] == "final"
    assert model._messages[2]["status"] == "done"


def test_send_result_after_history_reconcile_uses_shifted_active_row():
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
    _ = model.append_assistant("working", status="done")
    typing_row = model.append_assistant("", status="typing")
    svc._active_streaming_row = typing_row

    from app.backend.chat import ChatMessageModel

    prepared = ChatMessageModel.prepare_history(
        [
            {"role": "user", "content": "hello"},
            {"role": "tool", "content": "running tool"},
            {"role": "assistant", "content": "final", "status": "done", "format": "markdown"},
        ]
    )
    sig = svc._history_signature(prepared)
    statuses = []
    svc.statusSettled.connect(lambda row, status: statuses.append((row, status)))

    svc._handle_history_result(True, "", ("desktop:local", 1, sig, prepared))
    svc._handle_send_result(typing_row, True, "final")

    assert statuses[-1] == (2, "done")
