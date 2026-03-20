from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from bao.hub import HubControl, HubSendRequest
from bao.providers.retry import PROGRESS_RESET

from ._hub_types import _QueuedSendRequest


@dataclass(frozen=True)
class AgentCallRequest:
    text: str
    session_key: str
    client_token: str = ""
    display_text: str = ""
    media_paths: list[str] | None = None


@dataclass(frozen=True)
class SendResultState:
    ok: bool
    is_provider_error: bool
    final_status: str
    should_render_in_ui: bool


class ChatServiceSendMixin:
    def _current_profile_id(self) -> str:
        if not isinstance(self._profile_context_data, dict):
            return ""
        for key in ("profile_id", "profileId"):
            profile_id = self._profile_context_data.get(key)
            if isinstance(profile_id, str) and profile_id.strip():
                return profile_id.strip()
        return ""

    def _enqueue(self, request: _QueuedSendRequest) -> None:
        self._send_queue.put(request)
        if self._state == "running":
            self._drain_queue()

    def _drain_queue(self) -> None:
        request = self._next_queued_request()
        if request is None:
            return
        self._activate_send_request(request)
        assistant_row = self._append_typing_row()
        self._active_streaming_row = assistant_row
        self._active_streaming_session_key = request.session_key
        self._active_has_content = False
        self._pending_split = False
        future = self._runner.submit(
            self._call_agent(
                AgentCallRequest(
                    text=request.raw_text,
                    session_key=request.session_key,
                    client_token=request.client_token,
                    display_text=request.display_text,
                    media_paths=request.media_paths,
                )
            )
        )
        self._active_send_future = future
        future.add_done_callback(lambda done: self._on_send_done(done, assistant_row))

    def _next_queued_request(self) -> _QueuedSendRequest | None:
        with self._lock:
            if self._processing:
                return None
            try:
                request = self._send_queue.get_nowait()
            except Exception as exc:
                import queue

                if isinstance(exc, queue.Empty):
                    return None
                raise
            self._processing = True
            return request

    def _activate_send_request(self, request: _QueuedSendRequest) -> None:
        self._active_user = self._active_user.__class__(
            row=request.row,
            session_key=request.session_key,
            token=request.client_token,
        )
        self._set_session_running(request.session_key, True)

    def _on_send_done(self, future: Any, row: int) -> None:
        if future.cancelled():
            self._sendResult.emit(row, False, "Cancelled.")
            return
        exc = future.exception()
        if exc:
            self._sendResult.emit(row, False, f"Error: {exc}")
            return
        self._sendResult.emit(row, True, future.result() or "")

    def _handle_send_result(self, _row: int, ok: bool, content: str) -> None:
        self._active_send_future = None
        state = self._send_result_state(ok, content)
        active_row = self._resolve_active_send_row(state.should_render_in_ui)
        active_row = self._maybe_split_active_row(state, active_row, content)
        self._render_send_result(state, active_row, content)
        completed_session_key = self._clear_active_stream_state()
        self._complete_send_result(state, completed_session_key)
        self.statusSettled.emit(active_row, state.final_status)
        self._flush_pending_notifications()

    def _send_result_state(self, ok: bool, content: str) -> SendResultState:
        is_provider_error = ok and isinstance(content, str) and content.startswith("Error calling ")
        return SendResultState(
            ok=ok,
            is_provider_error=is_provider_error,
            final_status="error" if (not ok or is_provider_error) else "done",
            should_render_in_ui=self._should_render_active_stream(),
        )

    def _resolve_active_send_row(self, should_render_in_ui: bool) -> int:
        active_row = self._active_streaming_row
        if active_row < 0 and should_render_in_ui:
            return self._restore_active_streaming_row(emit_append_signal=True)
        return active_row

    def _maybe_split_active_row(
        self,
        state: SendResultState,
        active_row: int,
        content: str,
    ) -> int:
        should_split = (
            state.ok
            and not state.is_provider_error
            and self._pending_split
            and self._active_has_content
            and bool(content)
            and active_row >= 0
        )
        if not should_split:
            return active_row
        self._model.set_status(active_row, "done")
        next_row = self._append_typing_row()
        self._active_streaming_row = next_row
        self._active_has_content = False
        return next_row

    def _render_send_result(
        self,
        state: SendResultState,
        active_row: int,
        content: str,
    ) -> None:
        if not state.ok:
            self._render_send_error(active_row, content)
            return
        self._render_send_success(state, active_row, content)

    def _render_send_error(self, active_row: int, content: str) -> None:
        if active_row < 0:
            return
        self._model.set_format(active_row, "plain")
        self._model.update_content(active_row, content)
        self.incrementalContent.emit(active_row)
        self._model.set_status(active_row, "error")

    def _render_send_success(
        self,
        state: SendResultState,
        active_row: int,
        content: str,
    ) -> None:
        if content and active_row >= 0:
            if state.is_provider_error:
                self._model.set_format(active_row, "plain")
            self._model.update_content(active_row, content)
            self.incrementalContent.emit(active_row)
        if content:
            self._active_has_content = active_row >= 0
        if active_row >= 0:
            self._model.set_status(active_row, state.final_status)

    def _clear_active_stream_state(self) -> str | None:
        completed_session_key = self._active_streaming_session_key
        self._active_streaming_row = -1
        self._active_streaming_session_key = None
        self._active_has_content = False
        self._pending_split = False
        return completed_session_key

    def _complete_send_result(
        self,
        state: SendResultState,
        completed_session_key: str | None,
    ) -> None:
        should_mark_seen = (
            state.ok
            and not state.is_provider_error
            and completed_session_key
            and completed_session_key == self._committed_session_key
        )
        self._finalize_active_user_message(ok=state.ok and not state.is_provider_error)
        if completed_session_key and not should_mark_seen:
            self._set_session_running(completed_session_key, False)
        if should_mark_seen and isinstance(completed_session_key, str):
            self._mark_session_seen_ai(
                completed_session_key,
                emit_change=True,
                extra_updates={"session_running": False},
            )

    def _flush_pending_notifications(self) -> None:
        with self._lock:
            self._processing = False
            pending = self._pending_notifications[:]
            self._pending_notifications.clear()
        for message in pending:
            self._show_ui_message(message)

    async def _call_agent(
        self,
        request_or_text: AgentCallRequest | str,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        request = self._normalize_agent_call_request(request_or_text, args, kwargs)
        return await self._call_agent_request(request)

    def _normalize_agent_call_request(
        self,
        request_or_text: AgentCallRequest | str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> AgentCallRequest:
        if isinstance(request_or_text, AgentCallRequest):
            return request_or_text
        session_key = str(args[0]) if args else str(kwargs.pop("session_key", "") or "")
        return AgentCallRequest(
            text=request_or_text,
            session_key=session_key,
            client_token=str(kwargs.pop("client_token", "") or ""),
            display_text=str(kwargs.pop("display_text", "") or ""),
            media_paths=kwargs.pop("media_paths", None),
        )

    async def _call_agent_request(self, request: AgentCallRequest) -> str:
        dispatcher = getattr(self, "_dispatcher", None) or getattr(self, "_agent", None)
        if dispatcher is None:
            raise RuntimeError("Agent not initialized")

        from bao.agent.protocol import StreamEventType

        metadata = await self._prepare_user_message_metadata(
            request.session_key,
            request.display_text or request.text,
            client_token=request.client_token,
        )
        accumulated = ""

        async def _on_progress(delta: str) -> None:
            nonlocal accumulated
            if delta == PROGRESS_RESET:
                self._progressUpdate.emit(-2, "")
                accumulated = ""
                return
            accumulated += delta
            self._progressUpdate.emit(-1, accumulated)

        async def _on_event(event: Any) -> None:
            if getattr(event, "type", "") != StreamEventType.TOOL_HINT:
                return
            hint_text = getattr(event, "text", "")
            if isinstance(hint_text, str) and hint_text.strip() and self._tool_hints_enabled():
                self._toolHintUpdate.emit(hint_text)

        response = await HubControl(dispatcher).send(
            HubSendRequest(
                content=request.text,
                session_key=request.session_key,
                channel="desktop",
                chat_id="local",
                profile_id=self._current_profile_id(),
                media=request.media_paths or None,
                on_progress=_on_progress,
                on_event=_on_event,
                metadata=metadata,
            )
        )
        sync_runtime = getattr(self, "_sync_dispatcher_after_request", None)
        if callable(sync_runtime):
            sync_runtime(self._current_profile_id())
        return response
