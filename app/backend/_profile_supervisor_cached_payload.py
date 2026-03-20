from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from bao.profile import ProfileContext, ProfileSpec

from ._profile_supervisor_cached_domain import (
    CachedDomainCollectionsRequest,
    _build_cached_domain_collections,
)
from ._profile_supervisor_cards import ProfileCardRequest, _build_profile_card
from ._profile_supervisor_common import (
    ProfileStatusSummaryRequest,
    _clone_dict_list,
    _profile_status_summary,
)
from ._profile_supervisor_status_units import (
    HeartbeatWorkUnitRequest,
    _build_heartbeat_work_unit,
)
from ._profile_supervisor_storage import (
    _has_session_storage_roots,
    _heartbeat_static_snapshot,
    _load_cron_items,
    _load_sessions_from_root,
    _read_snapshot,
    _snapshot_path,
)
from ._profile_supervisor_units import CronWorkUnitsRequest, _build_cron_work_units
from ._profile_supervisor_view import (
    _automation_metrics,
    _avatar_source,
    _dedupe_channel_keys,
    _session_inventory,
)


@dataclass(frozen=True)
class CachedProfileStateRequest:
    spec: ProfileSpec
    context: ProfileContext
    avatar_source: str


@dataclass(frozen=True)
class CachedProfilePayloadRequest:
    spec: ProfileSpec
    context: ProfileContext


@dataclass(frozen=True)
class CachedInventoryFallbackRequest:
    state_request: CachedProfileStateRequest
    snapshot: dict[str, Any]
    hub_channels: list[object]
    automation: list[dict[str, Any]]
    attention: list[dict[str, Any]]
    workers: list[dict[str, Any]]


def load_cached_profile_state(request: CachedProfileStateRequest) -> dict[str, Any]:
    snapshot = _read_snapshot(_snapshot_path(request.context))
    working: list[dict[str, Any]] = []
    completed = _clone_dict_list(snapshot.get("completed", []))
    automation = _clone_dict_list(snapshot.get("automation", []))
    attention = _clone_dict_list(snapshot.get("attention", []))
    workers = _clone_dict_list(snapshot.get("workers", []))
    hub = dict(snapshot.get("hub", {}) or {})
    hub_channels = list(hub.get("channels", []) or [])
    domain = dict(snapshot.get("domain", {}) or {})
    if domain:
        cached_domain = _build_cached_domain_collections(
            CachedDomainCollectionsRequest(
                profile_id=request.spec.id,
                avatar_source=request.avatar_source,
                sessions=_clone_dict_list(domain.get("sessions", [])),
                cron_items=_clone_dict_list(domain.get("cron", [])),
                heartbeat_status=dict(domain.get("heartbeat", {}) or {}),
                hub_snapshot=dict(domain.get("hub", {}) or {}),
            )
        )
        working = list(cached_domain["working"])
        completed = list(cached_domain["completed"])
        automation = list(cached_domain["automation"])
        attention = list(cached_domain["attention"])
        workers = list(cached_domain["workers"])
        hub_channels = list(cached_domain["hub_channels"])
        inventory = dict(cached_domain["inventory"])
    else:
        inventory = _fallback_cached_inventory(
            CachedInventoryFallbackRequest(
                state_request=request,
                snapshot=snapshot,
                hub_channels=hub_channels,
                automation=automation,
                attention=attention,
                workers=workers,
            )
        )
    return {
        "snapshot_updated_at": str(snapshot.get("updated_at", "") or ""),
        "working": working,
        "completed": completed,
        "automation": automation,
        "attention": attention,
        "workers": workers,
        "inventory": inventory,
        "hub_state": str(hub.get("state", "") or ""),
        "hub_detail": str(hub.get("detail", "") or ""),
        "is_hub_live": bool(hub.get("is_live", False)),
        "snapshot_write": None,
    }


