from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._profile_supervisor_cards import WorkerTokenRequest, _build_worker_token
from ._profile_supervisor_status_units import (
    HeartbeatWorkUnitRequest,
    HubIssueRequest,
    StartupActivityUnitRequest,
    _build_heartbeat_work_unit,
    _build_hub_issue,
    _build_startup_activity_unit,
)
from ._profile_supervisor_units import (
    CronWorkUnitsRequest,
    SessionWorkUnitsRequest,
    _build_cron_work_units,
    _build_session_work_units,
)
from ._profile_supervisor_view import (
    _glyph_for_kind,
    _session_inventory,
)


@dataclass(frozen=True)
class CachedDomainCollectionsRequest:
    profile_id: str
    avatar_source: str
    sessions: list[dict[str, Any]]
    cron_items: list[dict[str, Any]]
    heartbeat_status: dict[str, Any]
    hub_snapshot: dict[str, Any]


@dataclass(frozen=True)
class CachedCollectionsRequest:
    session_units: list[dict[str, Any]]
    cron_units: list[dict[str, Any]]
    cron_issues: list[dict[str, Any]]
    heartbeat_unit: dict[str, Any] | None
    heartbeat_issue: dict[str, Any] | None
    startup_unit: dict[str, Any] | None
    hub_issue: dict[str, Any] | None


@dataclass(frozen=True)
class CachedWorkersRequest:
    profile_id: str
    avatar_source: str
    session_workers: list[dict[str, Any]]
    cron_workers: list[dict[str, Any]]
    heartbeat_unit: dict[str, Any] | None


def _build_cached_domain_collections(request: CachedDomainCollectionsRequest) -> dict[str, Any]:
    session_units, session_workers, cron_units, cron_workers, cron_issues = _cached_units(request)
    heartbeat_unit, heartbeat_issue = _build_heartbeat_work_unit(
        HeartbeatWorkUnitRequest(
            profile_id=request.profile_id,
            avatar_source=request.avatar_source,
            heartbeat_status=request.heartbeat_status,
            is_live=False,
        )
    )
    startup_unit = _build_startup_activity_unit(
        StartupActivityUnitRequest(
            profile_id=request.profile_id,
            avatar_source=request.avatar_source,
            startup_activity=dict(request.hub_snapshot.get("startup_activity", {}) or {}),
            is_live=False,
        )
    )
    hub_issue = _build_hub_issue(_cached_hub_issue_request(request))
    completed, automation, attention = _cached_collections(
        CachedCollectionsRequest(
            session_units=session_units,
            cron_units=cron_units,
            cron_issues=cron_issues,
            heartbeat_unit=heartbeat_unit,
            heartbeat_issue=heartbeat_issue,
            startup_unit=startup_unit,
            hub_issue=hub_issue,
        )
    )
    workers = _cached_workers(
        CachedWorkersRequest(
            profile_id=request.profile_id,
            avatar_source=request.avatar_source,
            session_workers=session_workers,
            cron_workers=cron_workers,
            heartbeat_unit=heartbeat_unit,
        )
    )
    hub_channels = list(request.hub_snapshot.get("channels", []) or [])
    return {
        "working": [],
        "completed": completed,
        "automation": automation,
        "attention": attention,
        "workers": workers,
        "hub_channels": hub_channels,
        "inventory": _session_inventory(request.sessions, hub_channels=hub_channels),
    }


def _cached_units(
    request: CachedDomainCollectionsRequest,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    session_units, session_workers = _build_session_work_units(
        SessionWorkUnitsRequest(
            profile_id=request.profile_id,
            avatar_source=request.avatar_source,
            sessions=request.sessions,
            is_live=False,
        )
    )
    cron_units, cron_workers, cron_issues = _build_cron_work_units(
        CronWorkUnitsRequest(
            profile_id=request.profile_id,
            avatar_source=request.avatar_source,
            cron_items=request.cron_items,
            is_live=False,
        )
    )
    return session_units, session_workers, cron_units, cron_workers, cron_issues


def _cached_collections(
    request: CachedCollectionsRequest,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    completed = [
        unit
        for unit in request.session_units
        if str(unit.get("kind", "") or "") == "subagent_task"
        and str(unit.get("statusKey", "") or "") == "completed"
    ]
    automation = request.cron_units + ([request.heartbeat_unit] if request.heartbeat_unit else [])
    attention = request.cron_issues + ([request.heartbeat_issue] if request.heartbeat_issue else [])
    if request.startup_unit is not None and str(request.startup_unit.get("statusKey", "") or "") == "completed":
        completed.insert(0, request.startup_unit)
    elif request.startup_unit is not None and str(request.startup_unit.get("statusKey", "") or "") == "error":
        attention.insert(0, request.startup_unit)
    if request.hub_issue is not None:
        attention.append(request.hub_issue)
    return completed, automation, attention


def _cached_workers(request: CachedWorkersRequest) -> list[dict[str, Any]]:
    workers = (request.session_workers + request.cron_workers)[:8]
    if request.heartbeat_unit is None:
        return workers
    workers.append(
        _build_worker_token(
            WorkerTokenRequest(
                profile_id=request.profile_id,
                avatar_source=request.avatar_source,
                title="自动检查",
                variant="automation",
                accent_key="heartbeat",
                glyph_source=_glyph_for_kind("heartbeat_check", "heartbeat"),
                status_key=str(request.heartbeat_unit.get("statusKey", "idle")),
                status_label=str(request.heartbeat_unit.get("statusLabel", "待命")),
                route_kind="heartbeat",
                route_value="heartbeat",
                unit_id=f"{request.profile_id}:heartbeat",
            )
        )
    )
    return workers


def _cached_hub_issue_request(request: CachedDomainCollectionsRequest) -> HubIssueRequest:
    return HubIssueRequest(
        profile_id=request.profile_id,
        avatar_source=request.avatar_source,
        hub_state=str(request.hub_snapshot.get("state", "") or ""),
        hub_detail=str(request.hub_snapshot.get("detail", "") or ""),
        hub_error=str(request.hub_snapshot.get("error", "") or ""),
        hub_detail_is_error=bool(request.hub_snapshot.get("detail_is_error", False)),
        is_live=False,
    )
