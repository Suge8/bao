from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.backend.asyncio_runner import AsyncioRunner
from app.backend.profile import ProfileService
from app.backend.profile_supervisor import (
    _SNAPSHOT_FILENAME,
    ProfileSupervisorServices,
    ProfileWorkSupervisorService,
)
from bao.profile import profile_context_from_mapping
from tests._profile_supervisor_service_snapshot import WorkSnapshotRequest, write_work_snapshot
from tests._profile_supervisor_service_testkit import (
    DummyChatService,
    DummyCronService,
    DummyHeartbeatService,
    DummySessionService,
    SessionItemRequest,
    cron_item,
    session_item,
    write_workspace,
)


@dataclass
class SupervisorHarness:
    runner: AsyncioRunner
    supervisor: ProfileWorkSupervisorService
    profile_service: ProfileService
    session_service: DummySessionService
    chat_service: DummyChatService
    cron_service: DummyCronService
    heartbeat_service: DummyHeartbeatService
    work_id: str


def build_supervisor(tmp_path: Path) -> SupervisorHarness:
    shared_workspace = tmp_path / "workspace"
    write_workspace(shared_workspace)
    profile_service = ProfileService()
    profile_service.refreshFromWorkspace(str(shared_workspace))
    profile_service.createProfile("Work")
    work_context = profile_context_from_mapping(profile_service.activeProfileContext)
    assert work_context is not None
    work_id = str(work_context.profile_id)
    write_work_snapshot(
        _SNAPSHOT_FILENAME,
        WorkSnapshotRequest(profile_context=work_context, session_key="telegram:work-room"),
    )
    profile_service.activateProfile("default")
    active_context = profile_context_from_mapping(profile_service.activeProfileContext)
    assert active_context is not None
    session_service, chat_service, cron_service, heartbeat_service = _build_services(active_context.heartbeat_file)
    runner = AsyncioRunner()
    runner.start()
    supervisor = ProfileWorkSupervisorService(
        runner,
        services=ProfileSupervisorServices(
            profile_service=profile_service,
            session_service=session_service,
            chat_service=chat_service,
            cron_service=cron_service,
            heartbeat_service=heartbeat_service,
        ),
    )
    return SupervisorHarness(
        runner=runner,
        supervisor=supervisor,
        profile_service=profile_service,
        session_service=session_service,
        chat_service=chat_service,
        cron_service=cron_service,
        heartbeat_service=heartbeat_service,
        work_id=work_id,
    )


def _build_services(heartbeat_file: Path) -> tuple[
    DummySessionService,
    DummyChatService,
    DummyCronService,
    DummyHeartbeatService,
]:
    return (
        DummySessionService(_default_sessions()),
        DummyChatService(),
        DummyCronService([cron_item("daily-review")]),
        DummyHeartbeatService(heartbeat_file, running=True),
    )


def _default_sessions() -> list[dict[str, object]]:
    return [
        session_item(
            SessionItemRequest(
                key="desktop:local::main",
                title="Main Thread",
                updated_at="2026-03-14T12:04:00+00:00",
                channel="desktop",
                visual_channel="desktop",
                is_child_session=False,
            )
        ),
        session_item(
            SessionItemRequest(
                key="subagent:child",
                title="Code Worker",
                updated_at="2026-03-14T12:05:00+00:00",
                channel="desktop",
                visual_channel="desktop",
                is_child_session=True,
                parent_session_key="desktop:local::main",
            )
        ),
    ]
