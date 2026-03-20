from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._profile_supervisor_cards import (
    ProfileCardRequest,
    WorkerTokenRequest,
    _build_profile_card,
    _build_worker_token,
)
from ._profile_supervisor_common import (
    _SNAPSHOT_SCHEMA_VERSION,
    ProfileStatusSummaryRequest,
    _profile_status_summary,
)
from ._profile_supervisor_view import (
    _automation_metrics,
    _glyph_for_kind,
    _hub_channel_keys,
    _session_metrics,
)


@dataclass(frozen=True)
class LiveSnapshotRequest:
    request: Any
    updated_at: str
    hub_live: bool
    inventory: dict[str, Any]
    workers: list[dict[str, Any]]
    working: list[dict[str, Any]]
    completed: list[dict[str, Any]]
    automation: list[dict[str, Any]]
    attention: list[dict[str, Any]]
    running_count: int


@dataclass(frozen=True)
class LiveUnitState:
    avatar_source: str
    hub_live: bool
    inventory: dict[str, Any]
    session_units: list[dict[str, Any]]
    session_workers: list[dict[str, Any]]
    cron_units: list[dict[str, Any]]
    cron_workers: list[dict[str, Any]]
    cron_issues: list[dict[str, Any]]
    heartbeat_unit: dict[str, Any] | None
    heartbeat_issue: dict[str, Any] | None
    startup_unit: dict[str, Any] | None
    hub_issue: dict[str, Any] | None


@dataclass(frozen=True)
class LiveProfileCardRequest:
    request: Any
    state: LiveUnitState
    updated_at: str
    working: list[dict[str, Any]]
    automation: list[dict[str, Any]]
    attention: list[dict[str, Any]]
    workers: list[dict[str, Any]]


def _live_workers(request: Any, state: LiveUnitState) -> list[dict[str, Any]]:
    workers = (state.session_workers + state.cron_workers)[:8]
    if state.heartbeat_unit is None:
        return workers
    workers.append(
        _build_worker_token(
            WorkerTokenRequest(
                profile_id=request.spec.id,
                avatar_source=state.avatar_source,
                title="自动检查",
                variant="automation",
                accent_key="heartbeat",
                glyph_source=_glyph_for_kind("heartbeat_check", "heartbeat"),
                status_key=str(state.heartbeat_unit.get("statusKey", "idle")),
                status_label=str(state.heartbeat_unit.get("statusLabel", "待命")),
                route_kind="heartbeat",
                route_value="heartbeat",
                unit_id=f"{request.spec.id}:heartbeat",
            )
        )
    )
    return workers


def _live_profile_card(request: LiveProfileCardRequest) -> dict[str, Any]:
    running_count = len(request.working)
    session_metrics = _session_metrics(request.working)
    return _build_profile_card(
        ProfileCardRequest(
            spec=request.request.spec,
            avatar_source=request.state.avatar_source,
            is_active=True,
            updated_at=request.updated_at,
            live_label="实时" if request.state.hub_live else "当前",
            snapshot_label="实时更新" if request.state.hub_live else "中枢未启动",
            status_summary=_profile_status_summary(
                ProfileStatusSummaryRequest(
                    is_active=True,
                    is_live=request.state.hub_live,
                    session_reply_count=int(session_metrics["sessionReplyCount"]),
                    subagent_count=int(session_metrics["subagentCount"]),
                    other_working_count=max(0, running_count - int(session_metrics["sessionReplyCount"]) - int(session_metrics["subagentCount"])),
                    automation_count=len(request.automation),
                    total_session_count=int(request.state.inventory["totalSessionCount"]),
                    total_child_session_count=int(request.state.inventory["totalChildSessionCount"]),
                )
            ),
            working_count=running_count,
            automation_count=len(request.automation),
            attention_count=len(request.attention),
            inventory=request.state.inventory,
            session_reply_count=int(session_metrics["sessionReplyCount"]),
            subagent_count=int(session_metrics["subagentCount"]),
            running_automation_count=int(_automation_metrics(request.automation)["runningAutomationCount"]),
            hub_state=request.request.hub_state,
            hub_detail=request.request.hub_detail,
            is_hub_live=request.state.hub_live,
            workers=request.workers,
        )
    )


def _build_snapshot(request: LiveSnapshotRequest) -> dict[str, Any]:
    return {
        "schema_version": _SNAPSHOT_SCHEMA_VERSION,
        "profile_id": request.request.spec.id,
        "display_name": request.request.spec.display_name,
        "avatar_key": request.request.spec.avatar_key,
        "updated_at": request.updated_at,
        "domain": {
            "sessions": [dict(item) for item in request.request.sessions],
            "cron": [dict(item) for item in request.request.cron_items],
            "heartbeat": dict(request.request.heartbeat_status),
            "hub": {
                "state": request.request.hub_state,
                "detail": request.request.hub_detail,
                "error": request.request.hub_error,
                "detail_is_error": request.request.hub_detail_is_error,
                "channels": list(request.request.hub_channels),
                "startup_activity": dict(request.request.startup_activity),
                "is_live": request.hub_live,
            },
        },
        "hub": {
            "state": request.request.hub_state,
            "detail": request.request.hub_detail,
            "channels": _hub_channel_keys(request.request.hub_channels),
            "is_live": request.hub_live,
        },
        "counts": {
            "running": request.running_count,
            "completed": len(request.completed),
            "automation": len(request.automation),
            "attention": len(request.attention),
        },
        "inventory": dict(request.inventory),
        "workers": request.workers,
        "working": request.working,
        "completed": request.completed,
        "automation": request.automation,
        "attention": request.attention,
    }
