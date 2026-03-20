from __future__ import annotations

from typing import Any

from PySide6.QtCore import QAbstractListModel, QByteArray, QModelIndex, QPersistentModelIndex, Qt

_ROLE_BASE = int(Qt.ItemDataRole.UserRole)
_SIDEBAR_ROLE_BASE = _ROLE_BASE + 100
_SIDEBAR_ROLE_ROW_ID = _SIDEBAR_ROLE_BASE + 1
_SIDEBAR_ROLE_IS_HEADER = _SIDEBAR_ROLE_BASE + 2
_SIDEBAR_ROLE_CHANNEL = _SIDEBAR_ROLE_BASE + 3
_SIDEBAR_ROLE_EXPANDED = _SIDEBAR_ROLE_BASE + 4
_SIDEBAR_ROLE_ITEM_KEY = _SIDEBAR_ROLE_BASE + 5
_SIDEBAR_ROLE_ITEM_TITLE = _SIDEBAR_ROLE_BASE + 6
_SIDEBAR_ROLE_ITEM_UPDATED_TEXT = _SIDEBAR_ROLE_BASE + 7
_SIDEBAR_ROLE_VISUAL_CHANNEL = _SIDEBAR_ROLE_BASE + 8
_SIDEBAR_ROLE_IS_READ_ONLY = _SIDEBAR_ROLE_BASE + 9
_SIDEBAR_ROLE_IS_RUNNING = _SIDEBAR_ROLE_BASE + 10
_SIDEBAR_ROLE_IS_CHILD_SESSION = _SIDEBAR_ROLE_BASE + 11
_SIDEBAR_ROLE_PARENT_SESSION_KEY = _SIDEBAR_ROLE_BASE + 12
_SIDEBAR_ROLE_ITEM_HAS_UNREAD = _SIDEBAR_ROLE_BASE + 14
_SIDEBAR_ROLE_ITEM_COUNT = _SIDEBAR_ROLE_BASE + 15
_SIDEBAR_ROLE_GROUP_UNREAD_COUNT = _SIDEBAR_ROLE_BASE + 16
_SIDEBAR_ROLE_GROUP_HAS_RUNNING = _SIDEBAR_ROLE_BASE + 17
_SIDEBAR_ROLE_IS_LAST_IN_GROUP = _SIDEBAR_ROLE_BASE + 18
_SIDEBAR_ROLE_IS_FIRST_IN_GROUP = _SIDEBAR_ROLE_BASE + 19

_SIDEBAR_FIELD_TO_ROLE = {
    "row_id": _SIDEBAR_ROLE_ROW_ID,
    "is_header": _SIDEBAR_ROLE_IS_HEADER,
    "channel": _SIDEBAR_ROLE_CHANNEL,
    "expanded": _SIDEBAR_ROLE_EXPANDED,
    "item_key": _SIDEBAR_ROLE_ITEM_KEY,
    "item_title": _SIDEBAR_ROLE_ITEM_TITLE,
    "item_updated_text": _SIDEBAR_ROLE_ITEM_UPDATED_TEXT,
    "visual_channel": _SIDEBAR_ROLE_VISUAL_CHANNEL,
    "is_read_only": _SIDEBAR_ROLE_IS_READ_ONLY,
    "is_running": _SIDEBAR_ROLE_IS_RUNNING,
    "is_child_session": _SIDEBAR_ROLE_IS_CHILD_SESSION,
    "parent_session_key": _SIDEBAR_ROLE_PARENT_SESSION_KEY,
    "item_has_unread": _SIDEBAR_ROLE_ITEM_HAS_UNREAD,
    "item_count": _SIDEBAR_ROLE_ITEM_COUNT,
    "group_unread_count": _SIDEBAR_ROLE_GROUP_UNREAD_COUNT,
    "group_has_running": _SIDEBAR_ROLE_GROUP_HAS_RUNNING,
    "is_last_in_group": _SIDEBAR_ROLE_IS_LAST_IN_GROUP,
    "is_first_in_group": _SIDEBAR_ROLE_IS_FIRST_IN_GROUP,
}


