from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field as dataclass_field
from typing import Any


@dataclass
class PendingDeleteState:
    sessions_before: list[dict[str, Any]]
    active_before: str
    optimistic_active: str
    expanded_groups: dict[str, bool]


@dataclass
class SessionUiState:
    session_rows: list[dict[str, Any]] = dataclass_field(default_factory=list)
    active_key: str = ""
    expanded_groups: dict[str, bool] = dataclass_field(default_factory=dict)
    unread_count: int = 0
    unread_fingerprint: str = ""
    loading: bool = False
    hub_ready: bool = False
    pending_select_key: str = ""
    pending_deletes: dict[str, PendingDeleteState] = dataclass_field(default_factory=dict)
    pending_creates: set[str] = dataclass_field(default_factory=set)


@dataclass(frozen=True)
class SessionViewRequest:
    sessions: list[dict[str, Any]]
    active_key: str
    sidebar_channels: set[str] | None = None
    backfill_keys: list[str] | None = None


@dataclass(frozen=True)
class SessionViewCommitRequest:
    sessions: list[dict[str, Any]]
    active_key: str
    model_apply: Any
    sidebar_channels: set[str] | None = None
    backfill_keys: list[str] | None = None
    derive_backfill_keys: bool = False
    emit_sessions_changed: bool = True
