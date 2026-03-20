from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from bao.profile import ProfileContextOptions, profile_context

from ._profile_supervisor_cached_payload import (
    CachedProfilePayloadRequest,
    build_cached_profile_payload,
)
from ._profile_supervisor_common import (
    _empty_projection,
    _filter_recent_completed_items,
    _now_iso,
    _profile_registry_from_snapshot,
    _relative_time,
)
from ._profile_supervisor_live_payload import LiveProfilePayloadRequest, build_live_profile_payload


@dataclass(frozen=True)
class OverviewRequest:
    profile_cards: list[dict[str, Any]]
    active_profile_id: str
    working_items: list[dict[str, Any]]
    completed_items: list[dict[str, Any]]
    automation_items: list[dict[str, Any]]
    attention_items: list[dict[str, Any]]


@dataclass(frozen=True)
class ProjectionItems:
    working_items: list[dict[str, Any]]
    completed_items: list[dict[str, Any]]
    automation_items: list[dict[str, Any]]
    attention_items: list[dict[str, Any]]


@dataclass(frozen=True)
class ProfilePayloadRequest:
    captured: dict[str, Any]
    registry: Any
    active_context: Any
    active_profile_id: str
    shared_workspace: Path
    spec: Any


@dataclass(frozen=True)
class PayloadAccumulator:
    profile_cards: list[dict[str, Any]]
    working_items: list[dict[str, Any]]
    completed_items: list[dict[str, Any]]
    automation_items: list[dict[str, Any]]
    attention_items: list[dict[str, Any]]
    snapshot_writes: list[dict[str, Any]]


@dataclass(frozen=True)
class ProfilePayloadsRequest:
    captured: dict[str, Any]
    registry: Any
    active_profile_id: str
    shared_workspace: Path


def build_supervisor_projection(
    captured: dict[str, Any],
    *,
    ensure_profile_registry_fn: Callable[[Path], Any],
) -> dict[str, Any]:
    shared_workspace_path = str(captured.get("shared_workspace_path", "") or "")
    if not shared_workspace_path:
        return _empty_projection()
    shared_workspace = Path(shared_workspace_path).expanduser()
    registry = _profile_registry_from_snapshot(captured.get("profile_registry_snapshot"))
    if registry is None:
        registry = ensure_profile_registry_fn(shared_workspace)
    active_profile_id = str(captured.get("active_profile_id", "") or "")
    profile_cards, working_items, completed_items, automation_items, attention_items, snapshot_writes = _profile_payloads(
        ProfilePayloadsRequest(
            captured=captured,
            registry=registry,
            active_profile_id=active_profile_id,
            shared_workspace=shared_workspace,
        )
    )
    _sort_projection_items(
        ProjectionItems(
            working_items=working_items,
            completed_items=completed_items,
            automation_items=automation_items,
            attention_items=attention_items,
        )
    )
    return _projection_payload(
        OverviewRequest(
            profile_cards=profile_cards,
            active_profile_id=active_profile_id,
            working_items=working_items,
            completed_items=completed_items,
            automation_items=automation_items,
            attention_items=attention_items,
        ),
        snapshot_writes,
    )


def _profile_payloads(request: ProfilePayloadsRequest) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    active_context = request.captured.get("active_context")
    profile_cards: list[dict[str, Any]] = []
    working_items: list[dict[str, Any]] = []
    completed_items: list[dict[str, Any]] = []
    automation_items: list[dict[str, Any]] = []
    attention_items: list[dict[str, Any]] = []
    snapshot_writes: list[dict[str, Any]] = []
    for spec in request.registry.profiles:
        payload = _profile_payload(
            ProfilePayloadRequest(
                captured=request.captured,
                registry=request.registry,
                active_context=active_context,
                active_profile_id=request.active_profile_id,
                shared_workspace=request.shared_workspace,
                spec=spec,
            )
        )
        _append_payload(
            payload,
            PayloadAccumulator(
                profile_cards=profile_cards,
                working_items=working_items,
                completed_items=completed_items,
                automation_items=automation_items,
                attention_items=attention_items,
                snapshot_writes=snapshot_writes,
            ),
        )
    return (
        profile_cards,
        working_items,
        completed_items,
        automation_items,
        attention_items,
        snapshot_writes,
    )


