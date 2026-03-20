from __future__ import annotations

from typing import Any

from PySide6.QtCore import QAbstractListModel, QByteArray, QModelIndex, QPersistentModelIndex, Qt

from app.backend.session_projection import session_sort_value

_ROLE_BASE = int(Qt.ItemDataRole.UserRole)
_ROLE_KEY = _ROLE_BASE + 1
_ROLE_TITLE = _ROLE_BASE + 2
_ROLE_IS_ACTIVE = _ROLE_BASE + 3
_ROLE_UPDATED_AT = _ROLE_BASE + 4
_ROLE_CHANNEL = _ROLE_BASE + 5
_ROLE_HAS_UNREAD = _ROLE_BASE + 6
_ROLE_UPDATED_LABEL = _ROLE_BASE + 7
_ROLE_MESSAGE_COUNT = _ROLE_BASE + 8
_ROLE_HAS_MESSAGES = _ROLE_BASE + 9
_ROLE_SESSION_KIND = _ROLE_BASE + 10
_ROLE_IS_READ_ONLY = _ROLE_BASE + 11
_ROLE_PARENT_SESSION_KEY = _ROLE_BASE + 12
_ROLE_PARENT_TITLE = _ROLE_BASE + 13
_ROLE_CHILD_STATUS = _ROLE_BASE + 14
_ROLE_IS_RUNNING = _ROLE_BASE + 15

_SESSION_FIELD_TO_ROLE = {
    "key": _ROLE_KEY,
    "title": _ROLE_TITLE,
    "updated_at": _ROLE_UPDATED_AT,
    "channel": _ROLE_CHANNEL,
    "has_unread": _ROLE_HAS_UNREAD,
    "updated_label": _ROLE_UPDATED_LABEL,
    "message_count": _ROLE_MESSAGE_COUNT,
    "has_messages": _ROLE_HAS_MESSAGES,
    "session_kind": _ROLE_SESSION_KIND,
    "is_read_only": _ROLE_IS_READ_ONLY,
    "parent_session_key": _ROLE_PARENT_SESSION_KEY,
    "parent_title": _ROLE_PARENT_TITLE,
    "child_status": _ROLE_CHILD_STATUS,
    "is_running": _ROLE_IS_RUNNING,
}


