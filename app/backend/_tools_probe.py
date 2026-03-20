from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from typing import Any

from PySide6.QtCore import Slot

from bao.agent.tool_probe_cache import delete_probe_result, save_probe_result
from bao.agent.tools.mcp import probe_mcp_server
from bao.config.schema import MCPServerConfig

from ._tools_common import _as_dict, _as_str


class ToolsServiceProbeMixin:
    def _submit_task(self, kind: str, coro: Coroutine[Any, Any, Any]) -> None:
        try:
            future = self._runner.submit(coro)
        except RuntimeError:
            coro.close()
            self._set_error("Asyncio runner is not available.")
            return
        self._set_busy(True)
        future.add_done_callback(lambda done, task_kind=kind: self._emit_runner_result(task_kind, done))

    def _save_patch(
        self,
        patch: dict[str, object],
        *,
        success_code: str,
        failure_code: str,
    ) -> bool:
        ok = self._config_service.save(patch)
        if not ok:
            self.operationFinished.emit(failure_code, False)
            return False
        self.setConfigData(self._config_service.exportData())
        self.operationFinished.emit(success_code, True)
        return True

    def _reject(self, message: str) -> None:
        self._set_error(message)
        self.operationFinished.emit(message, False)

    def _emit_runner_result(self, kind: str, future: Any) -> None:
        try:
            payload = future.result()
            self._runnerResult.emit(kind, True, "", payload)
        except asyncio.CancelledError:
            self._runnerResult.emit(kind, False, "cancelled", None)
        except Exception as exc:
            self._runnerResult.emit(kind, False, str(exc), None)

    @Slot(str, bool, str, object)
    def _handle_runner_result(self, *args: object) -> None:
        kind, ok, message, payload = self._runner_result_args(args)
        self._set_busy(False)
        if kind != "probe_server":
            return
        if not ok:
            self._set_error(message)
            self.operationFinished.emit(message, False)
            return
        result = _as_dict(payload) or {}
        name = _as_str(result.get("serverName", ""))
        if name:
            self._probe_results[name] = dict(
                save_probe_result(self._probe_cache_dir, name, dict(result))
            )
        self._refresh()
        can_connect = bool(result.get("canConnect"))
        message_code = "probe_ok" if can_connect else _as_str(result.get("error", "probe_failed"))
        self.operationFinished.emit(message_code, can_connect)

    @staticmethod
    def _runner_result_args(args: tuple[object, ...]) -> tuple[str, bool, str, object]:
        kind = str(args[0]) if len(args) > 0 else ""
        ok = bool(args[1]) if len(args) > 1 else False
        message = _as_str(args[2], "") if len(args) > 2 else ""
        payload = args[3] if len(args) > 3 else None
        return kind, ok, message, payload

    async def _probe_server(self, name: str, config_value: dict[str, object]) -> dict[str, object]:
        cfg = MCPServerConfig.model_validate(config_value)
        return await probe_mcp_server(name, cfg)

    def _schedule_probe(self, name: str, config_value: dict[str, object]) -> None:
        self._submit_task("probe_server", self._probe_server(name, config_value))

    def _normalize_server_payload(
        self,
        payload: dict[str, object],
    ) -> tuple[str, str, dict[str, object]]:
        previous_name = _as_str(payload.get("previousName", "")).strip()
        next_name = _as_str(payload.get("name", "")).strip()
        if not next_name:
            raise ValueError("Server name is required.")

        transport = _as_str(payload.get("transport", "stdio"), "stdio").strip().lower()
        if transport not in {"stdio", "http"}:
            transport = "stdio"
        command = _as_str(payload.get("command", "")).strip()
        url = _as_str(payload.get("url", "")).strip()
        if transport == "stdio" and not command:
            raise ValueError("Command is required for stdio MCP servers.")
        if transport == "http" and not url:
            raise ValueError("URL is required for HTTP MCP servers.")

        server_value: dict[str, object] = {
            "command": command if transport == "stdio" else "",
            "args": self._parse_multiline_list(_as_str(payload.get("argsText", ""))),
            "env": self._parse_key_values(_as_str(payload.get("envText", "")), separators=("=",)),
            "url": url if transport == "http" else "",
            "headers": self._parse_key_values(
                _as_str(payload.get("headersText", "")),
                separators=(":", "="),
            ),
            "toolTimeoutSeconds": max(1, self._coerce_int(payload.get("toolTimeoutSeconds"), 30)),
            "maxTools": self._normalize_optional_int(payload.get("maxTools")),
            "slimSchema": payload.get("slimSchema")
            if isinstance(payload.get("slimSchema"), bool)
            else None,
        }
        return previous_name, next_name, server_value

    @staticmethod
    def _parse_multiline_list(value: str) -> list[str]:
        return [line.strip() for line in value.splitlines() if line.strip()]

    @staticmethod
    def _parse_key_values(value: str, *, separators: tuple[str, ...]) -> dict[str, str]:
        result: dict[str, str] = {}
        for raw_line in value.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            pair: tuple[str, str] | None = None
            for separator in separators:
                if separator in line:
                    left, right = line.split(separator, 1)
                    pair = (left.strip(), right.strip())
                    break
            if pair is None or not pair[0]:
                raise ValueError(f"Invalid key/value line: {raw_line}")
            result[pair[0]] = pair[1]
        return result

    @staticmethod
    def _coerce_int(value: object, default: int) -> int:
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if stripped:
                try:
                    return int(stripped)
                except ValueError:
                    return default
        return default

    def _normalize_optional_int(self, value: object) -> int | None:
        coerced = self._coerce_int(value, 0)
        return coerced if coerced > 0 else None

    def _delete_probe_result(self, name: str) -> None:
        self._probe_results.pop(name, None)
        delete_probe_result(self._probe_cache_dir, name)
