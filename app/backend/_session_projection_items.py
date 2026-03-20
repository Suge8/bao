from __future__ import annotations

from typing import Any, Iterable

from bao.session.state import (
    session_routing_metadata,
    session_runtime_state,
    session_view_state,
    session_workflow_state,
)

from ._session_projection_core import (
    ActiveSessionProjection,
    SessionItemSpec,
    VisibleSessionSelection,
)
from ._session_projection_utils import (
    format_display_title,
    format_updated_label,
    session_channel_key,
)


def build_session_item(spec: SessionItemSpec) -> dict[str, Any]:
    normalized_count = (
        spec.message_count if isinstance(spec.message_count, int) and spec.message_count >= 0 else None
    )
    normalized_has_messages = (
        spec.has_messages
        if isinstance(spec.has_messages, bool)
        else (normalized_count > 0 if normalized_count is not None else None)
    )
    running = bool(spec.is_running)
    return {
        "key": spec.key,
        "title": format_display_title(spec.key, spec.title, natural_key=spec.natural_key),
        "updated_at": spec.updated_at,
        "updated_label": format_updated_label(spec.updated_at),
        "channel": spec.channel,
        "has_unread": spec.has_unread,
        "message_count": normalized_count,
        "has_messages": normalized_has_messages,
        "session_kind": spec.session_kind,
        "is_read_only": spec.read_only,
        "parent_session_key": spec.parent_session_key,
        "parent_title": spec.parent_title,
        "child_status": spec.child_status,
        "is_running": running,
        "self_running": running if spec.self_running is None else bool(spec.self_running),
        "needs_tail_backfill": bool(spec.needs_tail_backfill),
    }


def filter_session_dicts(raw_sessions: list[Any]) -> list[dict[str, Any]]:
    return [item for item in raw_sessions if isinstance(item, dict)]


def project_active_session(
    sessions: Iterable[dict[str, Any]],
    key: str,
) -> ActiveSessionProjection:
    for session in sessions:
        if str(session.get("key", "")) != key:
            continue
        message_count = session.get("message_count")
        has_messages = session.get("has_messages")
        return ActiveSessionProjection(
            key=key,
            message_count=message_count if isinstance(message_count, int) and message_count >= 0 else None,
            has_messages=has_messages if isinstance(has_messages, bool) else None,
            read_only=bool(session.get("is_read_only", False)),
        )
    return ActiveSessionProjection(key=key, message_count=None, has_messages=None, read_only=False)


def visible_session_key(selection: VisibleSessionSelection) -> str:
    for candidate in selection.candidates:
        if candidate and _is_visible_candidate(candidate, selection):
            return candidate
    return ""


def visible_session_key_for_channel(selection: VisibleSessionSelection, channel: str) -> str:
    for candidate in selection.candidates:
        if not candidate or not _is_visible_candidate(candidate, selection):
            continue
        if session_channel_key(candidate) == channel:
            return candidate
    return ""


def _is_visible_candidate(candidate: str, selection: VisibleSessionSelection) -> bool:
    return candidate in selection.pending_create_keys or candidate in selection.available_keys


def session_sort_value(item: dict[str, Any]) -> tuple[int, float | str, str]:
    updated_at = item.get("updated_at", "")
    if isinstance(updated_at, (int, float)):
        base: tuple[int, float | str] = (2, float(updated_at))
    elif isinstance(updated_at, str) and updated_at:
        base = (1, updated_at)
    else:
        base = (0, "")
    key = str(item.get("key", "") or "")
    return base[0], base[1], key


def title_by_key(sessions: Iterable[dict[str, Any]]) -> dict[str, str]:
    return {
        str(item.get("key", "")): str(item.get("title", "") or item.get("key", ""))
        for item in sessions
        if str(item.get("key", ""))
    }


def running_parent_keys(sessions: Iterable[dict[str, Any]]) -> set[str]:
    return {
        str(item.get("parent_session_key", ""))
        for item in sessions
        if str(item.get("child_status", "")) == "running"
        and str(item.get("parent_session_key", ""))
    }


