from __future__ import annotations

from typing import Any

from ._session_projection_core import SidebarProjection, SidebarProjectionRequest
from ._session_projection_utils import sidebar_channel_sort_key, visible_sidebar_items


def build_sidebar_projection(request: SidebarProjectionRequest) -> SidebarProjection:
    groups, order, unread_fingerprint_parts = _sidebar_channel_items(
        request.sessions,
        active_key=request.active_key,
    )
    expanded_groups = _expanded_groups(groups, order, request)
    previous_rows = [dict(row) for row in request.current_rows or []]
    rows = _projection_rows(groups, request, expanded_groups)
    _pin_sidebar_active_row(rows, active_key=request.active_key, current_rows=previous_rows)
    unread_fingerprint_parts.sort()
    return SidebarProjection(
        rows=rows,
        expanded_groups=expanded_groups,
        unread_count=len(unread_fingerprint_parts),
        unread_fingerprint="|".join(unread_fingerprint_parts),
    )


def _sidebar_channel_items(
    sessions: list[dict[str, Any]],
    *,
    active_key: str,
) -> tuple[dict[str, list[dict[str, Any]]], list[str], list[str]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    order: list[str] = []
    unread_fingerprint_parts: list[str] = []
    for session in sessions:
        item = _sidebar_channel_item(session, active_key=active_key)
        channel = str(item["channel"])
        if channel not in groups:
            groups[channel] = []
            order.append(channel)
        groups[channel].append(item)
        if item["has_unread"]:
            unread_fingerprint_parts.append(str(item["key"]))
    order.sort(key=sidebar_channel_sort_key)
    return groups, order, unread_fingerprint_parts


def _sidebar_channel_item(session: dict[str, Any], *, active_key: str) -> dict[str, Any]:
    key = str(session.get("key", ""))
    channel = str(session.get("channel", "other") or "other")
    return {
        "key": key,
        "title": str(session.get("title", "") or key),
        "channel": channel,
        "visual_channel": str(session.get("visual_channel", _visual_channel(session, channel)) or channel),
        "has_unread": bool(session.get("has_unread", False)) and key != active_key,
        "updated_text": str(session.get("updated_label", "") or ""),
        "is_read_only": bool(session.get("is_read_only", False)),
        "is_running": bool(session.get("is_running", False)),
        "parent_session_key": str(session.get("parent_session_key", "") or ""),
        "is_child_session": str(session.get("session_kind", "regular") or "regular") == "subagent_child",
    }


def _visual_channel(session: dict[str, Any], channel: str) -> str:
    if str(session.get("session_kind", "regular") or "regular") == "subagent_child":
        return "subagent"
    return channel


def _expanded_groups(
    groups: dict[str, list[dict[str, Any]]],
    order: list[str],
    request: SidebarProjectionRequest,
) -> dict[str, bool]:
    expanded_groups = {
        channel: expanded
        for channel, expanded in request.expanded_groups.items()
        if channel in groups
    }
    for channel in order:
        if channel not in expanded_groups:
            expanded_groups[channel] = _initial_group_expanded(
                channel,
                groups[channel],
                active_key=request.active_key,
            )
    return expanded_groups


def _initial_group_expanded(
    channel: str,
    items: list[dict[str, Any]],
    *,
    active_key: str,
) -> bool:
    if active_key and any(str(item.get("key", "")) == active_key for item in items):
        return True
    if active_key:
        return False
    return channel == "desktop"


def _projection_rows(
    groups: dict[str, list[dict[str, Any]]],
    request: SidebarProjectionRequest,
    expanded_groups: dict[str, bool],
) -> list[dict[str, Any]]:
    order = sorted(groups.keys(), key=sidebar_channel_sort_key)
    previous_rows = [dict(row) for row in request.current_rows or []]
    if request.channels is None or not previous_rows:
        return _fresh_projection_rows(groups, request, expanded_groups)
    existing_rows = _existing_channel_rows(previous_rows, groups, request.channels)
    rows: list[dict[str, Any]] = []
    for channel in order:
        if channel in request.channels:
            rows.extend(
                _build_sidebar_rows_for_channel(
                    (channel, expanded_groups[channel]),
                    groups[channel],
                    request.active_key,
                )
            )
            continue
        rows.extend(existing_rows.get(channel, []))
    return rows


def _fresh_projection_rows(
    groups: dict[str, list[dict[str, Any]]],
    request: SidebarProjectionRequest,
    expanded_groups: dict[str, bool],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for channel in sorted(groups.keys(), key=sidebar_channel_sort_key):
        rows.extend(
            _build_sidebar_rows_for_channel(
                (channel, expanded_groups[channel]),
                groups[channel],
                request.active_key,
            )
        )
    return rows


def _existing_channel_rows(
    previous_rows: list[dict[str, Any]],
    groups: dict[str, list[dict[str, Any]]],
    channels: set[str],
) -> dict[str, list[dict[str, Any]]]:
    available_channels = set(groups.keys())
    existing_rows: dict[str, list[dict[str, Any]]] = {}
    for row in previous_rows:
        channel = str(row.get("channel", "other") or "other")
        if channel not in available_channels and channel not in channels:
            continue
        existing_rows.setdefault(channel, []).append(dict(row))
    return existing_rows


def _build_sidebar_rows_for_channel(
    context: tuple[str, bool],
    items: list[dict[str, Any]],
    active_key: str,
) -> list[dict[str, Any]]:
    channel, expanded = context
    ordered_items = _reorder_sidebar_items(items)
    rows = [_header_row(channel, ordered_items, expanded)]
    rows.extend(
        _session_rows(
            channel,
            visible_sidebar_items(ordered_items, expanded=expanded, active_key=active_key),
        )
    )
    return rows


def _reorder_sidebar_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    child_buckets: dict[str, list[dict[str, Any]]] = {}
    child_remainder: list[dict[str, Any]] = []
    ordered_items: list[dict[str, Any]] = []
    for item in items:
        if not bool(item.get("is_child_session", False)):
            continue
        parent_key = str(item.get("parent_session_key", ""))
        if parent_key:
            child_buckets.setdefault(parent_key, []).append(item)
        else:
            child_remainder.append(item)
    for item in items:
        if bool(item.get("is_child_session", False)):
            continue
        ordered_items.append(item)
        ordered_items.extend(child_buckets.get(str(item.get("key", "")), []))
    ordered_items.extend(child_remainder)
    return ordered_items


def _header_row(channel: str, items: list[dict[str, Any]], expanded: bool) -> dict[str, Any]:
    return {
        "row_id": f"header:{channel}",
        "is_header": True,
        "channel": channel,
        "expanded": expanded,
        "item_key": "",
        "item_title": "",
        "item_updated_text": "",
        "visual_channel": channel,
        "is_read_only": False,
        "is_running": False,
        "is_child_session": False,
        "parent_session_key": "",
        "item_has_unread": False,
        "item_count": len(items),
        "group_unread_count": sum(1 for item in items if bool(item.get("has_unread", False))),
        "group_has_running": any(bool(item.get("is_running", False)) for item in items),
        "is_last_in_group": False,
        "is_first_in_group": False,
    }

def _session_rows(channel: str, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    last_index = len(items) - 1
    for index, item in enumerate(items):
        rows.append(
            {
                "row_id": f"session:{item.get('key', '')}",
                "is_header": False,
                "channel": channel,
                "expanded": False,
                "item_key": str(item.get("key", "")),
                "item_title": str(item.get("title", "") or item.get("key", "")),
                "item_updated_text": str(item.get("updated_text", "") or ""),
                "visual_channel": str(item.get("visual_channel", channel) or channel),
                "is_read_only": bool(item.get("is_read_only", False)),
                "is_running": bool(item.get("is_running", False)),
                "is_child_session": bool(item.get("is_child_session", False)),
                "parent_session_key": str(item.get("parent_session_key", "") or ""),
                "item_has_unread": bool(item.get("has_unread", False)),
                "item_count": 0,
                "group_unread_count": 0,
                "group_has_running": False,
                "is_last_in_group": index == last_index,
                "is_first_in_group": index == 0,
            }
        )
    return rows


def _pin_sidebar_active_row(
    rows: list[dict[str, Any]],
    *,
    active_key: str,
    current_rows: list[dict[str, Any]],
) -> None:
    if not active_key:
        return
    current_index = _current_active_row_index(current_rows, active_key)
    if current_index < 0 or current_index >= len(current_rows):
        return
    active_channel = str(current_rows[current_index].get("channel", "") or "")
    if not active_channel:
        return
    next_index = next((index for index, row in enumerate(rows) if str(row.get("item_key", "")) == active_key), -1)
    if next_index < 0 or next_index == current_index:
        return
    pinned_row = rows.pop(next_index)
    session_slot = 0
    for index in range(current_index - 1, -1, -1):
        row = current_rows[index]
        if str(row.get("channel", "") or "") != active_channel:
            continue
        if bool(row.get("is_header", False)):
            break
        session_slot += 1
    header_index = -1
    session_count = 0
    for index, row in enumerate(rows):
        if str(row.get("channel", "") or "") != active_channel:
            continue
        if bool(row.get("is_header", False)):
            header_index = index
            continue
        if header_index >= 0:
            session_count += 1
    if header_index < 0:
        rows.insert(max(0, min(current_index, len(rows))), pinned_row)
        return
    rows.insert(header_index + 1 + min(session_slot, session_count), pinned_row)


def _current_active_row_index(current_rows: list[dict[str, Any]], active_key: str) -> int:
    return next(
        (
            index
            for index, row in enumerate(current_rows)
            if str(row.get("row_id", "")) == f"session:{active_key}"
        ),
        -1,
    )
