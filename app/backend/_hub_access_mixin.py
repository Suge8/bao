from __future__ import annotations

from typing import Any


class ChatServiceHubAccessMixin:
    def setHubAccess(self, hub_access: Any) -> None:
        if hub_access is None:
            return
        self._hub_access = hub_access
        self._sync_hub_bindings()

    def _current_hub_dispatcher(self) -> Any:
        dispatcher = self._hub_access.current_dispatcher()
        if dispatcher is not None:
            return dispatcher
        return getattr(self, "_dispatcher", None)

    def _live_hub_directory(self) -> Any:
        dispatcher = self._current_hub_dispatcher()
        return getattr(dispatcher, "directory", None) if dispatcher is not None else None

    def _live_hub_runtime(self) -> Any:
        dispatcher = self._current_hub_dispatcher()
        return getattr(dispatcher, "runtime_port", None) if dispatcher is not None else None

    def _current_hub_directory(self) -> Any:
        self._sync_hub_bindings()
        return self._bound_hub_directory

    def _current_hub_runtime(self) -> Any:
        self._sync_hub_bindings()
        return self._bound_hub_runtime

    def _sync_hub_bindings(self) -> None:
        next_directory = self._live_hub_directory() or self._hub_access.local_directory()
        next_runtime = self._live_hub_runtime() or self._hub_access.local_runtime()
        previous_directory = self._bound_hub_directory
        if previous_directory is not next_directory:
            if previous_directory is not None:
                previous_directory.remove_change_listener(self._on_session_change)
            self._bound_hub_directory = next_directory
            if next_directory is not None:
                next_directory.add_change_listener(self._on_session_change)
        self._bound_hub_runtime = next_runtime
