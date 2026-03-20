from __future__ import annotations

from typing import Any


def normalize_discovery_items(raw: object) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    normalized: list[dict[str, Any]] = []
    for item in raw:
        snapshot = normalize_discovery_snapshot(item)
        if snapshot:
            normalized.append(snapshot)
    return normalized


def normalize_discovery_snapshot(raw: object) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {}
    snapshot = {str(key): value for key, value in raw.items() if isinstance(key, str)}
    session_ref = _text(snapshot.get("session_ref")) or _text(snapshot.get("id"))
    session_key = _text(snapshot.get("session_key")) or _text(snapshot.get("key"))
    item_id = session_ref or session_key
    if not item_id:
        return {}
    title = _text(snapshot.get("title")) or session_key or session_ref
    snapshot.update(
        {
            "id": item_id,
            "session_ref": session_ref,
            "session_key": session_key,
            "title": title,
            "channel": _text(snapshot.get("channel")),
            "availability": _text(snapshot.get("availability")),
            "binding_key": _text(snapshot.get("binding_key")),
            "reason": _text(snapshot.get("reason")),
            "scope": _text(snapshot.get("scope")),
            "identity_ref": _text(snapshot.get("identity_ref")),
            "default": bool(snapshot.get("default") or snapshot.get("is_default")),
        }
    )
    return snapshot


def _text(value: object) -> str:
    if isinstance(value, bool):
        return ""
    if isinstance(value, int):
        return str(value)
    if not isinstance(value, str):
        return ""
    return value.strip()
