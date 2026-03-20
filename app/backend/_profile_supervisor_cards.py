from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from bao.profile import ProfileSpec

from ._profile_supervisor_common import _relative_time


@dataclass(frozen=True)
class WorkerTokenRequest:
    profile_id: str
    avatar_source: str
    title: str
    variant: str
    accent_key: str
    glyph_source: str
    status_key: str
    status_label: str
    route_kind: str
    route_value: str
    unit_id: str


@dataclass(frozen=True)
class ProfileCardRequest:
    spec: ProfileSpec
    avatar_source: str
    is_active: bool
    updated_at: str
    live_label: str
    snapshot_label: str
    status_summary: str
    working_count: int
    automation_count: int
    attention_count: int
    inventory: dict[str, Any]
    session_reply_count: int
    subagent_count: int
    running_automation_count: int
    hub_state: str
    hub_detail: str
    is_hub_live: bool
    workers: list[dict[str, Any]]


def _build_worker_token(request: WorkerTokenRequest) -> dict[str, Any]:
    return {
        "workerId": request.unit_id,
        "profileId": request.profile_id,
        "avatarSource": request.avatar_source,
        "title": request.title,
        "variant": request.variant,
        "accentKey": request.accent_key,
        "glyphSource": request.glyph_source,
        "statusKey": request.status_key,
        "statusLabel": request.status_label,
        "routeKind": request.route_kind,
        "routeValue": request.route_value,
    }


def _build_profile_card(request: ProfileCardRequest) -> dict[str, Any]:
    return {
        "id": request.spec.id,
        "displayName": request.spec.display_name,
        "avatarKey": request.spec.avatar_key,
        "avatarSource": request.avatar_source,
        "isActive": request.is_active,
        "isLive": request.is_active,
        "liveLabel": request.live_label,
        "snapshotLabel": request.snapshot_label,
        "updatedAt": request.updated_at,
        "updatedLabel": _relative_time(request.updated_at),
        "statusSummary": request.status_summary,
        "workingCount": request.working_count,
        "automationCount": request.automation_count,
        "attentionCount": request.attention_count,
        "totalSessionCount": int(request.inventory["totalSessionCount"]),
        "totalChildSessionCount": int(request.inventory["totalChildSessionCount"]),
        "sessionReplyCount": request.session_reply_count,
        "subagentCount": request.subagent_count,
        "runningAutomationCount": request.running_automation_count,
        "channelKeys": list(request.inventory["channelKeys"]),
        "hubState": request.hub_state,
        "hubDetail": request.hub_detail,
        "isHubLive": request.is_hub_live,
        "workers": request.workers[:8],
    }
