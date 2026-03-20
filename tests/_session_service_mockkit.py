from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

from bao.hub import HubRuntimePort, local_hub_control
from bao.hub.directory import HubDirectory
from bao.session.manager import SessionChangeEvent
from bao.session.state import (
    build_session_snapshot,
    merge_runtime_metadata,
    nest_flat_persisted_metadata,
    split_runtime_metadata,
)


@dataclass(frozen=True)
class _MockSessionManagerOptions:
    active_key: str = ""
    fail_delete: bool = False
    delete_returns_false: bool = False
    delete_returns_false_after_delete: bool = False
    fail_set_active: bool = False


class _MockSessionManagerState:
    def __init__(
        self,
        sessions: list[dict[str, Any]],
        options: _MockSessionManagerOptions,
    ) -> None:
        self.options = options
        self.active_key = options.active_key
        self.listeners: list[Any] = []
        self.sessions = [self._normalize_session(session) for session in sessions]

    def _normalize_session(self, session: dict[str, Any]) -> dict[str, Any]:
        metadata = {"title": session.get("title", session["key"])}
        metadata.update(dict(session.get("metadata", {})))
        return {
            "key": session["key"],
            "updated_at": session.get("updated_at", 0),
            "metadata": metadata,
            "message_count": session.get("message_count"),
            "has_messages": session.get("has_messages"),
            "needs_tail_backfill": bool(session.get("needs_tail_backfill", False)),
        }

    def serialize_session(self, session: dict[str, Any]) -> dict[str, Any]:
        raw_metadata = dict(session.get("metadata", {}))
        if "title" in session and "title" not in raw_metadata:
            raw_metadata["title"] = session.get("title")
        persisted_metadata, runtime = split_runtime_metadata(raw_metadata)
        canonical = (
            dict(persisted_metadata)
            if any(key in persisted_metadata for key in ("routing", "workflow", "view"))
            else nest_flat_persisted_metadata(persisted_metadata)
        )
        snapshot = build_session_snapshot(canonical, runtime_updates=runtime)
        return {
            "key": session["key"],
            "updated_at": session.get("updated_at", 0),
            "metadata": merge_runtime_metadata(canonical, runtime),
            "routing": snapshot.routing.as_snapshot(),
            "runtime": snapshot.runtime.as_snapshot(),
            "workflow": snapshot.workflow.as_snapshot(),
            "view": snapshot.view.as_snapshot(),
            "message_count": session.get("message_count"),
            "has_messages": session.get("has_messages"),
            "needs_tail_backfill": bool(session.get("needs_tail_backfill", False)),
        }

    def find_session(self, key: str) -> dict[str, Any] | None:
        return next((session for session in self.sessions if session["key"] == key), None)

    def list_sessions(self) -> list[dict[str, Any]]:
        return [self.serialize_session(session) for session in self.sessions]

    def list_sessions_with_active_key(self, _natural_key: str) -> tuple[list[dict[str, Any]], str]:
        return [self.serialize_session(session) for session in self.sessions], self.active_key

    def get_active_session_key(self, _natural_key: str) -> str:
        return self.active_key

    def set_active_session_key(self, _natural_key: str, key: str) -> None:
        if self.options.fail_set_active:
            raise RuntimeError("set active failed")
        self.active_key = key

    def clear_active_session_key(self, _natural_key: str) -> None:
        self.active_key = ""

    def delete_session(self, key: str) -> bool:
        if self.options.fail_delete:
            raise RuntimeError("delete failed")
        if self.options.delete_returns_false:
            return False
        self.sessions = [session for session in self.sessions if session["key"] != key]
        return not self.options.delete_returns_false_after_delete

    def get_or_create(self, key: str) -> MagicMock:
        session = MagicMock()
        session.key = key
        session.metadata = {}
        session.messages = []
        session.created_at = datetime.now()
        session.updated_at = datetime.now()
        return session

    def save(self, session: Any) -> None:
        key = str(getattr(session, "key", ""))
        if not key:
            return
        updated_at = getattr(session, "updated_at", datetime.now())
        updated_value = updated_at.isoformat() if hasattr(updated_at, "isoformat") else str(updated_at)
        metadata = dict(getattr(session, "metadata", {}))
        existing = self.find_session(key)
        if existing is None:
            self.sessions.append({"key": key, "updated_at": updated_value, "metadata": metadata})
            return
        existing["updated_at"] = updated_value
        existing["metadata"] = metadata
        existing["needs_tail_backfill"] = bool(getattr(session, "needs_tail_backfill", False))

    def get_session_list_entry(self, key: str) -> dict[str, Any] | None:
        session = self.find_session(key)
        return self.serialize_session(session) if session is not None else None

    def backfill_display_tail_rows(self, _keys: list[str], _limit: int) -> None:
        return None

    def update_session(self, key: str, **changes: Any) -> None:
        session = self.find_session(key)
        if session is None:
            raise KeyError(key)
        for field, value in changes.items():
            session[field] = dict(value) if field == "metadata" and isinstance(value, dict) else value

    def add_change_listener(self, listener: Any) -> None:
        self.listeners.append(listener)

    def remove_change_listener(self, listener: Any) -> None:
        if listener in self.listeners:
            self.listeners.remove(listener)

    def emit_change(self, session_key: str, kind: str) -> None:
        event = SessionChangeEvent(session_key=session_key, kind=kind)
        for listener in list(self.listeners):
            listener(event)


def make_mock_session_manager(
    sessions: list[dict[str, Any]] | None = None,
    *,
    options: _MockSessionManagerOptions | None = None,
) -> MagicMock:
    state = _MockSessionManagerState(sessions or [], options or _MockSessionManagerOptions())
    manager = MagicMock()
    manager.list_sessions.side_effect = state.list_sessions
    manager.list_sessions_with_active_key.side_effect = state.list_sessions_with_active_key
    manager.get_active_session_key.side_effect = state.get_active_session_key
    manager.set_active_session_key.side_effect = state.set_active_session_key
    manager.clear_active_session_key.side_effect = state.clear_active_session_key
    manager.delete_session.side_effect = state.delete_session
    manager.delete_session_tree = manager.delete_session
    manager.get_or_create.side_effect = state.get_or_create
    manager.save.side_effect = state.save
    manager.get_session_list_entry.side_effect = state.get_session_list_entry
    manager.backfill_display_tail_rows = MagicMock(side_effect=state.backfill_display_tail_rows)
    manager.add_change_listener.side_effect = state.add_change_listener
    manager.remove_change_listener.side_effect = state.remove_change_listener
    manager.workspace = Path("/tmp/mock-session-root")
    manager.state_root = manager.workspace
    manager.directory = HubDirectory(manager)
    manager.control = local_hub_control(session_manager=manager)
    manager.runtime = HubRuntimePort(manager)
    manager._listeners = state.listeners
    manager._emit_change = state.emit_change
    manager._update_session = state.update_session
    manager._serialize_session = state.serialize_session
    return manager