def _sort_projection_items(request: ProjectionItems) -> None:
    request.working_items.sort(
        key=lambda item: (bool(item.get("isRunning", False)), str(item.get("updatedAt", "") or "")),
        reverse=True,
    )
    request.completed_items[:] = _filter_recent_completed_items(request.completed_items)
    request.automation_items.sort(key=lambda item: str(item.get("updatedAt", "") or ""), reverse=True)
    request.attention_items.sort(key=lambda item: str(item.get("updatedAt", "") or ""), reverse=True)


def _overview_payload(request: OverviewRequest) -> dict[str, Any]:
    updated_at = _now_iso()
    return {
        "title": "指挥舱",
        "subtitle": "统一查看分身回复、自动化与待处理事项",
        "profileCount": len(request.profile_cards),
        "totalSessionCount": sum(
            int(item.get("totalSessionCount", 0) or 0) for item in request.profile_cards
        ),
        "workingCount": len(request.working_items),
        "completedCount": len(request.completed_items),
        "automationCount": len(request.automation_items),
        "attentionCount": len(request.attention_items),
        "liveProfileId": request.active_profile_id,
        "liveProfileName": str(
            next(
                (
                    item.get("displayName", "")
                    for item in request.profile_cards
                    if item.get("id") == request.active_profile_id
                ),
                "",
            )
        ),
        "liveHubLive": bool(
            next(
                (
                    item.get("isHubLive", False)
                    for item in request.profile_cards
                    if item.get("id") == request.active_profile_id
                ),
                False,
            )
        ),
        "updatedAt": updated_at,
        "updatedLabel": _relative_time(updated_at),
    }


def _projection_payload(
    request: OverviewRequest,
    snapshot_writes: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "overview": _overview_payload(request),
        "profiles": request.profile_cards,
        "working": request.working_items,
        "completed": request.completed_items,
        "automation": request.automation_items,
        "attention": request.attention_items,
        "snapshot_writes": snapshot_writes,
    }


def _profile_payload(request: ProfilePayloadRequest) -> dict[str, Any]:
    context = profile_context(
        request.spec.id,
        ProfileContextOptions(shared_workspace=request.shared_workspace, registry=request.registry),
    )
    if request.active_context is not None and request.spec.id == request.active_profile_id:
        return build_live_profile_payload(
            LiveProfilePayloadRequest(
                context=context,
                spec=request.spec,
                sessions=request.captured.get("active_sessions", []),
                cron_items=request.captured.get("active_cron_items", []),
                heartbeat_status=dict(request.captured.get("heartbeat_status", {})),
                hub_state=str(request.captured.get("hub_state", "") or ""),
                hub_detail=str(request.captured.get("hub_detail", "") or ""),
                hub_error=str(request.captured.get("hub_error", "") or ""),
                hub_detail_is_error=bool(request.captured.get("hub_detail_is_error", False)),
                hub_channels=list(request.captured.get("hub_channels", []) or []),
                startup_activity=dict(request.captured.get("startup_activity", {}) or {}),
            )
        )
    return build_cached_profile_payload(
        CachedProfilePayloadRequest(spec=request.spec, context=context)
    )


def _append_payload(payload: dict[str, Any], accumulator: PayloadAccumulator) -> None:
    snapshot_write = payload.get("snapshot_write")
    if isinstance(snapshot_write, dict):
        accumulator.snapshot_writes.append(dict(snapshot_write))
    accumulator.profile_cards.append(payload["profile"])
    accumulator.working_items.extend(payload["working"])
    accumulator.completed_items.extend(payload["completed"])
    accumulator.automation_items.extend(payload["automation"])
    accumulator.attention_items.extend(payload["attention"])
