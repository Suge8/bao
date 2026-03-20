from __future__ import annotations

from typing import Any, cast

from loguru import logger

from app.backend.chat import ChatMessageModel
from bao.hub.directory import TranscriptReadRequest
from bao.utils.attachments import normalize_attachment_records

from ._hub_history_common import (
    _DEBUG_SWITCH,
    _HISTORY_CACHE_LIMIT,
    _PROFILE,
    HistorySnapshotRequest,
    LoadHistoryRequest,
    PreparedHistoryRequest,
)
from ._hub_types import _HistorySnapshot


class ChatServiceHistoryLoadMixin:
    async def _load_history(self, key: str, *args: Any, **kwargs: Any) -> tuple[Any, ...]:
        request = self._normalize_load_history_request(key, args, kwargs)
        return await self._load_history_request(request)

    def _normalize_load_history_request(
        self,
        key: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> LoadHistoryRequest:
        nav_id = int(args[0]) if args else int(kwargs.pop("nav_id", 0) or 0)
        limit = int(args[1]) if len(args) > 1 else int(kwargs.pop("limit", 0) or 0)
        return LoadHistoryRequest(
            key=key,
            nav_id=nav_id,
            limit=limit,
            raw_messages_override=kwargs.pop("raw_messages_override", None),
        )

    async def _load_history_request(
        self,
        request: LoadHistoryRequest,
    ) -> tuple[str, int, tuple[int, str], list[dict[str, Any]], bool]:
        import time

        t0 = time.perf_counter() if _PROFILE else 0
        directory = self._current_hub_directory()

        def _read_raw_messages() -> list[dict[str, Any]]:
            try:
                if directory is not None:
                    page = directory.read_transcript(
                        request.key,
                        TranscriptReadRequest(mode="tail", limit=request.limit),
                    )
                    return [dict(message) for message in page.messages]
                raise TypeError("tail_messages_not_list")
            except Exception:
                if directory is None:
                    return []
                page = directory.read_transcript(request.key, TranscriptReadRequest(mode="full"))
                return page.messages[-request.limit:] if request.limit > 0 else page.messages

        if request.raw_messages_override is not None:
            raw_messages = [dict(message) for message in request.raw_messages_override]
        else:
            raw_messages = await self._run_user_io(_read_raw_messages)
        raw_messages = await self._run_user_io(self._hydrate_history_attachments, raw_messages)
        t1 = time.perf_counter() if _PROFILE else 0
        if _PROFILE:
            logger.debug("History load read_raw={:.3f}s", t1 - t0)
        prepared_messages = await self._run_user_io(ChatMessageModel.prepare_history, raw_messages)
        fingerprint = self._history_signature(prepared_messages)
        if _PROFILE:
            logger.debug("History prepare={:.3f}s", time.perf_counter() - t1)
        return request.key, request.nav_id, fingerprint, prepared_messages, bool(raw_messages)

    def _hydrate_history_attachments(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        directory = self._current_hub_directory()
        workspace = getattr(directory, "workspace", None) if directory is not None else None
        hydrated: list[dict[str, Any]] = []
        for message in messages:
            item = dict(message)
            item["attachments"] = normalize_attachment_records(
                cast(list[dict[str, Any]] | None, item.get("attachments")),
                workspace=workspace,
            )
            hydrated.append(item)
        return hydrated

    def _on_history_done(self, future: Any) -> None:
        if future is not self._history_future:
            return
        self._history_future = None
        if future.cancelled():
            return
        exc = future.exception()
        if exc:
            self._historyResult.emit(False, str(exc), None)
            return
        self._historyResult.emit(True, "", future.result())

    def _handle_history_result(self, ok: bool, error: str, messages: Any) -> None:
        del error
        if not ok:
            self._set_history_loading(False)
            return
        loaded_key, loaded_nav_id, fingerprint, loaded_messages, loaded_has_messages, loaded_prepared = self._history_payload(messages)
        if loaded_nav_id and loaded_nav_id != self._current_nav_id:
            if _DEBUG_SWITCH:
                logger.debug(
                    "history_gating loaded_nav_id={} current_nav_id={}",
                    loaded_nav_id,
                    self._current_nav_id,
                )
            return
        if loaded_key != self._desired_session_key:
            return
        next_fingerprint = fingerprint or self._history_signature(loaded_messages)
        if self._history_initialized and next_fingerprint == self._history_fingerprint:
            self._set_history_loading(False)
            return
        self._history_initialized = True
        self._history_fingerprint = next_fingerprint
        self._committed_session_key = loaded_key
        self._session_key = loaded_key
        self._set_active_session_state(True, loaded_has_messages)
        if loaded_prepared:
            self._apply_prepared_history(
                loaded_key,
                next_fingerprint,
                loaded_messages,
                loaded_has_messages,
            )
        else:
            self._model.load_history(loaded_messages)
        if _DEBUG_SWITCH:
            logger.debug(
                "history_applied key={} rows={} nav_id={}",
                loaded_key,
                self._model.rowCount(),
                loaded_nav_id,
            )
        self._set_history_loading(False)
        if loaded_key == self._startup_target_key:
            self._drain_startup_pending()
        self._emit_session_viewport_ready(loaded_key)

    def _history_payload(
        self,
        messages: Any,
    ) -> tuple[str, int, tuple[int, str] | None, list[dict[str, Any]], bool, bool]:
        loaded_key = self._session_key
        loaded_nav_id = 0
        loaded_messages = messages or []
        loaded_fingerprint: tuple[int, str] | None = None
        loaded_has_messages = False
        loaded_prepared = False
        if isinstance(messages, tuple) and len(messages) == 5:
            loaded_key, loaded_nav_id, loaded_fingerprint, loaded_messages, loaded_has_messages = messages
            loaded_messages = loaded_messages or []
            loaded_prepared = True
        elif isinstance(messages, tuple) and len(messages) == 4:
            loaded_key, loaded_nav_id, loaded_fingerprint, loaded_messages = messages
            loaded_messages = loaded_messages or []
            loaded_has_messages = bool(loaded_messages)
            loaded_prepared = True
        elif isinstance(messages, tuple) and len(messages) == 3:
            loaded_key, loaded_nav_id, loaded_messages = messages
            loaded_messages = loaded_messages or []
            loaded_has_messages = bool(loaded_messages)
        elif isinstance(messages, tuple) and len(messages) == 2:
            loaded_key, loaded_messages = messages
            loaded_messages = loaded_messages or []
            loaded_has_messages = bool(loaded_messages)
        return (
            loaded_key,
            loaded_nav_id,
            loaded_fingerprint,
            loaded_messages,
            loaded_has_messages,
            loaded_prepared,
        )

    def _apply_prepared_history(self, loaded_key: str, *args: Any) -> None:
        request = self._normalize_prepared_history_request(loaded_key, args)
        self._apply_prepared_history_request(request)

    def _normalize_prepared_history_request(
        self,
        loaded_key: str,
        args: tuple[Any, ...],
    ) -> PreparedHistoryRequest:
        return PreparedHistoryRequest(
            loaded_key=loaded_key,
            fingerprint=args[0],
            loaded_messages=list(args[1]),
            loaded_has_messages=bool(args[2]),
        )

    def _apply_prepared_history_request(self, request: PreparedHistoryRequest) -> None:
        prepared_messages = [dict(msg) for msg in request.loaded_messages]
        self._cache_history_snapshot(
            request.loaded_key,
            request.fingerprint,
            prepared_messages,
            request.loaded_has_messages,
        )
        preserve_transient_tail = (
            self._processing and request.loaded_key == self._active_streaming_session_key
        )
        previous_active_row = self._active_streaming_row
        self._model.load_prepared(
            prepared_messages,
            preserve_transient_tail=preserve_transient_tail,
        )
        if request.loaded_key != self._active_streaming_session_key:
            return
        rebound_row = self._rebind_active_streaming_row_after_history()
        active_message = self._model.message_at(rebound_row)
        if active_message is None:
            self._active_has_content = False
            self._pending_split = False
            return
        if self._pending_split and (
            rebound_row != previous_active_row
            or active_message.get("status") != "typing"
        ):
            self._pending_split = False

    @staticmethod
    def _history_signature(messages: list[dict[str, Any]]) -> tuple[int, str]:
        if not messages:
            return (0, "")
        return (len(messages), repr(messages))

    def _set_active_session_state(self, ready: bool, has_messages: bool) -> None:
        if self._active_session_ready == ready and self._active_session_has_messages == has_messages:
            return
        self._active_session_ready = ready
        self._active_session_has_messages = has_messages
        self.activeSessionStateChanged.emit()
        self.viewPhaseChanged.emit(self._compute_view_phase())

    def _emit_session_view_applied(self, key: str, *, switched_session: bool) -> None:
        if not switched_session:
            return
        self.sessionViewApplied.emit(key)
        self.sessionSwitchedApplied.emit(key)

    def _compute_view_phase(self) -> str:
        if self._state == "error":
            return "error"
        if self._history_loading or self._state == "starting":
            return "loading"
        if self._active_session_ready:
            return "ready"
        if self._state in ("idle", "stopped"):
            return "idle"
        return "loading"

    def _emit_session_viewport_ready(self, key: str) -> None:
        if key:
            self.historyReady.emit(key)

    def _cache_history_snapshot(self, key: str, *args: Any) -> None:
        request = self._normalize_history_snapshot_request(key, args)
        self._cache_history_snapshot_request(request)

    def _normalize_history_snapshot_request(
        self,
        key: str,
        args: tuple[Any, ...],
    ) -> HistorySnapshotRequest:
        return HistorySnapshotRequest(
            key=key,
            fingerprint=args[0],
            prepared_messages=list(args[1]),
            has_messages=bool(args[2]),
        )

    def _cache_history_snapshot_request(self, request: HistorySnapshotRequest) -> None:
        if not request.key:
            return
        self._history_cache[request.key] = _HistorySnapshot(
            fingerprint=request.fingerprint,
            prepared_messages=[dict(msg) for msg in request.prepared_messages],
            has_messages=request.has_messages,
        )
        self._history_cache.move_to_end(request.key)
        while len(self._history_cache) > _HISTORY_CACHE_LIMIT:
            self._history_cache.popitem(last=False)
