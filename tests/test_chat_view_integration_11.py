# ruff: noqa: E402, N802, N815, F403, F405, I001
from __future__ import annotations

from tests._chat_view_integration_testkit import *

def test_sidebar_active_session_reorder_does_not_jump_to_top(qapp):
    _ = qapp
    rows = []
    for i in range(20):
        rows.append(
            {
                "key": f"imessage:chat::{i}",
                "title": f"Chat {i}",
                "updated_at": f"2026-03-06T10:{59 - i:02d}:00",
                "channel": "imessage",
                "has_unread": False,
            }
        )
    session_model = SessionsModel(rows)
    engine, root = _load_main_window(session_model=session_model)

    try:
        session_service = engine._test_refs["session_service"]
        session_list = _find_object(root, "sidebarSessionList")

        session_service.toggleSidebarGroup("imessage")
        session_service.setActiveKey("imessage:chat::15")
        session_service.sessionsChanged.emit()
        for _ in range(4):
            _process(30)

        max_y_before = max(
            0.0,
            float(session_list.property("contentHeight")) - float(session_list.property("height")),
        )
        session_list.setProperty("contentY", max_y_before)
        _process(30)
        before_y = float(session_list.property("contentY"))
        origin_y = float(session_list.property("originY"))
        assert before_y > origin_y + 100.0
        active_y_before = _sidebar_delegate_y(session_list, "imessage:chat::15")
        assert active_y_before < before_y + float(session_list.property("height"))

        reordered_rows = [dict(row) for row in rows]
        active_row = reordered_rows.pop(15)
        active_row["updated_at"] = "2026-03-06T11:59:00"
        reordered_rows.insert(0, active_row)

        session_model.replaceRows(reordered_rows)
        session_service.sessionsChanged.emit()
        for _ in range(4):
            _process(30)

        after_y = float(session_list.property("contentY"))
        assert after_y > origin_y + 100.0
        assert abs(after_y - before_y) < 40.0
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_sidebar_session_delegate_geometry_contains_row_spacing(qapp):
    _ = qapp
    rows = []
    for i in range(10):
        rows.append(
            {
                "key": f"desktop:local::s{i}",
                "title": f"Desktop {i}",
                "updated_at": f"2026-03-06T10:{i:02d}:00",
                "channel": "desktop",
                "has_unread": False,
            }
        )
    session_model = SessionsModel(rows)
    engine, root = _load_main_window(session_model=session_model)

    try:
        session_service = engine._test_refs["session_service"]
        session_service.setActiveKey("desktop:local::s0")
        session_service.sessionsChanged.emit()
        for _ in range(4):
            _process(30)

        session_list = _find_object(root, "sidebarSessionList")
        delegate = _sidebar_delegate_root(session_list, "desktop:local::s0")
        child_bottom = 0.0
        for child in delegate.childItems():
            if not bool(child.property("visible")):
                continue
            child_bottom = max(
                child_bottom, float(child.property("y")) + float(child.property("height"))
            )

        assert child_bottom <= float(delegate.property("height")) + 0.5
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_sidebar_near_bottom_refresh_keeps_visible_anchor(qapp):
    _ = qapp
    rows = []
    for i in range(30):
        rows.append(
            {
                "key": f"imessage:chat::{i}",
                "title": f"Chat {i}",
                "updated_at": f"2026-03-06T10:{59 - (i % 60):02d}:00",
                "channel": "imessage",
                "has_unread": False,
            }
        )
    session_model = SessionsModel(rows)
    engine, root = _load_main_window(session_model=session_model)

    try:
        session_service = engine._test_refs["session_service"]
        session_list = _find_object(root, "sidebarSessionList")

        session_service.setActiveKey("imessage:chat::25")
        session_service.sessionsChanged.emit()
        for _ in range(4):
            _process(30)

        max_y_before = max(
            0.0,
            float(session_list.property("contentHeight")) - float(session_list.property("height")),
        )
        session_list.setProperty("contentY", max_y_before)
        _process(30)

        current_rows = [dict(row) for row in rows]
        for step in range(3):
            moved = current_rows.pop(24 - step)
            moved["updated_at"] = f"2026-03-06T11:5{step}:00"
            current_rows.insert(0, moved)

            session_model.replaceRows(current_rows)
            session_service.sessionsChanged.emit()
            session_service.sessionsChanged.emit()
            for _ in range(6):
                _process(30)

            content_y = float(session_list.property("contentY"))
            origin_y = float(session_list.property("originY"))
            max_y = max(
                0.0,
                float(session_list.property("contentHeight"))
                - float(session_list.property("height")),
            )
            key, _offset = _first_visible_sidebar_session_anchor(root, session_list)

            assert key != ""
            assert content_y >= origin_y
            assert content_y <= max_y + 2.0
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_main_chat_view_system_message_append_forces_follow_to_end(qapp):
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

        max_y_before = max(
            0.0,
            float(message_list.property("contentHeight")) - float(message_list.property("height")),
        )
        assert max_y_before > 1.0

        _ = message_list.setProperty("contentY", 0.0)
        _process(30)

        row = messages_model.append_system(
            "Hub started", entrance_style="system", entrance_pending=True
        )
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


@pytest.mark.parametrize(
    ("history", "label"),
    [
        (
            [{"role": "user", "content": f"message {i}"} for i in range(72)],
            "many-short",
        ),
        (
            [
                {
                    "role": "assistant",
                    "content": " ".join([f"line{i}" for _ in range(18)]),
                }
                for i in range(17)
            ],
            "few-long",
        ),
    ],
    ids=lambda value: value if isinstance(value, str) else None,
)
def test_main_chat_view_preloaded_history_cold_open_follows_to_end(qapp, history, label):
    _ = qapp
    _ = label
    from app.backend.chat import ChatMessageModel

    messages_model = ChatMessageModel()
    messages_model.load_prepared(ChatMessageModel.prepare_history(history))

    engine, root = _load_main_window(messages_model=messages_model)

    try:
        message_list = _find_object(root, "chatMessageList")

        for _ in range(10):
            _process(30)

        origin_y = float(message_list.property("originY"))
        max_y = max(
            origin_y,
            origin_y
            + float(message_list.property("contentHeight"))
            - float(message_list.property("height")),
        )
        content_y = float(message_list.property("contentY"))

        assert max_y > origin_y + 20.0
        assert content_y >= max_y - 2.0
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)
