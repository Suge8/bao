from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, cast


@dataclass(frozen=True)
class PreparedMessageSpec:
    index: int
    role: str
    content: Any
    status: str
    entrance_style: str = "none"
    fmt: str = "plain"
    created_at: int = 0
    source: str | None = None
    attachments: list[dict[str, Any]] | None = None
    references: dict[str, Any] | None = None


@dataclass(frozen=True)
class MessageAppendOptions:
    status: str = "done"
    entrance_style: str = "none"
    entrance_pending: bool = True


class ChatMessagePrepareMixin:
    @staticmethod
    def _current_datetime() -> type[datetime]:
        from app.backend import chat as chat_module

        return chat_module.datetime

    @staticmethod
    def _normalize_status(status: Any, default: str = "done") -> str:
        if isinstance(status, str) and status in {"pending", "typing", "done", "error"}:
            return status
        return default

    @staticmethod
    def _normalize_entrance_style(style: Any, default: str = "none") -> str:
        if isinstance(style, str) and style in {
            "none",
            "assistantReceived",
            "userSent",
            "system",
            "greeting",
        }:
            return style
        return default

    @staticmethod
    def _normalize_format(fmt: Any, default: str = "plain") -> str:
        if isinstance(fmt, str) and fmt in {"plain", "markdown"}:
            return fmt
        return default

    @staticmethod
    def _build_prepared_message(spec: PreparedMessageSpec) -> dict[str, Any]:
        prepared = {
            "id": spec.index + 1,
            "createdat": spec.created_at,
            "role": spec.role,
            "content": spec.content,
            "format": spec.fmt,
            "status": spec.status,
            "entrancestyle": spec.entrance_style,
            "entrancepending": False,
            "dividertext": "",
            "attachments": list(spec.attachments or []),
            "references": dict(spec.references or {}),
        }
        if isinstance(spec.source, str) and spec.source:
            prepared["_source"] = spec.source
        return prepared

    @staticmethod
    def _normalize_created_at(value: Any) -> int:
        if isinstance(value, (int, float)):
            return max(0, int(value))
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return 0
            if raw.isdigit():
                return max(0, int(raw))
            try:
                dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            except ValueError:
                return 0
            return max(0, int(dt.timestamp() * 1000))
        return 0

    @classmethod
    def _message_created_at(cls, message: dict[str, Any]) -> int:
        for key in ("created_at", "createdAt", "createdat", "timestamp"):
            if key in message:
                return cls._normalize_created_at(message.get(key))
        return 0

    @staticmethod
    def _message_attachments(message: dict[str, Any]) -> list[dict[str, Any]] | None:
        attachments = message.get("attachments")
        if not isinstance(attachments, list):
            return None
        return cast(list[dict[str, Any]] | None, attachments)

    @staticmethod
    def _same_calendar_day(left_ms: int, right_ms: int) -> bool:
        left = datetime.fromtimestamp(left_ms / 1000)
        right = datetime.fromtimestamp(right_ms / 1000)
        return left.date() == right.date()

    @staticmethod
    def _format_day_divider(timestamp_ms: int) -> str:
        dt = datetime.fromtimestamp(timestamp_ms / 1000)
        now = ChatMessagePrepareMixin._current_datetime().now()
        if dt.year == now.year:
            return f"{dt.month}/{dt.day}"
        return f"{dt.year}/{dt.month}/{dt.day}"

    @staticmethod
    def _format_gap_divider(timestamp_ms: int) -> str:
        dt = datetime.fromtimestamp(timestamp_ms / 1000)
        return dt.strftime("%H:%M")

    @classmethod
    def _resolve_append_options(
        cls,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        defaults: MessageAppendOptions,
    ) -> MessageAppendOptions:
        if args and isinstance(args[0], MessageAppendOptions):
            if len(args) > 1 or kwargs:
                raise TypeError("MessageAppendOptions cannot be combined with legacy arguments.")
            return args[0]
        if len(args) > 2:
            raise TypeError("Too many positional arguments for chat message append.")
        status = args[0] if args else kwargs.pop("status", defaults.status)
        entrance_style = (
            args[1] if len(args) > 1 else kwargs.pop("entrance_style", defaults.entrance_style)
        )
        entrance_pending = kwargs.pop("entrance_pending", defaults.entrance_pending)
        if kwargs:
            names = ", ".join(sorted(kwargs))
            raise TypeError(f"Unexpected chat append arguments: {names}")
        return MessageAppendOptions(
            status=cls._normalize_status(status, default=defaults.status),
            entrance_style=cls._normalize_entrance_style(
                entrance_style,
                default=defaults.entrance_style,
            ),
            entrance_pending=bool(entrance_pending),
        )

    @classmethod
    def _divider_text_for(cls, current_created_at: int, previous_created_at: int) -> str:
        if current_created_at <= 0 or previous_created_at <= 0:
            return ""
        if not cls._same_calendar_day(previous_created_at, current_created_at):
            return cls._format_day_divider(current_created_at)
        if current_created_at - previous_created_at < 6 * 60 * 60 * 1000:
            return ""
        now_ms = int(cls._current_datetime().now().timestamp() * 1000)
        if cls._same_calendar_day(current_created_at, now_ms):
            return cls._format_gap_divider(current_created_at)
        return cls._format_day_divider(current_created_at)

    @classmethod
    def _apply_divider_texts(cls, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        previous_created_at = 0
        for message in messages:
            current_created_at = cls._normalize_created_at(message.get("createdat", 0))
            message["dividertext"] = cls._divider_text_for(current_created_at, previous_created_at)
            previous_created_at = current_created_at
        return messages

    @classmethod
    def prepare_history(cls, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        prepared: list[dict[str, Any]] = []
        for index, message in enumerate(messages):
            prepared_message = cls._prepare_history_message(index, message)
            if prepared_message is None:
                continue
            prepared.append(prepared_message)
        return cls._apply_divider_texts(prepared)

    @classmethod
    def _prepare_history_message(
        cls, index: int, message: dict[str, Any]
    ) -> dict[str, Any] | None:
        role = str(message.get("role", "user") or "user")
        content = message.get("content", "")
        status = cls._normalize_status(message.get("status"), default="done")
        fmt = cls._resolve_history_format(role, message)
        created_at = cls._message_created_at(message)
        attachments = cls._message_attachments(message)
        references = cls._message_references(message)
        common = PreparedMessageSpec(
            index=index,
            role=role,
            content=content,
            status=status,
            fmt=fmt,
            created_at=created_at,
            source=message.get("_source"),
            attachments=attachments,
            references=references,
        )
        if role in {"assistant", "system"}:
            return cls._prepare_direct_history_message(common, message)
        if role == "user":
            return cls._prepare_user_history_message(common, message)
        if role in {"tool", "tool_calls"}:
            return cls._prepare_tool_history_message(common, message)
        return None

    @staticmethod
    def _message_references(message: dict[str, Any]) -> dict[str, Any] | None:
        references = message.get("references")
        if isinstance(references, dict):
            return references
        return None

    @classmethod
    def _resolve_history_format(cls, role: str, message: dict[str, Any]) -> str:
        default_format = "markdown" if role == "assistant" else "plain"
        return cls._normalize_format(message.get("format"), default=default_format)

    @classmethod
    def _prepare_direct_history_message(
        cls, common: PreparedMessageSpec, message: dict[str, Any]
    ) -> dict[str, Any]:
        entrance_style = cls._normalize_entrance_style(
            message.get("entrance_style"), default="none"
        )
        return cls._build_prepared_message(
            PreparedMessageSpec(
                **{**common.__dict__, "role": common.role, "entrance_style": entrance_style}
            )
        )

    @classmethod
    def _prepare_user_history_message(
        cls, common: PreparedMessageSpec, message: dict[str, Any]
    ) -> dict[str, Any]:
        if not message.get("_source"):
            return cls._build_prepared_message(
                PreparedMessageSpec(
                    **{**common.__dict__, "role": "user", "source": None, "entrance_style": "none"}
                )
            )
        entrance_style = cls._normalize_entrance_style(
            message.get("entrance_style"), default="none"
        )
        return cls._build_prepared_message(
            PreparedMessageSpec(
                **{**common.__dict__, "role": "system", "entrance_style": entrance_style}
            )
        )

    @classmethod
    def _prepare_tool_history_message(
        cls, common: PreparedMessageSpec, message: dict[str, Any]
    ) -> dict[str, Any]:
        entrance_style = cls._normalize_entrance_style(
            message.get("entrance_style"), default="none"
        )
        label = "\U0001f527 " + (
            common.content if isinstance(common.content, str) else str(common.content)
        )
        return cls._build_prepared_message(
            PreparedMessageSpec(
                **{
                    **common.__dict__,
                    "role": "system",
                    "content": label,
                    "entrance_style": entrance_style,
                    "source": None,
                }
            )
        )
