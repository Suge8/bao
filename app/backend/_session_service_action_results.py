from __future__ import annotations

import os
from typing import Any

from loguru import logger

from app.backend._session_state import SessionViewRequest

_DEBUG_SWITCH = os.getenv("BAO_DESKTOP_DEBUG_SWITCH") == "1"


class SessionServiceActionResultsMixin:
    def _handle_select_result(self, ok: bool, error: str, key: str) -> None:
        if self._disposed:
            return
        if self._ui_state.pending_select_key and key != self._ui_state.pending_select_key:
            return
        if not self._ui_state.pending_select_key and key != self._ui_state.active_key:
            if _DEBUG_SWITCH:
                logger.debug("Ignore stale select result key={} active={} pending=<none>", key, self._ui_state.active_key)
            return
        if not ok:
            self._ui_state.pending_select_key = ""
            self.errorOccurred.emit(error)
            self.refresh()
            return
        self._set_local_active_key(key)

    def _handle_create_result(self, ok: bool, error: str, key: str) -> None:
        if self._disposed:
            return
        self._ui_state.pending_creates.discard(key)
        if not ok:
            self._handle_deleted_change(key)
            self.errorOccurred.emit(error)
            return
        if self._session_item_by_key(key) is None:
            self.refresh()
            return
        self._clear_pending_select_if_resolved(key)

    def _handle_delete_result(self, key: str, ok: bool, error: str) -> None:
        if self._disposed:
            return
        snapshot = self._ui_state.pending_deletes.pop(key, None)
        if not ok:
            if snapshot is not None:
                self._restore_failed_delete_snapshot(snapshot)
            self.errorOccurred.emit(error)
            self.deleteCompleted.emit(key, False, error)
            return
        if error:
            self.refresh()
        self.deleteCompleted.emit(key, True, "")

    def _restore_failed_delete_snapshot(self, snapshot: Any) -> None:
        if self._ui_state.active_key != snapshot.optimistic_active:
            self.refresh()
            return
        pending_keys = set(self._ui_state.pending_deletes.keys())
        if pending_keys:
            sessions_before = [
                session
                for session in snapshot.sessions_before
                if str(session.get("key", "")) not in pending_keys
            ]
            active_before = snapshot.active_before if snapshot.active_before not in pending_keys else self._ui_state.active_key
        else:
            sessions_before = snapshot.sessions_before
            active_before = snapshot.active_before
        self._ui_state.expanded_groups = dict(snapshot.expanded_groups)
        self._replace_session_view(SessionViewRequest(sessions=sessions_before, active_key=active_before))
