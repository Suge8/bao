from __future__ import annotations

import asyncio
import functools
from typing import Any

from app.backend.asyncio_runner import AsyncioRunner
from bao.cron.service import CronService
from bao.cron.types import CronSchedule

from ._cron_common import (
    _normalized_store_path,
    _parse_at_input,
    _serialize_job,
    _tr,
)


class CronBridgeRuntimeMixin:
    def _submit_safe(self, coro: Any) -> Any:
        try:
            return self._runner.submit(coro)
        except RuntimeError:
            close = getattr(coro, "close", None)
            if callable(close):
                close()
            self._set_error("Async runner unavailable")
            return None

    async def _run_user_io(self, fn: Any, *args: Any, **kwargs: Any) -> Any:
        call = functools.partial(fn, *args, **kwargs)
        if isinstance(self._runner, AsyncioRunner):
            return await self._runner.run_user_io(call)
        return await asyncio.to_thread(call)

    def _local_store_path(self) -> str:
        return _normalized_store_path(getattr(self._local_cron, "store_path", None))

    def _live_store_path(self) -> str:
        return _normalized_store_path(
            getattr(self._live_cron, "store_path", None) if self._live_cron is not None else None
        )

    def _live_matches_current_profile(self) -> bool:
        return self._live_cron is not None and self._live_store_path() == self._local_store_path()

    def _effective_service(self) -> CronService:
        return self._live_cron if self._live_matches_current_profile() else self._local_cron

    def _run_now_state(self) -> tuple[bool, str]:
        if not self._current_saved_task_id():
            return False, ""
        if not self._hub_running or self._live_cron is None:
            return False, _tr(self._lang, "请先启动中枢，再立即执行任务", "Start the hub to run a task now")
        if not self._live_matches_current_profile():
            return False, _tr(self._lang, "正在切换到当前 profile，请稍后再试", "Switching to the current profile. Try again in a moment")
        return True, ""

    async def _load_tasks(self) -> list[dict[str, Any]]:
        jobs = await self._run_user_io(self._effective_service().list_jobs, True)
        return [_serialize_job(job, self._lang) for job in jobs]

    async def _save_draft(self) -> tuple[str, str]:
        service = self._effective_service()
        draft = dict(self._draft)
        name = str(draft.get("name", "")).strip()
        if not name:
            raise ValueError(_tr(self._lang, "任务名称不能为空", "Task name is required"))
        message = str(draft.get("message", "")).strip()
        if not message:
            raise ValueError(_tr(self._lang, "消息内容不能为空", "Message is required"))
        deliver = bool(draft.get("deliver", False))
        channel = str(draft.get("channel", "")).strip() or None
        target = str(draft.get("target", "")).strip() or None
        if deliver and (not channel or not target):
            raise ValueError(_tr(self._lang, "投递模式必须同时填写渠道和目标", "Delivery requires both channel and target"))
        schedule = self._schedule_from_draft(draft)
        task_id = str(draft.get("id", "")).strip()
        enabled = bool(draft.get("enabled", True))
        delete_after_run = bool(draft.get("delete_after_run", False))
        if task_id:
            job = await self._run_user_io(
                service.update_job,
                task_id,
                name=name,
                enabled=enabled,
                schedule=schedule,
                message=message,
                deliver=deliver,
                channel=channel,
                to=target,
                delete_after_run=delete_after_run,
            )
            if job is None:
                raise ValueError(_tr(self._lang, "任务不存在", "Task not found"))
            return job.id, _tr(self._lang, "任务已更新", "Task updated")
        job = await self._run_user_io(
            service.add_job,
            name,
            schedule,
            message,
            enabled,
            deliver,
            channel,
            target,
            delete_after_run,
        )
        return job.id, _tr(self._lang, "任务已创建", "Task created")

    async def _delete_task(self, task_id: str) -> tuple[str, bool]:
        removed = await self._run_user_io(self._effective_service().remove_job, task_id)
        return task_id, bool(removed)

    async def _toggle_task(self, task_id: str, enabled: bool) -> tuple[str, bool]:
        job = await self._run_user_io(self._effective_service().enable_job, task_id, enabled)
        return task_id, job is not None

    async def _run_task_now(self, task_id: str) -> bool:
        ok, blocked_reason = self._run_now_state()
        if not ok:
            raise ValueError(blocked_reason)
        return await self._live_cron.run_job(task_id, force=True)

    def _schedule_from_draft(self, draft: dict[str, Any]) -> CronSchedule:
        kind = str(draft.get("schedule_kind", "every") or "every")
        if kind == "at":
            at_value = _parse_at_input(str(draft.get("at_input", "")))
            if not at_value:
                raise ValueError(_tr(self._lang, "单次任务必须填写执行时间", "One-shot tasks need a date and time"))
            return CronSchedule(kind="at", at_ms=at_value)
        if kind == "every":
            minutes_raw = str(draft.get("every_minutes", "")).strip()
            try:
                minutes = int(minutes_raw)
            except ValueError as exc:
                raise ValueError(_tr(self._lang, "循环间隔必须是整数分钟", "Repeat interval must be a whole number of minutes")) from exc
            if minutes <= 0:
                raise ValueError(_tr(self._lang, "循环间隔必须大于 0", "Repeat interval must be greater than zero"))
            return CronSchedule(kind="every", every_ms=minutes * 60_000)
        if kind == "cron":
            expr = str(draft.get("cron_expr", "")).strip()
            if not expr:
                raise ValueError(_tr(self._lang, "Cron 表达式不能为空", "Cron expression is required"))
            tz = str(draft.get("timezone", "")).strip() or None
            return CronSchedule(kind="cron", expr=expr, tz=tz)
        raise ValueError(_tr(self._lang, "不支持的调度类型", "Unsupported schedule type"))
