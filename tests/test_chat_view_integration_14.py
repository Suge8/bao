# ruff: noqa: E402, N802, N815, F403, F405, I001
from __future__ import annotations

from tests._chat_view_integration_testkit import *

def test_main_chat_view_history_merge_after_send_result_does_not_jump_to_top(qapp):
    _ = qapp
    from app.backend.chat import ChatMessageModel

    raw_history = [{"role": "user", "content": f"message {i}"} for i in range(48)]
    messages_model = ChatMessageModel()
    messages_model.load_prepared(
        ChatMessageModel.prepare_history(
            raw_history
            + [
                {"role": "assistant", "content": "working", "status": "done"},
                {"role": "assistant", "content": "final", "status": "done", "format": "markdown"},
            ]
        )
    )

    engine, root = _load_main_window(messages_model=messages_model)

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

        prepared = ChatMessageModel.prepare_history(
            raw_history
            + [
                {"role": "tool", "content": "running tool"},
                {"role": "assistant", "content": "final", "status": "done", "format": "markdown"},
            ]
        )
        messages_model.load_prepared(prepared)

        for _ in range(6):
            _process(30)

        content_y = float(message_list.property("contentY"))
        assert content_y > 2.0
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_main_chat_view_preserves_viewport_on_model_reset(qapp):
    _ = qapp
    from app.backend.chat import ChatMessageModel

    messages_model = ChatMessageModel()
    messages_model.load_prepared(
        ChatMessageModel.prepare_history(
            [{"role": "user", "content": f"message {i}"} for i in range(72)]
        )
    )

    engine, root = _load_main_window(messages_model=messages_model)

    try:
        message_list = _find_object(root, "chatMessageList")

        for _ in range(6):
            _process(30)

        max_y_before = max(
            0.0,
            float(message_list.property("contentHeight")) - float(message_list.property("height")),
        )
        assert max_y_before > 20.0

        target_y = max_y_before / 2.0
        _ = message_list.setProperty("contentY", target_y)
        _ = message_list.setProperty("bottomPinned", False)
        _process(30)

        messages_model.load_prepared(
            ChatMessageModel.prepare_history(
                [{"role": "assistant", "content": f"reply {i}"} for i in range(72)]
            )
        )

        for _ in range(6):
            _process(30)

        content_y = float(message_list.property("contentY"))
        assert content_y > 20.0
        assert abs(content_y - target_y) < 24.0
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_main_chat_view_keyboard_shortcuts_scroll_history(qapp):
    _ = qapp
    from app.backend.chat import ChatMessageModel

    messages_model = ChatMessageModel()
    messages_model.load_prepared(
        ChatMessageModel.prepare_history(
            [{"role": "user", "content": f"message {i}"} for i in range(72)]
        )
    )

    engine, root = _load_main_window(messages_model=messages_model)

    try:
        message_input = _find_object(root, "chatMessageInput")
        message_list = _find_object(root, "chatMessageList")
        root.requestActivate()

        for _ in range(6):
            _process(30)

        max_y = max(
            0.0,
            float(message_list.property("contentHeight")) - float(message_list.property("height")),
        )
        assert max_y > 20.0

        _ = message_list.setProperty("contentY", 0.0)
        message_list.forceActiveFocus()
        _process(20)

        for _ in range(2):
            QTest.keyClick(root, Qt.Key_Down)
            _process(30)
            if float(message_list.property("contentY")) > 0.0:
                break
            root.requestActivate()
            message_list.forceActiveFocus()
            _process(20)

        scrolled_down = float(message_list.property("contentY"))
        assert scrolled_down > 0.0

        for _ in range(2):
            QTest.keyClick(root, Qt.Key_Up)
            _process(30)
            if float(message_list.property("contentY")) < scrolled_down:
                break
            root.requestActivate()
            message_list.forceActiveFocus()
            _process(20)

        scrolled_up = float(message_list.property("contentY"))
        assert scrolled_up < scrolled_down

        message_input.forceActiveFocus()
        _process(20)
        _ = message_list.setProperty("contentY", 0.0)
        _process(20)

        QTest.keyClick(root, Qt.Key_Down)
        _process(30)

        assert float(message_list.property("contentY")) < 1.0
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_main_chat_view_keyboard_scroll_respects_list_bounds(qapp):
    _ = qapp
    from app.backend.chat import ChatMessageModel

    messages_model = ChatMessageModel()
    messages_model.load_prepared(
        ChatMessageModel.prepare_history(
            [{"role": "user", "content": f"message {i}"} for i in range(96)]
        )
    )

    engine, root = _load_main_window(messages_model=messages_model)

    try:
        message_list = _find_object(root, "chatMessageList")
        root.requestActivate()

        for _ in range(6):
            _process(30)

        message_list.forceActiveFocus()
        _process(20)

        QTest.keyClick(root, Qt.Key_End)
        _process(40)
        bottom_y = float(message_list.property("contentY"))

        QTest.keyClick(root, Qt.Key_Down)
        _process(30)
        QTest.keyClick(root, Qt.Key_PageDown)
        _process(30)

        assert abs(float(message_list.property("contentY")) - bottom_y) < 2.0

        for _ in range(160):
            QTest.keyClick(root, Qt.Key_Up)
            _process(8)

        QTest.keyClick(root, Qt.Key_Home)
        _process(40)
        top_y = float(message_list.property("contentY"))

        QTest.keyClick(root, Qt.Key_Up)
        _process(30)
        QTest.keyClick(root, Qt.Key_PageUp)
        _process(30)

        assert abs(float(message_list.property("contentY")) - top_y) < 2.0
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)
