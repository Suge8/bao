from __future__ import annotations

from dataclasses import dataclass

from ._hub_types import _QueuedUiMessage


@dataclass(frozen=True)
class TransientSystemMessageRequest:
    content: str
    status: str = "done"
    entrance_style: str = "system"
    session_key: str = ""
    show_in_ui: bool = True


@dataclass(frozen=True)
class TransientAssistantMessageRequest:
    content: str
    status: str = "done"
    session_key: str = ""
    entrance_style: str = "assistantReceived"
    show_in_ui: bool = True


class ChatServiceNotificationsMixin:
    def _handle_system_response(self, content: str, session_key: str = "") -> None:
        self._queue_or_show_ui_message(
            _QueuedUiMessage(
                role="system",
                content=content,
                session_key=session_key,
                entrance_style="system",
            )
        )

    def _queue_or_show_ui_message(self, message: _QueuedUiMessage) -> None:
        if not message.content:
            return
        if self._should_defer_startup_message(message.session_key):
            self._startup_pending.append(message)
            return
        target_session_key = (
            message.session_key or self._default_startup_session_key() or self._session_key
        )
        queued = message.with_session_key(target_session_key)
        with self._lock:
            if self._processing:
                self._pending_notifications.append(queued)
                return
        self._show_ui_message(queued)

    def _show_ui_message(self, message: _QueuedUiMessage) -> None:
        if message.role == "assistant":
            self._show_assistant_response(
                message.content,
                session_key=message.session_key,
                entrance_style=message.entrance_style,
            )
            return
        self._show_system_response(
            message.content,
            entrance_style=message.entrance_style,
            session_key=message.session_key,
        )

    def _show_system_response(
        self,
        content: str,
        *,
        entrance_style: str = "system",
        session_key: str = "",
    ) -> None:
        self._append_transient_system_message(
            TransientSystemMessageRequest(
                content=content,
                entrance_style=entrance_style,
                session_key=session_key or self._session_key,
                show_in_ui=self._should_show_startup_message(session_key or self._session_key),
            )
        )

    def _show_assistant_response(
        self,
        content: str,
        *,
        session_key: str = "",
        entrance_style: str = "assistantReceived",
    ) -> None:
        self._append_transient_assistant_message(
            TransientAssistantMessageRequest(
                content=content,
                session_key=session_key or self._session_key,
                entrance_style=entrance_style,
                show_in_ui=self._should_show_startup_message(session_key or self._session_key),
            )
        )

    def _should_show_startup_message(self, target_session_key: str) -> bool:
        if target_session_key == self._session_key:
            return True
        return (
            self._session_key == "desktop:local"
            and bool(self._startup_target_key)
            and target_session_key == self._startup_target_key
        )

    def _append_transient_system_message(
        self,
        request_or_content: TransientSystemMessageRequest | str,
        *args: object,
        **kwargs: object,
    ) -> None:
        request = self._normalize_system_message_request(request_or_content, kwargs)
        if not request.content:
            return
        self._schedule_system_message_persist(
            request.session_key,
            request.content,
            request.status,
            entrance_style=request.entrance_style,
        )
        if not request.show_in_ui:
            return
        row = self._model.append_system(
            request.content,
            status=request.status,
            entrance_style=request.entrance_style,
            entrance_pending=True,
        )
        self.appendAtBottom.emit(row)

    def _append_transient_assistant_message(
        self,
        request_or_content: TransientAssistantMessageRequest | str,
        *args: object,
        **kwargs: object,
    ) -> None:
        request = self._normalize_assistant_message_request(request_or_content, kwargs)
        if not request.content:
            return
        is_visible_active_session = (
            request.show_in_ui and request.session_key == self._committed_session_key
        )
        self._schedule_assistant_message_persist(
            request.session_key,
            request.content,
            request.status,
            emit_change=not is_visible_active_session,
            mark_seen=is_visible_active_session,
            entrance_style=request.entrance_style,
        )
        if not request.show_in_ui:
            return
        row = self._model.append_assistant(
            request.content,
            status=request.status,
            entrance_style=request.entrance_style,
            entrance_pending=True,
        )
        self.appendAtBottom.emit(row)

    def _normalize_system_message_request(
        self,
        request_or_content: TransientSystemMessageRequest | str,
        kwargs: dict[str, object],
    ) -> TransientSystemMessageRequest:
        if isinstance(request_or_content, TransientSystemMessageRequest):
            return request_or_content
        return TransientSystemMessageRequest(
            content=request_or_content,
            status=str(kwargs.pop("status", "done") or "done"),
            entrance_style=str(kwargs.pop("entrance_style", "system") or "system"),
            session_key=str(kwargs.pop("session_key", "") or ""),
            show_in_ui=bool(kwargs.pop("show_in_ui", True)),
        )

    def _normalize_assistant_message_request(
        self,
        request_or_content: TransientAssistantMessageRequest | str,
        kwargs: dict[str, object],
    ) -> TransientAssistantMessageRequest:
        if isinstance(request_or_content, TransientAssistantMessageRequest):
            return request_or_content
        return TransientAssistantMessageRequest(
            content=request_or_content,
            status=str(kwargs.pop("status", "done") or "done"),
            session_key=str(kwargs.pop("session_key", "") or ""),
            entrance_style=str(
                kwargs.pop("entrance_style", "assistantReceived") or "assistantReceived"
            ),
            show_in_ui=bool(kwargs.pop("show_in_ui", True)),
        )
