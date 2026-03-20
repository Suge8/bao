"""ChatMessageModel — QAbstractListModel for chat messages.

Roles: id, role, content, format, status, createdAt
Status values: "pending" | "typing" | "done" | "error"
Format values: "markdown" | "plain"
"""

from __future__ import annotations

import time
from datetime import datetime as _datetime
from enum import IntEnum
from typing import Any

from PySide6.QtCore import (
    QAbstractListModel,
    QByteArray,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
)

from app.backend._chat_message_load import ChatMessageLoadMixin
from app.backend._chat_message_prepare import ChatMessagePrepareMixin, MessageAppendOptions

datetime = _datetime


class _Role(IntEnum):
    _BASE = int(Qt.ItemDataRole.UserRole)
    Id = _BASE + 1
    Role = _BASE + 2
    Content = _BASE + 3
    Format = _BASE + 4
    Status = _BASE + 5
    CreatedAt = _BASE + 6
    EntranceStyle = _BASE + 7
    EntrancePending = _BASE + 8
    DividerText = _BASE + 9
    Attachments = _BASE + 10
    References = _BASE + 11


class ChatMessageModel(ChatMessageLoadMixin, ChatMessagePrepareMixin, QAbstractListModel):
    """Incremental list model for chat messages.

    Prefers incremental updates via beginInsertRows / dataChanged.
    Falls back to beginResetModel when history cannot be merged safely.
    """

    _ROLE_NAMES = {
        _Role.Id: b"id",
        _Role.Role: b"role",
        _Role.Content: b"content",
        _Role.Format: b"format",
        _Role.Status: b"status",
        _Role.CreatedAt: b"createdAt",
        _Role.EntranceStyle: b"entranceStyle",
        _Role.EntrancePending: b"entrancePending",
        _Role.DividerText: b"dividerText",
        _Role.Attachments: b"attachments",
        _Role.References: b"references",
    }
    _UPDATE_ROLES = [int(role) for role in _ROLE_NAMES]

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent)
        self._messages: list[dict[str, Any]] = []
        self._next_id = 1

    # ------------------------------------------------------------------
    # QAbstractListModel interface
    # ------------------------------------------------------------------

    def rowCount(
        self,
        parent: QModelIndex | QPersistentModelIndex = QModelIndex(),  # noqa: B008
    ) -> int:
        return len(self._messages)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = int(Qt.ItemDataRole.DisplayRole),
    ) -> Any:
        if not index.isValid() or not (0 <= index.row() < len(self._messages)):
            return None
        msg = self._messages[index.row()]
        try:
            r = _Role(role)
        except ValueError:
            return None
        return msg.get(r.name.lower())

    def roleNames(self) -> dict[int, QByteArray]:
        return {int(k): QByteArray(v) for k, v in self._ROLE_NAMES.items()}

    # ------------------------------------------------------------------
    # Mutation API
    # ------------------------------------------------------------------

    def append_user(self, text: str, *, status: str = "pending", client_token: str = "") -> int:
        """Append a user message; return its row index."""
        return self._append(
            {
                "role": "user",
                "content": text,
                "format": "plain",
                "status": self._normalize_status(status, default="pending"),
                "entranceStyle": "userSent",
                "entrancePending": True,
                "clientToken": client_token,
            }
        )

    def append_assistant(self, text: str = "", *args: Any, **kwargs: Any) -> int:
        """Append an assistant message placeholder; return its row index."""
        options = self._resolve_append_options(
            args,
            kwargs,
            MessageAppendOptions(status="typing", entrance_style="assistantReceived"),
        )
        return self._append(
            {
                "role": "assistant",
                "content": text,
                "format": "markdown",
                "status": options.status,
                "entranceStyle": options.entrance_style,
                "entrancePending": options.entrance_pending,
            }
        )

    def append_system(self, text: str, *args: Any, **kwargs: Any) -> int:
        """Append a system message (hub status, errors, etc.); return row index."""
        options = self._resolve_append_options(
            args,
            kwargs,
            MessageAppendOptions(status="done", entrance_style="system"),
        )
        return self._append(
            {
                "role": "system",
                "content": text,
                "format": "plain",
                "status": options.status,
                "entranceStyle": options.entrance_style,
                "entrancePending": options.entrance_pending,
            }
        )

    def consumeEntrance(self, row: int) -> None:
        if not (0 <= row < len(self._messages)):
            return
        msg = self._messages[row]
        if msg.get("entrancepending") is False:
            return
        msg["entrancepending"] = False
        idx = self.index(row)
        self.dataChanged.emit(idx, idx, [int(_Role.EntrancePending)])

    def consumeEntranceById(self, message_id: int) -> None:
        row = self._row_by_message_id(message_id)
        if row < 0:
            return
        self.consumeEntrance(row)

    def update_content(self, row: int, new_text: str) -> None:
        """Replace the content of an existing row (incremental typewriter update)."""
        if not (0 <= row < len(self._messages)):
            return
        self._messages[row]["content"] = new_text
        idx = self.index(row)
        self.dataChanged.emit(idx, idx, [int(_Role.Content)])

    def set_status(self, row: int, status: str) -> None:
        """Update the status field of an existing row."""
        if not (0 <= row < len(self._messages)):
            return
        self._messages[row]["status"] = status
        idx = self.index(row)
        self.dataChanged.emit(idx, idx, [int(_Role.Status)])

    def set_format(self, row: int, fmt: str) -> None:
        if not (0 <= row < len(self._messages)):
            return
        self._messages[row]["format"] = fmt
        idx = self.index(row)
        self.dataChanged.emit(idx, idx, [int(_Role.Format)])

    def clear(self) -> None:
        """Remove all messages without emitting reset (uses removeRows)."""
        if not self._messages:
            return
        self.beginRemoveRows(QModelIndex(), 0, len(self._messages) - 1)
        self._messages.clear()
        self.endRemoveRows()

    def _append(self, fields: dict[str, Any]) -> int:
        row = len(self._messages)
        msg = {
            "id": self._next_id,
            "createdat": int(time.time() * 1000),
            **{k.lower(): v for k, v in fields.items()},
        }
        msg.setdefault("entrancestyle", "none")
        msg.setdefault("entrancepending", False)
        previous_created_at = 0
        if self._messages:
            previous_created_at = self._normalize_created_at(self._messages[-1].get("createdat", 0))
        msg["dividertext"] = self._divider_text_for(
            self._normalize_created_at(msg.get("createdat", 0)),
            previous_created_at,
        )
        self._next_id += 1
        self.beginInsertRows(QModelIndex(), row, row)
        self._messages.append(msg)
        self.endInsertRows()
        return row

    def _row_by_message_id(self, message_id: int) -> int:
        for i, msg in enumerate(self._messages):
            if msg.get("id") == message_id:
                return i
        return -1

    def remove_row(self, row: int) -> None:
        if not (0 <= row < len(self._messages)):
            return
        self.beginRemoveRows(QModelIndex(), row, row)
        del self._messages[row]
        self.endRemoveRows()

    def message_at(self, row: int) -> dict[str, Any] | None:
        if not (0 <= row < len(self._messages)):
            return None
        return self._messages[row]
