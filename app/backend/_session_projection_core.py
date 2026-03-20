from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SidebarProjection:
    rows: list[dict[str, Any]]
    expanded_groups: dict[str, bool]
    unread_count: int
    unread_fingerprint: str


@dataclass(frozen=True)
class ActiveSessionProjection:
    key: str
    message_count: int | None
    has_messages: bool | None
    read_only: bool


@dataclass(frozen=True)
class SessionItemSpec:
    key: str
    natural_key: str
    updated_at: Any = ""
    channel: str = "desktop"
    has_unread: bool = False
    title: Any = None
    message_count: Any = None
    has_messages: Any = None
    session_kind: str = "regular"
    read_only: bool = False
    parent_session_key: str = ""
    parent_title: str = ""
    child_status: str = ""
    is_running: bool = False
    self_running: bool | None = None
    needs_tail_backfill: bool = False


@dataclass(frozen=True)
class SidebarProjectionRequest:
    sessions: list[dict[str, Any]]
    active_key: str
    expanded_groups: dict[str, bool]
    current_rows: list[dict[str, Any]] | None = None
    channels: set[str] | None = None


@dataclass(frozen=True)
class VisibleSessionSelection:
    candidates: tuple[str, ...]
    available_keys: set[str]
    pending_create_keys: set[str]
