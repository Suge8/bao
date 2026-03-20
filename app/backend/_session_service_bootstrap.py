from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from pathlib import Path
from typing import Any

from loguru import logger
from PySide6.QtCore import Slot

from app.backend._hub_access import DesktopHubAccess
from app.backend.asyncio_runner import AsyncioRunner


class SessionServiceBootstrapMixin:
    def setHubAccess(self, hub_access: Any) -> None:
        self._hub_access = hub_access if hub_access is not None else DesktopHubAccess()
        self._hub_access.set_local_ports(self._local_hub_ports)

    def setHubDispatcherProvider(self, provider: Any) -> None:
        self._hub_access.set_dispatcher_provider(provider)

    def _current_hub_dispatcher(self) -> Any:
        return self._hub_access.current_dispatcher()

    def initialize(self, hub_local_ports: Any) -> None:
        if self._disposed:
            return
        if self._local_hub_ports is hub_local_ports:
            return
        self._attach_local_hub_ports(hub_local_ports)
        self.refresh()

    @Slot(str)
    def bootstrapWorkspace(self, workspace_path: str) -> None:
        self.bootstrapStorageRoot(workspace_path)

    @Slot(str)
    def bootstrapStorageRoot(self, storage_root: str) -> None:
        if self._disposed:
            return
        raw_path = storage_root.strip()
        if not raw_path:
            return
        current = getattr(self._local_hub_ports, "state_root", None)
        if isinstance(current, Path) and current == Path(raw_path).expanduser():
            self.refresh()
            return
        self._set_sessions_loading(True)
        self._bootstrap_storage_root = str(Path(raw_path).expanduser())
        future = self._submit_safe(self._create_hub_local_ports(raw_path))
        if future is None:
            self._set_sessions_loading(False)
            return
        future.add_done_callback(self._on_bootstrap_done)

    @Slot()
    def shutdown(self) -> None:
        if self._disposed:
            return
        self._disposed = True
        self._ui_state.pending_select_key = ""
        self._ui_state.pending_deletes.clear()
        self._ui_state.pending_creates.clear()
        self._ui_state.session_rows = []
        self._ui_state.active_key = ""
        self._session_entry_request_seq.clear()
        self._list_inflight_count = 0
        self._refresh_inflight = False
        self._refresh_requested = False
        self._set_sessions_loading(False)
        self._ui_state.expanded_groups = {}
        self._sidebar_model.clear_rows()
        self._set_sidebar_unread_summary(0, "")
        self._set_active_session_projection("")
        self._detach_local_hub_ports(self._local_hub_ports)
        self._local_hub_ports = None
        self._hub_access.set_local_ports(None)
        self._bound_hub_directory = None

    def _submit_safe(self, coro: Coroutine[Any, Any, Any]) -> Any:
        try:
            return self._runner.submit(coro)
        except RuntimeError:
            coro.close()
            return None

    async def _run_user_io(self, fn: Any, *args: Any) -> Any:
        if isinstance(self._runner, AsyncioRunner):
            return await self._runner.run_user_io(fn, *args)
        return await asyncio.to_thread(fn, *args)

    async def _run_bg_io(self, fn: Any, *args: Any) -> Any:
        if isinstance(self._runner, AsyncioRunner):
            return await self._runner.run_bg_io(fn, *args)
        return await asyncio.to_thread(fn, *args)

    async def _create_hub_local_ports(self, storage_root: str) -> Any:
        from bao.hub import open_local_hub_ports

        root = Path(storage_root).expanduser()
        await self._run_user_io(lambda: root.mkdir(parents=True, exist_ok=True))
        return await self._run_user_io(open_local_hub_ports, root)

    def _on_bootstrap_done(self, future: Any) -> None:
        if future.cancelled():
            return
        exc = future.exception()
        if exc:
            self._bootstrapResult.emit(False, str(exc), None)
            return
        self._bootstrapResult.emit(True, "", future.result())

    async def _backfill_listed_session_tails(self, keys: list[str]) -> None:
        directory = self._hub_access.local_directory()
        if directory is None or not keys:
            return
        backfill = getattr(directory, "backfill_display_tail_rows", None)
        if not callable(backfill):
            return
        await self._run_bg_io(backfill, keys, 200)

    def _on_backfill_done(self, future: Any) -> None:
        if future.cancelled():
            return
        exc = self._future_exception_or_none(future)
        if exc is not None:
            logger.debug("Skip display tail backfill: {}", exc)

    def _handle_bootstrap_result(self, ok: bool, error: str, hub_local_ports: Any) -> None:
        if not ok:
            self._set_sessions_loading(False)
            logger.debug("Skip early session bootstrap: {}", error)
            return
        if self._disposed:
            return
        if self._local_hub_ports is not None and not self._bootstrap_storage_root:
            return
        expected_root = self._bootstrap_storage_root
        state_root = getattr(hub_local_ports, "state_root", None)
        actual_root = str(state_root) if isinstance(state_root, Path) else ""
        if expected_root and actual_root and expected_root != actual_root:
            return
        self.initialize(hub_local_ports)
        self.hubLocalPortsReady.emit(hub_local_ports)

    def _attach_local_hub_ports(self, hub_local_ports: Any) -> None:
        previous = self._local_hub_ports
        if previous is hub_local_ports:
            return
        self._detach_local_hub_ports(previous)
        self._local_hub_ports = hub_local_ports
        self._hub_access.set_local_ports(hub_local_ports)
        self._sync_hub_directory_binding()

    def _detach_local_hub_ports(self, hub_local_ports: Any) -> None:
        if hub_local_ports is None:
            return
        local_directory = self._hub_access.local_directory()
        if self._bound_hub_directory is local_directory and self._bound_hub_directory is not None:
            self._bound_hub_directory.remove_change_listener(self._on_session_change)
            self._bound_hub_directory = None
