from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from bao.profile import ProfileContext, ProfileSpec

from ._profile_supervisor_common import _now_iso
from ._profile_supervisor_live_helpers import (
    LiveProfileCardRequest,
    LiveSnapshotRequest,
    LiveUnitState,
    _build_snapshot,
    _live_profile_card,
    _live_workers,
)
from ._profile_supervisor_status_units import (
    HeartbeatWorkUnitRequest,
    HubIssueRequest,
    StartupActivityUnitRequest,
    _build_heartbeat_work_unit,
    _build_hub_issue,
    _build_startup_activity_unit,
)
from ._profile_supervisor_storage import _snapshot_path
from ._profile_supervisor_units import (
    CronWorkUnitsRequest,
    SessionWorkUnitsRequest,
    _build_cron_work_units,
    _build_session_work_units,
)
from ._profile_supervisor_view import (
    _avatar_source,
    _is_hub_live,
    _session_inventory,
)


@dataclass(frozen=True)
class LiveProfilePayloadRequest:
    context: ProfileContext
    spec: ProfileSpec
    sessions: list[dict[str, Any]]
    cron_items: list[dict[str, Any]]
    heartbeat_status: dict[str, Any]
    hub_state: str
    hub_detail: str
    hub_error: str
    hub_detail_is_error: bool
    hub_channels: list[object]
    startup_activity: dict[str, Any]


def build_live_profile_payload(request: LiveProfilePayloadRequest) -> dict[str, Any]:
    state = _live_unit_state(request)
    working, completed, automation, attention = _live_collections(state)
    workers = _live_workers(request, state)
    updated_at = _now_iso()
    snapshot = _build_snapshot(
        LiveSnapshotRequest(
            request=request,
            updated_at=updated_at,
            hub_live=state.hub_live,
            inventory=state.inventory,
            workers=workers,
            working=working,
            completed=completed,
            automation=automation,
            attention=attention,
            running_count=len(working),
        )
    )
    profile_card = _live_profile_card(
        LiveProfileCardRequest(
            request=request,
            state=state,
            updated_at=updated_at,
            working=working,
            automation=automation,
            attention=attention,
            workers=workers,
        )
    )
    return {
        "profile": profile_card,
        "working": working,
        "completed": completed,
        "automation": automation,
        "attention": attention,
        "snapshot_write": {
            "profileId": request.spec.id,
            "path": str(_snapshot_path(request.context)),
            "payload": snapshot,
        },
    }


def _live_unit_state(request: LiveProfilePayloadRequest) -> LiveUnitState:
    avatar_source = _avatar_source(request.spec.avatar_key)
    hub_live = _is_hub_live(request.hub_state)
    inventory = _session_inventory(request.sessions, hub_channels=request.hub_channels)
    session_units, session_workers = _build_session_work_units(
        SessionWorkUnitsRequest(
            profile_id=request.spec.id,
            avatar_source=avatar_source,
            sessions=request.sessions,
            is_live=True,
        )
    )
    cron_units, cron_workers, cron_issues = _build_cron_work_units(
        CronWorkUnitsRequest(
            profile_id=request.spec.id,
            avatar_source=avatar_source,
            cron_items=request.cron_items,
            is_live=True,
        )
    )
    heartbeat_unit, heartbeat_issue, startup_unit, hub_issue = _live_status_units(
        request,
        avatar_source,
    )
    return LiveUnitState(
        avatar_source=avatar_source,
        hub_live=hub_live,
        inventory=inventory,
        session_units=session_units,
        session_workers=session_workers,
        cron_units=cron_units,
        cron_workers=cron_workers,
        cron_issues=cron_issues,
        heartbeat_unit=heartbeat_unit,
        heartbeat_issue=heartbeat_issue,
        startup_unit=startup_unit,
        hub_issue=hub_issue,
    )


def _live_collections(
    state: LiveUnitState,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    working = [unit for unit in state.session_units if bool(unit.get("isRunning", False))] if state.hub_live else []
    completed = [
        unit
        for unit in state.session_units
        if str(unit.get("kind", "") or "") == "subagent_task"
        and str(unit.get("statusKey", "") or "") == "completed"
    ]
    if state.startup_unit is not None:
        if str(state.startup_unit.get("statusKey", "") or "") == "running":
            working.insert(0, state.startup_unit)
        elif str(state.startup_unit.get("statusKey", "") or "") == "completed":
            completed.insert(0, state.startup_unit)
    automation = state.cron_units + ([state.heartbeat_unit] if state.heartbeat_unit else [])
    attention = state.cron_issues + ([state.heartbeat_issue] if state.heartbeat_issue else [])
    if state.startup_unit is not None and str(state.startup_unit.get("statusKey", "") or "") == "error":
        attention.insert(0, state.startup_unit)
    if state.hub_issue is not None:
        attention.append(state.hub_issue)
    return working, completed, automation, attention


def _live_status_units(
    request: LiveProfilePayloadRequest,
    avatar_source: str,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None]:
    heartbeat_unit, heartbeat_issue = _build_heartbeat_work_unit(
        HeartbeatWorkUnitRequest(
            profile_id=request.spec.id,
            avatar_source=avatar_source,
            heartbeat_status=request.heartbeat_status,
            is_live=True,
        )
    )
    startup_unit = _build_startup_activity_unit(
        StartupActivityUnitRequest(
            profile_id=request.spec.id,
            avatar_source=avatar_source,
            startup_activity=request.startup_activity,
            is_live=True,
        )
    )
    hub_issue = _build_hub_issue(
        HubIssueRequest(
            profile_id=request.spec.id,
            avatar_source=avatar_source,
            hub_state=request.hub_state,
            hub_detail=request.hub_detail,
            hub_error=request.hub_error,
            hub_detail_is_error=request.hub_detail_is_error,
            is_live=True,
        )
    )
    return heartbeat_unit, heartbeat_issue, startup_unit, hub_issue
