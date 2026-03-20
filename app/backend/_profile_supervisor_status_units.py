from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._profile_supervisor_common import (
    _now_iso,
    _relative_time,
    _safe_text,
)
from ._profile_supervisor_view import (
    _glyph_for_kind,
    _hub_channel_keys,
    _primary_visual_channel,
    _status_label,
)


@dataclass(frozen=True)
class HeartbeatWorkUnitRequest:
    profile_id: str
    avatar_source: str
    heartbeat_status: dict[str, Any]
    is_live: bool


@dataclass(frozen=True)
class HubIssueRequest:
    profile_id: str
    avatar_source: str
    hub_state: str
    hub_detail: str
    hub_error: str
    hub_detail_is_error: bool
    is_live: bool


@dataclass(frozen=True)
class StartupActivityUnitRequest:
    profile_id: str
    avatar_source: str
    startup_activity: dict[str, Any]
    is_live: bool


@dataclass(frozen=True)
class HeartbeatRenderRequest:
    request: HeartbeatWorkUnitRequest
    status_key: str
    updated_label: str
    relative_label: str
    exists: bool
    last_error: str
    enabled: bool
def _build_heartbeat_work_unit(
    request: HeartbeatWorkUnitRequest,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    enabled = bool(request.heartbeat_status.get("enabled", False))
    exists = bool(request.heartbeat_status.get("heartbeat_file_exists", False))
    if not enabled and not exists:
        return None, None
    status_key = "running" if bool(request.heartbeat_status.get("running", False)) else "idle"
    last_error = str(request.heartbeat_status.get("last_error", "") or "")
    if last_error:
        status_key = "error"
    updated_label = _relative_time(request.heartbeat_status.get("last_checked_at_ms"))
    relative_label = _relative_time(request.heartbeat_status.get("last_run_at_ms"))
    unit = _heartbeat_unit(
        HeartbeatRenderRequest(
            request=request,
            status_key=status_key,
            updated_label=updated_label,
            relative_label=relative_label,
            exists=exists,
            last_error=last_error,
            enabled=enabled,
        )
    )
    if not (last_error or not exists):
        return unit, None
    return unit, _heartbeat_issue(unit, request)


def _build_hub_issue(request: HubIssueRequest) -> dict[str, Any] | None:
    if request.hub_state != "error" and not request.hub_error and not request.hub_detail_is_error:
        return None
    return {
        "id": f"{request.profile_id}:hub:issue",
        "profileId": request.profile_id,
        "kind": "issue",
        "title": "中枢状态",
        "summary": request.hub_error or request.hub_detail or "中枢异常",
        "statusKey": "error",
        "statusLabel": "待处理",
        "visualChannel": "system",
        "accentKey": "system",
        "glyphSource": _glyph_for_kind("issue", "system"),
        "updatedAt": _now_iso(),
        "updatedLabel": "刚刚",
        "relativeLabel": "刚刚",
        "isLive": request.is_live,
        "personaVariant": "automation",
        "avatarSource": request.avatar_source,
        "routeKind": "profile",
        "routeValue": request.profile_id,
        "canOpen": True,
        "canToggleCron": False,
        "canRunHeartbeat": False,
    }


def _build_startup_activity_unit(
    request: StartupActivityUnitRequest,
) -> dict[str, Any] | None:
    if str(request.startup_activity.get("kind", "") or "") != "startup_greeting":
        return None
    status = str(request.startup_activity.get("status", "") or "").strip()
    if status not in {"running", "completed", "error"}:
        return None
    channel_keys = _primary_channel_keys(request.startup_activity)
    session_keys = [
        str(value).strip()
        for value in request.startup_activity.get("sessionKeys", [])
        if str(value).strip()
    ]
    session_key = str(request.startup_activity.get("sessionKey", "") or "").strip()
    if session_key and session_key not in session_keys:
        session_keys.append(session_key)
    primary_session_key = session_keys[0] if len(session_keys) == 1 else ""
    error_text = _safe_text(request.startup_activity.get("error", "") or "", limit=44)
    updated_at = request.startup_activity.get("updatedAt")
    updated_label = _relative_time(updated_at)
    return {
        "id": f"{request.profile_id}:startup:greeting",
        "profileId": request.profile_id,
        "kind": "startup_greeting",
        "title": "AI 问候",
        "summary": {"running": "启动后正在发送问候", "completed": "刚发送完问候", "error": error_text or "问候发送失败"}[status],
        "sessionKey": primary_session_key,
        "sessionKeys": session_keys,
        "channelKeys": channel_keys,
        "visualChannel": channel_keys[0] if channel_keys else "desktop",
        "accentKey": channel_keys[0] if channel_keys else "desktop",
        "glyphSource": _glyph_for_kind("session_reply", channel_keys[0] if channel_keys else "desktop"),
        "statusKey": "running" if status == "running" else ("completed" if status == "completed" else "error"),
        "statusLabel": {"running": "发送中", "completed": "已完成", "error": "待处理"}[status],
        "updatedAt": str(updated_at or ""),
        "updatedLabel": updated_label,
        "relativeLabel": updated_label,
        "isLive": request.is_live,
        "personaVariant": "primary",
        "avatarSource": request.avatar_source,
        "routeKind": "session" if primary_session_key else "profile",
        "routeValue": primary_session_key or request.profile_id,
        "canOpen": bool(primary_session_key or request.profile_id),
        "canToggleCron": False,
        "canRunHeartbeat": False,
        "isRunning": status == "running",
    }


def _primary_channel_keys(startup_activity: dict[str, Any]) -> list[str]:
    channel_keys = _hub_channel_keys(startup_activity.get("channelKeys", []) or [])
    primary_channel = _primary_visual_channel(channel_keys)
    if primary_channel in channel_keys:
        return [primary_channel] + [key for key in channel_keys if key != primary_channel]
    return channel_keys


def _heartbeat_unit(request: HeartbeatRenderRequest) -> dict[str, Any]:
    heartbeat_request = request.request
    return {
        "id": f"{heartbeat_request.profile_id}:heartbeat",
        "profileId": heartbeat_request.profile_id,
        "kind": "heartbeat_check",
        "title": "自动检查",
        "summary": request.last_error
        or (
            "缺少检查说明"
            if not request.exists
            else (f"上次检查 {request.updated_label}" if request.updated_label else "待首次执行")
        ),
        "sessionKey": "heartbeat",
        "visualChannel": "heartbeat",
        "accentKey": "heartbeat",
        "glyphSource": _glyph_for_kind("heartbeat_check", "heartbeat"),
        "statusKey": request.status_key,
        "statusLabel": _status_label(request.status_key),
        "updatedAt": str(heartbeat_request.heartbeat_status.get("updated_at", "") or "")
        or str(heartbeat_request.heartbeat_status.get("last_checked_at_ms", "") or ""),
        "updatedLabel": request.updated_label,
        "relativeLabel": request.relative_label,
        "isLive": heartbeat_request.is_live,
        "personaVariant": "automation",
        "avatarSource": heartbeat_request.avatar_source,
        "routeKind": "heartbeat",
        "routeValue": "heartbeat",
        "canOpen": True,
        "canToggleCron": False,
        "canRunHeartbeat": heartbeat_request.is_live,
        "enabled": request.enabled,
        "isRunning": request.status_key == "running",
    }


def _heartbeat_issue(
    unit: dict[str, Any],
    request: HeartbeatWorkUnitRequest,
) -> dict[str, Any]:
    return {
        "id": f"{request.profile_id}:heartbeat:issue",
        "profileId": request.profile_id,
        "kind": "issue",
        "title": "自动检查",
        "summary": str(unit.get("summary", "") or "缺少检查说明"),
        "statusKey": "error",
        "statusLabel": "待处理",
        "visualChannel": "heartbeat",
        "accentKey": "heartbeat",
        "glyphSource": _glyph_for_kind("issue", "heartbeat"),
        "updatedAt": str(request.heartbeat_status.get("updated_at", "") or ""),
        "updatedLabel": str(unit.get("updatedLabel", "")),
        "relativeLabel": str(unit.get("relativeLabel", "")),
        "isLive": request.is_live,
        "personaVariant": "automation",
        "avatarSource": request.avatar_source,
        "routeKind": "heartbeat",
        "routeValue": "heartbeat",
        "canOpen": True,
        "canToggleCron": False,
        "canRunHeartbeat": request.is_live,
    }
