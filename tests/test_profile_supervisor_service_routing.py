# ruff: noqa: E402, N802, N815
from __future__ import annotations

from pathlib import Path

from tests._profile_supervisor_service_harness import build_supervisor
from tests._profile_supervisor_service_testkit import wait_until

pytest_plugins = ("tests._profile_supervisor_service_testkit",)


def test_supervisor_queues_cross_profile_session_open(tmp_path: Path, qt_app, fake_home: Path) -> None:
    _ = qt_app
    _ = fake_home
    harness = build_supervisor(tmp_path)
    try:
        routes: list[str] = []
        harness.supervisor.profileNavigationRequested.connect(routes.append)
        harness.supervisor.refresh()
        wait_until(lambda: harness.supervisor.overview.get("profileCount") == 2)
        harness.supervisor.selectProfile(harness.work_id)
        wait_until(lambda: harness.supervisor.selectedProfile.get("id") == harness.work_id)
        target = next(
            item
            for item in harness.supervisor.automationModel._items
            if item["profileId"] == harness.work_id and item["routeKind"] == "cron"
        )
        harness.supervisor.selectItem(str(target["id"]))
        harness.supervisor.openSelectedTarget()
        assert harness.profile_service.activeProfileId == harness.work_id
        assert harness.session_service.selected == []
        harness.session_service.hubLocalPortsReady.emit(object())
        assert routes == ["cron"]
        assert harness.cron_service.selected == [str(target["routeValue"])]
    finally:
        harness.runner.shutdown(grace_s=1.0)


def test_supervisor_uses_profile_service_registry_snapshot(
    tmp_path: Path, fake_home: Path, monkeypatch
) -> None:
    _ = fake_home
    harness = build_supervisor(tmp_path)
    try:
        import app.backend.profile_supervisor as profile_supervisor_module

        monkeypatch.setattr(
            profile_supervisor_module,
            "ensure_profile_registry",
            lambda _shared_workspace: (_ for _ in ()).throw(
                AssertionError("supervisor should consume ProfileService.registrySnapshot")
            ),
        )
        harness.supervisor.refresh()
        wait_until(lambda: harness.supervisor.overview.get("profileCount") == 2)
        assert harness.supervisor.overview["liveProfileId"] == "default"
    finally:
        harness.runner.shutdown(grace_s=1.0)
