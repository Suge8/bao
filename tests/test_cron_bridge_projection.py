from __future__ import annotations

import importlib
from pathlib import Path

from tests._cron_bridge_testkit import (
    FakeSessionService,
    start_bridge_service,
    wait_until,
)

pytest = importlib.import_module("pytest")
pytestmark = [pytest.mark.integration, pytest.mark.gui]


def test_cron_bridge_refreshes_and_selects_first_job(monkeypatch, tmp_path: Path) -> None:
    from bao.cron.types import CronSchedule

    runner, service = start_bridge_service(monkeypatch, tmp_path)
    try:
        service._local_cron.add_job(
            name="Morning Briefing",
            schedule=CronSchedule(kind="every", every_ms=60_000),
            message="Send summary",
        )
        service.refresh()
        wait_until(lambda: service.totalTaskCount == 1)

        selected_task = service.property("selectedTask")
        draft = service.property("draft")
        tasks_model = service.property("tasksModel")
        assert service.selectedTaskId
        assert isinstance(selected_task, dict)
        assert isinstance(draft, dict)
        assert selected_task["name"] == "Morning Briefing"
        assert draft["name"] == "Morning Briefing"
        assert tasks_model.rowCount() == 1
    finally:
        runner.shutdown(grace_s=1.0)


def test_cron_bridge_can_create_and_update_job(monkeypatch, tmp_path: Path) -> None:
    runner, service = start_bridge_service(monkeypatch, tmp_path)
    try:
        service.newDraft()
        service.updateDraftField("name", "Nightly Review")
        service.updateDraftField("schedule_kind", "cron")
        service.updateDraftField("cron_expr", "0 21 * * *")
        service.updateDraftField("timezone", "Australia/Sydney")
        service.updateDraftField("message", "Review the project status")
        service.saveDraft()
        wait_until(
            lambda: (
                service.totalTaskCount == 1
                and not service.busy
                and isinstance(service.property("selectedTask"), dict)
                and service.property("selectedTask").get("name") == "Nightly Review"
            )
        )

        selected = service.property("selectedTask")
        assert service.noticeText == "Task created"
        assert isinstance(selected, dict)
        assert selected["name"] == "Nightly Review"
        assert selected["schedule_kind"] == "cron"

        service.updateDraftField("name", "Nightly Digest")
        service.saveDraft()
        wait_until(
            lambda: (
                isinstance(service.property("selectedTask"), dict)
                and service.property("selectedTask").get("name") == "Nightly Digest"
                and not service.busy
            )
        )

        updated_task = service.property("selectedTask")
        assert isinstance(updated_task, dict)
        assert updated_task["name"] == "Nightly Digest"
        assert service.noticeText == "Task updated"
    finally:
        runner.shutdown(grace_s=1.0)


def test_cron_bridge_opens_selected_session(monkeypatch, tmp_path: Path) -> None:
    from bao.cron.types import CronSchedule

    runner, service = start_bridge_service(monkeypatch, tmp_path)
    try:
        fake_session_service = FakeSessionService()
        service.setSessionService(fake_session_service)
        job = service._local_cron.add_job(
            name="Ping",
            schedule=CronSchedule(kind="every", every_ms=120_000),
            message="Ping me",
        )
        service.refresh()
        wait_until(lambda: service.totalTaskCount == 1)
        service.selectTask(job.id)
        service.openSelectedSession()
        assert fake_session_service.selected == [f"cron:{job.id}"]
    finally:
        runner.shutdown(grace_s=1.0)


def test_cron_bridge_localizes_projection(monkeypatch, tmp_path: Path) -> None:
    from bao.cron.types import CronSchedule

    runner, service = start_bridge_service(monkeypatch, tmp_path)
    try:
        service.setLanguage("zh")
        service._local_cron.add_job(
            name="中文任务",
            schedule=CronSchedule(kind="every", every_ms=180 * 60_000),
            message="发送中文摘要",
        )
        service.refresh()
        wait_until(
            lambda: (
                isinstance(service.property("selectedTask"), dict)
                and service.property("selectedTask").get("name") == "中文任务"
            ),
            timeout_ms=4000,
        )
        task = service.property("selectedTask")
        assert isinstance(task, dict)
        assert service.totalTaskCount == 1
        assert task["status_label"] == "已调度"
        assert "每 3 小时" in task["schedule_summary"]
        assert "从未执行" in task["last_result_text"]
    finally:
        runner.shutdown(grace_s=1.0)


def test_new_draft_clears_selection(monkeypatch, tmp_path: Path) -> None:
    from app.backend.cron import _DRAFT_PREVIEW_ID
    from bao.cron.types import CronSchedule

    runner, service = start_bridge_service(monkeypatch, tmp_path)
    try:
        job = service._local_cron.add_job(
            name="Existing Task",
            schedule=CronSchedule(kind="every", every_ms=60_000),
            message="Run existing task",
        )
        service.refresh()
        wait_until(lambda: service.totalTaskCount == 1)
        service.selectTask(job.id)
        assert service.selectedTaskId == job.id
        service.newDraft()

        model = service.property("tasksModel")
        draft = service.property("draft")
        assert service.selectedTaskId == ""
        assert service.hasSelection is False
        assert service.editingNewTask is True
        assert service.activeListItemId == _DRAFT_PREVIEW_ID
        assert service.totalTaskCount == 2
        assert service.visibleTaskCount == 2
        assert model.rowCount() == 2
        assert isinstance(draft, dict)
        assert draft.get("id") == ""
    finally:
        runner.shutdown(grace_s=1.0)
