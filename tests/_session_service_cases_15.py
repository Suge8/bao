# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._session_service_testkit import *


class _DirectoryWithoutDiscovery:
    def __init__(self, base_directory):
        self._base_directory = base_directory

    def list_sessions_with_active_key(self, natural_key):
        return self._base_directory.list_sessions_with_active_key(natural_key)

    def add_change_listener(self, listener):
        return self._base_directory.add_change_listener(listener)

    def remove_change_listener(self, listener):
        return self._base_directory.remove_change_listener(listener)


def _mock_discovery_directory(base_directory, **overrides):
    directory = MagicMock()
    directory.list_sessions_with_active_key.side_effect = base_directory.list_sessions_with_active_key
    directory.add_change_listener.side_effect = base_directory.add_change_listener
    directory.remove_change_listener.side_effect = base_directory.remove_change_listener
    for name, value in overrides.items():
        getattr(directory, name).return_value = value
    return directory


def test_session_discovery_refresh_populates_backend_snapshots():
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
        ports.directory = _mock_discovery_directory(
            base_directory,
            list_recent_sessions=[
                {
                    "session_ref": "sess_recent",
                    "session_key": "telegram:-100::main",
                    "title": "Bao Dev",
                    "channel": "telegram",
                    "availability": "active",
                }
            ],
            get_default_session={
                "session_ref": "sess_default",
                "session_key": "desktop:local::main",
                "title": "Main",
                "channel": "desktop",
                "default": True,
            },
            lookup_sessions=[],
            resolve_session_ref={},
        )
        svc.initialize(ports)

        _spin_until(lambda: svc.recentSessionsModel.rowCount() == 1)

        assert svc.recentSessions[0]["session_ref"] == "sess_recent"
        assert svc.defaultSession["session_ref"] == "sess_default"
        assert svc.defaultSession["default"] is True
    finally:
        runner.shutdown(grace_s=1.0)


def test_session_discovery_lookup_and_resolve_use_directory_results():
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
        ports.directory = _mock_discovery_directory(
            base_directory,
            list_recent_sessions=[],
            get_default_session={},
            lookup_sessions=[
                {
                    "session_ref": "sess_lookup",
                    "session_key": "imessage:+61400::focus",
                    "title": "Alice",
                    "channel": "imessage",
                    "reason": "handle_match",
                }
            ],
            resolve_session_ref={
                "session_ref": "sess_lookup",
                "session_key": "imessage:+61400::focus",
                "title": "Alice",
                "channel": "imessage",
            },
        )
        svc.initialize(ports)

        svc.setSessionLookupQuery("alice")
        _spin_until(lambda: svc.lookupResultsModel.rowCount() == 1)
        assert svc.sessionLookupQuery == "alice"
        assert svc.lookupResults[0]["reason"] == "handle_match"
        assert svc.lookupResults[0]["id"] == "sess_lookup"

        svc.resolveSessionReference("sess_lookup")
        _spin_until(lambda: svc.resolvedSession.get("session_ref", "") == "sess_lookup")
        assert svc.resolvedSessionRef == "sess_lookup"
        assert svc.resolvedSession["title"] == "Alice"
    finally:
        runner.shutdown(grace_s=1.0)


def test_session_discovery_clears_when_directory_methods_are_unavailable():
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
        ports.directory = _DirectoryWithoutDiscovery(base_directory)
        svc.initialize(ports)
        svc._recent_sessions = [{"id": "stale", "session_ref": "stale"}]
        svc._lookup_results = [{"id": "stale", "session_ref": "stale"}]
        svc._default_session = {"id": "stale", "session_ref": "stale"}
        svc._resolved_session = {"id": "stale", "session_ref": "stale"}

        svc.refreshSessionDiscovery()

        assert svc.recentSessions == []
        assert svc.lookupResults == []
        assert svc.defaultSession == {}
        assert svc.resolvedSession == {}
    finally:
        runner.shutdown(grace_s=1.0)
