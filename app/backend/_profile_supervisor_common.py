from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from bao.profile import ProfileRegistry, ProfileSpec

_SNAPSHOT_FILENAME = "supervisor_snapshot.json"
_SNAPSHOT_SCHEMA_VERSION = 2
_NATURAL_KEY = "desktop:local"
_RECENT_COMPLETED_WINDOW_SECONDS = 2 * 60 * 60
_RECENT_COMPLETED_LIMIT = 8
_COLLECTION_NAMES = ("working", "completed", "automation", "attention")
_PROFILE_CHANNEL_KEYS = {
    "desktop",
    "telegram",
    "discord",
    "whatsapp",
    "feishu",
    "slack",
    "qq",
    "dingtalk",
    "imessage",
    "email",
}


@dataclass(frozen=True)
class ProfileStatusSummaryRequest:
    is_active: bool
    is_live: bool
    session_reply_count: int
    subagent_count: int
    other_working_count: int
    automation_count: int
    total_session_count: int
    total_child_session_count: int


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_dt(value: object) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
    if isinstance(value, (int, float)):
        raw = float(value)
        if raw <= 0:
            return None
        if raw > 1_000_000_000_000:
            raw /= 1000.0
        try:
            return datetime.fromtimestamp(raw, tz=timezone.utc)
        except (OSError, OverflowError, ValueError):
            return None
    text = str(value or "").strip()
    if not text:
        return None
    if text.isdigit():
        return _coerce_dt(int(text))
    normalized = text.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(normalized)
        return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def _relative_time(value: object) -> str:
    dt = _coerce_dt(value)
    if dt is None:
        return ""
    now = datetime.now(dt.tzinfo or timezone.utc)
    seconds = int((dt - now).total_seconds())
    future = seconds > 0
    distance = abs(seconds)
    if distance < 60:
        return "稍后" if future else "刚刚"
    if distance < 3600:
        minutes = max(1, distance // 60)
        return f"{minutes} 分钟后" if future else f"{minutes} 分钟前"
    if distance < 86400:
        hours = max(1, distance // 3600)
        return f"{hours} 小时后" if future else f"{hours} 小时前"
    if distance < 2592000:
        days = max(1, distance // 86400)
        return f"{days} 天后" if future else f"{days} 天前"
    if distance < 31536000:
        months = max(1, distance // 2592000)
        return f"{months} 个月后" if future else f"{months} 个月前"
    years = max(1, distance // 31536000)
    return f"{years} 年后" if future else f"{years} 年前"


def _safe_text(value: object, *, limit: int = 120) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _clone_dict_list(values: list[object]) -> list[dict[str, Any]]:
    return [dict(item) for item in values if isinstance(item, dict)]


def _profile_registry_from_snapshot(value: object) -> ProfileRegistry | None:
    if not isinstance(value, dict):
        return None
    raw_profiles = value.get("profiles")
    if not isinstance(raw_profiles, list):
        return None
    profiles: list[ProfileSpec] = []
    profile_ids: set[str] = set()
    for item in raw_profiles:
        if not isinstance(item, dict):
            continue
        profile_id = str(item.get("id", "") or "").strip()
        if not profile_id:
            continue
        profile_ids.add(profile_id)
        profiles.append(
            ProfileSpec(
                id=profile_id,
                display_name=str(item.get("display_name") or item.get("displayName") or profile_id).strip()
                or profile_id,
                storage_key=str(item.get("storage_key") or item.get("storageKey") or profile_id).strip()
                or profile_id,
                avatar_key=str(item.get("avatar_key") or item.get("avatarKey") or "mochi").strip()
                or "mochi",
                enabled=bool(item.get("enabled", True)),
                created_at=str(item.get("created_at") or item.get("createdAt") or ""),
            )
        )
    if not profiles:
        return None
    default_profile_id = str(value.get("defaultProfileId") or value.get("default_profile_id") or "").strip()
    if default_profile_id not in profile_ids:
        default_profile_id = profiles[0].id
    active_profile_id = str(value.get("activeProfileId") or value.get("active_profile_id") or "").strip()
    if active_profile_id not in profile_ids:
        active_profile_id = default_profile_id
    try:
        version = int(value.get("version", 1))
    except (TypeError, ValueError):
        version = 1
    return ProfileRegistry(
        version=version,
        default_profile_id=default_profile_id,
        active_profile_id=active_profile_id,
        profiles=tuple(profiles),
    )


def _empty_projection() -> dict[str, Any]:
    return {"overview": {}, "profiles": [], **{name: [] for name in _COLLECTION_NAMES}}


def _filter_recent_completed_items(
    items: list[dict[str, Any]],
    *,
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    current = now or datetime.now(timezone.utc)
    recent: list[dict[str, Any]] = []
    for item in items:
        dt = _coerce_dt(item.get("updatedAt") or item.get("updated_at") or item.get("lastRunAt"))
        if dt is None:
            continue
        age_seconds = max(0.0, (current - dt).total_seconds())
        if age_seconds > _RECENT_COMPLETED_WINDOW_SECONDS:
            continue
        recent.append(dict(item))
    recent.sort(key=lambda item: str(item.get("updatedAt", "") or ""), reverse=True)
    return recent[:_RECENT_COMPLETED_LIMIT]


def _profile_status_summary(request: ProfileStatusSummaryRequest) -> str:
    if request.is_active and request.is_live:
        if request.session_reply_count or request.subagent_count:
            parts: list[str] = []
            if request.session_reply_count:
                parts.append(f"{request.session_reply_count} 个会话")
            if request.subagent_count:
                parts.append(f"{request.subagent_count} 个子代理")
            return " / ".join(parts) + " 工作中"
        if request.other_working_count:
            return f"{request.other_working_count} 项工作进行中"
        if request.automation_count:
            return f"{request.automation_count} 个自动化待命"
        return "当前分身空闲"
    if request.is_active:
        if request.automation_count:
            return f"网关未启动 · {request.automation_count} 个自动化待命"
        return "网关未启动"
    if request.automation_count:
        return f"{request.automation_count} 个自动化待命"
    parts: list[str] = []
    if request.total_session_count:
        parts.append(f"{request.total_session_count} 个会话")
    if request.total_child_session_count:
        parts.append(f"{request.total_child_session_count} 个子代理")
    return " / ".join(parts) if parts else "当前空闲"


def _task_time_label(task: dict[str, Any]) -> str:
    for value in (
        task.get("next_run_at_ms"),
        task.get("next_run_text"),
        task.get("last_run_at_ms"),
        task.get("updated_at_ms"),
    ):
        label = _relative_time(value)
        if label:
            return label
    return ""
