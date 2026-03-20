from __future__ import annotations

from app.backend._session_state import SessionViewRequest
from app.backend.session_projection import pick_latest_key, session_channel_key
from bao.session.manager import SessionChangeEvent


class SessionServiceChangeEventsMixin:
    def _on_session_change(self, event: SessionChangeEvent) -> None:
        self._sessionChange.emit(event)

    def _handle_session_change(self, event: object) -> None:
        if self._disposed or not isinstance(event, SessionChangeEvent):
            return
        if event.session_key in self._ui_state.pending_deletes:
            return
        if event.kind == "deleted":
            self._handle_deleted_change(event.session_key)
            return
        if event.kind not in {"metadata", "messages"}:
            self.refresh()
            return
        if self._current_hub_directory() is None:
            self.refresh()
            return
        request_seq = self._session_entry_request_seq.get(event.session_key, 0) + 1
        self._session_entry_request_seq[event.session_key] = request_seq
        future = self._submit_safe(
            self._load_session_entry(
                event.session_key,
                request_seq=request_seq,
                generation=self._session_entry_generation,
            )
        )
        if future is not None:
            future.add_done_callback(self._on_session_entry_done)

    def _clear_pending_select_if_resolved(self, active_key: str) -> None:
        if self._ui_state.pending_select_key == active_key:
            self._ui_state.pending_select_key = ""

    def _schedule_select_commit(self, key: str) -> None:
        if not key or not self._has_hub_control():
            return
        future = self._submit_safe(self._select_session(key, self._next_active_commit_seq()))
        if future is not None:
            future.add_done_callback(self._on_select_done)

    def _handle_deleted_change(self, key: str) -> None:
        normalized = str(key or "")
        if not normalized:
            return
        self._session_entry_request_seq.pop(normalized, None)
        self._ui_state.pending_creates.discard(normalized)
        if self._ui_state.pending_select_key == normalized:
            self._ui_state.pending_select_key = ""
        current_sessions = [dict(item) for item in self._model._sessions]
        next_sessions = [item for item in current_sessions if str(item.get("key", "")) != normalized]
        if len(next_sessions) == len(current_sessions):
            return
        removed = next((item for item in current_sessions if str(item.get("key", "")) == normalized), None)
        removed_channel = str((removed or {}).get("channel") or session_channel_key(normalized) or "desktop")
        active_key = self._ui_state.active_key if self._ui_state.active_key != normalized else ""
        if not active_key and next_sessions:
            active_key = pick_latest_key(next_sessions, preferred_channel=(removed_channel or "desktop"))
        self._apply_session_view(
            SessionViewRequest(
                sessions=next_sessions,
                active_key=active_key,
                sidebar_channels={removed_channel},
            )
        )
        self._request_session_discovery_refresh()
        self._finalize_active_resolution(active_key)
        self._emit_startup_target_if_applicable()
        if next_sessions:
            if self._ui_state.active_key == normalized and self._ui_state.hub_ready and not self._ui_state.pending_select_key:
                self._schedule_select_commit(active_key)
            return
        if self._ui_state.hub_ready and self._has_hub_control():
            self.newSession("")
