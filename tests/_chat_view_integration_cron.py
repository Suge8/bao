# ruff: noqa: E402, N802, N815, F403, F405, I001
from __future__ import annotations

from tests._chat_view_integration_shared import *

class DummyCronService(QObject):
    tasksChanged = Signal()
    selectedTaskChanged = Signal()
    draftChanged = Signal()
    busyChanged = Signal(bool)
    errorChanged = Signal(str)
    noticeChanged = Signal(str, bool)
    filtersChanged = Signal()
    profileChanged = Signal()
    executionStateChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._tasks_model = CronTasksModel(self)
        self._tasks: list[dict[str, object]] = [
            {
                "id": "task-1",
                "name": "Existing Task",
                "enabled": True,
                "status_key": "scheduled",
                "status_label": "已调度",
                "schedule_summary": "每 3 小时",
                "next_run_text": "2026-03-12 17:00",
                "last_result_text": "成功",
                "last_error": "",
                "session_key": "cron:task-1",
            }
        ]
        self._tasks_model.reset_rows(self._tasks)
        self._selected_task_id = ""
        self._draft: dict[str, object] = {}
        self._draft_dirty = False
        self._busy = False
        self._notice_text = ""
        self._notice_success = True
        self._filter_query = ""
        self._status_filter = "all"
        self._current_profile_name = "Work"

    def _sync_rows(self) -> None:
        rows = list(self._tasks)
        if self.editingNewTask:
            rows = [
                {
                    "id": "__draft__",
                    "name": self._draft.get("name") or "未命名任务",
                    "enabled": True,
                    "status_key": "draft",
                    "status_label": "新草稿",
                    "schedule_summary": "保存后生成",
                    "next_run_text": "保存后生成",
                    "last_result_text": "尚未保存",
                    "last_error": "",
                    "session_key": "",
                    "is_draft": True,
                },
                *rows,
            ]
        self._tasks_model.reset_rows(rows)

    @Property(QObject, constant=True)
    def tasksModel(self) -> QObject:
        return self._tasks_model

    @Property(int, constant=True)
    def totalTaskCount(self) -> int:
        return len(self._tasks) + (1 if self.editingNewTask else 0)

    @Property(int, constant=True)
    def visibleTaskCount(self) -> int:
        return self._tasks_model.rowCount()

    @Property(str, notify=selectedTaskChanged)
    def activeListItemId(self) -> str:
        return "__draft__" if self.editingNewTask else self._selected_task_id

    @Property(str, notify=selectedTaskChanged)
    def selectedTaskId(self) -> str:
        return self._selected_task_id

    @Property(bool, notify=selectedTaskChanged)
    def hasSelection(self) -> bool:
        return bool(self._selected_task_id)

    @Property(dict, notify=selectedTaskChanged)
    def selectedTask(self) -> dict[str, object]:
        for task in self._tasks:
            if task["id"] == self._selected_task_id:
                return dict(task)
        return {}

    @Property(dict, notify=draftChanged)
    def draft(self) -> dict[str, object]:
        return dict(self._draft)

    @Property(bool, notify=draftChanged)
    def hasDraft(self) -> bool:
        return bool(self._draft.get("id") or self._draft_dirty or self._draft.get("name"))

    @Property(bool, notify=draftChanged)
    def editingNewTask(self) -> bool:
        return self.hasDraft and not bool(self._draft.get("id"))

    @Property(bool, notify=draftChanged)
    def draftDirty(self) -> bool:
        return self._draft_dirty

    @Property(bool, notify=busyChanged)
    def busy(self) -> bool:
        return self._busy

    @Property(str, notify=errorChanged)
    def lastError(self) -> str:
        return ""

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
    def currentProfileName(self) -> str:
        return self._current_profile_name

    @Property(bool, notify=executionStateChanged)
    def canRunSelectedNow(self) -> bool:
        return True

    @Property(str, notify=executionStateChanged)
    def runNowBlockedReason(self) -> str:
        return ""

    @Slot()
    def refresh(self) -> None:
        return None

    @Slot(str)
    def selectTask(self, task_id: str) -> None:
        self._selected_task_id = task_id
        self._draft = self.selectedTask
        self._draft_dirty = False
        self.selectedTaskChanged.emit()
        self.draftChanged.emit()

    @Slot()
    def newDraft(self) -> None:
        self._selected_task_id = ""
        self._draft = {
            "id": "",
            "name": "",
            "enabled": True,
            "schedule_kind": "every",
            "every_minutes": "60",
            "message": "",
            "deliver": False,
            "channel": "",
            "target": "",
            "delete_after_run": False,
        }
        self._draft_dirty = True
        self._sync_rows()
        self.selectedTaskChanged.emit()
        self.draftChanged.emit()

    @Slot()
    def duplicateSelected(self) -> None:
        return None

    @Slot(str, "QVariant")
    def updateDraftField(self, path: str, value: object) -> None:
        _ = (path, value)

    @Slot(str)
    def setFilterQuery(self, query: str) -> None:
        self._filter_query = query
        self.filtersChanged.emit()

    @Slot(str)
    def setStatusFilter(self, value: str) -> None:
        self._status_filter = value
        self.filtersChanged.emit()

    @Slot()
    def saveDraft(self) -> None:
        return None

    @Slot()
    def deleteSelected(self) -> None:
        return None

    @Slot(bool)
    def setSelectedEnabled(self, enabled: bool) -> None:
        _ = enabled

    @Slot()
    def runSelectedNow(self) -> None:
        return None

    @Slot()
    def openSelectedSession(self) -> None:
        return None


class DummyHeartbeatService(QObject):
    stateChanged = Signal()
    busyChanged = Signal(bool)
    noticeChanged = Signal(str, bool)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._busy = False
        self._notice_text = ""
        self._notice_success = True
        self.refresh_calls = 0
        self.run_calls = 0
        self.open_calls = 0
        self.open_file_calls = 0

    @Property(bool, notify=stateChanged)
    def heartbeatFileExists(self) -> bool:
        return True

    @Property(str, notify=stateChanged)
    def heartbeatPreview(self) -> str:
        return "Review inbox and triage follow-ups"

    @Property(bool, notify=busyChanged)
    def busy(self) -> bool:
        return self._busy

    @Property(bool, notify=stateChanged)
    def canRunNow(self) -> bool:
        return True

    @Property(str, notify=stateChanged)
    def intervalText(self) -> str:
        return "Every 15m"

    @Property(str, notify=stateChanged)
    def lastCheckedText(self) -> str:
        return "2026-03-12 11:20"

    @Property(str, notify=stateChanged)
    def lastDecisionLabel(self) -> str:
        return "Nothing to do"

    @Property(str, notify=stateChanged)
    def runNowBlockedReason(self) -> str:
        return ""

    @Property(str, notify=stateChanged)
    def lastError(self) -> str:
        return ""

    @Property(str, notify=noticeChanged)
    def noticeText(self) -> str:
        return self._notice_text

    @Property(bool, notify=noticeChanged)
    def noticeSuccess(self) -> bool:
        return self._notice_success

    @Slot()
    def refresh(self) -> None:
        self.refresh_calls += 1

    @Slot()
    def runNow(self) -> None:
        self.run_calls += 1

    @Slot()
    def openHeartbeatSession(self) -> None:
        self.open_calls += 1

    @Slot()
    def openHeartbeatFile(self) -> None:
        self.open_file_calls += 1

__all__ = [name for name in globals() if name != "__all__" and not (name.startswith("__") and name.endswith("__"))]
