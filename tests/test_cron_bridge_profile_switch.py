from __future__ import annotations

import importlib
from pathlib import Path

from tests._cron_bridge_testkit import start_bridge_service, wait_until

pytest = importlib.import_module("pytest")
pytestmark = [pytest.mark.integration, pytest.mark.gui]


def test_bridge_bootstraps_local_store_from_active_profile(monkeypatch, tmp_path: Path) -> None:
    from bao.profile import CreateProfileOptions, create_profile

    shared_workspace = tmp_path / "workspace"
    _registry, work_context = create_profile(
        "Work",
        CreateProfileOptions(shared_workspace=shared_workspace, data_dir=tmp_path),
    )

    runner, service = start_bridge_service(monkeypatch, tmp_path)
    try:
        assert Path(service._local_cron.store_path) == work_context.cron_store_path
    finally:
        runner.shutdown(grace_s=1.0)


def test_profile_switch_uses_current_profile_store_even_if_live_cron_is_stale(
    monkeypatch, tmp_path: Path
) -> None:
    from bao.cron.service import CronService
    from bao.cron.types import CronSchedule

    runner, service = start_bridge_service(monkeypatch, tmp_path)
    try:
        stale_live = service._local_cron
        stale_live.add_job(
            name="Default Task",
            schedule=CronSchedule(kind="every", every_ms=60_000),
            message="default",
        )

        next_store_path = tmp_path / "profiles" / "work" / "cron" / "jobs.json"
        next_store = CronService(next_store_path)
        next_store.add_job(
            name="Work Task",
            schedule=CronSchedule(kind="every", every_ms=120_000),
            message="work",
        )

        service.setLiveCronService(stale_live)
        service.setLocalStorePath(str(next_store_path))
        wait_until(
            lambda: (
                isinstance(service.property("selectedTask"), dict)
                and service.property("selectedTask").get("name") == "Work Task"
            )
        )
        selected = service.property("selectedTask")
        assert isinstance(selected, dict)
        assert selected["name"] == "Work Task"
    finally:
        runner.shutdown(grace_s=1.0)


def test_run_now_is_blocked_while_live_cron_targets_previous_profile(
    monkeypatch, tmp_path: Path
) -> None:
    from bao.cron.service import CronService
    from bao.cron.types import CronSchedule

    runner, service = start_bridge_service(monkeypatch, tmp_path)
    try:
        stale_live = service._local_cron
        stale_live.add_job(
            name="Default Task",
            schedule=CronSchedule(kind="every", every_ms=60_000),
            message="default",
        )

        next_store_path = tmp_path / "profiles" / "work" / "cron" / "jobs.json"
        next_store = CronService(next_store_path)
        work_job = next_store.add_job(
            name="Work Task",
            schedule=CronSchedule(kind="every", every_ms=120_000),
            message="work",
        )

        service.setLiveCronService(stale_live)
        service.setHubRunning(True)
        service.setLocalStorePath(str(next_store_path))
        wait_until(
            lambda: (
                isinstance(service.property("selectedTask"), dict)
                and service.property("selectedTask").get("name") == "Work Task"
            )
        )

        assert service.canRunSelectedNow is False
        assert service.runNowBlockedReason == "Switching to the current profile. Try again in a moment"
        service.runSelectedNow()
        wait_until(lambda: not service.busy)

        selected = service.property("selectedTask")
        refreshed_job = next(job for job in next_store.list_jobs(True) if job.id == work_job.id)
        assert isinstance(selected, dict)
        assert selected["name"] == "Work Task"
        assert service.noticeText == "Switching to the current profile. Try again in a moment"
        assert service.noticeSuccess is False
        assert refreshed_job.state.last_run_at_ms is None
    finally:
        runner.shutdown(grace_s=1.0)
