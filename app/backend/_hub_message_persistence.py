from __future__ import annotations

from typing import Any

from loguru import logger

from app.backend.asyncio_runner import AsyncioRunner
from bao.hub import HubPersistMessageRequest

from ._hub_notifications import (
    TransientAssistantMessageRequest,
    TransientSystemMessageRequest,
)


class ChatServiceMessagePersistenceMixin:
    async def _persist_message_async(self, request: HubPersistMessageRequest) -> None:
        runtime = self._current_hub_runtime()
        if runtime is None:
            return
        await self._run_bg_io(runtime.persist_message, request)

    def _on_message_persist_done(
        self,
        future: Any,
        *,
        session_key: str = "",
        mark_seen: bool = False,
        log_label: str,
    ) -> None:
        try:
            future.result()
        except Exception as exc:
            logger.warning("Failed to persist {}: {}", log_label, exc)
            return
        if mark_seen and session_key:
            self._mark_session_seen_ai(session_key)

    def _schedule_persist_request(
        self,
        request: HubPersistMessageRequest,
        *,
        session_key: str = "",
        mark_seen: bool = False,
        log_label: str,
    ) -> None:
        runtime = self._current_hub_runtime()
        if runtime is None:
            return
        if isinstance(self._runner, AsyncioRunner):
            try:
                future = self._runner.submit(self._persist_message_async(request))
                future.add_done_callback(
                    lambda done, key=session_key, should_mark=mark_seen: (
                        self._on_message_persist_done(
                            done,
                            session_key=key,
                            mark_seen=should_mark,
                            log_label=log_label,
                        )
                    )
                )
                return
            except RuntimeError:
                pass
        try:
            runtime.persist_message(request)
        except Exception as exc:
            logger.warning("Failed to persist {}: {}", log_label, exc)
            return
        if mark_seen and session_key:
            self._mark_session_seen_ai(session_key)

    def _schedule_system_message_persist(
        self,
        request_or_session_key: TransientSystemMessageRequest | str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        request = self._normalize_system_message_persist_request(
            request_or_session_key,
            args,
            kwargs,
        )
        self._schedule_persist_request(
            HubPersistMessageRequest(
                session_key=request.session_key,
                role="user",
                content=request.content,
                status=request.status,
                entrance_style=request.entrance_style,
                source="desktop-system",
            ),
            log_label="desktop system message",
        )

    def _schedule_assistant_message_persist(
        self,
        request_or_session_key: TransientAssistantMessageRequest | str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        emit_change = bool(kwargs.pop("emit_change", False))
        mark_seen = bool(kwargs.pop("mark_seen", False))
        request = self._normalize_assistant_message_persist_request(
            request_or_session_key,
            args,
            kwargs,
        )
        self._schedule_persist_request(
            HubPersistMessageRequest(
                session_key=request.session_key,
                role="assistant",
                content=request.content,
                status=request.status,
                format="markdown",
                entrance_style=request.entrance_style,
                emit_change=emit_change,
            ),
            session_key=request.session_key,
            mark_seen=mark_seen,
            log_label="desktop startup assistant message",
        )

    def _normalize_system_message_persist_request(
        self,
        request_or_session_key: TransientSystemMessageRequest | str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> TransientSystemMessageRequest:
        if isinstance(request_or_session_key, TransientSystemMessageRequest):
            return request_or_session_key
        content = str(args[0]) if len(args) > 0 else str(kwargs.pop("content", "") or "")
        status = str(args[1]) if len(args) > 1 else str(kwargs.pop("status", "done") or "done")
        entrance_style = (
            str(args[2])
            if len(args) > 2
            else str(kwargs.pop("entrance_style", "system") or "system")
        )
        return TransientSystemMessageRequest(
            content=content,
            status=status,
            entrance_style=entrance_style,
            session_key=str(request_or_session_key or ""),
            show_in_ui=bool(kwargs.pop("show_in_ui", True)),
        )

    def _normalize_assistant_message_persist_request(
        self,
        request_or_session_key: TransientAssistantMessageRequest | str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> TransientAssistantMessageRequest:
        if isinstance(request_or_session_key, TransientAssistantMessageRequest):
            return request_or_session_key
        content = str(args[0]) if len(args) > 0 else str(kwargs.pop("content", "") or "")
        status = str(args[1]) if len(args) > 1 else str(kwargs.pop("status", "done") or "done")
        entrance_style = (
            str(args[2])
            if len(args) > 2
            else str(kwargs.pop("entrance_style", "assistantReceived") or "assistantReceived")
        )
        return TransientAssistantMessageRequest(
            content=content,
            status=status,
            session_key=str(request_or_session_key or ""),
            entrance_style=entrance_style,
            show_in_ui=bool(kwargs.pop("show_in_ui", True)),
        )
