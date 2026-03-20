# ruff: noqa: E402, N802, N815
from __future__ import annotations

from pathlib import Path

from app.backend.profile_supervisor import _has_session_storage_roots
from tests._profile_supervisor_service_harness import build_supervisor
from tests._profile_supervisor_service_testkit import model_items, profile_items, wait_until

pytest_plugins = ("tests._profile_supervisor_service_testkit",)


def test_has_session_storage_roots_ignores_non_directory_placeholders(tmp_path: Path) -> None:
    state_root = tmp_path / "state"
    state_root.mkdir(parents=True, exist_ok=True)
    (state_root / "sessions").write_text("broken", encoding="utf-8")
    assert _has_session_storage_roots(state_root) is False


def test_supervisor_projects_live_and_snapshot_profiles(tmp_path: Path, qt_app, fake_home: Path) -> None:
    _ = qt_app
    _ = fake_home
    harness = build_supervisor(tmp_path)
    try:
        harness.supervisor.refresh()
        wait_until(lambda: harness.supervisor.overview.get("profileCount") == 2)
        assert harness.supervisor.overview["workingCount"] == 2
        assert harness.supervisor.overview["automationCount"] == 3
        assert harness.supervisor.selectedProfile == {}
        assert all(item["profileId"] == "default" for item in model_items(harness.supervisor.workingModel))
        default_profile = next(item for item in profile_items(harness.supervisor) if item["id"] == "default")
        work_profile = next(item for item in profile_items(harness.supervisor) if item["id"] == harness.work_id)
        assert default_profile["totalSessionCount"] == 1
        assert default_profile["totalChildSessionCount"] == 1
        assert default_profile["channelKeys"] == ["desktop", "telegram"]
        assert work_profile["totalSessionCount"] == 1
        assert work_profile["channelKeys"] == ["telegram"]
        assert work_profile["workingCount"] == 0
        assert any(item["id"] == harness.work_id and item["isLive"] is False for item in profile_items(harness.supervisor))
    finally:
        harness.runner.shutdown(grace_s=1.0)


def test_supervisor_stays_idle_until_hydrated(tmp_path: Path, qt_app, fake_home: Path) -> None:
    _ = qt_app
    _ = fake_home
    harness = build_supervisor(tmp_path)
    try:
        harness.profile_service.activateProfile(harness.work_id)
        harness.session_service.hubLocalPortsReady.emit(object())
        from tests._profile_supervisor_service_testkit import spin

        spin(150)
        assert harness.supervisor.overview == {}
        assert profile_items(harness.supervisor) == []
        harness.supervisor.hydrateIfNeeded()
        wait_until(lambda: harness.supervisor.overview.get("profileCount") == 2)
        assert any(item["id"] == harness.work_id for item in profile_items(harness.supervisor))
    finally:
        harness.runner.shutdown(grace_s=1.0)


def test_supervisor_refresh_if_hydrated_keeps_idle_when_cold(tmp_path: Path, qt_app, fake_home: Path) -> None:
    _ = qt_app
    _ = fake_home
    harness = build_supervisor(tmp_path)
    try:
        harness.supervisor.refreshIfHydrated()
        from tests._profile_supervisor_service_testkit import spin

        spin(150)
        assert harness.supervisor.overview == {}
        assert profile_items(harness.supervisor) == []
    finally:
        harness.runner.shutdown(grace_s=1.0)