class SessionListModel(QAbstractListModel):
    _ROLES = {
        _ROLE_KEY: QByteArray(b"key"),
        _ROLE_TITLE: QByteArray(b"title"),
        _ROLE_IS_ACTIVE: QByteArray(b"isActive"),
        _ROLE_UPDATED_AT: QByteArray(b"updatedAt"),
        _ROLE_CHANNEL: QByteArray(b"channel"),
        _ROLE_HAS_UNREAD: QByteArray(b"hasUnread"),
        _ROLE_UPDATED_LABEL: QByteArray(b"updatedLabel"),
        _ROLE_MESSAGE_COUNT: QByteArray(b"messageCount"),
        _ROLE_HAS_MESSAGES: QByteArray(b"hasMessages"),
        _ROLE_SESSION_KIND: QByteArray(b"sessionKind"),
        _ROLE_IS_READ_ONLY: QByteArray(b"isReadOnly"),
        _ROLE_PARENT_SESSION_KEY: QByteArray(b"parentSessionKey"),
        _ROLE_PARENT_TITLE: QByteArray(b"parentTitle"),
        _ROLE_CHILD_STATUS: QByteArray(b"childStatus"),
        _ROLE_IS_RUNNING: QByteArray(b"isRunning"),
    }

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent)
        self._sessions: list[dict[str, Any]] = []
        self._active_key = ""

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:  # noqa: B008
        if parent.isValid():
            return 0
        return len(self._sessions)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = int(Qt.ItemDataRole.DisplayRole),
    ) -> Any:
        if not index.isValid() or not (0 <= index.row() < len(self._sessions)):
            return None
        session = self._sessions[index.row()]
        if role == _ROLE_KEY:
            return session.get("key", "")
        if role == _ROLE_TITLE:
            title = session.get("title", "")
            return title if isinstance(title, str) and title else session.get("key", "")
        if role == _ROLE_IS_ACTIVE:
            return session.get("key", "") == self._active_key
        if role == _ROLE_UPDATED_AT:
            return session.get("updated_at", 0)
        if role == _ROLE_CHANNEL:
            return session.get("channel", "other")
        if role == _ROLE_HAS_UNREAD:
            return bool(session.get("has_unread", False))
        if role == _ROLE_UPDATED_LABEL:
            return session.get("updated_label", "")
        if role == _ROLE_MESSAGE_COUNT:
            return session.get("message_count")
        if role == _ROLE_HAS_MESSAGES:
            return session.get("has_messages")
        if role == _ROLE_SESSION_KIND:
            return session.get("session_kind", "regular")
        if role == _ROLE_IS_READ_ONLY:
            return bool(session.get("is_read_only", False))
        if role == _ROLE_PARENT_SESSION_KEY:
            return session.get("parent_session_key", "")
        if role == _ROLE_PARENT_TITLE:
            return session.get("parent_title", "")
        if role == _ROLE_CHILD_STATUS:
            return session.get("child_status", "")
        if role == _ROLE_IS_RUNNING:
            return bool(session.get("is_running", False))
        return None

    def roleNames(self) -> dict[int, QByteArray]:
        return dict(self._ROLES)

    def reset_sessions(self, sessions: list[dict[str, Any]], active_key: str) -> None:
        self.beginResetModel()
        self._sessions = [dict(session) for session in sessions]
        self._active_key = active_key
        self.endResetModel()

    def sync_sessions(self, sessions: list[dict[str, Any]], active_key: str) -> None:
        next_sessions = [dict(session) for session in sessions]
        next_keys = {str(session.get("key", "")) for session in next_sessions}
        for remove_index in range(len(self._sessions) - 1, -1, -1):
            if str(self._sessions[remove_index].get("key", "")) in next_keys:
                continue
            self.beginRemoveRows(QModelIndex(), remove_index, remove_index)
            del self._sessions[remove_index]
            self.endRemoveRows()
        row_index = 0
        while row_index < len(next_sessions):
            next_session = next_sessions[row_index]
            next_key = str(next_session.get("key", ""))
            if row_index < len(self._sessions) and str(self._sessions[row_index].get("key", "")) == next_key:
                self._update_session_row(row_index, next_session)
                row_index += 1
                continue
            found_index = -1
            for search_index in range(row_index + 1, len(self._sessions)):
                if str(self._sessions[search_index].get("key", "")) == next_key:
                    found_index = search_index
                    break
            if found_index >= 0:
                self.beginMoveRows(QModelIndex(), found_index, found_index, QModelIndex(), row_index)
                session = self._sessions.pop(found_index)
                self._sessions.insert(row_index, session)
                self.endMoveRows()
            else:
                self.beginInsertRows(QModelIndex(), row_index, row_index)
                self._sessions.insert(row_index, dict(next_session))
                self.endInsertRows()
            self._update_session_row(row_index, next_session)
            row_index += 1
        self._apply_active_key(active_key)

    def _update_session_row(self, index: int, next_session: dict[str, Any]) -> None:
        current = self._sessions[index]
        changed_roles: list[int] = []
        for field, role in _SESSION_FIELD_TO_ROLE.items():
            next_value = next_session.get(field)
            if current.get(field) == next_value:
                continue
            current[field] = next_value
            changed_roles.append(role)
        for field in ("self_running", "needs_tail_backfill"):
            current[field] = next_session.get(field)
        if not changed_roles:
            return
        model_index = self.index(index)
        self.dataChanged.emit(model_index, model_index, changed_roles)

    def _find_session_index(self, key: str) -> int:
        for index, session in enumerate(self._sessions):
            if str(session.get("key", "")) == key:
                return index
        return -1

    def _target_index_for_session(self, next_session: dict[str, Any], *, skip_index: int = -1) -> int:
        next_sort = session_sort_value(next_session)
        target_index = 0
        for index, session in enumerate(self._sessions):
            if index == skip_index:
                continue
            if session_sort_value(session) >= next_sort:
                target_index += 1
                continue
            break
        return target_index

    def upsert_sessions(self, sessions: list[dict[str, Any]], active_key: str) -> None:
        for next_session in sessions:
            next_key = str(next_session.get("key", ""))
            if not next_key:
                continue
            existing_index = self._find_session_index(next_key)
            if existing_index < 0:
                target_index = self._target_index_for_session(next_session)
                self.beginInsertRows(QModelIndex(), target_index, target_index)
                self._sessions.insert(target_index, dict(next_session))
                self.endInsertRows()
                self._update_session_row(target_index, next_session)
                continue
            self._update_session_row(existing_index, next_session)
            target_index = self._target_index_for_session(next_session, skip_index=existing_index)
            if target_index == existing_index:
                continue
            destination = target_index if target_index < existing_index else target_index + 1
            self.beginMoveRows(QModelIndex(), existing_index, existing_index, QModelIndex(), destination)
            session = self._sessions.pop(existing_index)
            insert_index = target_index if target_index < existing_index else target_index
            self._sessions.insert(insert_index, session)
            self.endMoveRows()
        self._apply_active_key(active_key)

    def _apply_active_key(self, key: str) -> None:
        old_key = self._active_key
        self._active_key = key
        affected_keys = {old_key, key}
        for index, session in enumerate(self._sessions):
            session_key = str(session.get("key", ""))
            changed_roles: list[int] = []
            if session_key == key and session.get("has_unread"):
                session["has_unread"] = False
                changed_roles.append(_ROLE_HAS_UNREAD)
            if session_key in affected_keys:
                changed_roles.append(_ROLE_IS_ACTIVE)
            if not changed_roles:
                continue
            model_index = self.index(index)
            self.dataChanged.emit(model_index, model_index, changed_roles)

    def set_active(self, key: str) -> None:
        self._apply_active_key(key)
