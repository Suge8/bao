from __future__ import annotations

import os
from typing import Any

from app.backend._session_state import SessionViewCommitRequest, SessionViewRequest
from app.backend.session_projection import (
    SidebarProjectionRequest,
    build_sidebar_projection,
    project_active_session,
    session_channel_key,
    tail_backfill_keys,
)

_DEBUG_SWITCH = os.getenv("BAO_DESKTOP_DEBUG_SWITCH") == "1"


class SessionServiceViewMixin:
    def _emit_active_key_if_changed(self, new_key: str) -> None:
        if new_key != self._last_emitted_active_key:
            self._last_emitted_active_key = new_key
            self.activeKeyChanged.emit(new_key)
            self._emit_active_ready_if_applicable(new_key)

    def _session_item_by_key(self, key: str) -> dict[str, Any] | None:
        if not key:
            return None
        for session in self._model._sessions:
            if str(session.get("key", "")) == key:
                return session
        return None

    def _set_active_session_projection(self, key: str) -> None:
        projection = project_active_session(self._model._sessions, key)
        self._active_session_projection = projection
        if self._active_session_read_only == projection.read_only:
            return
        self._active_session_read_only = projection.read_only
        self.activeSessionMetaChanged.emit()

    def _is_read_only_session(self, key: str) -> bool:
        session = self._session_item_by_key(key)
        return bool(session.get("is_read_only", False)) if session is not None else False

    def _emit_active_summary(self, key: str) -> None:
        self._set_active_session_projection(key)
        projection = self._active_session_projection
        self.activeSummaryChanged.emit(key, projection.message_count, projection.has_messages)

    def _rebuild_sidebar_projection(self, channels: set[str] | None = None) -> None:
        self.sidebarProjectionWillChange.emit()
        projection = build_sidebar_projection(
            SidebarProjectionRequest(
                sessions=self._model._sessions,
                active_key=self._ui_state.active_key,
                expanded_groups=self._ui_state.expanded_groups,
                current_rows=self._sidebar_model._rows,
                channels=channels,
            )
        )
        self._ui_state.expanded_groups = projection.expanded_groups
        self._sidebar_model.sync_rows(projection.rows)
        self._set_sidebar_unread_summary(projection.unread_count, projection.unread_fingerprint)
        self.sidebarProjectionChanged.emit()

    def _apply_session_view(self, request: SessionViewRequest) -> None:
        self._commit_session_view(
            SessionViewCommitRequest(
                sessions=request.sessions,
                active_key=request.active_key,
                model_apply=self._model.sync_sessions,
                sidebar_channels=request.sidebar_channels,
                backfill_keys=request.backfill_keys,
                derive_backfill_keys=request.backfill_keys is None,
            )
        )

    def _apply_incremental_session_updates(self, request: SessionViewRequest) -> None:
        self._commit_session_view(
            SessionViewCommitRequest(
                sessions=request.sessions,
                active_key=request.active_key,
                model_apply=self._model.upsert_sessions,
                sidebar_channels=request.sidebar_channels,
                backfill_keys=request.backfill_keys,
            )
        )

    def _set_sessions_loading(self, loading: bool) -> None:
        if self._ui_state.loading == loading:
            return
        self._ui_state.loading = loading
        self.sessionsLoadingChanged.emit(loading)

    def _begin_list_request(self) -> None:
        self._list_inflight_count += 1
        self._set_sessions_loading(True)

    def _finish_list_request(self) -> None:
        self._list_inflight_count = max(0, self._list_inflight_count - 1)
        self._set_sessions_loading(self._list_inflight_count > 0)

    def _next_active_commit_seq(self) -> int:
        self._active_commit_seq += 1
        return self._active_commit_seq

    def _set_sidebar_unread_summary(self, unread_count: int, unread_fingerprint: str) -> None:
        self._ui_state.unread_count = unread_count
        self._ui_state.unread_fingerprint = unread_fingerprint

    @staticmethod
    def _with_active_session_read(sessions: list[dict[str, Any]], active_key: str) -> list[dict[str, Any]]:
        next_sessions = [dict(item) for item in sessions]
        for item in next_sessions:
            if str(item.get("key", "")) == active_key:
                item["has_unread"] = False
        return next_sessions

    def _schedule_tail_backfill(self, backfill_keys: list[str]) -> None:
        if not backfill_keys:
            return
        future = self._submit_safe(self._backfill_listed_session_tails(list(dict.fromkeys(backfill_keys))))
        if future is not None:
            future.add_done_callback(self._on_backfill_done)

    def _commit_session_view(self, request: SessionViewCommitRequest) -> None:
        next_sessions = self._with_active_session_read(request.sessions, request.active_key)
        request.model_apply(next_sessions, request.active_key)
        self._commit_active_view(
            request.active_key,
            sidebar_channels=request.sidebar_channels,
            emit_sessions_changed=request.emit_sessions_changed,
        )
        target_backfill_keys = (
            tail_backfill_keys(next_sessions)
            if request.derive_backfill_keys
            else list(request.backfill_keys or [])
        )
        self._schedule_tail_backfill(target_backfill_keys)

    def _replace_session_view(self, request: SessionViewRequest) -> None:
        self._commit_session_view(
            SessionViewCommitRequest(
                sessions=request.sessions,
                active_key=request.active_key,
                model_apply=self._model.reset_sessions,
                sidebar_channels=request.sidebar_channels,
                backfill_keys=request.backfill_keys,
                derive_backfill_keys=request.backfill_keys is None,
            )
        )

    def _commit_active_view(
        self,
        key: str,
        *,
        sidebar_channels: set[str] | None = None,
        emit_sessions_changed: bool,
    ) -> None:
        self._ui_state.active_key = key
        self._ui_state.session_rows = [dict(item) for item in self._model._sessions]
        self._rebuild_sidebar_projection(sidebar_channels)
        if emit_sessions_changed:
            self.sessionsChanged.emit()
        self._emit_active_summary(key)
        self._emit_active_key_if_changed(key)

    def _set_local_active_key(self, key: str) -> None:
        if self._ui_state.active_key == key:
            return
        self._model.set_active(key)
        if _DEBUG_SWITCH:
            from loguru import logger

            logger.debug("session_select_commit key={}", key)
        self._commit_active_view(key, emit_sessions_changed=False)

    def _finalize_active_resolution(self, active_for_view: str) -> None:
        self._clear_pending_select_if_resolved(active_for_view)

    def _desktop_startup_target_key(self) -> str:
        active_key = self._ui_state.active_key
        if active_key and session_channel_key(active_key) == "desktop":
            for session in self._model._sessions:
                if str(session.get("key", "")) == active_key:
                    return active_key
        for session in self._model._sessions:
            key = str(session.get("key", ""))
            if session_channel_key(key) == "desktop":
                return key
        return ""

    def _emit_active_ready_if_applicable(self, key: str) -> None:
        if self._ui_state.hub_ready and key:
            self.activeReady.emit(key)

    def _emit_startup_target_if_applicable(self) -> None:
        if not self._ui_state.hub_ready:
            return
        target_key = self._desktop_startup_target_key()
        if target_key:
            self.startupTargetReady.emit(target_key)
