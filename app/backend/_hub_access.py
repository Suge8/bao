from __future__ import annotations

from typing import Any

from bao.hub import HubControl


class DesktopHubAccess:
    def __init__(self) -> None:
        self._dispatcher_provider: Any = None
        self._local_ports: Any = None

    def set_dispatcher_provider(self, provider: Any) -> None:
        self._dispatcher_provider = provider if callable(provider) else None

    def set_local_ports(self, hub_local_ports: Any) -> None:
        self._local_ports = hub_local_ports

    def current_dispatcher(self) -> Any:
        provider = self._dispatcher_provider
        if not callable(provider):
            return None
        try:
            return provider()
        except Exception:
            return None

    def local_ports(self) -> Any:
        return self._local_ports

    def local_directory(self) -> Any:
        ports = self._local_ports
        return getattr(ports, "directory", None) if ports is not None else None

    def local_control(self) -> Any:
        ports = self._local_ports
        return getattr(ports, "control", None) if ports is not None else None

    def local_runtime(self) -> Any:
        ports = self._local_ports
        return getattr(ports, "runtime", None) if ports is not None else None

    def current_directory(self) -> Any:
        dispatcher = self.current_dispatcher()
        live_directory = getattr(dispatcher, "directory", None) if dispatcher is not None else None
        return live_directory or self.local_directory()

    def current_control(self) -> Any:
        dispatcher = self.current_dispatcher()
        if dispatcher is not None:
            return HubControl(dispatcher)
        return self.local_control()

    def current_runtime(self) -> Any:
        dispatcher = self.current_dispatcher()
        live_runtime = getattr(dispatcher, "runtime_port", None) if dispatcher is not None else None
        return live_runtime or self.local_runtime()
