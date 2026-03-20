from __future__ import annotations

from typing import ClassVar

from PySide6.QtCore import Property, QObject, Signal, Slot

from app.backend._tools_common import _as_dict
from app.backend._tools_probe import ToolsServiceProbeMixin
from app.backend._tools_projection import ToolsServiceProjectionMixin
from app.backend.asyncio_runner import AsyncioRunner
from app.backend.config import ConfigService
from app.backend.list_model import KeyValueListModel
from bao.agent.tool_catalog import ToolCatalog
from bao.agent.tool_probe_cache import load_probe_results
from bao.runtime_diagnostics import get_runtime_diagnostics_store


class ToolsService(ToolsServiceProbeMixin, ToolsServiceProjectionMixin, QObject):
    changed: ClassVar[Signal] = Signal()
    busyChanged: ClassVar[Signal] = Signal()
    errorChanged: ClassVar[Signal] = Signal(str)
    operationFinished: ClassVar[Signal] = Signal(str, bool)

    _runnerResult: ClassVar[Signal] = Signal(str, bool, str, object)

    def __init__(
        self,
        runner: AsyncioRunner,
        config_service: ConfigService,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._runner = runner
        self._config_service = config_service
        self._catalog = ToolCatalog()
        self._runtime_diagnostics = get_runtime_diagnostics_store()
        self._probe_cache_dir = self._resolve_probe_cache_dir()
        self._config_data: dict[str, object] = {}
        self._query = ""
        self._source_filter = "all"
        self._busy = False
        self._busy_count = 0
        self._error = ""
        self._items: list[dict[str, object]] = []
        self._catalog_model = KeyValueListModel(self)
        self._server_model = KeyValueListModel(self)
        self._selected_id = ""
        self._overview: dict[str, object] = {}
        self._probe_results: dict[str, dict[str, object]] = load_probe_results(self._probe_cache_dir)
        _ = self._runnerResult.connect(self._handle_runner_result)

    @Property(str, notify=changed)
    def query(self) -> str:
        return self._query

    @Property(str, notify=changed)
    def sourceFilter(self) -> str:
        return self._source_filter

    @Property(bool, notify=busyChanged)
    def busy(self) -> bool:
        return self._busy

    @Property(str, notify=errorChanged)
    def lastError(self) -> str:
        return self._error

    @Property(QObject, constant=True)
    def catalogModel(self) -> QObject:
        return self._catalog_model

    @Property(QObject, constant=True)
    def serverModel(self) -> QObject:
        return self._server_model

    @Property(int, notify=changed)
    def catalogCount(self) -> int:
        return self._catalog_model.rowCount()

    @Property(int, notify=changed)
    def serverCount(self) -> int:
        return self._server_model.rowCount()

    @Property(str, notify=changed)
    def firstCatalogItemId(self) -> str:
        items = self._catalog_model.items()
        return str(items[0].get("id", "")) if items else ""

    @Property(str, notify=changed)
    def firstServerItemId(self) -> str:
        items = self._server_model.items()
        return str(items[0].get("id", "")) if items else ""

    @Property(dict, notify=changed)
    def selectedItem(self) -> dict[str, object]:
        return self._selected_item()

    @Property(str, notify=changed)
    def selectedItemId(self) -> str:
        return self._selected_id

    @Property(dict, notify=changed)
    def overview(self) -> dict[str, object]:
        return dict(self._overview)

    @Slot("QVariant")
    def setConfigData(self, data: object) -> None:
        next_data = _as_dict(data) or {}
        self._config_data = dict(next_data)
        self._reload_probe_cache()
        self._refresh()

    @Slot(str)
    def setQuery(self, value: str) -> None:
        next_value = value.strip()
        if next_value == self._query:
            return
        self._query = next_value
        self._refresh()

    @Slot(str)
    def setSourceFilter(self, value: str) -> None:
        next_value = value if value in {"all", "builtin", "mcp", "attention"} else "all"
        if next_value == self._source_filter:
            return
        self._source_filter = next_value
        self._refresh()

    @Slot(str)
    def selectItem(self, item_id: str) -> None:
        target = next((item for item in self._items if item.get("id") == item_id), None)
        if target is None:
            return
        self._selected_id = item_id
        self.changed.emit()

    @Slot("QVariant", result=bool)
    def saveConfig(self, changes: object) -> bool:
        change_map = _as_dict(changes)
        if change_map is None:
            self._reject("Invalid config payload.")
            return False
        return self._save_patch(change_map, success_code="saved", failure_code="Save failed")

    @Slot("QVariant", result=bool)
    def saveMcpServer(self, payload: object) -> bool:
        data = _as_dict(payload)
        if data is None:
            self._reject("Invalid MCP server payload.")
            return False
        try:
            previous_name, next_name, server_value = self._normalize_server_payload(data)
        except ValueError as exc:
            self._reject(str(exc))
            return False

        current_servers = self._current_mcp_servers()
        if next_name in current_servers and next_name != previous_name:
            self._reject(f"MCP server already exists: {next_name}")
            return False
        if previous_name and previous_name != next_name:
            current_servers.pop(previous_name, None)
            self._probe_results.pop(previous_name, None)
        current_servers[next_name] = server_value
        if not self._save_patch(
            {"tools.mcpServers": current_servers},
            success_code="saved",
            failure_code="Save failed",
        ):
            return False
        if previous_name and previous_name != next_name:
            self._delete_probe_result(previous_name)
        self._schedule_probe(next_name, server_value)
        return True

    @Slot(str, result=bool)
    def deleteMcpServer(self, name: str) -> bool:
        target = name.strip()
        if not target:
            return False
        current_servers = self._current_mcp_servers()
        if target not in current_servers:
            return False
        current_servers.pop(target, None)
        self._delete_probe_result(target)
        return self._save_patch(
            {"tools.mcpServers": current_servers},
            success_code="deleted",
            failure_code="Delete failed",
        )

    @Slot(str)
    def testMcpServer(self, name: str) -> None:
        target = name.strip()
        if not target:
            return
        current_servers = self._current_mcp_servers()
        raw_cfg = current_servers.get(target)
        cfg_dict = _as_dict(raw_cfg)
        if cfg_dict is None:
            message = f"Unknown MCP server: {target}"
            self._set_error(message)
            self.operationFinished.emit(message, False)
            return
        self._submit_task("probe_server", self._probe_server(target, cfg_dict))

    @Slot("QVariant")
    def probeMcpServerPayload(self, payload: object) -> None:
        data = _as_dict(payload)
        if data is None:
            self._reject("Invalid MCP server payload.")
            return
        try:
            _previous_name, next_name, server_value = self._normalize_server_payload(data)
        except ValueError as exc:
            self._reject(str(exc))
            return
        self._submit_task("probe_server", self._probe_server(next_name, server_value))

    def _current_mcp_servers(self) -> dict[str, object]:
        return dict(_as_dict(self._config_service.get("tools.mcpServers", {})) or {})
