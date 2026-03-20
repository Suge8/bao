from __future__ import annotations

import time
from concurrent.futures import CancelledError as FutureCancelledError
from typing import Any

from loguru import logger

from app.backend.session_projection import normalize_session_items, project_session_item
from bao.hub import (
    HubClearActiveSessionRequest,
    HubCreateSessionRequest,
    HubDeleteRequest,
    HubSetActiveSessionRequest,
)


class SessionServiceAsyncMixin:
    async def _list_sessions(self, seq: int) -> tuple[int, list[dict[str, Any]], str]:
        directory = self._current_hub_directory()
        raw_sessions, active_raw = await self._run_user_io(directory.list_sessions_with_active_key, self._natural_key)
        result = [
            project_session_item(session, natural_key=self._natural_key, current_sessions=[])
            for session in raw_sessions
        ]
        return seq, normalize_session_items(result), active_raw or ""

    async def _load_session_entry(
        self,
        key: str,
        *,
        request_seq: int,
        generation: int,
    ) -> tuple[str, int, int, dict[str, Any] | None]:
        directory = self._current_hub_directory()
        if directory is None:
            return key, request_seq, generation, None
        entry = await self._run_user_io(directory.get_session, key)
        return key, request_seq, generation, entry

    async def _load_session_discovery(
        self,
        *,
        seq: int,
        lookup_query: str,
        resolved_session_ref: str,
    ) -> tuple[int, list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
        directory = self._current_hub_directory()
        if directory is None:
            return seq, [], [], {}, {}
        recent = await self._run_user_io(self._call_directory_list, directory, "list_recent_sessions")
        default_session = await self._run_user_io(
            self._call_directory_snapshot,
            directory,
            "get_default_session",
        )
        lookup_results: list[dict[str, Any]] = []
        if lookup_query:
            lookup_results = await self._run_user_io(
                self._call_directory_list,
                directory,
                "lookup_sessions",
                lookup_query,
            )
        resolved_session: dict[str, Any] = {}
        if resolved_session_ref:
            resolved_session = await self._run_user_io(
                self._call_directory_snapshot,
                directory,
                "resolve_session_ref",
                resolved_session_ref,
            )
        return seq, recent, lookup_results, default_session, resolved_session

    async def _commit_active_selection(self, key: str, seq: int) -> None:
        control = self._current_hub_control()
        if control is None or not key or seq != self._active_commit_seq:
            return
        await control.set_active_session(
            HubSetActiveSessionRequest(
                natural_key=self._natural_key,
                session_key=key,
            )
        )

    async def _clear_active_selection(self, seq: int) -> None:
        control = self._current_hub_control()
        if control is None or seq != self._active_commit_seq:
            return
        await control.clear_active_session(HubClearActiveSessionRequest(natural_key=self._natural_key))

    def _build_new_session_key(self, name: str) -> str:
        if name:
            return f"{self._natural_key}::{name}"
        return f"{self._natural_key}::session-{int(time.time())}"

    async def _create_session(self, key: str, seq: int) -> str:
        control = self._current_hub_control()
        if control is None:
            raise RuntimeError("Hub control unavailable")
        await control.create_session(
            HubCreateSessionRequest(
                session_key=key,
                natural_key=self._natural_key,
                activate=False,
            )
        )
        await self._commit_active_selection(key, seq)
        return key

    async def _select_session(self, key: str, seq: int) -> str:
        await self._commit_active_selection(key, seq)
        return key

    async def _delete_session(self, key: str, new_active: str, seq: int | None) -> str:
        directory = self._current_hub_directory()
        control = self._delete_hub_control()

        async def _delete() -> bool:
            if directory is None:
                raise RuntimeError("Hub directory unavailable")
            _, active_raw = await self._run_user_io(directory.list_sessions_with_active_key, self._natural_key)
            was_active = active_raw == key
            deleted = await control.delete(HubDeleteRequest(session_key=key, include_children=True))
            if deleted:
                return was_active
            still_exists = True
            try:
                sessions = directory.list_sessions() if directory is not None else []
                still_exists = any(session.get("key") == key for session in sessions)
            except Exception:
                still_exists = True
            if still_exists:
                raise RuntimeError(f"delete session failed: {key}")
            return was_active

        was_active = await _delete()
        if not was_active or seq is None:
            return ""
        try:
            if new_active:
                await self._commit_active_selection(new_active, seq)
            else:
                await self._clear_active_selection(seq)
        except Exception as exc:
            logger.warning("Session deleted but active sync failed: {}", exc)
            return str(exc)
        return ""

    def _delete_hub_control(self) -> Any:
        control = self._current_hub_control()
        if control is None:
            raise RuntimeError("Hub control unavailable")
        return control

    def _future_exception_or_none(self, future: Any) -> Exception | None:
        try:
            return future.exception()
        except FutureCancelledError:
            return None

    def _on_list_done(self, future: Any) -> None:
        if self._disposed or future.cancelled():
            return
        exc = self._future_exception_or_none(future)
        if exc:
            self._listResult.emit(False, str(exc), None)
            return
        self._listResult.emit(True, "", future.result())

    def _on_session_entry_done(self, future: Any) -> None:
        if self._disposed or future.cancelled():
            return
        exc = self._future_exception_or_none(future)
        if exc:
            self._sessionEntryResult.emit(False, str(exc), None)
            return
        self._sessionEntryResult.emit(True, "", future.result())

    def _on_discovery_done(self, future: Any) -> None:
        if self._disposed or future.cancelled():
            return
        exc = self._future_exception_or_none(future)
        if exc:
            self._discoveryResult.emit(False, str(exc), None)
            return
        self._discoveryResult.emit(True, "", future.result())

    def _on_select_done(self, future: Any) -> None:
        if self._disposed or future.cancelled():
            return
        exc = self._future_exception_or_none(future)
        if exc:
            self._selectResult.emit(False, str(exc), "")
            return
        self._selectResult.emit(True, "", future.result())

    def _on_create_done(self, key: str, future: Any) -> None:
        if self._disposed or future.cancelled():
            return
        exc = self._future_exception_or_none(future)
        if exc:
            self._createResult.emit(False, str(exc), key)
            return
        self._createResult.emit(True, "", str(future.result() or key))

    def _on_delete_done(self, key: str, future: Any) -> None:
        if self._disposed or future.cancelled():
            return
        exc = self._future_exception_or_none(future)
        if exc:
            self._deleteResult.emit(key, False, str(exc))
            return
        self._deleteResult.emit(key, True, str(future.result() or ""))

    @staticmethod
    def _call_directory_list(directory: Any, method_name: str, *args: Any) -> list[dict[str, Any]]:
        method = getattr(directory, method_name, None)
        if not callable(method):
            return []
        result = method(*args)
        return [dict(item) for item in result] if isinstance(result, list) else []

    @staticmethod
    def _call_directory_snapshot(directory: Any, method_name: str, *args: Any) -> dict[str, Any]:
        method = getattr(directory, method_name, None)
        if not callable(method):
            return {}
        result = method(*args)
        return dict(result) if isinstance(result, dict) else {}
