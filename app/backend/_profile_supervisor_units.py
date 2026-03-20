from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._profile_supervisor_cards import WorkerTokenRequest, _build_worker_token
from ._profile_supervisor_common import _task_time_label
from ._profile_supervisor_view import _glyph_for_kind, _status_label


@dataclass(frozen=True)
class SessionWorkUnitsRequest:
    profile_id: str
    avatar_source: str
    sessions: list[dict[str, Any]]
    is_live: bool


@dataclass(frozen=True)
class CronWorkUnitsRequest:
    profile_id: str
    avatar_source: str
    cron_items: list[dict[str, Any]]
    is_live: bool


@dataclass(frozen=True)
class SessionWorkerRequest:
    profile_id: str
    avatar_source: str
    unit: dict[str, Any]


@dataclass(frozen=True)
class CronIssueRequest:
    profile_id: str
    avatar_source: str
    task: dict[str, Any]
    unit: dict[str, Any]


def _session_summary(item: dict[str, Any]) -> str:
    if bool(item.get("is_running", False)):
        return "长任务中" if bool(item.get("is_child_session", False)) else "回复中"
    child_status = str(item.get("child_status", "") or "")
    if child_status == "completed":
        return "已完成"
    if child_status == "failed":
        return "已失败"
    if child_status == "cancelled":
        return "已取消"
    return "最近会话"


