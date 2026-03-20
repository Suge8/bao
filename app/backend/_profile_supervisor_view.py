from __future__ import annotations

from typing import Any


def _avatar_source(avatar_key: str) -> str:
    key = str(avatar_key or "mochi").strip() or "mochi"
    return f"../resources/profile-avatars/{key}.svg"


def _icon_source(name: str) -> str:
    return f"../resources/icons/{name}.svg"


def _channel_icon_source(channel: str) -> str:
    normalized = str(channel or "").strip().lower()
    if normalized in {
        "telegram",
        "discord",
        "whatsapp",
        "feishu",
        "slack",
        "qq",
        "dingtalk",
        "imessage",
    }:
        return f"../resources/icons/channel-{normalized}.svg"
    if normalized == "desktop":
        return _icon_source("sidebar-monitor")
    if normalized == "subagent":
        return _icon_source("sidebar-subagent")
    if normalized == "heartbeat":
        return _icon_source("sidebar-heartbeat")
    if normalized == "cron":
        return _icon_source("sidebar-cron")
    if normalized == "system":
        return _icon_source("sidebar-system")
    if normalized == "email":
        return _icon_source("sidebar-mail")
    return _icon_source("sidebar-chat")


def _glyph_for_kind(kind: str, channel: str) -> str:
    if kind == "subagent_task":
        return _icon_source("sidebar-subagent")
    if kind == "cron_job":
        return _icon_source("sidebar-cron")
    if kind == "heartbeat_check":
        return _icon_source("sidebar-heartbeat")
    if kind == "issue":
        return _icon_source("sidebar-pulse")
    return _channel_icon_source(channel)


def _status_label(key: str) -> str:
    if key == "running":
        return "运行中"
    if key == "completed":
        return "已完成"
    if key == "failed":
        return "失败"
    if key == "scheduled":
        return "已调度"
    if key == "disabled":
        return "已停用"
    if key == "error":
        return "异常"
    return "待命"


def _is_hub_live(state: str) -> bool:
    return state in {"running", "starting"}


def _channel_key(value: object) -> str:
    return str(value or "").strip().lower()


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


def _dedupe_channel_keys(values: list[object]) -> list[str]:
    keys: list[str] = []
    for value in values:
        key = _channel_key(value)
        if key and key in _PROFILE_CHANNEL_KEYS and key not in keys:
            keys.append(key)
    return keys


def _hub_channel_keys(items: list[object]) -> list[str]:
    keys: list[object] = []
    for item in items:
        if isinstance(item, dict):
            keys.append(
                item.get("channel")
                or item.get("key")
                or item.get("id")
                or item.get("name")
                or item.get("label")
            )
            continue
        keys.append(item)
    return _dedupe_channel_keys(keys)


def _primary_visual_channel(channel_keys: list[object]) -> str:
    keys = _dedupe_channel_keys(channel_keys)
    for key in keys:
        if key != "desktop":
            return key
    return keys[0] if keys else "desktop"


def _session_inventory(
    sessions: list[dict[str, Any]],
    *,
    hub_channels: list[object] | None = None,
) -> dict[str, Any]:
    total_session_count = 0
    total_child_session_count = 0
    channel_keys = _hub_channel_keys(hub_channels or [])
    for item in sessions:
        kind = str(item.get("kind", "") or "")
        is_child = bool(item.get("is_child_session", item.get("isChildSession", False))) or kind == "subagent_task"
        session_key = str(item.get("key", item.get("sessionKey", "")) or "")
        if is_child:
            total_child_session_count += 1
        elif session_key or kind == "session_reply":
            total_session_count += 1
        channel = item.get("visual_channel") or item.get("visualChannel") or item.get("channel") or item.get("accentKey")
        channel_keys = _dedupe_channel_keys([*channel_keys, channel])
    return {
        "totalSessionCount": total_session_count,
        "totalChildSessionCount": total_child_session_count,
        "channelKeys": channel_keys[:4],
    }


def _session_metrics(items: list[dict[str, Any]]) -> dict[str, Any]:
    session_reply_count = 0
    subagent_count = 0
    channels: list[str] = []
    for item in items:
        kind = str(item.get("kind", "") or "")
        if kind == "session_reply":
            session_reply_count += 1
        elif kind == "subagent_task":
            subagent_count += 1
        channel = str(item.get("visualChannel", "") or "")
        if channel and channel not in channels:
            channels.append(channel)
    return {
        "sessionReplyCount": session_reply_count,
        "subagentCount": subagent_count,
        "channelKeys": channels[:3],
    }


def _automation_metrics(items: list[dict[str, Any]]) -> dict[str, Any]:
    return {"runningAutomationCount": sum(bool(item.get("isRunning", False)) for item in items)}
