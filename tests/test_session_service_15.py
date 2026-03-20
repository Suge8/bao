# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._session_service_cases_15 import *
from tests._session_service_cases_15 import _hub_local_ports, _make_mock_session_manager, _new_session_service


def test_session_discovery_clears_when_directory_only_exposes_partial_api():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        manager = _make_mock_session_manager(
            [
                {"key": "desktop:local::main", "title": "Main", "updated_at": 1, "channel": "desktop"},
            ]
        )
        ports = _hub_local_ports(manager)
        base_directory = ports.directory
        class _PartialDirectory:
            def list_sessions_with_active_key(self, natural_key):
                return base_directory.list_sessions_with_active_key(natural_key)

            def add_change_listener(self, listener):
                base_directory.add_change_listener(listener)

            def remove_change_listener(self, listener):
                base_directory.remove_change_listener(listener)

            def list_recent_sessions(self):
                return [{"session_ref": "stale", "session_key": "desktop:local::stale"}]

        ports.directory = _PartialDirectory()
        svc.initialize(ports)
        svc._recent_sessions = [{"id": "stale", "session_ref": "stale"}]
        svc._default_session = {"id": "stale", "session_ref": "stale"}

        svc.refreshSessionDiscovery()

        assert svc.recentSessions == []
        assert svc.defaultSession == {}
    finally:
        runner.shutdown(grace_s=1.0)