def _build_session_work_units(
    request: SessionWorkUnitsRequest,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    units: list[dict[str, Any]] = []
    workers: list[dict[str, Any]] = []
    for session in _ordered_sessions(request.sessions):
        key = str(session.get("key", "") or "")
        if not key:
            continue
        unit = _session_unit(request, session, key)
        units.append(unit)
        workers.append(
            _session_worker(
                SessionWorkerRequest(
                    profile_id=request.profile_id,
                    avatar_source=request.avatar_source,
                    unit=unit,
                )
            )
        )
    return units, workers


def _build_cron_work_units(
    request: CronWorkUnitsRequest,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    units: list[dict[str, Any]] = []
    workers: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    for task in request.cron_items:
        task_id = str(task.get("id", "") or "")
        if not task_id:
            continue
        unit = _cron_unit(request, task, task_id)
        units.append(unit)
        workers.append(_cron_worker(request, unit))
        issue = _cron_issue(
            CronIssueRequest(
                profile_id=request.profile_id,
                avatar_source=request.avatar_source,
                task=task,
                unit=unit,
            )
        )
        if issue is not None:
            issues.append(issue)
    return units, workers, issues


def _ordered_sessions(sessions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        [dict(item) for item in sessions],
        key=lambda item: (bool(item.get("is_running", False)), str(item.get("updated_at", "") or "")),
        reverse=True,
    )


def _session_unit(
    request: SessionWorkUnitsRequest,
    session: dict[str, Any],
    key: str,
) -> dict[str, Any]:
    is_child = bool(session.get("is_child_session", False))
    kind = "subagent_task" if is_child else "session_reply"
    status_key = "running" if bool(session.get("is_running", False)) else str(session.get("child_status", "") or "idle")
    accent_key = str(session.get("visual_channel", session.get("channel", "desktop")) or "desktop")
    return {
        "id": f"{request.profile_id}:{kind}:{key}",
        "profileId": request.profile_id,
        "kind": kind,
        "title": str(session.get("title", "") or key),
        "summary": _session_summary(session),
        "sessionKey": key,
        "parentSessionKey": str(session.get("parent_session_key", "") or ""),
        "visualChannel": accent_key,
        "accentKey": "subagent" if is_child else accent_key,
        "glyphSource": _glyph_for_kind(kind, accent_key),
        "statusKey": status_key or "idle",
        "statusLabel": _status_label(status_key or "idle"),
        "updatedAt": str(session.get("updated_at", "") or ""),
        "updatedLabel": str(session.get("updated_label", "") or ""),
        "relativeLabel": str(session.get("updated_label", "") or ""),
        "isLive": request.is_live,
        "personaVariant": "mini" if is_child else "primary",
        "avatarSource": request.avatar_source,
        "routeKind": "session",
        "routeValue": key,
        "canOpen": True,
        "canToggleCron": False,
        "canRunHeartbeat": False,
        "isRunning": bool(session.get("is_running", False)),
    }


def _session_worker(request: SessionWorkerRequest) -> dict[str, Any]:
    unit = request.unit
    is_child = str(unit.get("kind", "")) == "subagent_task"
    accent_key = "subagent" if is_child else str(unit.get("visualChannel", "desktop"))
    title = str(unit.get("title", "") or unit.get("routeValue", ""))
    return _build_worker_token(
        WorkerTokenRequest(
            profile_id=request.profile_id,
            avatar_source=request.avatar_source,
            title=title,
            variant="mini" if is_child else "primary",
            accent_key=accent_key,
            glyph_source=_glyph_for_kind("subagent_task" if is_child else "session_reply", accent_key),
            status_key=str(unit["statusKey"]),
            status_label=str(unit["statusLabel"]),
            route_kind="session",
            route_value=str(unit["routeValue"]),
            unit_id=str(unit["id"]),
        )
    )


def _cron_unit(
    request: CronWorkUnitsRequest,
    task: dict[str, Any],
    task_id: str,
) -> dict[str, Any]:
    status_key = str(task.get("status_key", "draft") or "draft")
    time_label = _task_time_label(task)
    return {
        "id": f"{request.profile_id}:cron:{task_id}",
        "profileId": request.profile_id,
        "kind": "cron_job",
        "title": str(task.get("name", "") or "未命名任务"),
        "summary": str(task.get("schedule_summary", "") or "自动化任务"),
        "sessionKey": str(task.get("session_key", "") or ""),
        "visualChannel": "cron",
        "accentKey": "cron",
        "glyphSource": _glyph_for_kind("cron_job", "cron"),
        "statusKey": status_key,
        "statusLabel": str(task.get("status_label", "") or _status_label(status_key)),
        "updatedAt": str(task.get("updated_at_ms", "") or ""),
        "updatedLabel": time_label,
        "relativeLabel": time_label,
        "isLive": request.is_live,
        "personaVariant": "automation",
        "avatarSource": request.avatar_source,
        "routeKind": "cron",
        "routeValue": task_id,
        "canOpen": True,
        "canToggleCron": True,
        "canRunHeartbeat": False,
        "enabled": bool(task.get("enabled", False)),
        "isRunning": False,
    }


def _cron_worker(
    request: CronWorkUnitsRequest,
    unit: dict[str, Any],
) -> dict[str, Any]:
    return _build_worker_token(
        WorkerTokenRequest(
            profile_id=request.profile_id,
            avatar_source=request.avatar_source,
            title=str(unit.get("title", "") or "未命名任务"),
            variant="automation",
            accent_key="cron",
            glyph_source=_glyph_for_kind("cron_job", "cron"),
            status_key=str(unit["statusKey"]),
            status_label=str(unit["statusLabel"]),
            route_kind="cron",
            route_value=str(unit["routeValue"]),
            unit_id=str(unit["id"]),
        )
    )


def _cron_issue(request: CronIssueRequest) -> dict[str, Any] | None:
    unit = request.unit
    if str(unit["statusKey"]) != "error":
        return None
    return {
        "id": f"{unit['id']}:issue",
        "profileId": request.profile_id,
        "kind": "issue",
        "title": str(unit.get("title", "") or "未命名任务"),
        "summary": str(request.task.get("last_error", "") or "定时任务异常"),
        "statusKey": "error",
        "statusLabel": "待处理",
        "visualChannel": "cron",
        "accentKey": "cron",
        "glyphSource": _glyph_for_kind("issue", "cron"),
        "updatedAt": str(request.task.get("updated_at_ms", "") or ""),
        "updatedLabel": str(unit["updatedLabel"]),
        "relativeLabel": str(unit["relativeLabel"]),
        "isLive": request.is_live,
        "personaVariant": "automation",
        "avatarSource": request.avatar_source,
        "routeKind": "cron",
        "routeValue": str(unit["routeValue"]),
        "canOpen": True,
        "canToggleCron": True,
        "canRunHeartbeat": False,
    }