class SidebarRowsModel(QAbstractListModel):
    _ROLES = {
        _SIDEBAR_ROLE_ROW_ID: QByteArray(b"rowId"),
        _SIDEBAR_ROLE_IS_HEADER: QByteArray(b"isHeader"),
        _SIDEBAR_ROLE_CHANNEL: QByteArray(b"channel"),
        _SIDEBAR_ROLE_EXPANDED: QByteArray(b"expanded"),
        _SIDEBAR_ROLE_ITEM_KEY: QByteArray(b"itemKey"),
        _SIDEBAR_ROLE_ITEM_TITLE: QByteArray(b"itemTitle"),
        _SIDEBAR_ROLE_ITEM_UPDATED_TEXT: QByteArray(b"itemUpdatedText"),
        _SIDEBAR_ROLE_VISUAL_CHANNEL: QByteArray(b"visualChannel"),
        _SIDEBAR_ROLE_IS_READ_ONLY: QByteArray(b"isReadOnly"),
        _SIDEBAR_ROLE_IS_RUNNING: QByteArray(b"isRunning"),
        _SIDEBAR_ROLE_IS_CHILD_SESSION: QByteArray(b"isChildSession"),
        _SIDEBAR_ROLE_PARENT_SESSION_KEY: QByteArray(b"parentSessionKey"),
        _SIDEBAR_ROLE_ITEM_HAS_UNREAD: QByteArray(b"itemHasUnread"),
        _SIDEBAR_ROLE_ITEM_COUNT: QByteArray(b"itemCount"),
        _SIDEBAR_ROLE_GROUP_UNREAD_COUNT: QByteArray(b"groupUnreadCount"),
        _SIDEBAR_ROLE_GROUP_HAS_RUNNING: QByteArray(b"groupHasRunning"),
        _SIDEBAR_ROLE_IS_LAST_IN_GROUP: QByteArray(b"isLastInGroup"),
        _SIDEBAR_ROLE_IS_FIRST_IN_GROUP: QByteArray(b"isFirstInGroup"),
    }

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent)
        self._rows: list[dict[str, Any]] = []

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:  # noqa: B008
        if parent.isValid():
            return 0
        return len(self._rows)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = int(Qt.ItemDataRole.DisplayRole),
    ) -> Any:
        if not index.isValid() or not (0 <= index.row() < len(self._rows)):
            return None
        row = self._rows[index.row()]
        if role == _SIDEBAR_ROLE_ROW_ID:
            return row.get("row_id", "")
        if role == _SIDEBAR_ROLE_IS_HEADER:
            return bool(row.get("is_header", False))
        if role == _SIDEBAR_ROLE_CHANNEL:
            return row.get("channel", "other")
        if role == _SIDEBAR_ROLE_EXPANDED:
            return bool(row.get("expanded", False))
        if role == _SIDEBAR_ROLE_ITEM_KEY:
            return row.get("item_key", "")
        if role == _SIDEBAR_ROLE_ITEM_TITLE:
            return row.get("item_title", "")
        if role == _SIDEBAR_ROLE_ITEM_UPDATED_TEXT:
            return row.get("item_updated_text", "")
        if role == _SIDEBAR_ROLE_VISUAL_CHANNEL:
            return row.get("visual_channel", row.get("channel", "other"))
        if role == _SIDEBAR_ROLE_IS_READ_ONLY:
            return bool(row.get("is_read_only", False))
        if role == _SIDEBAR_ROLE_IS_RUNNING:
            return bool(row.get("is_running", False))
        if role == _SIDEBAR_ROLE_IS_CHILD_SESSION:
            return bool(row.get("is_child_session", False))
        if role == _SIDEBAR_ROLE_PARENT_SESSION_KEY:
            return row.get("parent_session_key", "")
        if role == _SIDEBAR_ROLE_ITEM_HAS_UNREAD:
            return bool(row.get("item_has_unread", False))
        if role == _SIDEBAR_ROLE_ITEM_COUNT:
            return int(row.get("item_count", 0) or 0)
        if role == _SIDEBAR_ROLE_GROUP_UNREAD_COUNT:
            return int(row.get("group_unread_count", 0) or 0)
        if role == _SIDEBAR_ROLE_GROUP_HAS_RUNNING:
            return bool(row.get("group_has_running", False))
        if role == _SIDEBAR_ROLE_IS_LAST_IN_GROUP:
            return bool(row.get("is_last_in_group", False))
        if role == _SIDEBAR_ROLE_IS_FIRST_IN_GROUP:
            return bool(row.get("is_first_in_group", False))
        return None

    def roleNames(self) -> dict[int, QByteArray]:
        return dict(self._ROLES)

    def active_row_index(self, key: str) -> int:
        row_id = f"session:{key}"
        for index, row in enumerate(self._rows):
            if str(row.get("row_id", "")) == row_id:
                return index
        return -1

    def sync_rows(self, rows: list[dict[str, Any]]) -> None:
        next_rows = [dict(row) for row in rows]
        next_ids = {str(row.get("row_id", "")) for row in next_rows}
        for remove_index in range(len(self._rows) - 1, -1, -1):
            if str(self._rows[remove_index].get("row_id", "")) in next_ids:
                continue
            self.beginRemoveRows(QModelIndex(), remove_index, remove_index)
            del self._rows[remove_index]
            self.endRemoveRows()
        row_index = 0
        while row_index < len(next_rows):
            next_row = next_rows[row_index]
            next_id = str(next_row.get("row_id", ""))
            if row_index < len(self._rows) and str(self._rows[row_index].get("row_id", "")) == next_id:
                self._update_row(row_index, next_row)
                row_index += 1
                continue
            found_index = -1
            for search_index in range(row_index + 1, len(self._rows)):
                if str(self._rows[search_index].get("row_id", "")) == next_id:
                    found_index = search_index
                    break
            if found_index >= 0:
                self.beginMoveRows(QModelIndex(), found_index, found_index, QModelIndex(), row_index)
                row = self._rows.pop(found_index)
                self._rows.insert(row_index, row)
                self.endMoveRows()
            else:
                self.beginInsertRows(QModelIndex(), row_index, row_index)
                self._rows.insert(row_index, dict(next_row))
                self.endInsertRows()
            self._update_row(row_index, next_row)
            row_index += 1

    def clear_rows(self) -> None:
        if not self._rows:
            return
        self.beginResetModel()
        self._rows = []
        self.endResetModel()

    def _update_row(self, index: int, next_row: dict[str, Any]) -> None:
        current = self._rows[index]
        changed_roles: list[int] = []
        for field, role in _SIDEBAR_FIELD_TO_ROLE.items():
            next_value = next_row.get(field)
            if current.get(field) == next_value:
                continue
            current[field] = next_value
            changed_roles.append(role)
        if not changed_roles:
            return
        model_index = self.index(index)
        self.dataChanged.emit(model_index, model_index, changed_roles)
