from __future__ import annotations

import importlib
from pathlib import Path

from tests._cron_bridge_testkit import start_bridge_service, wait_until

pytest = importlib.import_module("pytest")
pytestmark = [pytest.mark.integration, pytest.mark.gui]


def test_selecting_existing_task_restores_saved_fields_after_new_draft(
    monkeypatch, tmp_path: Path
) -> None:
    from bao.cron.types import CronSchedule

    runner, service = start_bridge_service(monkeypatch, tmp_path)
    try:
        job = service._local_cron.add_job(
            name="Existing Task",
            schedule=CronSchedule(kind="every", every_ms=180 * 60_000),
            message="Run the saved task",
        )
        service.refresh()
        wait_until(lambda: service.totalTaskCount == 1)
        service.newDraft()
        wait_until(lambda: service.visibleTaskCount == 2)

        service.selectTask(job.id)
        wait_until(
            lambda: (
                service.selectedTaskId == job.id
                and isinstance(service.property("draft"), dict)
                and service.property("draft").get("name") == "Existing Task"
            )
        )

        draft = service.property("draft")
        assert isinstance(draft, dict)
        assert draft["name"] == "Existing Task"
        assert draft["message"] == "Run the saved task"
        assert service.visibleTaskCount == 1
    finally:
        runner.shutdown(grace_s=1.0)


def test_reselecting_same_task_repairs_stale_empty_draft(
    monkeypatch, tmp_path: Path
) -> None:
    from app.backend.cron import _empty_draft
    from bao.cron.types import CronSchedule

    runner, service = start_bridge_service(monkeypatch, tmp_path)
    try:
        job = service._local_cron.add_job(
            name="Existing Task",
            schedule=CronSchedule(kind="every", every_ms=180 * 60_000),
            message="Run the saved task",
        )
        service.refresh()
        wait_until(lambda: service.totalTaskCount == 1)
        service.selectTask(job.id)
        service._draft = _empty_draft()
        service._draft_dirty = True
        service.selectTask(job.id)

        draft = service.property("draft")
        assert isinstance(draft, dict)
        assert draft["id"] == job.id
        assert draft["name"] == "Existing Task"
        assert draft["message"] == "Run the saved task"
        assert service.editingNewTask is False
    finally:
        runner.shutdown(grace_s=1.0)
