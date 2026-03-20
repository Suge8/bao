# ruff: noqa: E402, N802, N815, F403, F405, I001
from __future__ import annotations

from tests._chat_view_integration_shared import *
def _session_role_value(model: QAbstractListModel, index: QModelIndex, offset: int) -> object:
    return model.data(index, int(Qt.ItemDataRole.UserRole) + offset)

def _reorder_sidebar_items(items: list[dict[str, object]]) -> list[dict[str, object]]:
    child_buckets: dict[str, list[dict[str, object]]] = {}
    child_remainder: list[dict[str, object]] = []
    reordered_items: list[dict[str, object]] = []
    for item in items:
        if item.get("session_kind") != "subagent_child":
            continue
        parent_key = str(item.get("parent_session_key", "") or "")
        if parent_key:
            child_buckets.setdefault(parent_key, []).append(item)
            continue
        child_remainder.append(item)
    for item in items:
        if item.get("session_kind") == "subagent_child":
            continue
        reordered_items.append(item)
        reordered_items.extend(child_buckets.get(str(item.get("key", "")), []))
    reordered_items.extend(child_remainder)
    return reordered_items

def _sidebar_header_row(
    channel: str,
    expanded: bool,
    items: list[dict[str, object]],
) -> dict[str, object]:
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

def _sidebar_item_row(
    channel: str,
    item: dict[str, object],
    position: tuple[int, int],
) -> dict[str, object]:
    index, total = position
    return {
        "row_id": f"session:{item.get('key', '')}",
        "is_header": False,
        "channel": channel,
        "expanded": False,
        "item_key": str(item.get("key", "")),
        "item_title": str(item.get("title", item.get("key", "")) or ""),
        "item_updated_text": str(item.get("updated_label", "") or ""),
        "visual_channel": "subagent"
        if item.get("session_kind") == "subagent_child"
        else str(item.get("channel", channel) or channel),
        "is_read_only": bool(item.get("is_read_only", False)),
        "is_running": bool(item.get("is_running", False)),
        "is_child_session": item.get("session_kind") == "subagent_child",
        "parent_session_key": str(item.get("parent_session_key", "") or ""),
        "item_has_unread": bool(item.get("has_unread", False)),
        "item_count": 0,
        "group_unread_count": 0,
        "group_has_running": False,
        "is_last_in_group": index == total - 1,
        "is_first_in_group": index == 0,
    }
