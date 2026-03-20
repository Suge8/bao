# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from types import SimpleNamespace

from bao.profile import ProfileContext, profile_context_to_dict
from tests._chat_service_testkit import _hub_local_ports
from tests._chat_service_testkit import *


def _profile_context(name: str, root: Path) -> ProfileContext:
    return ProfileContext(
        profile_id=name,
        display_name=name.title(),
        storage_key=name,
        shared_workspace_path=root / "workspace",
        profile_root=root / "profiles" / name,
        prompt_root=root / "profiles" / name / "prompt",
        state_root=root / "profiles" / name / "state",
        cron_store_path=root / "profiles" / name / "cron" / "jobs.json",
        heartbeat_file=root / "profiles" / name / "prompt" / "HEARTBEAT.md",
    )


class _DispatcherProfileSyncDouble:
    def __init__(self, current_profile_id: str, *, default_services, work_services) -> None:
        self.current_profile_id = current_profile_id
        self._services = {
            "default": default_services,
            "work": work_services,
        }

    def set_current_profile(self, profile_id: object) -> bool:
        normalized = str(profile_id or "").strip() or self.current_profile_id
        changed = normalized != self.current_profile_id
        self.current_profile_id = normalized
        return changed

    @property
    def agent(self):
        return self._services[self.current_profile_id]["agent"]

    @property
    def session_manager(self):
        return self._services[self.current_profile_id]["session_manager"]

    @property
    def directory(self):
        return _hub_local_ports(self.session_manager).directory

    @property
    def runtime_port(self):
        return _hub_local_ports(self.session_manager).runtime

    @property
    def cron(self):
        return self._services[self.current_profile_id]["cron"]

    @property
    def heartbeat(self):
        return self._services[self.current_profile_id]["heartbeat"]

    async def process_direct(self, _request):
        return "ok"


def test_current_profile_id_accepts_camel_case_profile_context(tmp_path) -> None:
    svc, _model = make_service()

    svc.setProfileContext(profile_context_to_dict(_profile_context("work", tmp_path)))

    assert svc._current_profile_id() == "work"


def test_set_profile_context_and_direct_send_sync_dispatcher_runtime(tmp_path) -> None:
    svc, _model = make_service()
    default_services = {
        "agent": SimpleNamespace(),
        "session_manager": _SessionManagerWithListeners(tmp_path / "default"),
        "cron": SimpleNamespace(status=lambda: {"jobs": 0}),
        "heartbeat": SimpleNamespace(interval_s=1800),
    }
    work_services = {
        "agent": SimpleNamespace(),
        "session_manager": _SessionManagerWithListeners(tmp_path / "work"),
        "cron": SimpleNamespace(status=lambda: {"jobs": 3}),
        "heartbeat": SimpleNamespace(interval_s=1200),
    }
    dispatcher = _DispatcherProfileSyncDouble(
        "default",
        default_services=default_services,
        work_services=work_services,
    )
    cron_events: list[object] = []
    heartbeat_events: list[object] = []
    ready_events: list[tuple[object, list[str]]] = []
    svc._dispatcher = dispatcher
    svc._cron = default_services["cron"]
    svc._heartbeat = default_services["heartbeat"]
    svc._enabled_hub_channels = ["desktop"]
    svc.cronServiceChanged.connect(cron_events.append)
    svc.heartbeatServiceChanged.connect(heartbeat_events.append)
    svc.hubReady.connect(
        lambda: ready_events.append((svc._current_hub_runtime().session_manager, list(svc._enabled_hub_channels)))
    )

    svc.setProfileContext(profile_context_to_dict(_profile_context("work", tmp_path)))
    assert dispatcher.current_profile_id == "work"
    assert svc._cron is work_services["cron"]
    assert svc._heartbeat is work_services["heartbeat"]
    assert cron_events[-1] is work_services["cron"]
    assert heartbeat_events[-1] is work_services["heartbeat"]

    result = asyncio.run(svc._call_agent("hello", "desktop:local::s1"))

    assert result == "ok"
    assert svc._session_manager is work_services["session_manager"]
    assert ready_events == [(work_services["session_manager"], ["desktop"])]
