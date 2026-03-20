from __future__ import annotations

from typing import Any

from PySide6.QtCore import (
    QAbstractListModel,
    QByteArray,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    Qt,
)


class CronTasksModel(QAbstractListModel):
    _ROLE_BASE = int(Qt.ItemDataRole.UserRole)
    _ROLE_NAMES = {
        _ROLE_BASE + 1: QByteArray(b"taskId"),
        _ROLE_BASE + 2: QByteArray(b"name"),
        _ROLE_BASE + 3: QByteArray(b"enabled"),
        _ROLE_BASE + 4: QByteArray(b"statusKey"),
        _ROLE_BASE + 5: QByteArray(b"statusLabel"),
        _ROLE_BASE + 6: QByteArray(b"scheduleSummary"),
        _ROLE_BASE + 7: QByteArray(b"nextRunText"),
        _ROLE_BASE + 8: QByteArray(b"lastResultText"),
        _ROLE_BASE + 9: QByteArray(b"lastError"),
        _ROLE_BASE + 10: QByteArray(b"sessionKey"),
        _ROLE_BASE + 11: QByteArray(b"isDraft"),
    }
    _FIELD_MAP = {
        _ROLE_BASE + 1: "id",
        _ROLE_BASE + 2: "name",
        _ROLE_BASE + 3: "enabled",
        _ROLE_BASE + 4: "status_key",
        _ROLE_BASE + 5: "status_label",
        _ROLE_BASE + 6: "schedule_summary",
        _ROLE_BASE + 7: "next_run_text",
        _ROLE_BASE + 8: "last_result_text",
        _ROLE_BASE + 9: "last_error",
        _ROLE_BASE + 10: "session_key",
        _ROLE_BASE + 11: "is_draft",
    }

    def __init__(self, parent: QObject | None = None) -> None:
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
        field = self._FIELD_MAP.get(role)
        if field is None:
            return None
        return self._rows[index.row()].get(field)

    def roleNames(self) -> dict[int, QByteArray]:
        return dict(self._ROLE_NAMES)

    def reset_rows(self, rows: list[dict[str, Any]]) -> None:
        self.beginResetModel()
        self._rows = [dict(row) for row in rows]
        self.endResetModel()

    def sync_rows(self, rows: list[dict[str, Any]]) -> None:
        next_rows = [dict(row) for row in rows]
        next_ids = {str(row.get("id", "")) for row in next_rows}
        for remove_index in range(len(self._rows) - 1, -1, -1):
            if str(self._rows[remove_index].get("id", "")) in next_ids:
                continue
            self.beginRemoveRows(QModelIndex(), remove_index, remove_index)
            del self._rows[remove_index]
            self.endRemoveRows()

        row_index = 0
        while row_index < len(next_rows):
            next_row = next_rows[row_index]
            next_id = str(next_row.get("id", ""))
            if row_index < len(self._rows) and str(self._rows[row_index].get("id", "")) == next_id:
                self._update_row(row_index, next_row)
                row_index += 1
                continue
            found_index = next(
                (
                    search_index
                    for search_index in range(row_index + 1, len(self._rows))
                    if str(self._rows[search_index].get("id", "")) == next_id
                ),
                -1,
            )
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

    def _update_row(self, row_index: int, next_row: dict[str, Any]) -> None:
        current = self._rows[row_index]
        if current == next_row:
            return
        self._rows[row_index] = dict(next_row)
        model_index = self.index(row_index)
        self.dataChanged.emit(model_index, model_index, list(self._FIELD_MAP))
