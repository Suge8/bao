from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

EXPERIENCE_DEPRECATED_MODES = frozenset({"active", "all", "deprecated"})
EXPERIENCE_SORT_OPTIONS = frozenset({"updated_desc", "quality_desc", "uses_desc"})


def parse_updated_at(value: Any) -> datetime | None:
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def format_updated_label(value: Any) -> str:
    dt = parse_updated_at(value)
    if dt is None:
        return ""
    now = datetime.now(tz=dt.tzinfo)
    delta = now - dt
    seconds = max(0, int(delta.total_seconds()))
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


@dataclass(frozen=True)
class ExperienceQueryState:
    query: str = ""
    category: str = ""
    outcome: str = ""
    deprecated_mode: str = "active"
    min_quality: int = 0
    sort_by: str = "updated_desc"


@dataclass(frozen=True)
class RunnerTaskResult:
    kind: str
    blocking: bool
    ok: bool
    error: str
    payload: object

