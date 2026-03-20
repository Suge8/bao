from __future__ import annotations

from datetime import datetime
from pathlib import Path


def _tr(lang: str, zh: str, en: str) -> str:
    return zh if lang == "zh" else en


def _normalized_path(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    return str(Path(text).expanduser())


def _format_timestamp(value_ms: int | None) -> str:
    if not value_ms:
        return ""
    try:
        return datetime.fromtimestamp(value_ms / 1000).strftime("%Y-%m-%d %H:%M")
    except (OSError, OverflowError, ValueError):
        return ""


def _preview_text(content: str, limit: int = 160) -> str:
    normalized = " ".join(part.strip() for part in content.splitlines() if part.strip())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "…"


def _strip_line_prefix(text: str) -> str:
    normalized = text.strip()
    for prefix in ("- [ ] ", "- [x] ", "- [X] ", "- ", "* "):
        if normalized.startswith(prefix):
            return normalized[len(prefix) :].strip()
    parts = normalized.split(". ", 1)
    if len(parts) == 2 and parts[0].isdigit():
        return parts[1].strip()
    return normalized


def _heartbeat_preview(content: str, limit: int = 160) -> str:
    lines: list[str] = []
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("<!--") or line.endswith("-->") or line.startswith("#"):
            continue
        cleaned = _strip_line_prefix(line)
        if cleaned:
            lines.append(cleaned)
    return _preview_text("\n".join(lines), limit=limit)
