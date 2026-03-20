from __future__ import annotations

import copy
from typing import Any

from PySide6.QtCore import Slot

from bao.profile import ProfileContext

from ._hub_common import (
    _CHANNEL_ERROR_LABELS,
    _normalize_hub_channels,
    _session_manager_root,
    _target_session_root,
)
from ._hub_runtime_cache import (
    cache_session_manager,
    remove_cached_session_manager,
    reuse_cached_session_manager,
)
from ._hub_runtime_dispatcher import (
    sync_dispatcher_after_request,
    sync_dispatcher_profile_context,
    sync_dispatcher_runtime_state,
)
from ._hub_runtime_lifecycle import (
    cancel_lifecycle_future,
    clear_runtime_handles,
    has_runtime_handles,
    lifecycle_in_progress,
    maybe_restart_after_lifecycle,
    submit_shutdown_if_needed,
)
from ._hub_runtime_startup import init_hub_stack


class ChatServiceRuntimeMixin:
    @Slot("QVariant")
    def setConfigData(self, data: object) -> None:
        self._config_data = copy.deepcopy(data) if isinstance(data, dict) else None

    @Slot("QVariant")
    def setProfileContext(self, data: object) -> None:
        next_data = copy.deepcopy(data) if isinstance(data, dict) else None
        if self._profile_context_data == next_data:
            return
        self._profile_context_data = next_data
        self._startup_pending = []
        self._startup_target_key = ""
        self._clear_startup_activity()
        self._sync_dispatcher_profile_context()

    @Slot()
    def start(self) -> None:
        if self._state in ("starting", "running"):
            return
        if lifecycle_in_progress(self):
            self._restart_requested = True
            return
        self._restart_requested = False
        self._channel_errors.clear()
        self._clear_hub_detail()
        self._set_startup_activity(
            {
                "kind": "startup_greeting",
                "status": "running",
                "sessionKey": self._default_startup_session_key(),
                "sessionKeys": [],
                "channelKeys": [],
                "content": "",
                "error": "",
            }
        )
        self._set_state("starting")
        self._refresh_hub_channels()
        self._runner.start()
        self._lifecycle_request_id += 1
        request_id = self._lifecycle_request_id
        future = self._runner.submit(self._init_hub())
        self._init_future = future
        future.add_done_callback(
            lambda future, rid=request_id: self._on_init_done(rid, future)
        )

    @Slot()
    def stop(self) -> None:
        self._stop(restart_after_stop=False)

    @Slot()
    def restart(self) -> None:
        if self._state == "stopped" and not lifecycle_in_progress(self) and not has_runtime_handles(self):
            self.start()
            return
        self._stop(restart_after_stop=True)

    def _stop(self, *, restart_after_stop: bool) -> None:
        if (
            self._state == "stopped"
            and not lifecycle_in_progress(self)
            and not has_runtime_handles(self)
        ):
            if restart_after_stop:
                self.start()
            return
        self._restart_requested = restart_after_stop
        if self._state == "stopped":
            cancelled_init = cancel_lifecycle_future(self._init_future)
            submitted_shutdown = submit_shutdown_if_needed(self)
            if not cancelled_init and not submitted_shutdown and not lifecycle_in_progress(self):
                maybe_restart_after_lifecycle(self)
            return
        self._channel_errors.clear()
        self._enabled_hub_channels = []
        self._clear_hub_detail()
        self._clear_running_startup_activity()
        if self._cron is not None:
            self._cron = None
            self.cronServiceChanged.emit(None)
        if self._heartbeat is not None:
            self._heartbeat = None
            self.heartbeatServiceChanged.emit(None)
        self._lifecycle_request_id += 1
        self._set_state("stopped")
        self._refresh_hub_channels()
        cancelled_init = cancel_lifecycle_future(self._init_future)
        submitted_shutdown = submit_shutdown_if_needed(self)
        if not cancelled_init and not submitted_shutdown and not lifecycle_in_progress(self):
            maybe_restart_after_lifecycle(self)

    @Slot(object)
    def setFallbackHubPorts(self, hub_local_ports: Any) -> None:
        previous = self._hub_access.local_ports()
        if previous is hub_local_ports:
            return
        previous_runtime = self._hub_access.local_runtime()
        previous_manager = getattr(previous_runtime, "session_manager", None)
        previous_root = _session_manager_root(previous_manager)
        next_runtime = getattr(hub_local_ports, "runtime", None)
        next_manager = getattr(next_runtime, "session_manager", None)
        next_root = _session_manager_root(next_manager)
        if previous_manager is not None and previous_root is not None and previous_root != next_root:
            cache_session_manager(self._hot_session_managers, previous_manager)
        self._history_cache.clear()
        self._set_active_session_state(False, False)
        self._hub_access.set_local_ports(hub_local_ports)
        remove_cached_session_manager(self._hot_session_managers, next_manager)
        self._sync_hub_bindings()

    def _sync_dispatcher_profile_context(self) -> None:
        sync_dispatcher_profile_context(self)

    def _sync_dispatcher_after_request(self, profile_id: str) -> None:
        sync_dispatcher_after_request(self, profile_id)

    def _sync_dispatcher_runtime_state(
        self,
        *,
        update_hub_bindings: bool,
        emit_hub_ready: bool,
    ) -> None:
        sync_dispatcher_runtime_state(
            self,
            update_hub_bindings=update_hub_bindings,
            emit_hub_ready=emit_hub_ready,
        )

    async def _init_hub(self) -> tuple[Any, list[str]]:
        return await init_hub_stack(self)

    def _reusable_session_manager(
        self,
        config: Any,
        profile_context: ProfileContext | None,
    ) -> Any:
        expected_root = _target_session_root(config, profile_context)
        active_runtime = self._current_hub_runtime()
        active_manager = getattr(active_runtime, "session_manager", None)
        if _session_manager_root(active_manager) == expected_root:
            return active_manager
        return reuse_cached_session_manager(self._hot_session_managers, expected_root)

    def _handle_channel_error(self, stage: str, name: str, detail: str) -> None:
        error_message = self._format_channel_error(stage, name, detail)
        self._channel_errors[name] = detail
        self._refresh_hub_channels()
        self._controlPlaneError.emit(error_message)

    def _handle_control_plane_error(self, message: str) -> None:
        self._set_hub_detail(message, error=message)

    def _format_channel_error(self, stage: str, name: str, detail: str) -> str:
        is_zh = self._lang == "zh"
        zh_label, en_label = _CHANNEL_ERROR_LABELS.get(stage, ("通道错误", "Channel error"))
        prefix = zh_label if is_zh else en_label
        return f"⚠ {prefix}: {name}: {detail}"

    def _on_init_done(self, request_id: int, future: Any) -> None:
        if self._init_future is future:
            self._init_future = None
        if future.cancelled():
            maybe_restart_after_lifecycle(self)
            return
        try:
            session_manager, channels = future.result()
        except Exception as exc:
            if request_id != self._lifecycle_request_id:
                submitted_shutdown = submit_shutdown_if_needed(self)
                if not submitted_shutdown and not lifecycle_in_progress(self):
                    clear_runtime_handles(self)
                    maybe_restart_after_lifecycle(self)
                return
            self._initResult.emit(request_id, False, f"Hub init failed: {exc}", None, [])
            return
        if request_id != self._lifecycle_request_id:
            submitted_shutdown = submit_shutdown_if_needed(self)
            if not submitted_shutdown and not lifecycle_in_progress(self):
                clear_runtime_handles(self)
                maybe_restart_after_lifecycle(self)
            return
        self._initResult.emit(request_id, True, "", session_manager, channels)

    def _handle_init_result(self, request_id: int, ok: bool, *args: Any) -> None:
        error_msg = str(args[0] or "") if len(args) > 0 else ""
        channels = args[2] if len(args) > 2 and isinstance(args[2], list) else []
        if request_id != self._lifecycle_request_id:
            return
        if not ok:
            self._clear_running_startup_activity()
            self._set_error(error_msg)
            return
        self._set_state("running")
        self._enabled_hub_channels = _normalize_hub_channels(channels)
        self._refresh_hub_channels()
        self._finish_hub_startup(channels)

    def _finish_hub_startup(self, channels: list[str]) -> None:
        if not self._last_error:
            self._set_hub_summary(self._hub_started_summary(channels))
        self._sync_dispatcher_runtime_state(update_hub_bindings=True, emit_hub_ready=False)
        self.hubReady.emit()
        self._drain_queue()

    def _hub_started_summary(self, channels: list[str]) -> str:
        is_zh = self._lang == "zh"
        parts = ["✓ 中枢已启动" if is_zh else "✓ Hub started"]
        if channels:
            parts.append(f"{'通道' if is_zh else 'channels'}: {', '.join(channels)}")
        cron_jobs = self._cron_status.get("jobs", 0)
        if cron_jobs > 0:
            label = "定时任务" if is_zh else "cron"
            parts.append(f"{label}: {cron_jobs} {'个' if is_zh else 'jobs'}")
        interval_s = int(getattr(self._heartbeat, "interval_s", 30 * 60) or 30 * 60)
        minutes = max(1, interval_s // 60)
        parts.append(f"心跳: 每 {minutes} 分钟" if is_zh else f"heartbeat: every {minutes}m")
        return " — ".join(parts)

    async def _shutdown_hub(self) -> None:
        self._cancel_history_future()
        for task in self._background_tasks:
            task.cancel()
        if self._dispatcher is not None:
            await self._dispatcher.close_mcp()
            self._dispatcher.stop()
        elif self._agent:
            await self._agent.close_mcp()
            self._agent.stop()
        if self._channels:
            await self._channels.stop_all()

    def handle_session_deleted(self, key: str, success: bool, _error: str) -> None:
        if not success:
            return
        if key != self._active_streaming_session_key or not self._active_send_future:
            return
        try:
            self._active_send_future.cancel()
        except Exception:
            pass
