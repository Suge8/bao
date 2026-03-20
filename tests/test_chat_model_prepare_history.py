"""prepare_history normalization behaviors."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

pytest_plugins = ("tests._chat_model_testkit",)


def test_prepare_history_preserves_valid_status(qapp):
    from app.backend.chat import ChatMessageModel

    prepared = ChatMessageModel.prepare_history(
        [
            {"role": "assistant", "content": "a", "status": "error"},
            {"role": "system", "content": "s", "status": "typing"},
            {"role": "user", "content": "u", "_source": "cron", "status": "error"},
            {"role": "tool", "content": "t", "status": "typing"},
        ]
    )
    assert [item["status"] for item in prepared] == ["error", "typing", "error", "typing"]


def test_prepare_history_preserves_system_entrance_style(qapp):
    from app.backend.chat import ChatMessageModel

    prepared = ChatMessageModel.prepare_history(
        [
            {"role": "system", "content": "hello", "entrance_style": "greeting"},
            {"role": "user", "content": "notice", "_source": "desktop-system", "entrance_style": "system"},
            {"role": "tool", "content": "work", "entrance_style": "system"},
        ]
    )
    assert [item["entrancestyle"] for item in prepared] == ["greeting", "system", "system"]


def test_prepare_history_invalid_entrance_style_falls_back_none(qapp):
    from app.backend.chat import ChatMessageModel

    prepared = ChatMessageModel.prepare_history(
        [
            {"role": "system", "content": "hello", "entrance_style": "bad-style"},
            {"role": "user", "content": "notice", "_source": "desktop-system", "entrance_style": 1},
            {"role": "tool", "content": "work", "entrance_style": None},
        ]
    )
    assert [item["entrancestyle"] for item in prepared] == ["none", "none", "none"]


def test_normalize_entrance_style_accepts_user_sent(qapp):
    from app.backend.chat import ChatMessageModel

    assert ChatMessageModel._normalize_entrance_style("userSent") == "userSent"


def test_prepare_history_invalid_status_falls_back_done(qapp):
    from app.backend.chat import ChatMessageModel

    prepared = ChatMessageModel.prepare_history(
        [
            {"role": "assistant", "content": "a", "status": "bad"},
            {"role": "system", "content": "s", "status": 1},
            {"role": "user", "content": "u", "_source": "desktop-system", "status": None},
        ]
    )
    assert [item["status"] for item in prepared] == ["done", "done", "done"]


def test_prepare_history_preserves_assistant_markdown_format(qapp):
    from app.backend.chat import ChatMessageModel

    prepared = ChatMessageModel.prepare_history(
        [{"role": "assistant", "content": "[bao](https://bao.bot)", "format": "markdown"}]
    )
    assert prepared[0]["format"] == "markdown"


def test_prepare_history_defaults_assistant_format_to_markdown(qapp):
    from app.backend.chat import ChatMessageModel

    prepared = ChatMessageModel.prepare_history([{"role": "assistant", "content": "**bao**"}])
    assert prepared[0]["format"] == "markdown"


def test_prepare_history_preserves_created_at_from_iso_string(qapp):
    from app.backend.chat import ChatMessageModel

    prepared = ChatMessageModel.prepare_history(
        [{"role": "assistant", "content": "hi", "created_at": "2024-01-02T03:04:05+00:00"}]
    )
    assert prepared[0]["createdat"] == 1704164645000


def test_prepare_history_preserves_created_at_from_epoch_millis(qapp):
    from app.backend.chat import ChatMessageModel

    prepared = ChatMessageModel.prepare_history([{"role": "user", "content": "hi", "created_at": 1704164645000}])
    assert prepared[0]["createdat"] == 1704164645000


def test_prepare_history_adds_gap_divider_text(qapp):
    from app.backend.chat import ChatMessageModel

    prepared = ChatMessageModel.prepare_history(
        [
            {"role": "user", "content": "morning", "created_at": "2024-01-02T09:00:00"},
            {"role": "assistant", "content": "night", "created_at": "2024-01-02T18:30:00"},
        ]
    )
    assert prepared[0]["dividertext"] == ""
    assert prepared[1]["dividertext"] == "2024/1/2"


def test_prepare_history_uses_time_for_same_day_gap_today(qapp):
    from app.backend.chat import ChatMessageModel

    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 3, 7, 20, 0, 0, tzinfo=tz)

    with patch("app.backend.chat.datetime", FrozenDateTime):
        prepared = ChatMessageModel.prepare_history(
            [
                {"role": "user", "content": "morning", "created_at": "2026-03-07T09:00:00"},
                {"role": "assistant", "content": "night", "created_at": "2026-03-07T18:30:00"},
            ]
        )
    assert prepared[1]["dividertext"] == "18:30"
