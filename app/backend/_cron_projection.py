from __future__ import annotations

from typing import Any

from ._cron_common import _draft_from_task, _draft_preview_task, _empty_draft, _tr


class CronBridgeProjectionMixin:
    def _selected_task(self) -> dict[str, Any] | None:
        for task in self._all_tasks:
            if str(task.get("id", "")) == self._selected_task_id:
                return task
        return None

    def _draft_id(self) -> str:
        return str(self._draft.get("id", "")).strip()

    def _current_saved_task_id(self) -> str:
        draft_id = self._draft_id()
        return draft_id or self._selected_task_id

    def _current_saved_task(self) -> dict[str, Any] | None:
        task_id = self._current_saved_task_id()
        for task in self._all_tasks:
            if str(task.get("id", "")) == task_id:
                return task
        return None

    def _first_saved_task(self) -> dict[str, Any] | None:
        return self._all_tasks[0] if self._all_tasks else None

    def _matches_filter(self, task: dict[str, Any]) -> bool:
        query = self._filter_query.lower()
        if query:
            haystack = " ".join(
                [
                    str(task.get("name", "")),
                    str(task.get("schedule_summary", "")),
                    str(task.get("message", "")),
                    str(task.get("channel", "")),
                    str(task.get("target", "")),
                ]
            ).lower()
            if query not in haystack:
                return False
        status_filter = self._status_filter
        if status_filter == "all":
            return True
        if status_filter == "enabled":
            return bool(task.get("enabled", False))
        if status_filter == "disabled":
            return not bool(task.get("enabled", False))
        if status_filter == "issues":
            return str(task.get("status_key", "")) == "error"
        if status_filter == "scheduled":
            return str(task.get("status_key", "")) == "scheduled"
        return True

    def _apply_projection(self) -> None:
        if not self.editingNewTask:
            current_task = self._current_saved_task() or self._first_saved_task()
            self._selected_task_id = str(current_task.get("id", "")) if current_task else ""
            if current_task is not None and self._draft_id() != str(current_task.get("id", "")):
                self._draft = _draft_from_task(current_task)
                self._draft_dirty = False
        projected = [task for task in self._all_tasks if self._matches_filter(task)]
        if self.editingNewTask:
            projected = [_draft_preview_task(self._draft, self._lang), *projected]
        projected_changed = projected != self._projected_tasks
        self._projected_tasks = projected
        self._tasks_model.sync_rows(self._projected_tasks)
        self.tasksChanged.emit()
        self.filtersChanged.emit()
        self.selectedTaskChanged.emit()
        if projected_changed:
            self.executionStateChanged.emit()

    def _set_busy(self, busy: bool) -> None:
        if self._busy == busy:
            return
        self._busy = busy
        self.busyChanged.emit(busy)

    def _set_error(self, message: str) -> None:
        text = message.strip()
        if self._last_error == text:
            return
        self._last_error = text
        self.errorChanged.emit(text)

    def _set_notice(self, message: str, ok: bool) -> None:
        self._notice_text = message.strip()
        self._notice_success = ok
        self.noticeChanged.emit(self._notice_text, ok)

    def _on_load_done(self, generation: int, future: Any) -> None:
        if future.cancelled():
            return
        exc = future.exception()
        if exc is not None:
            self._loadResult.emit(False, str(exc), (generation, []))
            return
        self._loadResult.emit(True, "", (generation, future.result()))

    def _handle_load_result(self, ok: bool, error: str, payload: object) -> None:
        generation = -1
        items_payload: object = payload
        if isinstance(payload, tuple) and len(payload) == 2:
            generation, items_payload = payload
        if generation not in {-1, self._load_generation}:
            return
        if not ok:
            self._set_error(error)
            self._set_notice(error, False)
            return
        items = items_payload if isinstance(items_payload, list) else []
        self._all_tasks = [dict(item) for item in items if isinstance(item, dict)]
        if self._selected_task_id and self._selected_task() is None:
            self._selected_task_id = ""
        if not self._selected_task_id and self._all_tasks and not self.editingNewTask:
            self._selected_task_id = str(self._all_tasks[0].get("id", ""))
        current_draft_id = str(self._draft.get("id", "")).strip()
        if self._selected_task_id and (not self._draft_dirty or current_draft_id != self._selected_task_id):
            task = self._selected_task()
            if task is not None:
                self._draft = _draft_from_task(task)
                self._draft_dirty = False
        self._apply_projection()
        self.draftChanged.emit()
        self._set_error("")

    def _on_save_done(self, future: Any) -> None:
        if future.cancelled():
            self._set_busy(False)
            return
        exc = future.exception()
        if exc is not None:
            self._saveResult.emit(False, str(exc), "")
            return
        task_id, message = future.result()
        self._saveResult.emit(True, message, task_id)

    def _handle_save_result(self, ok: bool, error: str, task_id: str) -> None:
        self._set_busy(False)
        if not ok:
            self._set_error(error)
            self._set_notice(error, False)
            return
        self._selected_task_id = task_id
        self._draft_dirty = False
        self.selectedTaskChanged.emit()
        self.executionStateChanged.emit()
        self.draftChanged.emit()
        self._set_error("")
        self._set_notice(error, True)
        self.refresh()

    def _on_delete_done(self, future: Any) -> None:
        if future.cancelled():
            self._set_busy(False)
            return
        exc = future.exception()
        if exc is not None:
            self._deleteResult.emit(False, str(exc), "")
            return
        task_id, removed = future.result()
        if not removed:
            self._deleteResult.emit(False, _tr(self._lang, "任务不存在", "Task not found"), task_id)
            return
        self._deleteResult.emit(True, _tr(self._lang, "任务已删除", "Task deleted"), task_id)

    def _handle_delete_result(self, ok: bool, error: str, task_id: str) -> None:
        self._set_busy(False)
        if not ok:
            self._set_error(error)
            self._set_notice(error, False)
            return
        if self._selected_task_id == task_id:
            self._selected_task_id = ""
            self._draft = _empty_draft()
            self._draft_dirty = False
            self.selectedTaskChanged.emit()
            self.executionStateChanged.emit()
            self.draftChanged.emit()
        self._set_error("")
        self._set_notice(error, True)
        self.refresh()

    def _on_toggle_done(self, future: Any) -> None:
        if future.cancelled():
            self._set_busy(False)
            return
        exc = future.exception()
        if exc is not None:
            self._toggleResult.emit(False, str(exc), "")
            return
        task_id, ok = future.result()
        if not ok:
            self._toggleResult.emit(False, _tr(self._lang, "任务不存在", "Task not found"), task_id)
            return
        self._toggleResult.emit(True, _tr(self._lang, "任务已更新", "Task updated"), task_id)

    def _handle_toggle_result(self, ok: bool, error: str, _task_id: str) -> None:
        self._set_busy(False)
        if not ok:
            self._set_error(error)
            self._set_notice(error, False)
            return
        self._set_error("")
        self._set_notice(error, True)
        self.refresh()

    def _on_run_done(self, future: Any) -> None:
        if future.cancelled():
            self._set_busy(False)
            return
        exc = future.exception()
        if exc is not None:
            self._runResult.emit(False, str(exc))
            return
        ok = bool(future.result())
        self._runResult.emit(
            ok,
            _tr(self._lang, "任务已开始执行", "Task started")
            if ok
            else _tr(self._lang, "任务未能启动", "Task could not be started"),
        )

    def _handle_run_result(self, ok: bool, message: str) -> None:
        self._set_busy(False)
        if not ok:
            self._set_error(message)
            self._set_notice(message, False)
            return
        self._set_error("")
        self._set_notice(message, True)
        self.refresh()
