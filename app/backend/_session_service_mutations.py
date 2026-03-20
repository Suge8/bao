from __future__ import annotations

import os

from loguru import logger
from PySide6.QtCore import Slot

from app.backend._session_state import PendingDeleteState, SessionViewRequest
from app.backend.session_projection import SessionItemSpec, build_session_item, pick_latest_key

_DEBUG_SWITCH = os.getenv("BAO_DESKTOP_DEBUG_SWITCH") == "1"


class SessionServiceMutationMixin:
    @Slot()
    def refresh(self) -> None:
        if self._disposed or self._current_hub_directory() is None:
            return
        if self._refresh_inflight:
            self._refresh_requested = True
            return
        self._refresh_inflight = True
        self._refresh_requested = False
        self._session_entry_generation += 1
        self._begin_list_request()
        self._list_request_seq += 1
        seq = self._list_request_seq
        self._list_latest_seq = seq
        future = self._submit_safe(self._list_sessions(seq))
        if future is None:
            self._refresh_inflight = False
            self._finish_list_request()
            return
        future.add_done_callback(self._on_list_done)

    @Slot()
    def setHubReady(self) -> None:
        self._ui_state.hub_ready = True
        if self._ui_state.active_key:
            self._emit_active_ready_if_applicable(self._ui_state.active_key)
        self._emit_startup_target_if_applicable()

    @Slot(object)
    def adoptLiveHubRuntime(self, session_manager: object) -> None:
        self.setHubReady()

    @Slot(str)
    def newSession(self, name: str = "") -> None:
        if self._disposed or not self._has_hub_control():
            return
        key = self._build_new_session_key(name)
        if any(str(session.get("key", "")) == key for session in self._model._sessions):
            self.selectSession(key)
            return
        sessions_before = [dict(session) for session in self._model._sessions]
        self._ui_state.pending_creates.add(key)
        self._ui_state.hub_ready = True
        self._ui_state.pending_select_key = key
        self._replace_session_view(
            SessionViewRequest(
                sessions=[build_session_item(SessionItemSpec(key=key, natural_key=self._natural_key)), *sessions_before],
                active_key=key,
            )
        )
        future = self._submit_safe(self._create_session(key, self._next_active_commit_seq()))
        if future is not None:
            future.add_done_callback(lambda result, session_key=key: self._on_create_done(session_key, result))

    @Slot(str)
    def selectSession(self, key: str) -> None:
        if self._disposed:
            return
        if _DEBUG_SWITCH:
            logger.debug("session_select_request key={}", key)
        if not key:
            return
        self._ui_state.hub_ready = True
        if self._ui_state.pending_select_key == key:
            return
        self._ui_state.pending_select_key = key
        self._set_local_active_key(key)
        future = self._submit_safe(self._select_session(key, self._next_active_commit_seq()))
        if future is not None:
            future.add_done_callback(self._on_select_done)

    @Slot(str)
    def deleteSession(self, key: str) -> None:
        if self._disposed:
            return
        if not key or not self._has_hub_directory() or key in self._ui_state.pending_deletes:
            return
        if self._is_read_only_session(key):
            return
        sessions_before = [dict(session) for session in self._model._sessions]
        active_before = self._ui_state.active_key
        removed_index = next((i for i, session in enumerate(sessions_before) if session.get("key") == key), -1)
        sessions_after = [dict(session) for session in sessions_before if session.get("key") != key]
        if removed_index < 0 or len(sessions_after) == len(sessions_before):
            return
        new_active = active_before
        removed_channel = str(sessions_before[removed_index].get("channel") or "")
        if not sessions_after:
            new_active = self._build_new_session_key("")
            self._ui_state.pending_creates.add(new_active)
            sessions_after = [build_session_item(SessionItemSpec(key=new_active, natural_key=self._natural_key))]
            create_seq = self._next_active_commit_seq()
            future = self._submit_safe(self._create_session(new_active, create_seq))
            if future is not None:
                future.add_done_callback(
                    lambda result, session_key=new_active: self._on_create_done(session_key, result)
                )
        elif active_before == key:
            new_active = pick_latest_key(sessions_after, preferred_channel=(removed_channel or "desktop"))
        for item in sessions_after:
            if str(item.get("key", "")) == new_active:
                item["has_unread"] = False
        self._ui_state.pending_deletes[key] = PendingDeleteState(
            sessions_before=sessions_before,
            active_before=active_before,
            optimistic_active=new_active,
            expanded_groups=dict(self._ui_state.expanded_groups),
        )
        self._replace_session_view(SessionViewRequest(sessions=sessions_after, active_key=new_active))
        delete_seq = self._next_active_commit_seq() if active_before == key else None
        future = self._submit_safe(self._delete_session(key, new_active, delete_seq))
        if future is None:
            self._ui_state.pending_deletes.pop(key, None)
            return
        future.add_done_callback(lambda result, session_key=key: self._on_delete_done(session_key, result))

    @Slot(str)
    def toggleSidebarGroup(self, channel: str) -> None:
        if not channel:
            return
        self._ui_state.expanded_groups[channel] = self._ui_state.expanded_groups.get(channel, False) is not True
        self._rebuild_sidebar_projection()
