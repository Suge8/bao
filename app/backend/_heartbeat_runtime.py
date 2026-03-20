from __future__ import annotations

import asyncio
import functools
from pathlib import Path
from typing import Any

from app.backend.asyncio_runner import AsyncioRunner
from bao.config.onboarding import infer_language, write_heartbeat
from bao.heartbeat.service import HeartbeatService

from ._heartbeat_common import (
    _format_timestamp,
    _heartbeat_preview,
    _normalized_path,
    _tr,
)


class HeartbeatBridgeRuntimeMixin:
    def _submit_safe(self, coro: Any) -> Any:
        try:
            return self._runner.submit(coro)
        except RuntimeError:
            close = getattr(coro, "close", None)
            if callable(close):
                close()
            self._set_notice("Async runner unavailable", False)
            return None

    async def _run_user_io(self, fn: Any, *args: Any, **kwargs: Any) -> Any:
        call = functools.partial(fn, *args, **kwargs)
        if isinstance(self._runner, AsyncioRunner):
            return await self._runner.run_user_io(call)
        return await asyncio.to_thread(call)

    def _heartbeat_workspace(self) -> Path:
        return self._local_heartbeat_file.parent

    def _heartbeat_lang(self, workspace: Path) -> str:
        if (workspace / "INSTRUCTIONS.md").exists():
            return infer_language(workspace)
        return self._lang

    def _ensure_local_heartbeat_file(self) -> Path:
        workspace = self._heartbeat_workspace()
        workspace.mkdir(parents=True, exist_ok=True)
        if not self._local_heartbeat_file.exists():
            write_heartbeat(workspace, self._heartbeat_lang(workspace))
        if not self._local_heartbeat_file.exists():
            raise FileNotFoundError("HEARTBEAT.md not created")
        return self._local_heartbeat_file

    def _file_matches_current_profile(self, service: HeartbeatService | None) -> bool:
        if service is None:
            return False
        return _normalized_path(service.heartbeat_file) == _normalized_path(self._local_heartbeat_file)

    def _effective_live(self) -> HeartbeatService | None:
        return self._live_heartbeat if self._file_matches_current_profile(self._live_heartbeat) else None

    def _missing_file_reason(self) -> str:
        return _tr(
            self._lang,
            "还没有设置自动检查说明，先补充你希望 Bao 定期查看的事项",
            "Set up automatic check instructions before running this check",
        )

    def _hub_not_ready_reason(self) -> str:
        return _tr(
            self._lang,
            "请先启动当前空间的网关，再开始自动检查",
            "Start the hub for this space before running an automatic check",
        )

    def _switching_profile_reason(self) -> str:
        return _tr(
            self._lang,
            "正在切换到当前空间，请稍后再试",
            "Switching to the current space. Try again in a moment",
        )

    def _run_notice(self, decision: str, response: str | None) -> tuple[bool, str]:
        if decision == "missing":
            return False, self._missing_file_reason()
        if decision == "skip":
            return True, _tr(self._lang, "这次检查没有发现需要 Bao 处理的新任务", "No new tasks found")
        if decision == "run" and isinstance(response, str) and response.strip():
            return True, _tr(self._lang, "已开始处理这次检查发现的任务", "Tasks from this check are now running")
        return True, _tr(self._lang, "自动检查已完成", "Automatic check completed")

    def _run_now_state(self) -> tuple[bool, str]:
        if not self._local_heartbeat_file.exists():
            return False, self._missing_file_reason()
        live = self._effective_live()
        if self._live_heartbeat is not None and live is None:
            return False, self._switching_profile_reason()
        if not self._hub_running or live is None:
            return False, self._hub_not_ready_reason()
        return True, ""

    def _empty_snapshot(self) -> dict[str, Any]:
        return {
            "heartbeat_file": str(self._local_heartbeat_file),
            "heartbeat_file_exists": False,
            "heartbeat_preview": "",
            "enabled": False,
            "interval_text": "",
            "last_checked_text": "",
            "last_decision_label": "",
            "last_error": "",
        }

    def _decision_label(self, value: str) -> str:
        if value == "run":
            return _tr(self._lang, "发现任务", "Tasks found")
        if value == "skip":
            return _tr(self._lang, "无需执行", "Nothing to do")
        if value == "missing":
            return _tr(self._lang, "缺少 HEARTBEAT.md", "Missing HEARTBEAT.md")
        return ""

    def _interval_text(self, interval_s: int | None) -> str:
        seconds = int(interval_s or 0)
        if seconds <= 0:
            return ""
        minutes, remainder = divmod(seconds, 60)
        if remainder == 0 and minutes > 0:
            if minutes < 60:
                return _tr(self._lang, f"每 {minutes} 分钟", f"Every {minutes}m")
            hours, minutes = divmod(minutes, 60)
            if minutes == 0:
                return _tr(self._lang, f"每 {hours} 小时", f"Every {hours}h")
            return _tr(self._lang, f"每 {hours} 小时 {minutes} 分钟", f"Every {hours}h {minutes}m")
        return _tr(self._lang, f"每 {seconds} 秒", f"Every {seconds}s")

    async def _refresh_snapshot(self) -> dict[str, Any]:
        heartbeat_file = self._local_heartbeat_file
        content = ""
        if heartbeat_file.exists():
            content = await self._run_user_io(heartbeat_file.read_text, encoding="utf-8")
        live = self._effective_live()
        status = live.status() if live is not None else {}
        return {
            "heartbeat_file": str(heartbeat_file),
            "heartbeat_file_exists": heartbeat_file.exists(),
            "heartbeat_preview": _heartbeat_preview(content),
            "enabled": bool(status.get("enabled", False)),
            "interval_text": self._interval_text(status.get("interval_s")),
            "last_checked_text": _format_timestamp(status.get("last_checked_at_ms")),
            "last_decision_label": self._decision_label(str(status.get("last_decision", ""))),
            "last_error": str(status.get("last_error", "") or ""),
        }

    async def _run_now(self) -> tuple[bool, str]:
        ok, blocked_reason = self._run_now_state()
        if not ok:
            return False, blocked_reason
        live = self._effective_live()
        assert live is not None
        response = await live.trigger_now()
        status = live.status()
        last_error = str(status.get("last_error", "") or "").strip()
        if last_error:
            return False, last_error
        return self._run_notice(str(status.get("last_decision", "") or "").strip(), response)

    def _set_busy(self, busy: bool) -> None:
        if self._busy == busy:
            return
        self._busy = busy
        self.busyChanged.emit(busy)

    def _set_notice(self, message: str, ok: bool) -> None:
        self._notice_text = message.strip()
        self._notice_success = ok
        self.noticeChanged.emit(self._notice_text, ok)

    def _on_refresh_done(self, future: Any) -> None:
        if future.cancelled():
            return
        exc = future.exception()
        if exc is not None:
            self._refreshResult.emit(self._empty_snapshot())
            self._set_notice(str(exc), False)
            return
        self._refreshResult.emit(future.result())

    def _handle_refresh_result(self, payload: object) -> None:
        self._snapshot = dict(payload) if isinstance(payload, dict) else self._empty_snapshot()
        self.stateChanged.emit()

    def _on_run_done(self, future: Any) -> None:
        self._set_busy(False)
        if future.cancelled():
            return
        exc = future.exception()
        if exc is not None:
            self._runResult.emit(False, str(exc))
            return
        ok, message = future.result()
        self._runResult.emit(ok, message)

    def _handle_run_result(self, ok: bool, message: str) -> None:
        self._set_notice(message, ok)
        self.refresh()
