# ruff: noqa: E402, N802, N815, F403, F405, I001
from __future__ import annotations

from tests._chat_view_integration_testkit import *


def _collect_target_qml_messages(messages: list[str]) -> list[str]:
    markers = (
        "ReferenceError:",
        "TypeError: Cannot read property",
        "Cannot assign to non-existent property",
    )
    return [message for message in messages if any(marker in message for marker in markers)]


def test_main_chat_view_message_bubbles_do_not_emit_runtime_qml_errors(qapp):
    _ = qapp
    from app.backend.chat import ChatMessageModel

    messages_model = ChatMessageModel()
    _ = messages_model.append_system("欢迎回来。", entrance_style="greeting")
    _ = messages_model.append_system("自动检查失败。", status="error", entrance_style="system")
    _ = messages_model.append_assistant("收到，我来处理。", status="done")
    _ = messages_model.append_user("看一下这个问题。", status="done")

    chat_service = DummyChatService(
        messages_model,
        state="running",
        active_session_ready=True,
        active_session_has_messages=True,
    )

    qt_messages: list[str] = []

    def _handler(_msg_type, _context, message) -> None:
        qt_messages.append(str(message))

    previous_handler = QtCore.qInstallMessageHandler(_handler)
    try:
        engine, root = _load_main_window(messages_model=messages_model, chat_service=chat_service)
        try:
            message_list = _find_object(root, "chatMessageList")
            assert message_list is not None

            for _ in range(8):
                _process(30)

            assert int(message_list.property("count") or 0) >= 4
            assert _collect_target_qml_messages(qt_messages) == []
        finally:
            root.deleteLater()
            engine.deleteLater()
            _process(0)
    finally:
        QtCore.qInstallMessageHandler(previous_handler)
