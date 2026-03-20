from __future__ import annotations

from datetime import datetime
from typing import Any


def format_display_title(key: str, title: Any, *, natural_key: str = "desktop:local") -> str:
    if isinstance(title, str):
        cleaned = title.strip()
        if cleaned:
            return cleaned
    if key == natural_key:
        return "default"
    if "::" in key:
        _prefix, _sep, suffix = key.partition("::")
        if suffix:
            return suffix
    return key


def session_family_key(key: str) -> str:
    if "::" in key:
        prefix, _sep, _suffix = key.partition("::")
        return prefix
    return key


def session_channel_key(key: str) -> str:
    family = session_family_key(key)
    if ":" in family:
        prefix, _sep, _rest = family.partition(":")
        return prefix or "other"
    return family if family == "heartbeat" else "other"


def parse_updated_at(value: Any) -> datetime | None:
    if isinstance(value, (int, float)):
        raw = float(value)
        if raw <= 0:
            return None
        if raw > 10_000_000_000:
            raw /= 1000.0
        try:
            return datetime.fromtimestamp(raw)
        except (OverflowError, OSError, ValueError):
            return None
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        if raw.isdigit():
            return parse_updated_at(int(raw))
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def format_updated_label(updated: Any) -> str:
    dt = parse_updated_at(updated)
    if dt is None:
        return ""
    now = datetime.now(tz=dt.tzinfo)
    seconds = max(0, int((now - dt).total_seconds()))
    if seconds < 60:
        return "<1m"
    if seconds < 3600:
        return f"{seconds // 60}m"
    if seconds < 86400:
        return f"{seconds // 3600}h"
    if seconds < 604800:
        return f"{seconds // 86400}d"
    if dt.year == now.year:
        return f"{dt.month}/{dt.day}"
    return f"{dt.year}/{dt.month}/{dt.day}"


def sidebar_channel_sort_key(channel: str) -> tuple[int, str]:
    if channel == "desktop":
        return (0, channel)
    if channel == "heartbeat":
        return (2, channel)
    return (1, channel)


def visible_sidebar_items(
    items: list[dict[str, Any]],
    *,
    expanded: bool,
    active_key: str,
) -> list[dict[str, Any]]:
    if expanded:
        return items
    if not active_key:
        return []
    return [item for item in items if str(item.get("key", "")) == active_key]
