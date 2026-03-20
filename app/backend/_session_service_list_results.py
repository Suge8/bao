from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.backend._session_state import SessionViewRequest
from app.backend.session_projection import (
    SessionItemSpec,
    VisibleSessionSelection,
    build_session_item,
    filter_session_dicts,
    pick_latest_key,
    visible_session_key,
    visible_session_key_for_channel,
)


@dataclass(frozen=True)
class ListResultPayload:
    sessions: list[dict[str, Any]]
    stored_active: str


@dataclass(frozen=True)
class ListRefreshPlan:
    sessions: list[dict[str, Any]]
    active_key: str
    auto_selected_key: str = ""
    clear_active: bool = False


class SessionServiceListResultsMixin:
    def _handle_list_result(self, ok: bool, error: str, data: Any) -> None:
        if self._disposed:
            return
        self._refresh_inflight = False
        self._finish_list_request()
        payload = self._parse_list_result_payload(ok, error, data)
        if payload is None:
            return
        plan = self._build_list_refresh_plan(payload)
        if plan is None:
            return
        if plan.clear_active:
            self._ui_state.active_key = ""
            self._emit_active_key_if_changed("")
        self._apply_session_view(SessionViewRequest(sessions=plan.sessions, active_key=plan.active_key))
        self._emit_startup_target_if_applicable()
        self._finalize_active_resolution(plan.active_key)
        if plan.auto_selected_key and self._has_hub_control():
            future = self._submit_safe(self._select_session(plan.auto_selected_key, self._next_active_commit_seq()))
            if future is not None:
                future.add_done_callback(self._on_select_done)
        self._request_session_discovery_refresh()
        self._drain_requested_refresh()

    def _parse_list_result_payload(
        self,
        ok: bool,
        error: str,
        data: Any,
    ) -> ListResultPayload | None:
        if not ok:
            self.errorOccurred.emit(error)
            self._drain_requested_refresh()
            return None
        if isinstance(data, tuple) and len(data) == 3 and isinstance(data[0], int):
            seq, sessions, active = data
            if seq != self._list_latest_seq:
                return None
            return ListResultPayload(sessions=sessions, stored_active=active if isinstance(active, str) else "")
        if not (isinstance(data, tuple) and len(data) == 2):
            return None
        raw_sessions, raw_active = data
        if not isinstance(raw_sessions, list):
            return None
        return ListResultPayload(
            sessions=filter_session_dicts(raw_sessions),
            stored_active=raw_active if isinstance(raw_active, str) else "",
        )

    def _build_list_refresh_plan(self, payload: ListResultPayload) -> ListRefreshPlan | None:
        sessions = self._sessions_after_pending_filters(payload.sessions)
        active_key, auto_selected_key = self._resolved_list_active_key(sessions, payload.stored_active)
        pending_create_keys = set(self._ui_state.pending_creates)
        if self._ui_state.hub_ready and not sessions and not pending_create_keys and self._has_hub_control():
            self._refresh_requested = False
            self.newSession("")
            return None
        if self._ui_state.hub_ready and not self._ui_state.pending_select_key and not active_key:
            if sessions:
                active_key = pick_latest_key(sessions, preferred_channel="desktop")
                auto_selected_key = active_key
            elif self._has_hub_control():
                self._refresh_requested = False
                self.newSession("")
                return None
        return ListRefreshPlan(
            sessions=sessions,
            active_key=active_key,
            auto_selected_key=auto_selected_key,
            clear_active=not sessions and bool(self._ui_state.active_key),
        )

    def _sessions_after_pending_filters(self, sessions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        pending_keys = set(self._ui_state.pending_deletes.keys())
        next_sessions = [session for session in sessions if session.get("key") not in pending_keys]
        pending_create_keys = set(self._ui_state.pending_creates)
        if not pending_create_keys:
            return next_sessions
        existing_keys = {str(session.get("key", "")) for session in next_sessions}
        for key in pending_create_keys:
            if key in existing_keys:
                continue
            next_sessions.insert(0, build_session_item(SessionItemSpec(key=key, natural_key=self._natural_key)))
            existing_keys.add(key)
        return next_sessions

    def _resolved_list_active_key(self, sessions: list[dict[str, Any]], stored_active: str) -> tuple[str, str]:
        pending_create_keys = set(self._ui_state.pending_creates)
        available_keys = {str(session.get("key", "")) for session in sessions}
        selection = VisibleSessionSelection(candidates=(), available_keys=available_keys, pending_create_keys=pending_create_keys)
        pending_candidate = visible_session_key(
            VisibleSessionSelection(
                candidates=(self._ui_state.pending_select_key,),
                available_keys=selection.available_keys,
                pending_create_keys=selection.pending_create_keys,
            )
        )
        local_candidate = visible_session_key(
            VisibleSessionSelection(
                candidates=(self._ui_state.active_key,),
                available_keys=selection.available_keys,
                pending_create_keys=selection.pending_create_keys,
            )
        )
        stored_candidate = visible_session_key_for_channel(
            VisibleSessionSelection(
                candidates=(stored_active,),
                available_keys=selection.available_keys,
                pending_create_keys=selection.pending_create_keys,
            ),
            channel="desktop",
        )
        if pending_candidate:
            return pending_candidate, ""
        if local_candidate:
            return local_candidate, ""
        if stored_candidate:
            return stored_candidate, ""
        return "", ""

    def _drain_requested_refresh(self) -> None:
        if self._refresh_requested and not self._disposed and self._current_hub_directory() is not None:
            self._refresh_requested = False
            self.refresh()
