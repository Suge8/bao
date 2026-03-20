from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from loguru import logger

from app.backend._session_state import SessionViewRequest
from app.backend.session_projection import (
    normalize_session_item,
    pick_latest_key,
    project_session_item,
    running_parent_keys,
    title_by_key,
)


@dataclass(frozen=True)
class SessionEntryPayload:
    key: str
    entry: dict[str, Any] | None


@dataclass(frozen=True)
class SessionEntryPlan:
    sessions: list[dict[str, Any]]
    active_key: str
    sidebar_channels: set[str] | None = None
    backfill_keys: list[str] | None = None


@dataclass(frozen=True)
class NormalizedUpdateRequest:
    key: str
    projected: dict[str, Any]
    old_item: dict[str, Any] | None
    current_sessions: list[dict[str, Any]]
    current_by_key: dict[str, dict[str, Any]]


class SessionServiceEntryResultsMixin:
    def _handle_session_entry_result(self, ok: bool, error: str, data: Any) -> None:
        if self._disposed:
            return
        payload = self._parse_session_entry_payload(ok, error, data)
        if payload is None:
            return
        if payload.entry is None:
            self._handle_deleted_change(payload.key)
            return
        plan = self._build_session_entry_plan(payload)
        if plan is None:
            self.refresh()
            return
        self._apply_incremental_session_updates(
            SessionViewRequest(
                sessions=plan.sessions,
                active_key=plan.active_key,
                sidebar_channels=plan.sidebar_channels,
                backfill_keys=plan.backfill_keys,
            )
        )
        self._request_session_discovery_refresh()
        self._emit_startup_target_if_applicable()

    def _parse_session_entry_payload(self, ok: bool, error: str, data: Any) -> SessionEntryPayload | None:
        if not ok:
            logger.debug("Skip incremental session update: {}", error)
            self.refresh()
            return None
        if not (isinstance(data, tuple) and len(data) == 4):
            self.refresh()
            return None
        key, request_seq, generation, entry = data
        if key in self._ui_state.pending_deletes:
            return None
        if generation != self._session_entry_generation:
            return None
        if self._session_entry_request_seq.get(key, 0) != request_seq:
            return None
        if entry is None:
            return SessionEntryPayload(key=str(key), entry=None)
        if not isinstance(entry, dict):
            self.refresh()
            return None
        return SessionEntryPayload(key=str(key), entry=entry)

    def _build_session_entry_plan(self, payload: SessionEntryPayload) -> SessionEntryPlan | None:
        current_sessions = [dict(item) for item in self._model._sessions]
        current_by_key = {
            str(item.get("key", "")): dict(item)
            for item in current_sessions
            if str(item.get("key", ""))
        }
        old_item = current_by_key.get(payload.key)
        projected = project_session_item(payload.entry, natural_key=self._natural_key, current_sessions=current_sessions)
        updates, affected_keys = self._normalized_session_updates(
            NormalizedUpdateRequest(
                key=payload.key,
                projected=projected,
                old_item=old_item,
                current_sessions=current_sessions,
                current_by_key=current_by_key,
            )
        )
        sidebar_channels = {
            str(item.get("channel", "other") or "other")
            for item in updates
            if str(item.get("key", "")) in affected_keys
        }
        if old_item is not None and str(old_item.get("channel", "other") or "other"):
            sidebar_channels.add(str(old_item.get("channel", "other") or "other"))
        return SessionEntryPlan(
            sessions=updates,
            active_key=self._entry_active_key(payload.key, current_by_key, updates),
            sidebar_channels=sidebar_channels or None,
            backfill_keys=[payload.key] if bool(projected.get("needs_tail_backfill", False)) else [],
        )

    def _normalized_session_updates(
        self,
        request: NormalizedUpdateRequest,
    ) -> tuple[list[dict[str, Any]], set[str]]:
        related_parent_keys = {
            str(parent_key)
            for parent_key in (
                request.projected.get("parent_session_key", ""),
                request.old_item.get("parent_session_key", "") if request.old_item else "",
            )
            if str(parent_key)
        }
        affected_keys = {request.key, *related_parent_keys}
        for item in request.current_sessions:
            item_key = str(item.get("key", ""))
            parent_key = str(item.get("parent_session_key", ""))
            if parent_key == request.key or parent_key in related_parent_keys:
                affected_keys.add(item_key)
        updates: dict[str, dict[str, Any]] = {request.key: request.projected}
        for affected_key in affected_keys:
            if affected_key in updates:
                continue
            existing = request.current_by_key.get(affected_key)
            if existing is not None:
                updates[affected_key] = dict(existing)
        normalization_source = [
            updates.get(item_key, request.current_by_key[item_key])
            for item_key in request.current_by_key
            if item_key in request.current_by_key
        ]
        normalization_source.extend(
            session for item_key, session in updates.items() if item_key not in request.current_by_key
        )
        title_index = title_by_key(normalization_source)
        running_parent_index = running_parent_keys(normalization_source)
        normalized = [
            normalize_session_item(session, title_index=title_index, running_parent_index=running_parent_index)
            for session in updates.values()
        ]
        return normalized, affected_keys

    def _entry_active_key(
        self,
        key: str,
        current_by_key: dict[str, dict[str, Any]],
        updates: list[dict[str, Any]],
    ) -> str:
        available_keys = set(current_by_key)
        available_keys.add(key)
        active_key = self._ui_state.active_key if self._ui_state.active_key in available_keys else ""
        if active_key or not updates or self._ui_state.pending_select_key:
            return active_key
        updated_keys = {str(item.get("key", "")) for item in updates}
        candidate_sessions = [current_by_key[item_key] for item_key in current_by_key if item_key not in updated_keys] + updates
        return pick_latest_key(candidate_sessions, preferred_channel="desktop")
