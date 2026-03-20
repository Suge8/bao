from __future__ import annotations

from PySide6.QtCore import Slot

from bao.hub.builder import DesktopStartupMessage
from bao.session.manager import SessionChangeEvent

from ._hub_types import _QueuedUiMessage


class ChatServiceHistoryStartupMixin:
    @Slot(str)
    def setSessionKey(self, key: str) -> None:
        if key == self._desired_session_key and (
            self._history_initialized or self._history_future is not None
        ):
            return
        self._cancel_history_future()
        self._current_nav_id += 1
        self._apply_session_key(key, self._current_nav_id)

    @Slot(str, object, object)
    def setSessionSummary(self, key: str, message_count: object, has_messages: object) -> None:
        self._active_summary_key = key
        self._active_summary_message_count = (
            message_count if isinstance(message_count, int) and message_count >= 0 else None
        )
        self._active_summary_has_messages = has_messages if isinstance(has_messages, bool) else None

    @Slot(bool)
    def setActiveSessionReadOnly(self, read_only: bool) -> None:
        self._active_session_read_only = bool(read_only)

    @Slot(str)
    def notifyStartupSessionReady(self, key: str) -> None:
        if not key:
            return
        self._startup_target_key = key
        self._set_startup_activity({"sessionKey": key})
        self._drain_startup_pending()

    def _drain_startup_pending(self) -> None:
        if not self._startup_pending or not self._can_flush_startup_messages():
            return
        pending, self._startup_pending = self._startup_pending, []
        for message in pending:
            self._queue_or_show_ui_message(message.with_session_key(self._startup_target_key))

    def _handle_startup_message(self, message: object) -> None:
        if not isinstance(message, DesktopStartupMessage) or not message.content:
            return
        key = self._default_startup_session_key()
        self._set_startup_activity(
            {
                "kind": "startup_greeting",
                "status": "completed",
                "sessionKey": key,
                "sessionKeys": [key] if key else [],
                "channelKeys": ["desktop"],
                "content": message.content,
                "error": "",
            }
        )
        if not key:
            self._startup_pending.append(_QueuedUiMessage.from_startup(message))
            return
        self._queue_or_show_ui_message(_QueuedUiMessage.from_startup(message, session_key=key))

    def _handle_startup_activity_update(self, payload: object) -> None:
        if payload is None:
            self._clear_startup_activity()
            return
        if not isinstance(payload, dict):
            return
        if bool(payload.get("_clear", False)):
            self._clear_startup_activity()
            return
        patch = {str(key): value for key, value in payload.items() if key != "_clear"}
        self._set_startup_activity(patch)

    def _default_startup_session_key(self) -> str:
        if self._startup_target_key:
            return self._startup_target_key
        if self._session_key and self._session_key.startswith("desktop:"):
            return self._session_key
        return ""

    def _should_defer_startup_message(self, session_key: str) -> bool:
        if self._current_hub_runtime() is None:
            return False
        target_key = session_key or self._default_startup_session_key()
        if not target_key:
            return True
        if target_key != (self._startup_target_key or self._session_key):
            return False
        return not self._can_flush_startup_messages()

    def _can_flush_startup_messages(self) -> bool:
        return bool(self._startup_target_key) and self._history_initialized

    def _on_session_change(self, event: SessionChangeEvent) -> None:
        self._sessionChange.emit(event)

    def _handle_session_change(self, event: object) -> None:
        if not isinstance(event, SessionChangeEvent):
            return
        if event.kind == "deleted":
            self._history_cache.pop(event.session_key, None)
            return
        if event.kind != "messages":
            return
        active_key = self._desired_session_key or self._committed_session_key
        if not active_key or event.session_key != active_key:
            self._history_cache.pop(event.session_key, None)
            return
        self._cancel_history_future()
        self._request_history_load(active_key, self._current_nav_id, show_loading=False)
