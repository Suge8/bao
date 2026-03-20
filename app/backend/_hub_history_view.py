from __future__ import annotations

from typing import Any

from loguru import logger

from ._hub_history_common import (
    _DEBUG_SWITCH,
    _HISTORY_FULL_LIMIT,
    HistoryLoadRequest,
    RawTailReloadRequest,
)
from ._hub_types import _HistorySnapshot


class ChatServiceHistoryViewMixin:
    def _apply_session_key(self, key: str, nav_id: int) -> None:
        previous_committed = self._committed_session_key
        switched_session = previous_committed != key
        needs_seen_commit = bool(key) and (
            previous_committed != key or not self._history_initialized
        )
        cached_snapshot = self._history_cache.get(key) if key else None
        raw_tail_snapshot = self._tail_snapshot(key, bool(cached_snapshot))
        summary_knows_empty = self._summary_knows_empty(key)
        if cached_snapshot is not None and key:
            self._history_cache.move_to_end(key)
        self._desired_session_key = key
        self._committed_session_key = key
        self._session_key = key
        if _DEBUG_SWITCH:
            logger.debug(
                "switch_request desired={} committed={} nav_id={}",
                self._desired_session_key,
                self._committed_session_key,
                nav_id,
            )
        if previous_committed != key:
            self._active_streaming_row = -1
            self._active_has_content = False
            self._pending_split = False
        if self._current_hub_runtime() is not None and needs_seen_commit:
            self._mark_session_seen_ai(key)
        if self._current_hub_directory() is None or not key:
            self._clear_visible_history(key, switched_session=switched_session)
            return
        if cached_snapshot is None and raw_tail_snapshot is None:
            if summary_knows_empty:
                self._prime_empty_session(key, nav_id, switched_session=switched_session)
                return
            self._reset_history_state()
            self._model.clear()
        elif cached_snapshot is None and not raw_tail_snapshot:
            self._prime_cached_empty_history(key)
        elif cached_snapshot is None:
            self._request_raw_tail_reload(
                key,
                nav_id,
                raw_tail_snapshot,
                switched_session=switched_session,
            )
            return
        else:
            self._apply_cached_history(key, cached_snapshot)
        self._emit_session_view_applied(key, switched_session=switched_session)
        self._request_history_load(
            key,
            nav_id,
            show_loading=(cached_snapshot is None and raw_tail_snapshot is None),
        )

    def _tail_snapshot(self, key: str, has_cache: bool) -> list[dict[str, Any]] | None:
        if has_cache or not key or self._summary_knows_empty(key):
            return None
        directory = self._current_hub_directory()
        if directory is None:
            return None
        try:
            tail_messages_obj: object = directory.peek_transcript_tail(key, _HISTORY_FULL_LIMIT)
        except Exception:
            return None
        if not isinstance(tail_messages_obj, list):
            return None
        return [dict(message) for message in tail_messages_obj if isinstance(message, dict)]

    def _summary_knows_empty(self, key: str) -> bool:
        return bool(
            key
            and key == self._active_summary_key
            and (
                self._active_summary_message_count == 0
                or self._active_summary_has_messages is False
            )
        )

    def _clear_visible_history(self, key: str, *, switched_session: bool) -> None:
        self._set_history_loading(False)
        self._reset_history_state()
        self._set_active_session_state(False, False)
        self._model.clear()
        self._emit_session_view_applied(key, switched_session=switched_session)

    def _reset_history_state(self) -> None:
        self._history_initialized = False
        self._history_fingerprint = None
        self._set_active_session_state(False, False)

    def _prime_empty_session(self, key: str, nav_id: int, *, switched_session: bool) -> None:
        fingerprint = self._history_signature([])
        self._history_initialized = True
        self._history_fingerprint = fingerprint
        self._set_active_session_state(True, False)
        self._cache_history_snapshot(key, fingerprint, [], False)
        self._model.clear()
        self._set_history_loading(False)
        self._emit_session_viewport_ready(key)
        self._emit_session_view_applied(key, switched_session=switched_session)
        self._request_history_load(key, nav_id, show_loading=False)

    def _prime_cached_empty_history(self, key: str) -> None:
        fingerprint = self._history_signature([])
        self._history_initialized = True
        self._history_fingerprint = fingerprint
        self._set_active_session_state(True, False)
        self._cache_history_snapshot(key, fingerprint, [], False)
        self._model.clear()
        self._emit_session_viewport_ready(key)

    def _request_raw_tail_reload(self, key: str, *args: Any, **kwargs: Any) -> None:
        request = self._normalize_raw_tail_reload_request(key, args, kwargs)
        self._request_raw_tail_reload_request(request)

    def _normalize_raw_tail_reload_request(
        self,
        key: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> RawTailReloadRequest:
        return RawTailReloadRequest(
            key=key,
            nav_id=int(args[0]),
            raw_tail_snapshot=list(args[1]),
            switched_session=bool(kwargs.get("switched_session", False)),
        )

    def _request_raw_tail_reload_request(self, request: RawTailReloadRequest) -> None:
        self._reset_history_state()
        self._model.clear()
        self._emit_session_view_applied(request.key, switched_session=request.switched_session)
        self._request_history_load(
            request.key,
            request.nav_id,
            show_loading=False,
            raw_messages_override=request.raw_tail_snapshot,
        )

    def _apply_cached_history(self, key: str, cached_snapshot: _HistorySnapshot) -> None:
        self._history_initialized = True
        self._history_fingerprint = cached_snapshot.fingerprint
        self._set_active_session_state(True, cached_snapshot.has_messages)
        self._model.load_prepared([dict(msg) for msg in cached_snapshot.prepared_messages])
        self._emit_session_viewport_ready(key)

    def _request_history_load(self, key: str, *args: Any, **kwargs: Any) -> None:
        request = self._normalize_history_load_request(key, args, kwargs)
        self._request_history_load_request(request)

    def _normalize_history_load_request(
        self,
        key: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> HistoryLoadRequest:
        nav_id = int(args[0]) if args else int(kwargs.pop("nav_id", 0) or 0)
        return HistoryLoadRequest(
            key=key,
            nav_id=nav_id,
            show_loading=kwargs.pop("show_loading", None),
            raw_messages_override=kwargs.pop("raw_messages_override", None),
        )

    def _request_history_load_request(self, request: HistoryLoadRequest) -> None:
        show_loading = (
            request.show_loading
            if request.show_loading is not None
            else not self._history_initialized
        )
        if show_loading:
            self._set_history_loading(True)
        if _DEBUG_SWITCH:
            logger.debug("history_load key={} nav_id={}", request.key, request.nav_id)
        future = self._runner.submit(
            self._load_history(
                request.key,
                request.nav_id,
                _HISTORY_FULL_LIMIT,
                raw_messages_override=request.raw_messages_override,
            )
        )
        self._history_future = future
        future.add_done_callback(self._on_history_done)
