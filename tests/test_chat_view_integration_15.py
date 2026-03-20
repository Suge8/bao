# ruff: noqa: E402, N802, N815, F403, F405, I001
from __future__ import annotations

from tests._chat_view_integration_testkit import *

def test_main_chat_view_active_session_switch_follows_to_end_after_reset(qapp):
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
        chat_service = engine._test_refs["chat_service"]
        message_list = _find_object(root, "chatMessageList")
        session_service = engine._test_refs["session_service"]

        for _ in range(6):
            _process(30)

        _ = message_list.setProperty("contentY", 0.0)
        _process(20)

        session_service.setActiveKey("desktop:local::other")
        messages_model.load_prepared(
            ChatMessageModel.prepare_history(
                [{"role": "assistant", "content": f"reply {i}"} for i in range(72)]
            )
        )
        chat_service.emitSessionViewApplied("desktop:local::other")

        for _ in range(12):
            _process(30)
            max_y = max(
                0.0,
                float(message_list.property("contentHeight"))
                - float(message_list.property("height")),
            )
            content_y = float(message_list.property("contentY"))
            if max_y <= 20.0 or content_y < max_y - 2.0:
                continue
            break

        max_y = max(
            0.0,
            float(message_list.property("contentHeight")) - float(message_list.property("height")),
        )
        follow_lower_bound = max_y - float(message_list.property("topMargin")) - 2.0
        follow_upper_bound = max_y + float(message_list.property("topMargin")) + 2.0
        content_y = float(message_list.property("contentY"))

        assert max_y > 20.0
        assert content_y >= follow_lower_bound
        assert content_y <= follow_upper_bound
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_main_chat_view_render_equivalent_session_switch_keeps_future_restore(qapp):
    _ = qapp
    from app.backend.chat import ChatMessageModel

    prepared = ChatMessageModel.prepare_history(
        [{"role": "user", "content": f"message {i}"} for i in range(72)]
    )
    messages_model = ChatMessageModel()
    messages_model.load_prepared(prepared)

    engine, root = _load_main_window(messages_model=messages_model)

    try:
        chat_service = engine._test_refs["chat_service"]
        session_service = engine._test_refs["session_service"]
        message_list = _find_object(root, "chatMessageList")

        for _ in range(6):
            _process(30)

        session_service.setActiveKey("desktop:local::other")
        chat_service.setHistoryLoading(True)
        messages_model.load_prepared(prepared)
        chat_service.emitSessionViewApplied("desktop:local::other")
        _process(20)
        chat_service.setHistoryLoading(False)

        for _ in range(8):
            _process(30)

        max_y = max(
            0.0,
            float(message_list.property("contentHeight")) - float(message_list.property("height")),
        )
        assert max_y > 20.0

        target_y = max_y / 2.0
        _ = message_list.setProperty("contentY", target_y)
        _ = message_list.setProperty("bottomPinned", False)
        _process(30)

        messages_model.load_prepared(
            ChatMessageModel.prepare_history(
                [{"role": "assistant", "content": f"reply {i}"} for i in range(72)]
            )
        )

        for _ in range(8):
            _process(30)

        content_y = float(message_list.property("contentY"))
        assert abs(content_y - target_y) < 24.0
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)
