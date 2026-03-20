from __future__ import annotations

from typing import Any

from PySide6.QtCore import (
    Property,
    QObject,
    Signal,
)

from app.backend._cron_actions import CronBridgeActionsMixin
from app.backend._cron_common import _DRAFT_PREVIEW_ID, _empty_draft, _serialize_job
from app.backend._cron_model import CronTasksModel
from app.backend._cron_projection import CronBridgeProjectionMixin
from app.backend._cron_runtime import CronBridgeRuntimeMixin
from app.backend._profile_bootstrap import initial_active_profile_context
from app.backend.asyncio_runner import AsyncioRunner
from bao.cron.service import CronService

__all__ = ["CronBridgeService", "_DRAFT_PREVIEW_ID", "_empty_draft", "_serialize_job"]


class CronBridgeService(
    CronBridgeActionsMixin,
    CronBridgeRuntimeMixin,
    CronBridgeProjectionMixin,
    QObject,
):
    tasksChanged = Signal()
    selectedTaskChanged = Signal()
    draftChanged = Signal()
    busyChanged = Signal(bool)
    errorChanged = Signal(str)
    noticeChanged = Signal(str, bool)
    filtersChanged = Signal()
    profileChanged = Signal()
    executionStateChanged = Signal()
    _refreshRequested = Signal()
    _loadResult = Signal(bool, str, object)
    _saveResult = Signal(bool, str, str)
    _deleteResult = Signal(bool, str, str)
    _toggleResult = Signal(bool, str, str)
    _runResult = Signal(bool, str)

    def __init__(self, runner: AsyncioRunner, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._runner = runner
        self._tasks_model = CronTasksModel(self)
        self._all_tasks: list[dict[str, Any]] = []
        self._projected_tasks: list[dict[str, Any]] = []
        self._selected_task_id = ""
        self._draft: dict[str, Any] = _empty_draft()
        self._draft_dirty = False
        self._busy = False
        self._last_error = ""
        self._notice_text = ""
        self._notice_success = True
        self._filter_query = ""
        self._status_filter = "all"
        self._session_service: Any = None
        self._hub_running = False
        self._lang = "en"
        self._load_generation = 0
        self._current_profile_id = ""
        self._current_profile_name = ""
        self._local_cron = CronService(initial_active_profile_context().cron_store_path)
        self._live_cron: CronService | None = None
        self._local_listener = lambda: self._refreshRequested.emit()
        self._live_listener = lambda: self._refreshRequested.emit()
        self._local_cron.add_change_listener(self._local_listener)

        self._refreshRequested.connect(self.refresh)
        self._loadResult.connect(self._handle_load_result)
        self._saveResult.connect(self._handle_save_result)
        self._deleteResult.connect(self._handle_delete_result)
        self._toggleResult.connect(self._handle_toggle_result)
        self._runResult.connect(self._handle_run_result)

    @Property(QObject, constant=True)
    def tasksModel(self) -> CronTasksModel:
        return self._tasks_model

    @Property(int, notify=tasksChanged)
    def totalTaskCount(self) -> int:
        return len(self._all_tasks) + (1 if self.editingNewTask else 0)

    @Property(int, notify=tasksChanged)
    def visibleTaskCount(self) -> int:
        return len(self._projected_tasks)

    @Property(str, notify=selectedTaskChanged)
    def activeListItemId(self) -> str:
        draft_id = self._draft_id()
        if draft_id:
            return draft_id
        if self.editingNewTask:
            return _DRAFT_PREVIEW_ID
        return self._selected_task_id

    @Property(str, notify=selectedTaskChanged)
    def selectedTaskId(self) -> str:
        return self._selected_task_id

    @Property(bool, notify=selectedTaskChanged)
    def hasSelection(self) -> bool:
        return bool(self._current_saved_task_id())

    @Property(dict, notify=selectedTaskChanged)
    def selectedTask(self) -> dict[str, Any]:
        task = self._current_saved_task()
        return dict(task) if task is not None else {}

    @Property(dict, notify=draftChanged)
    def draft(self) -> dict[str, Any]:
        return dict(self._draft)

    @Property(bool, notify=draftChanged)
    def draftDirty(self) -> bool:
        return self._draft_dirty

    @Property(bool, notify=draftChanged)
    def hasDraft(self) -> bool:
        return bool(self._draft.get("id") or self._draft_dirty or self._draft.get("name"))

    @Property(bool, notify=draftChanged)
    def editingNewTask(self) -> bool:
        return self.hasDraft and not bool(self._draft.get("id"))

    @Property(bool, notify=busyChanged)
    def busy(self) -> bool:
        return self._busy

    @Property(str, notify=errorChanged)
    def lastError(self) -> str:
        return self._last_error

    @Property(str, notify=noticeChanged)
    def noticeText(self) -> str:
        return self._notice_text

    @Property(bool, notify=noticeChanged)
    def noticeSuccess(self) -> bool:
        return self._notice_success

    @Property(str, notify=filtersChanged)
    def filterQuery(self) -> str:
        return self._filter_query

    @Property(str, notify=filtersChanged)
    def statusFilter(self) -> str:
        return self._status_filter

    @Property(str, notify=profileChanged)
    def currentProfileId(self) -> str:
        return self._current_profile_id

    def supervisorTasksSnapshot(self) -> list[dict[str, Any]]:
        return [dict(item) for item in self._all_tasks if isinstance(item, dict)]

    @Property(str, notify=profileChanged)
    def currentProfileName(self) -> str:
        return self._current_profile_name

    @Property(bool, notify=executionStateChanged)
    def canRunSelectedNow(self) -> bool:
        return self._run_now_state()[0]

    @Property(str, notify=executionStateChanged)
    def runNowBlockedReason(self) -> str:
        return self._run_now_state()[1]
