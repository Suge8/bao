from __future__ import annotations

from pathlib import Path

from app.backend.list_model import build_selection_projection
from bao.agent.capability_registry import (
    CapabilityRegistryRequest,
    build_capability_registry_snapshot,
)
from bao.agent.tool_probe_cache import load_probe_results


class ToolsServiceProjectionMixin:
    def _refresh(self) -> None:
        diagnostics_snapshot = self._runtime_diagnostics.snapshot(
            max_events=0,
            max_log_lines=0,
        )
        snapshot = build_capability_registry_snapshot(
            catalog=self._catalog,
            request=CapabilityRegistryRequest(
                config_data=self._config_data,
                probe_results=self._probe_results,
                query=self._query.lower(),
                source_filter=self._source_filter,
                selected_id=self._selected_id,
                tool_observability=diagnostics_snapshot.get("tool_observability", {}),
            ),
        )
        next_overview = dict(snapshot.overview)
        selection = build_selection_projection(
            [dict(item) for item in snapshot.items],
            preferred_id=snapshot.selected_id or self._selected_id,
        )
        next_items = selection.items
        if (
            next_overview == self._overview
            and next_items == self._items
            and selection.selected_id == self._selected_id
        ):
            return
        self._overview = next_overview
        self._items = next_items
        self._catalog_model.sync_items(self._items_for_kind("builtin"))
        self._server_model.sync_items(self._items_for_kind("mcp_server"))
        self._selected_id = selection.selected_id
        self.changed.emit()

    def _selected_item(self) -> dict[str, object]:
        if not self._selected_id:
            return {}
        return next(
            (dict(item) for item in self._items if str(item.get("id", "")) == self._selected_id),
            {},
        )

    def _items_for_kind(self, kind: str) -> list[dict[str, object]]:
        return [dict(item) for item in self._items if str(item.get("kind", "")) == kind]

    def _resolve_probe_cache_dir(self) -> Path:
        config_path = self._config_service.getConfigFilePath()
        if config_path:
            return Path(config_path).expanduser().resolve().parent
        return Path.home() / ".bao"

    def _reload_probe_cache(self) -> None:
        self._probe_cache_dir = self._resolve_probe_cache_dir()
        cached = load_probe_results(self._probe_cache_dir)
        current_servers = set(self._current_mcp_servers())
        self._probe_results = {
            name: dict(result)
            for name, result in cached.items()
            if not current_servers or name in current_servers
        }

    def _set_busy(self, active: bool) -> None:
        self._busy_count = max(0, self._busy_count + (1 if active else -1))
        next_busy = self._busy_count > 0
        if next_busy == self._busy:
            return
        self._busy = next_busy
        self.busyChanged.emit()

    def _set_error(self, message: str) -> None:
        if message == self._error:
            return
        self._error = message
        self.errorChanged.emit(message)