def project_session_item(
    session: dict[str, Any],
    *,
    natural_key: str,
    current_sessions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    key = str(session.get("key") or "")
    routing_payload = session.get("routing") if isinstance(session.get("routing"), dict) else {}
    runtime_payload = session.get("runtime") if isinstance(session.get("runtime"), dict) else {}
    workflow_payload = session.get("workflow") if isinstance(session.get("workflow"), dict) else {}
    view_payload = session.get("view") if isinstance(session.get("view"), dict) else {}
    if not (routing_payload and runtime_payload and workflow_payload and view_payload):
        raise ValueError(f"session entry missing structured snapshot fields: {key}")
    routing = session_routing_metadata({"routing": routing_payload})
    runtime = session_runtime_state(runtime_payload)
    workflow = session_workflow_state({"workflow": workflow_payload})
    view = session_view_state({"view": view_payload})
    return build_session_item(
        SessionItemSpec(
            key=key,
            natural_key=natural_key,
            updated_at=session.get("updated_at", ""),
            channel=_project_channel(key, routing.session_kind, routing.parent_session_key),
            has_unread=view.read_receipts.has_unread_ai,
            title=view.title,
            message_count=session.get("message_count"),
            has_messages=session.get("has_messages"),
            session_kind=routing.session_kind,
            read_only=routing.read_only,
            parent_session_key=routing.parent_session_key,
            parent_title=_parent_title(routing.parent_session_key, current_sessions or []),
            child_status=workflow.child_outcome.status or ("running" if runtime.child_running else ""),
            is_running=runtime.is_running,
            self_running=runtime.is_running,
            needs_tail_backfill=bool(session.get("needs_tail_backfill", False)),
        )
    )


def _project_channel(key: str, session_kind: str, parent_session_key: str) -> str:
    if session_kind == "subagent_child" and parent_session_key:
        return session_channel_key(parent_session_key)
    return session_channel_key(key)


def _parent_title(parent_session_key: str, current_sessions: list[dict[str, Any]]) -> str:
    if not parent_session_key:
        return ""
    for item in current_sessions:
        if str(item.get("key", "")) == parent_session_key:
            return str(item.get("title", "") or parent_session_key)
    return ""


def normalize_session_item(
    session: dict[str, Any],
    *,
    title_index: dict[str, str],
    running_parent_index: set[str],
) -> dict[str, Any]:
    normalized = dict(session)
    key = str(normalized.get("key", ""))
    parent_key = str(normalized.get("parent_session_key", "") or "")
    normalized["parent_title"] = title_index.get(parent_key, "")
    self_running = bool(normalized.get("self_running", normalized.get("is_running", False)))
    normalized["is_running"] = self_running or key in running_parent_index
    return normalized


def normalize_session_items(sessions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    title_index = title_by_key(sessions)
    running_parent_index = running_parent_keys(sessions)
    return [
        normalize_session_item(
            session,
            title_index=title_index,
            running_parent_index=running_parent_index,
        )
        for session in sessions
    ]


def tail_backfill_keys(sessions: Iterable[dict[str, Any]]) -> list[str]:
    keys: list[str] = []
    for item in sessions:
        if not bool(item.get("needs_tail_backfill", False)):
            continue
        key = str(item.get("key", "")).strip()
        if key:
            keys.append(key)
    return keys


def pick_latest_key(sessions: list[dict[str, Any]], *, preferred_channel: str) -> str:
    preferred = [s for s in sessions if str(s.get("channel", "")) == preferred_channel]
    candidates = preferred if preferred else sessions
    if not candidates:
        return ""
    sort_values = [session_sort_value(s)[:2] for s in candidates]
    if not any(value[0] > 0 for value in sort_values):
        return str(candidates[0].get("key", "") or "")
    if len(set(sort_values)) == 1:
        return str(candidates[0].get("key", "") or "")
    return str(max(candidates, key=session_sort_value).get("key", "") or "")
