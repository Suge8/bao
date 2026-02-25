"""Tests for ChatService state machine and message queue."""

from __future__ import annotations

import sys
import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from PySide6.QtCore import QCoreApplication


@pytest.fixture(scope="module", autouse=True)
def qt_app():
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    yield app


from app.backend.chat import ChatMessageModel
from app.backend.gateway import ChatService


def make_service():
    model = ChatMessageModel()
    svc = ChatService(model)
    return svc, model


def test_initial_state():
    svc, _ = make_service()
    assert svc.state == "idle"
    assert svc.lastError == ""


def test_send_message_appends_user_row():
    svc, model = make_service()
    svc.sendMessage("hello")
    assert model.rowCount() == 1
    assert model._messages[0]["role"] == "user"
    assert model._messages[0]["content"] == "hello"


def test_send_empty_message_ignored():
    svc, model = make_service()
    svc.sendMessage("   ")
    assert model.rowCount() == 0


def test_send_message_emits_signal():
    svc, model = make_service()
    emitted = []
    svc.messageAppended.connect(emitted.append)
    svc.sendMessage("test")
    assert len(emitted) == 1
    assert emitted[0] == 0  # row 0


def test_stop_from_idle_is_noop():
    svc, _ = make_service()
    svc.stop()  # should not raise
    assert svc.state == "stopped"


def test_state_transitions_to_starting_on_start():
    svc, _ = make_service()
    states = []
    svc.stateChanged.connect(states.append)

    # Patch _init_gateway to avoid real bao init
    async def fake_init():
        pass

    with patch.object(svc, "_init_gateway", return_value=fake_init()):
        svc.start()

    assert "starting" in states


def test_double_start_is_noop():
    svc, _ = make_service()
    states = []
    svc.stateChanged.connect(states.append)

    async def fake_init():
        pass

    with patch.object(svc, "_init_gateway", return_value=fake_init()):
        svc.start()
        svc.start()  # second call should be ignored

    assert states.count("starting") == 1


def test_set_error_changes_state():
    svc, _ = make_service()
    errors = []
    states = []
    svc.errorChanged.connect(errors.append)
    svc.stateChanged.connect(states.append)
    svc._set_error("boom")
    assert svc.state == "error"
    assert svc.lastError == "boom"
    assert "boom" in errors
    assert "error" in states


def test_typewriter_effect_fills_content():
    """Typewriter should eventually set full content on the model."""
    svc, model = make_service()
    row = model.append_assistant("", status="typing")
    full_text = "Hello world"

    # Run the typewriter synchronously by processing Qt events
    svc._start_typewriter(row, full_text)

    # Process Qt timer events
    from PySide6.QtCore import QEventLoop, QTimer

    loop = QEventLoop()
    # Give enough time for all ticks (11 chars / 4 per tick = 3 ticks * 20ms = 60ms + buffer)
    QTimer.singleShot(200, loop.quit)
    loop.exec()

    assert model._messages[row]["content"] == full_text
    assert model._messages[row]["status"] == "done"


def test_typewriter_empty_text_sets_done():
    svc, model = make_service()
    row = model.append_assistant("", status="typing")
    svc._start_typewriter(row, "")
    assert model._messages[row]["status"] == "done"
