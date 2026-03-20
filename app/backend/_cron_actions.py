from __future__ import annotations

import functools
from pathlib import Path
from typing import Any

from PySide6.QtCore import Slot

from bao.cron.service import CronService

from ._cron_common import _DRAFT_PREVIEW_ID, _draft_from_task, _empty_draft


class CronBridgeActionsMixin:
    @Slot(object)
    def setSessionService(self, service: object) -> None:
        self._session_service = service

    @Slot(str, str)
    def setProfileInfo(self, profile_id: str, profile_name: str) -> None:
        next_profile_id = profile_id.strip()
        next_profile_name = profile_name.strip()
        if (
            self._current_profile_id == next_profile_id
            and self._current_profile_name == next_profile_name
        ):
            return
        self._current_profile_id = next_profile_id
        self._current_profile_name = next_profile_name
        self.profileChanged.emit()

    @Slot(str)
    def setLanguage(self, lang: str) -> None:
        normalized = "zh" if lang == "zh" else "en"
        if self._lang == normalized:
            return
        self._lang = normalized
        self.refresh()

    @Slot(str)
    def setLocalStorePath(self, path: str) -> None:
        raw = path.strip()
        if not raw:
            return
        next_path = str(raw)
        current_path = str(getattr(self._local_cron, "store_path", ""))
        if current_path == next_path:
            self.refresh()
            return
        self._local_cron.remove_change_listener(self._local_listener)
        self._local_cron = CronService(Path(next_path))
        self._local_cron.add_change_listener(self._local_listener)
        self.executionStateChanged.emit()
        self.refresh()

    @Slot(object)
    def setLiveCronService(self, service: object) -> None:
        next_service = service if isinstance(service, CronService) else None
        if self._live_cron is next_service:
            return
        if self._live_cron is not None:
            self._live_cron.remove_change_listener(self._live_listener)
        self._live_cron = next_service
        if self._live_cron is not None:
            self._live_cron.add_change_listener(self._live_listener)
        self.executionStateChanged.emit()
        self.refresh()

    @Slot(bool)
    def setHubRunning(self, running: bool) -> None:
        self._hub_running = bool(running)
        self.executionStateChanged.emit()

    @Slot()
    def refresh(self) -> None:
        self._load_generation += 1
        generation = self._load_generation
        future = self._submit_safe(self._load_tasks())
        if future is None:
            return
        future.add_done_callback(functools.partial(self._on_load_done, generation))

    @Slot(str)
    def selectTask(self, task_id: str) -> None:
        if task_id == _DRAFT_PREVIEW_ID:
            self.newDraft()
            return
        if task_id == self._selected_task_id:
            task = self._selected_task()
            draft_id = str(self._draft.get("id", "")).strip()
            if task is None or (draft_id == task_id and not self.editingNewTask):
                return
            self._draft = _draft_from_task(task)
            self._draft_dirty = False
            self._apply_projection()
            self.selectedTaskChanged.emit()
            self.draftChanged.emit()
            return
        self._selected_task_id = task_id
        task = self._selected_task()
        self._draft = _draft_from_task(task) if task else _empty_draft()
        self._draft_dirty = False
        self._apply_projection()
        self.selectedTaskChanged.emit()
        self.draftChanged.emit()

    @Slot()
    def newDraft(self) -> None:
        self._selected_task_id = ""
        self._draft = _empty_draft()
        self._draft_dirty = True
        self._apply_projection()
        self.selectedTaskChanged.emit()
        self.draftChanged.emit()

    @Slot()
    def duplicateSelected(self) -> None:
        task = self._selected_task()
        if not task:
            return
        self._selected_task_id = ""
        self._draft = _draft_from_task(task)
        self._draft["id"] = ""
        self._draft["name"] = f"{self._draft['name']} Copy".strip()
        self._draft_dirty = True
        self._apply_projection()
        self.selectedTaskChanged.emit()
        self.draftChanged.emit()

    @Slot(str, "QVariant")
    def updateDraftField(self, path: str, value: Any) -> None:
        parts = [part for part in path.split(".") if part]
        if not parts:
            return
        draft = dict(self._draft)
        node: dict[str, Any] = draft
        for part in parts[:-1]:
            child = node.get(part)
            if not isinstance(child, dict):
                child = {}
            child = dict(child)
            node[part] = child
            node = child
        node[parts[-1]] = value
        self._draft = draft
        self._draft_dirty = True
        if self.editingNewTask:
            self._apply_projection()
        self.draftChanged.emit()

    @Slot(str)
    def setFilterQuery(self, query: str) -> None:
        normalized = query.strip()
        if self._filter_query == normalized:
            return
        self._filter_query = normalized
        self._apply_projection()

    @Slot(str)
    def setStatusFilter(self, value: str) -> None:
        normalized = value.strip() or "all"
        if self._status_filter == normalized:
            return
        self._status_filter = normalized
        self._apply_projection()

    @Slot()
    def saveDraft(self) -> None:
        if self._busy:
            return
        self._set_busy(True)
        future = self._submit_safe(self._save_draft())
        if future is None:
            self._set_busy(False)
            return
        future.add_done_callback(self._on_save_done)

    @Slot()
    def deleteSelected(self) -> None:
        task = self._selected_task()
        if task is None or self._busy:
            return
        self._set_busy(True)
        future = self._submit_safe(self._delete_task(str(task.get("id", ""))))
        if future is None:
            self._set_busy(False)
            return
        future.add_done_callback(self._on_delete_done)

    @Slot(bool)
    def setSelectedEnabled(self, enabled: bool) -> None:
        task = self._selected_task()
        if task is None or self._busy:
            return
        self._set_busy(True)
        future = self._submit_safe(self._toggle_task(str(task.get("id", "")), bool(enabled)))
        if future is None:
            self._set_busy(False)
            return
        future.add_done_callback(self._on_toggle_done)

    @Slot()
    def runSelectedNow(self) -> None:
        task = self._selected_task()
        if task is None or self._busy:
            return
        self._set_busy(True)
        future = self._submit_safe(self._run_task_now(str(task.get("id", ""))))
        if future is None:
            self._set_busy(False)
            return
        future.add_done_callback(self._on_run_done)

    @Slot()
    def openSelectedSession(self) -> None:
        task = self._selected_task()
        if task is None or self._session_service is None:
            return
        select_session = getattr(self._session_service, "selectSession", None)
        if callable(select_session):
            select_session(str(task.get("session_key", "")))
