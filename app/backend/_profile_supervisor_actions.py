from __future__ import annotations

from typing import Any

from PySide6.QtCore import Slot

from bao.profile import profile_context_from_mapping

from ._profile_supervisor_common import _clone_dict_list, _now_iso


class ProfileSupervisorActionsMixin:
    def _empty_collections(self) -> dict[str, list[dict[str, Any]]]:
        return {name: [] for name in self._collection_names}

    def _section_items(self, section: str) -> list[dict[str, Any]]:
        return [dict(item) for item in self._visible_items.get(section, [])]

    def _wire_signals(self) -> None:
        refresh_if_hydrated = self._refresh_if_hydrated
        _ = self._profile_service.activeProfileChanged.connect(self._on_profile_switched)
        _ = self._profile_service.profilesChanged.connect(refresh_if_hydrated)
        _ = self._session_service.sessionsChanged.connect(refresh_if_hydrated)
        _ = self._session_service.hubLocalPortsReady.connect(self._on_session_manager_ready)
        _ = self._chat_service.stateChanged.connect(lambda _state: refresh_if_hydrated())
        _ = self._chat_service.errorChanged.connect(lambda _error: refresh_if_hydrated())
        _ = self._chat_service.hubChannelsChanged.connect(refresh_if_hydrated)
        _ = self._chat_service.hubDetailChanged.connect(refresh_if_hydrated)
        _ = self._chat_service.startupActivityChanged.connect(refresh_if_hydrated)
        _ = self._cron_service.tasksChanged.connect(refresh_if_hydrated)
        _ = self._cron_service.profileChanged.connect(refresh_if_hydrated)
        _ = self._heartbeat_service.stateChanged.connect(refresh_if_hydrated)
        _ = self._heartbeat_service.profileChanged.connect(refresh_if_hydrated)

    @Slot()
    def hydrateIfNeeded(self) -> None:
        if self._hydrated:
            return
        self.refresh()

    @Slot()
    def refreshIfHydrated(self) -> None:
        self._refresh_if_hydrated()

    @Slot()
    def refresh(self) -> None:
        self._hydrated = True
        if self._refresh_inflight:
            self._refresh_requested = True
            return
        self._refresh_inflight = True
        self._refresh_requested = False
        self._set_busy(True)
        snapshot = self._capture_active_inputs()
        future = self._submit_safe(self._build_projection(snapshot))
        if future is None:
            self._refresh_inflight = False
            self._set_busy(False)
            return
        future.add_done_callback(self._on_refresh_done)

    def _refresh_if_hydrated(self) -> None:
        if not self._hydrated:
            return
        self.refresh()

    @Slot(str)
    def selectProfile(self, profile_id: str) -> None:
        self._set_profile_filter(str(profile_id or "").strip(), toggle=True)

    @Slot()
    def clearProfileFilter(self) -> None:
        self._set_profile_filter("", toggle=False)

    @Slot(str)
    def selectItem(self, item_id: str) -> None:
        self._selected_item_id = str(item_id or "").strip()
        self.selectionChanged.emit()

    @Slot()
    def clearSelection(self) -> None:
        if not self._selected_item_id:
            return
        self._selected_item_id = ""
        self.selectionChanged.emit()

    @Slot(str)
    def activateProfile(self, profile_id: str) -> None:
        next_id = str(profile_id or "").strip()
        if not next_id:
            return
        self._profile_service.activateProfile(next_id)

    @Slot()
    def openSelectedTarget(self) -> None:
        selected = self.selectedItem
        if not selected:
            selected_profile = self.selectedProfile
            if selected_profile:
                self.activateProfile(str(selected_profile.get("id", "")))
            return
        self._queue_or_run_action(
            str(selected.get("profileId", "") or ""),
            action={
                "kind": str(selected.get("routeKind", "") or ""),
                "value": str(selected.get("routeValue", "") or ""),
            },
        )

    @Slot()
    def toggleSelectedCron(self) -> None:
        selected = self.selectedItem
        if not selected or str(selected.get("kind", "")) != "cron_job":
            return
        self._queue_or_run_action(
            str(selected.get("profileId", "") or ""),
            action={"kind": "toggle_cron", "value": str(selected.get("routeValue", "") or "")},
        )

    @Slot()
    def runSelectedHeartbeat(self) -> None:
        selected = self.selectedItem
        if not selected or str(selected.get("kind", "")) != "heartbeat_check":
            return
        self._queue_or_run_action(
            str(selected.get("profileId", "") or ""),
            action={"kind": "heartbeat", "value": "heartbeat"},
        )

    @Slot()
    def toggleActiveHub(self) -> None:
        state = str(getattr(self._chat_service, "state", "") or "")
        if state in {"running", "starting"}:
            self._chat_service.stop()
            return
        self._chat_service.start()

    def _queue_or_run_action(self, profile_id: str, *, action: dict[str, Any]) -> None:
        active_profile_id = str(getattr(self._profile_service, "activeProfileId", "") or "")
        next_profile_id = str(profile_id or "").strip()
        if next_profile_id and next_profile_id != active_profile_id:
            self._pending_action = {"profile_id": next_profile_id, **action}
            self._profile_service.activateProfile(next_profile_id)
            return
        self._run_pending_action(action)

    def _on_profile_switched(self) -> None:
        self._refresh_if_hydrated()
        self._try_flush_pending_action(session_manager_ready=False)

    def _on_session_manager_ready(self, _manager: object) -> None:
        self._refresh_if_hydrated()
        self._try_flush_pending_action(session_manager_ready=True)

    def _pending_action_needs_session_manager(self, action: dict[str, Any]) -> bool:
        return str(action.get("kind", "") or "") == "session"

    def _try_flush_pending_action(self, *, session_manager_ready: bool) -> None:
        action = self._pending_action
        if action is None:
            return
        expected_profile = str(action.get("profile_id", "") or "")
        active_profile_id = str(getattr(self._profile_service, "activeProfileId", "") or "")
        if not expected_profile or expected_profile != active_profile_id:
            return
        if self._pending_action_needs_session_manager(action) and not session_manager_ready:
            return
        self._pending_action = None
        self._run_pending_action(dict(action))

    def _open_cron_target(self, task_id: str, *, toggle_enabled: bool) -> None:
        self.profileNavigationRequested.emit("cron")
        self._cron_service.selectTask(task_id)
        if not toggle_enabled:
            return
        selected_task = getattr(self._cron_service, "selectedTask", {})
        if isinstance(selected_task, dict):
            self._cron_service.toggleEnabled(not bool(selected_task.get("enabled", False)))

    def _run_pending_action(self, action: dict[str, Any]) -> None:
        kind = str(action.get("kind", "") or "")
        value = str(action.get("value", "") or "")
        if kind == "profile" and value:
            self._set_profile_filter(value, toggle=False)
            return
        if kind == "session" and value:
            self.profileNavigationRequested.emit("sessions")
            self._session_service.selectSession(value)
            return
        if kind == "cron" and value:
            self._open_cron_target(value, toggle_enabled=False)
            return
        if kind == "toggle_cron" and value:
            self._open_cron_target(value, toggle_enabled=True)
            return
        if kind == "heartbeat":
            self.profileNavigationRequested.emit("cron")
            self._heartbeat_service.runNow()

    def _set_profile_filter(self, profile_id: str, *, toggle: bool) -> None:
        next_id = str(profile_id or "").strip()
        if toggle and self._selected_profile_id == next_id:
            next_id = ""
        if self._selected_profile_id == next_id and not self._selected_item_id:
            return
        self._selected_profile_id = next_id
        self._selected_item_id = ""
        self.selectionChanged.emit()
        self._apply_filter()
        self._emit_collection_changes()

    def _session_snapshot(self) -> list[dict[str, Any]]:
        snapshot_fn = getattr(self._session_service, "supervisorSessionsSnapshot", None)
        return _clone_dict_list(snapshot_fn()) if callable(snapshot_fn) else []

    def _cron_snapshot(self) -> list[dict[str, Any]]:
        snapshot_fn = getattr(self._cron_service, "supervisorTasksSnapshot", None)
        return _clone_dict_list(snapshot_fn()) if callable(snapshot_fn) else []

    def _heartbeat_snapshot(self) -> dict[str, Any]:
        snapshot_fn = getattr(self._heartbeat_service, "supervisorSnapshot", None)
        if callable(snapshot_fn):
            snapshot = snapshot_fn()
            if isinstance(snapshot, dict):
                next_snapshot = dict(snapshot)
                next_snapshot.setdefault("updated_at", _now_iso())
                return next_snapshot
        return {"updated_at": _now_iso()}

    def _hub_snapshot(self) -> dict[str, Any]:
        snapshot_fn = getattr(self._chat_service, "supervisorHubSnapshot", None)
        if callable(snapshot_fn):
            snapshot = snapshot_fn()
            if isinstance(snapshot, dict):
                return dict(snapshot)
        return {}

    def _capture_active_inputs(self) -> dict[str, Any]:
        hub_snapshot = self._hub_snapshot()
        return {
            "shared_workspace_path": str(getattr(self._profile_service, "sharedWorkspacePath", "") or ""),
            "active_profile_id": str(getattr(self._profile_service, "activeProfileId", "") or ""),
            "profile_registry_snapshot": dict(getattr(self._profile_service, "registrySnapshot", {}) or {}),
            "active_context": profile_context_from_mapping(getattr(self._profile_service, "activeProfileContext", None)),
            "active_sessions": self._session_snapshot(),
            "active_cron_items": self._cron_snapshot(),
            "heartbeat_status": self._heartbeat_snapshot(),
            "hub_state": str(hub_snapshot.get("state", "") or ""),
            "hub_detail": str(hub_snapshot.get("detail", "") or ""),
            "hub_error": str(hub_snapshot.get("error", "") or ""),
            "hub_detail_is_error": bool(hub_snapshot.get("detail_is_error", False)),
            "hub_channels": list(hub_snapshot.get("channels", []) or []),
            "startup_activity": dict(hub_snapshot.get("startup_activity", {}) or {}),
        }

    def _submit_safe(self, coro: Any) -> Any:
        try:
            return self._runner.submit(coro)
        except RuntimeError:
            coro.close()
            return None
