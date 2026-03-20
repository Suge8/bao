from __future__ import annotations

import asyncio
from typing import Any

from loguru import logger

from app.backend.asyncio_runner import AsyncioRunner
from bao.hub import HubRunningStateRequest, HubSeenRequest

from ._hub_common import _normalize_hub_channels, _now_iso
from ._hub_history_common import _DEBUG_SWITCH


class ChatServiceStateMixin:
    def supervisorHubSnapshot(self) -> dict[str, Any]:
        return {
            "state": self.hubState, "detail": self.hubDetail, "error": self.lastError,
            "detail_is_error": self.hubDetailIsError, "channels": self.hubChannels,
            "startup_activity": self.startupActivity,
        }

    def _set_state(self, state: str) -> None:
        if self._state == state:
            return
        self._state = state
        self.stateChanged.emit(state)
        self.viewPhaseChanged.emit(self._compute_view_phase())
        self._refresh_hub_channels()

    def _cancel_history_future(self) -> None:
        future = self._history_future
        self._history_future = None
        if future is None:
            return
        try:
            future.cancel()
        except Exception:
            pass

    async def _run_user_io(self, fn: Any, *args: Any) -> Any:
        if isinstance(self._runner, AsyncioRunner):
            return await self._runner.run_user_io(fn, *args)
        return await asyncio.to_thread(fn, *args)

    async def _run_bg_io(self, fn: Any, *args: Any) -> Any:
        if isinstance(self._runner, AsyncioRunner):
            return await self._runner.run_bg_io(fn, *args)
        return await asyncio.to_thread(fn, *args)

    def _set_history_loading(self, loading: bool) -> None:
        if self._history_loading == loading:
            return
        self._history_loading = loading
        if _DEBUG_SWITCH:
            logger.debug(
                "history_loading key={} desired={} loading={} rows={}",
                self._session_key,
                self._desired_session_key,
                loading,
                self._model.rowCount(),
            )
        self.historyLoadingChanged.emit(loading)
        self.viewPhaseChanged.emit(self._compute_view_phase())

    def _set_error(self, msg: str) -> None:
        message = msg.strip()
        self._set_hub_detail(message, error=message)
        self._set_state("error")

    def _set_startup_activity(self, patch: dict[str, Any]) -> None:
        next_patch = {str(key): value for key, value in patch.items() if str(key)}
        if not next_patch:
            return
        next_value = dict(self._startup_activity)
        changed = False
        for key, value in next_patch.items():
            if next_value.get(key) == value:
                continue
            next_value[key] = value
            changed = True
        if not changed:
            return
        status = str(next_value.get("status", "") or "").strip()
        if not status:
            self._clear_startup_activity()
            return
        next_value["kind"] = str(next_value.get("kind", "") or "startup_greeting")
        next_value["status"] = status
        next_value["sessionKey"] = self._normalized_startup_key(next_value, "sessionKey")
        next_value["sessionKeys"] = self._merged_startup_keys(next_value, "sessionKeys", "sessionKey")
        next_value["channelKeys"] = self._merged_startup_keys(next_value, "channelKeys", "channelKey")
        next_value["content"] = str(next_value.get("content", "") or "")
        next_value["error"] = str(next_value.get("error", "") or "")
        next_value.pop("channelKey", None)
        next_value["updatedAt"] = _now_iso()
        if self._startup_activity == next_value:
            return
        self._startup_activity = next_value
        self.startupActivityChanged.emit()

    def _merged_startup_keys(self, next_value: dict[str, Any], list_key: str, single_key: str) -> list[str]:
        current = [
            str(value).strip()
            for value in self._startup_activity.get(list_key, [])
            if str(value).strip()
        ]
        for key in next_value.get(list_key, []) or []:
            text = str(key).strip()
            if text and text not in current:
                current.append(text)
        single_value = self._normalized_startup_key(next_value, single_key)
        if single_value and single_value not in current:
            current.append(single_value)
        return current

    @staticmethod
    def _normalized_startup_key(values: dict[str, Any], key: str) -> str:
        return str(values.get(key, "") or "").strip()

    def _clear_startup_activity(self) -> None:
        if not self._startup_activity:
            return
        self._startup_activity = {}
        self.startupActivityChanged.emit()

    def _clear_running_startup_activity(self) -> None:
        if str(self._startup_activity.get("status", "") or "") != "running":
            return
        self._clear_startup_activity()

    def _set_hub_detail(self, detail: str, *, error: str = "") -> None:
        detail = detail.strip()
        error = error.strip()
        if self._hub_detail == detail and self._last_error == error:
            return
        detail_changed = self._hub_detail != detail
        error_changed = self._last_error != error
        self._hub_detail = detail
        self._last_error = error
        if error_changed:
            self.errorChanged.emit(error)
        if detail_changed:
            self.hubDetailChanged.emit(detail)

    def _set_hub_summary(self, summary: str) -> None:
        self._set_hub_detail(summary)

    def _clear_hub_detail(self) -> None:
        self._set_hub_detail("")

    def _refresh_hub_channels(self) -> None:
        channels = self._build_hub_channels_projection()
        if self._hub_channels == channels:
            return
        self._hub_channels = channels
        self.hubChannelsChanged.emit()

    def _project_hub_state(self) -> str:
        if self._state == "running":
            return "running"
        if self._state == "starting":
            return "starting"
        if self._state == "error":
            return "error"
        return "idle"

    def _set_session_running(self, key: str, is_running: bool, *, emit_change: bool = True) -> None:
        runtime = self._current_hub_runtime()
        if not key or runtime is None:
            return
        self._run_runtime_port_op(
            lambda: runtime.set_session_running(
                HubRunningStateRequest(
                    session_key=key,
                    is_running=bool(is_running),
                    emit_change=emit_change,
                )
            ),
            debug_action="session running update",
            key=key,
        )

    def _build_hub_channels_projection(self) -> list[dict[str, Any]]:
        base_channels = self._enabled_hub_channels or self._configured_hub_channels
        ordered = _normalize_hub_channels(base_channels + list(self._channel_errors.keys()))
        if not ordered:
            return []
        default_state = self._project_hub_state()
        if default_state == "error":
            default_state = "idle"
        return [
            {
                "channel": channel,
                "state": "error" if self._channel_errors.get(channel, "") else default_state,
                "detail": self._channel_errors.get(channel, ""),
            }
            for channel in ordered
        ]

    def _mark_session_seen_ai(
        self, key: str, *, emit_change: bool = False, extra_updates: dict[str, Any] | None = None
    ) -> None:
        runtime = self._current_hub_runtime()
        if not key or runtime is None:
            return
        metadata_updates, clear_running = self._seen_metadata_updates(extra_updates)
        self._run_runtime_port_op(
            lambda: runtime.mark_seen(
                HubSeenRequest(
                    session_key=key,
                    emit_change=emit_change,
                    metadata_updates=metadata_updates,
                    clear_running=clear_running,
                )
            ),
            debug_action="desktop seen update",
            key=key,
        )

    @staticmethod
    def _seen_metadata_updates(extra_updates: dict[str, Any] | None) -> tuple[dict[str, Any], bool]:
        metadata_updates: dict[str, Any] = {}
        clear_running = False
        if not isinstance(extra_updates, dict):
            return metadata_updates, clear_running
        for field, value in extra_updates.items():
            if field == "session_running":
                clear_running = clear_running or value is False
                continue
            metadata_updates[field] = value
        return metadata_updates, clear_running

    def _run_runtime_port_op(self, op: Any, *, debug_action: str, key: str) -> None:
        if isinstance(self._runner, AsyncioRunner):
            try:
                future = self._runner.submit(self._run_bg_io(op))
                future.add_done_callback(self._on_metadata_update_done)
                return
            except RuntimeError:
                pass
            except Exception as exc:
                logger.debug("Skip {} {}: {}", debug_action, key, exc)
        try:
            op()
        except Exception as exc:
            logger.debug("Skip {} {}: {}", debug_action, key, exc)

    @staticmethod
    def _on_metadata_update_done(future: Any) -> None:
        try:
            future.result()
        except Exception as exc:
            logger.debug("Skip metadata update: {}", exc)
