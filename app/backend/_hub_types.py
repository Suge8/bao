from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from bao.hub.builder import DesktopStartupMessage


@dataclass(frozen=True)
class _QueuedUiMessage:
    role: str
    content: str
    session_key: str = ""
    status: str = "done"
    entrance_style: str = "none"

    @classmethod
    def from_startup(
        cls,
        message: DesktopStartupMessage,
        session_key: str = "",
    ) -> _QueuedUiMessage:
        return cls(
            role=message.role,
            content=message.content,
            session_key=session_key,
            entrance_style=message.entrance_style,
        )

    def with_session_key(self, session_key: str) -> _QueuedUiMessage:
        return replace(self, session_key=session_key)


@dataclass(frozen=True)
class _HistorySnapshot:
    fingerprint: tuple[int, str]
    prepared_messages: list[dict[str, Any]]
    has_messages: bool


@dataclass(frozen=True)
class _ActiveUserMessage:
    row: int = -1
    session_key: str = ""
    token: str = ""


@dataclass(frozen=True)
class _QueuedSendRequest:
    session_key: str
    raw_text: str
    display_text: str
    media_paths: list[str]
    row: int
    client_token: str