def _fallback_cached_inventory(request: CachedInventoryFallbackRequest) -> dict[str, Any]:
    state_request = request.state_request
    if not request.automation and not request.attention and not request.workers:
        try:
            cron_items = _load_cron_items(state_request.context.cron_store_path)
        except Exception:
            cron_items = []
        cron_units, cron_workers, cron_issues = _build_cron_work_units(
            CronWorkUnitsRequest(
                profile_id=state_request.spec.id,
                avatar_source=state_request.avatar_source,
                cron_items=cron_items,
                is_live=False,
            )
        )
        request.automation[:] = cron_units
        request.attention[:] = cron_issues
        request.workers[:] = cron_workers[:4]
        heartbeat_unit, heartbeat_issue = _build_heartbeat_work_unit(
            HeartbeatWorkUnitRequest(
                profile_id=state_request.spec.id,
                avatar_source=state_request.avatar_source,
                heartbeat_status=_heartbeat_static_snapshot(state_request.context.heartbeat_file),
                is_live=False,
            )
        )
        if heartbeat_unit is not None:
            request.automation.append(heartbeat_unit)
        if heartbeat_issue is not None:
            request.attention.append(heartbeat_issue)
    snapshot_inventory = dict(request.snapshot.get("inventory", {}) or {})
    inventory = {
        "totalSessionCount": int(snapshot_inventory.get("totalSessionCount", 0) or 0),
        "totalChildSessionCount": int(snapshot_inventory.get("totalChildSessionCount", 0) or 0),
        "channelKeys": _dedupe_channel_keys(snapshot_inventory.get("channelKeys", []) or []),
    }
    if inventory["totalSessionCount"] or inventory["totalChildSessionCount"] or inventory["channelKeys"]:
        return inventory
    try:
        stored_sessions = (
            _load_sessions_from_root(state_request.context.state_root)
            if _has_session_storage_roots(state_request.context.state_root)
            else []
        )
    except Exception:
        stored_sessions = []
    return _session_inventory(stored_sessions, hub_channels=request.hub_channels)


def build_cached_profile_payload(request: CachedProfilePayloadRequest) -> dict[str, Any]:
    avatar_source = _avatar_source(request.spec.avatar_key)
    cached_state = load_cached_profile_state(
        CachedProfileStateRequest(
            spec=request.spec,
            context=request.context,
            avatar_source=avatar_source,
        )
    )
    inventory = dict(cached_state["inventory"])
    automation = list(cached_state["automation"])
    profile_card = _build_profile_card(
        ProfileCardRequest(
            spec=request.spec,
            avatar_source=avatar_source,
            is_active=False,
            updated_at=str(cached_state["snapshot_updated_at"]),
            live_label="",
            snapshot_label="",
            status_summary=_profile_status_summary(
                ProfileStatusSummaryRequest(
                    is_active=False,
                    is_live=False,
                    session_reply_count=0,
                    subagent_count=0,
                    other_working_count=0,
                    automation_count=len(automation),
                    total_session_count=int(inventory["totalSessionCount"]),
                    total_child_session_count=int(inventory["totalChildSessionCount"]),
                )
            ),
            working_count=len(cached_state["working"]),
            automation_count=len(automation),
            attention_count=len(cached_state["attention"]),
            inventory=inventory,
            session_reply_count=0,
            subagent_count=0,
            running_automation_count=int(_automation_metrics(automation)["runningAutomationCount"]),
            hub_state=str(cached_state["hub_state"]),
            hub_detail=str(cached_state["hub_detail"]),
            is_hub_live=bool(cached_state["is_hub_live"]),
            workers=list(cached_state["workers"]),
        )
    )
    return {
        "profile": profile_card,
        "working": list(cached_state["working"]),
        "completed": list(cached_state["completed"]),
        "automation": list(cached_state["automation"]),
        "attention": list(cached_state["attention"]),
        "snapshot_write": cached_state.get("snapshot_write"),
    }
