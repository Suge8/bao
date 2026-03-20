# ruff: noqa: E402, N802, N815, F403, F405, I001
from __future__ import annotations

from tests._chat_view_integration_testkit import *

@pytest.mark.parametrize(
    ("append_message", "label"),
    [
        (lambda model: model.append_user("hello"), "user"),
        (lambda model: model.append_assistant("hello", status="done"), "assistant"),
        (
            lambda model: model.append_system(
                "Hub started", entrance_style="system", entrance_pending=True
            ),
            "system",
        ),
        (
            lambda model: model.append_system(
                "Welcome back", entrance_style="greeting", entrance_pending=True
            ),
            "greeting",
        ),
    ],
    ids=lambda value: value if isinstance(value, str) else None,
)
def test_main_chat_view_appended_messages_force_follow_to_end(qapp, append_message, label):
    _ = qapp
    _ = label
    from app.backend.chat import ChatMessageModel

    messages_model = ChatMessageModel()
    for i in range(48):
        messages_model.append_user(f"message {i}")

    engine, root = _load_main_window(messages_model=messages_model)

    try:
        chat_service = engine._test_refs["chat_service"]
        message_list = _find_object(root, "chatMessageList")

        for _ in range(6):
            _process(30)

        max_y_before = max(
            0.0,
            float(message_list.property("contentHeight")) - float(message_list.property("height")),
        )
        assert max_y_before > 1.0

        _ = message_list.setProperty("contentY", 0.0)
        _process(30)

        row = append_message(messages_model)
        chat_service.appendAtBottom.emit(row)

        for _ in range(8):
            _process(30)

        max_y_after = max(
            0.0,
            float(message_list.property("contentHeight")) - float(message_list.property("height")),
        )
        follow_upper_bound = max_y_after + float(message_list.property("topMargin")) + 2.0
        content_y = float(message_list.property("contentY"))

        assert max_y_after > 1.0
        assert content_y >= max_y_after - 2.0
        assert content_y <= follow_upper_bound
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_main_chat_view_deferred_follow_respects_history_loading(qapp):
    _ = qapp
    from app.backend.chat import ChatMessageModel

    messages_model = ChatMessageModel()
    for i in range(48):
        messages_model.append_user(f"message {i}")

    engine, root = _load_main_window(messages_model=messages_model)

    try:
        chat_service = engine._test_refs["chat_service"]
        message_list = _find_object(root, "chatMessageList")

        for _ in range(6):
            _process(30)

        row = messages_model.append_system(
            "Hub started", entrance_style="system", entrance_pending=True
        )
        chat_service.appendAtBottom.emit(row)

        _ = message_list.setProperty("contentY", 0.0)
        _ = message_list.setProperty("bottomPinned", False)
        chat_service.setHistoryLoading(True)

        for _ in range(4):
            _process(30)

        assert float(message_list.property("contentY")) < 2.0
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_main_chat_view_streaming_update_follows_when_active(qapp):
    _ = qapp
    from app.backend.chat import ChatMessageModel

    messages_model = ChatMessageModel()
    for i in range(48):
        messages_model.append_user(f"message {i}")

    engine, root = _load_main_window(messages_model=messages_model)

    try:
        chat_service = engine._test_refs["chat_service"]
        message_list = _find_object(root, "chatMessageList")

        for _ in range(6):
            _process(30)

        typing_row = messages_model.append_assistant("", status="typing")
        chat_service.appendAtBottom.emit(typing_row)
        for _ in range(4):
            _process(30)

        for i in range(12):
            streamed = "\n".join(f"stream line {j}" for j in range((i + 1) * 6))
            messages_model.update_content(typing_row, streamed)
            chat_service.incrementalContent.emit(typing_row)
            _process(25)

        for _ in range(4):
            _process(30)

        max_y_after = max(
            0.0,
            float(message_list.property("contentHeight")) - float(message_list.property("height")),
        )
        content_y = float(message_list.property("contentY"))

        assert max_y_after > 1.0
        assert content_y >= max_y_after - 2.0
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_main_chat_view_streaming_update_preserves_manual_viewport_when_scrolled_away(qapp):
    _ = qapp
    from app.backend.chat import ChatMessageModel

    messages_model = ChatMessageModel()
    for i in range(48):
        messages_model.append_user(f"message {i}")

    engine, root = _load_main_window(messages_model=messages_model)

    try:
        chat_service = engine._test_refs["chat_service"]
        message_list = _find_object(root, "chatMessageList")

        for _ in range(6):
            _process(30)

        typing_row = messages_model.append_assistant("", status="typing")
        chat_service.appendAtBottom.emit(typing_row)
        for _ in range(4):
            _process(30)

        _ = message_list.setProperty("contentY", 0.0)
        _ = message_list.setProperty("bottomPinned", False)
        _process(30)

        for i in range(8):
            streamed = "\n".join(f"stream line {j}" for j in range((i + 1) * 6))
            messages_model.update_content(typing_row, streamed)
            chat_service.incrementalContent.emit(typing_row)
            _process(25)

        for _ in range(4):
            _process(30)

        assert float(message_list.property("contentY")) < 2.0
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_main_chat_view_composer_activation_keeps_bottom_visible(qapp):
    _ = qapp
    from app.backend.chat import ChatMessageModel

    messages_model = ChatMessageModel()
    for i in range(48):
        messages_model.append_user(f"message {i}")

    chat_service = DummyChatService(messages_model, state="starting")
    engine, root = _load_main_window(messages_model=messages_model, chat_service=chat_service)

    try:
        message_list = _find_object(root, "chatMessageList")

        for _ in range(6):
            _process(30)

        max_y_before = max(
            0.0,
            float(message_list.property("contentHeight")) - float(message_list.property("height")),
        )
        assert max_y_before > 1.0

        _ = message_list.setProperty("contentY", max_y_before)
        _process(30)

        chat_service.setState("running")
        for _ in range(12):
            _process(30)

        max_y_after = max(
            0.0,
            float(message_list.property("contentHeight")) - float(message_list.property("height")),
        )
        content_y = float(message_list.property("contentY"))

        assert max_y_after > max_y_before
        assert content_y >= max_y_after - 2.0
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_main_chat_view_startup_greeting_lands_immediately_above_composer(qapp):
    _ = qapp
    from app.backend.chat import ChatMessageModel

    messages_model = ChatMessageModel()
    for i in range(20):
        messages_model.append_assistant(f"old {i}", status="done")

    chat_service = DummyChatService(messages_model, state="starting")
    engine, root = _load_main_window(messages_model=messages_model, chat_service=chat_service)

    try:
        message_list = _find_object(root, "chatMessageList")

        for _ in range(6):
            _process(30)

        chat_service.setState("running")
        _process(40)

        row = messages_model.append_assistant(
            "hello",
            status="done",
            entrance_style="greeting",
            entrance_pending=True,
        )
        chat_service.appendAtBottom.emit(row)
        _wait_until(
            lambda: float(message_list.property("contentY")) >= _scroll_max_y(message_list) - 2.0
        )

        max_y = _scroll_max_y(message_list)
        content_y = float(message_list.property("contentY"))

        assert content_y >= max_y - 2.0
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)