class DummySessionService(QObject):
    sessionsChanged = Signal()
    sidebarProjectionWillChange = Signal()
    sidebarProjectionChanged = Signal()
    activeKeyChanged = Signal(str)
    deleteCompleted = Signal(str, bool, str)
    activeReady = Signal()
    sessionsLoadingChanged = Signal(bool)
    sessionDiscoveryChanged = Signal()

    def __init__(self, sessions_model: QAbstractListModel, parent: QObject | None = None) -> None:
        super().__init__(parent)
        from app.backend.session import SidebarRowsModel

        self._sessions_model = sessions_model
        self._sidebar_model = SidebarRowsModel()
        self._active_key = ""
        self._sessions_loading = False
        self._sidebar_expanded_groups: dict[str, bool] = {}
        self._sidebar_unread_count = 0
        self._sidebar_unread_fingerprint = ""
        self._recent_sessions: list[dict[str, object]] = []
        self._lookup_results: list[dict[str, object]] = []
        self._default_session: dict[str, object] = {}
        self._resolved_session: dict[str, object] = {}
        self._session_lookup_query = ""
        self.new_session_calls: list[str] = []
        self.select_session_calls: list[str] = []
        self.delete_session_calls: list[str] = []
        self.lookup_query_calls: list[str] = []
        self.resolve_session_ref_calls: list[str] = []
        self.sessionsChanged.connect(self._rebuild_sidebar_model)
        self._rebuild_sidebar_model()

    @Property(str, notify=activeKeyChanged)
    def activeKey(self) -> str:
        return self._active_key

    @Property(bool, constant=True)
    def activeSessionReadOnly(self) -> bool:
        return False

    def setActiveKey(self, key: str) -> None:
        if self._active_key == key:
            return
        self._active_key = key
        rows = getattr(self._sessions_model, "_rows", None)
        if isinstance(rows, list):
            for row in rows:
                if isinstance(row, dict) and row.get("key") == key:
                    row["has_unread"] = False
        self._rebuild_sidebar_model()
        self.activeKeyChanged.emit(key)

    @Property(QObject, constant=True)
    def sessionsModel(self) -> QObject:
        return self._sessions_model

    @Property(QObject, constant=True)
    def sidebarModel(self) -> QObject:
        return self._sidebar_model

    @Property(int, notify=sidebarProjectionChanged)
    def sidebarUnreadCount(self) -> int:
        return self._sidebar_unread_count

    @Property(str, notify=sidebarProjectionChanged)
    def sidebarUnreadFingerprint(self) -> str:
        return self._sidebar_unread_fingerprint

    @Property(bool, notify=sessionsLoadingChanged)
    def sessionsLoading(self) -> bool:
        return self._sessions_loading

    @Property("QVariantList", notify=sessionDiscoveryChanged)
    def recentSessions(self) -> list[dict[str, object]]:
        return [dict(item) for item in self._recent_sessions]

    @Property("QVariantList", notify=sessionDiscoveryChanged)
    def lookupResults(self) -> list[dict[str, object]]:
        return [dict(item) for item in self._lookup_results]

    @Property("QVariantMap", notify=sessionDiscoveryChanged)
    def defaultSession(self) -> dict[str, object]:
        return dict(self._default_session)

    @Property("QVariantMap", notify=sessionDiscoveryChanged)
    def resolvedSession(self) -> dict[str, object]:
        return dict(self._resolved_session)

    @Property(str, notify=sessionDiscoveryChanged)
    def sessionLookupQuery(self) -> str:
        return self._session_lookup_query

    def setSessionsLoading(self, loading: bool) -> None:
        if self._sessions_loading == loading:
            return
        self._sessions_loading = loading
        self.sessionsLoadingChanged.emit(loading)

    def setDiscoveryPayload(
        self,
        *,
        recent_sessions: list[dict[str, object]] | None = None,
        lookup_results: list[dict[str, object]] | None = None,
        default_session: dict[str, object] | None = None,
        resolved_session: dict[str, object] | None = None,
        lookup_query: str | None = None,
    ) -> None:
        if recent_sessions is not None:
            self._recent_sessions = [dict(item) for item in recent_sessions]
        if lookup_results is not None:
            self._lookup_results = [dict(item) for item in lookup_results]
        if default_session is not None:
            self._default_session = dict(default_session)
        if resolved_session is not None:
            self._resolved_session = dict(resolved_session)
        if lookup_query is not None:
            self._session_lookup_query = str(lookup_query)
        self.sessionDiscoveryChanged.emit()

    @Slot(str)
    def newSession(self, name: str) -> None:
        self.new_session_calls.append(name)

    @Slot(str)
    def selectSession(self, key: str) -> None:
        self.select_session_calls.append(key)

    @Slot(str)
    def deleteSession(self, key: str) -> None:
        self.delete_session_calls.append(key)

    @Slot(str)
    def setSessionLookupQuery(self, value: str) -> None:
        next_value = str(value or "")
        self.lookup_query_calls.append(next_value)
        if self._session_lookup_query == next_value:
            return
        self._session_lookup_query = next_value
        self.sessionDiscoveryChanged.emit()

    @Slot()
    def clearSessionLookup(self) -> None:
        self.setSessionLookupQuery("")

    @Slot(str)
    def resolveSessionReference(self, value: str) -> None:
        next_value = str(value or "")
        self.resolve_session_ref_calls.append(next_value)
        if next_value and str(self._resolved_session.get("session_ref", "")) != next_value:
            self._resolved_session = {"session_ref": next_value}
        elif not next_value:
            self._resolved_session = {}
        self.sessionDiscoveryChanged.emit()

    @Slot(str)
    def toggleSidebarGroup(self, channel: str) -> None:
        if not channel:
            return
        self._sidebar_expanded_groups[channel] = (
            self._sidebar_expanded_groups.get(channel, False) is not True
        )
        self._rebuild_sidebar_model()

    def _session_rows(self) -> list[dict[str, object]]:
        rows = getattr(self._sessions_model, "_rows", None)
        if isinstance(rows, list):
            return [dict(row) for row in rows if isinstance(row, dict)]
        result: list[dict[str, object]] = []
        for i in range(self._sessions_model.rowCount()):
            idx = self._sessions_model.index(i)
            key = _session_role_value(self._sessions_model, idx, 1)
            if not isinstance(key, str) or not key:
                continue
            result.append(
                {
                    "key": key,
                    "title": _session_role_value(self._sessions_model, idx, 2) or key,
                    "updated_label": _session_role_value(self._sessions_model, idx, 7) or "",
                    "channel": _session_role_value(self._sessions_model, idx, 5) or "other",
                    "has_unread": bool(_session_role_value(self._sessions_model, idx, 6) or False),
                    "session_kind": _session_role_value(self._sessions_model, idx, 10)
                    or "regular",
                    "is_read_only": bool(_session_role_value(self._sessions_model, idx, 11) or False),
                    "parent_session_key": _session_role_value(self._sessions_model, idx, 12) or "",
                    "is_running": bool(_session_role_value(self._sessions_model, idx, 15) or False),
                }
            )
        return result

    def _initial_group_expanded(self, channel: str, items: list[dict[str, object]]) -> bool:
        if self._active_key and any(str(item.get("key", "")) == self._active_key for item in items):
            return True
        if self._active_key:
            return False
        return channel == "desktop"

    def _visible_items_for_group(
        self, items: list[dict[str, object]], *, expanded: bool
    ) -> list[dict[str, object]]:
        from app.backend import session as session_backend

        visible_items = getattr(session_backend, "_visible_sidebar_items")
        return visible_items(items, expanded=expanded, active_key=self._active_key)

    def _group_sessions(
        self, sessions: list[dict[str, object]]
    ) -> tuple[dict[str, list[dict[str, object]]], list[str], list[str]]:
        groups: dict[str, list[dict[str, object]]] = {}
        order: list[str] = []
        unread_parts: list[str] = []
        for session in sessions:
            channel = str(session.get("channel", "other") or "other")
            if channel not in groups:
                groups[channel] = []
                order.append(channel)
            session_copy = dict(session)
            if str(session_copy.get("key", "")) == self._active_key:
                session_copy["has_unread"] = False
            groups[channel].append(session_copy)
            if bool(session_copy.get("has_unread", False)):
                unread_parts.append(str(session_copy.get("key", "")))
        return groups, order, unread_parts

    def _sync_expanded_groups(
        self, order: list[str], groups: dict[str, list[dict[str, object]]]
    ) -> list[str]:
        available = set(order)
        self._sidebar_expanded_groups = {
            channel: expanded
            for channel, expanded in self._sidebar_expanded_groups.items()
            if channel in available
        }
        order.sort(
            key=lambda channel: (
                (0, channel)
                if channel == "desktop"
                else ((2, channel) if channel == "heartbeat" else (1, channel))
            )
        )
        for channel in order:
            if channel in self._sidebar_expanded_groups:
                continue
            self._sidebar_expanded_groups[channel] = self._initial_group_expanded(
                channel, groups[channel]
            )
        return order

    def _append_group_rows(self, rows: list[dict[str, object]], channel: str, items: list[dict[str, object]]) -> None:
        expanded = self._sidebar_expanded_groups.get(channel, False) is True
        reordered_items = _reorder_sidebar_items(items)
        rows.append(_sidebar_header_row(channel, expanded, reordered_items))
        visible_items = self._visible_items_for_group(reordered_items, expanded=expanded)
        total = len(visible_items)
        rows.extend(
            _sidebar_item_row(channel, item, (index, total))
            for index, item in enumerate(visible_items)
        )

    def _rebuild_sidebar_model(self) -> None:
        self.sidebarProjectionWillChange.emit()
        sessions = self._session_rows()
        groups, order, unread_parts = self._group_sessions(sessions)
        order = self._sync_expanded_groups(order, groups)
        rows: list[dict[str, object]] = []
        for channel in order:
            self._append_group_rows(rows, channel, groups[channel])

        active_index = self._sidebar_model.active_row_index(self._active_key)
        if active_index >= 0 and self._active_key:
            next_index = next(
                (
                    idx
                    for idx, row in enumerate(rows)
                    if str(row.get("item_key", "")) == self._active_key
                ),
                -1,
            )
            if next_index >= 0 and next_index != active_index:
                pinned = rows.pop(next_index)
                rows.insert(max(0, min(active_index, len(rows))), pinned)

        unread_parts.sort()
        self._sidebar_model.sync_rows(rows)
        self._sidebar_unread_count = len(unread_parts)
        self._sidebar_unread_fingerprint = "|".join(unread_parts)
        self.sidebarProjectionChanged.emit()

__all__ = [name for name in globals() if name != "__all__" and not (name.startswith("__") and name.endswith("__"))]
