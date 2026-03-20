from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

_DEBUG_SWITCH = os.getenv("BAO_DESKTOP_DEBUG_SWITCH") == "1"
_PROFILE = os.getenv("BAO_DESKTOP_PROFILE") == "1"
_HISTORY_FULL_LIMIT = 200
_HISTORY_CACHE_LIMIT = 16


@dataclass(frozen=True)
class RawTailReloadRequest:
    key: str
    nav_id: int
    raw_tail_snapshot: list[dict[str, Any]]
    switched_session: bool


@dataclass(frozen=True)
class HistoryLoadRequest:
    key: str
    nav_id: int
    show_loading: bool | None = None
    raw_messages_override: list[dict[str, Any]] | None = None


@dataclass(frozen=True)
class LoadHistoryRequest:
    key: str
    nav_id: int
    limit: int
    raw_messages_override: list[dict[str, Any]] | None = None


@dataclass(frozen=True)
class PreparedHistoryRequest:
    loaded_key: str
    fingerprint: tuple[int, str]
    loaded_messages: list[dict[str, Any]]
    loaded_has_messages: bool


@dataclass(frozen=True)
class HistorySnapshotRequest:
    key: str
    fingerprint: tuple[int, str]
    prepared_messages: list[dict[str, Any]]
    has_messages: bool
