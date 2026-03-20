# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._chat_service_testkit import *

def test_history_signature_changes_when_earlier_prepared_message_changes():
    svc, _ = make_service()

    old_prepared = [
        {
            "role": "system",
            "content": "welcome",
            "format": "plain",
            "status": "done",
            "entrancestyle": "system",
        },
        {
            "role": "assistant",
            "content": "hello",
            "format": "markdown",
            "status": "done",
            "entrancestyle": "none",
        },
    ]
    new_prepared = [
        {
            "role": "system",
            "content": "welcome",
            "format": "plain",
            "status": "done",
            "entrancestyle": "greeting",
        },
        {
            "role": "assistant",
            "content": "hello",
            "format": "markdown",
            "status": "done",
            "entrancestyle": "none",
        },
    ]

    assert svc._history_signature(old_prepared) != svc._history_signature(new_prepared)


def test_progress_update_does_not_mutate_model_when_session_mismatch():
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

    svc._handle_progress_update(-1, "streaming content")

    assert model.rowCount() == 0
    assert svc._active_has_content is True
    assert svc._committed_session_key == "desktop:new"
