from __future__ import annotations

from typing import Any

from PySide6.QtCore import QModelIndex


class ChatMessageLoadMixin:
    def load_prepared(
        self, prepared_messages: list[dict[str, Any]], *, preserve_transient_tail: bool = False
    ) -> None:
        next_messages = self._messages_for_prepared_load(
            prepared_messages, preserve_transient_tail=preserve_transient_tail
        )
        if self._is_render_equivalent(next_messages):
            return
        if self._can_update_without_reset(next_messages):
            self._update_without_reset(next_messages)
            return
        if self._can_reconcile_transient_tail_without_reset(next_messages):
            self._reconcile_transient_tail_without_reset(next_messages)
            return
        if self._can_append_without_reset(next_messages):
            self._append_without_reset(next_messages)
            return
        if self._can_prepend_without_reset(next_messages):
            self._prepend_without_reset(next_messages)
            return
        self._reset_messages(next_messages)

    def _append_without_reset(self, next_messages: list[dict[str, Any]]) -> None:
        append_from = len(self._messages)
        self.beginInsertRows(QModelIndex(), append_from, len(next_messages) - 1)
        self._messages = next_messages
        self._next_id = len(next_messages) + 1
        self.endInsertRows()

    def _prepend_without_reset(self, next_messages: list[dict[str, Any]]) -> None:
        prepend_count = len(next_messages) - len(self._messages)
        self.beginInsertRows(QModelIndex(), 0, prepend_count - 1)
        self._messages = next_messages
        self._next_id = len(next_messages) + 1
        self.endInsertRows()

    def _reset_messages(self, next_messages: list[dict[str, Any]]) -> None:
        self.beginResetModel()
        self._messages = next_messages
        self._next_id = len(next_messages) + 1
        self.endResetModel()

    def _is_render_equivalent(self, prepared_messages: list[dict[str, Any]]) -> bool:
        if len(prepared_messages) != len(self._messages):
            return False
        return self._render_sequences_match(self._messages, prepared_messages)

    def _can_prepend_without_reset(self, prepared_messages: list[dict[str, Any]]) -> bool:
        if not self._messages or len(prepared_messages) <= len(self._messages):
            return False
        tail = prepared_messages[-len(self._messages) :]
        return self._render_sequences_match(self._messages, tail)

    def _can_update_without_reset(self, prepared_messages: list[dict[str, Any]]) -> bool:
        if len(prepared_messages) != len(self._messages):
            return False
        for current, prepared in zip(self._messages, prepared_messages):
            current_role = current.get("role")
            if current_role != prepared.get("role"):
                return False
            if current_role != "system":
                continue
            if self._system_message_style_changed(current, prepared):
                return False
        return True

    @staticmethod
    def _system_message_style_changed(
        current: dict[str, Any], prepared: dict[str, Any]
    ) -> bool:
        current_pending = bool(current.get("entrancepending"))
        prepared_pending = bool(prepared.get("entrancepending"))
        return (
            not current_pending
            and not prepared_pending
            and current.get("entrancestyle", "none") != prepared.get("entrancestyle", "none")
        )

    def _update_without_reset(self, prepared_messages: list[dict[str, Any]]) -> None:
        for row, prepared in enumerate(prepared_messages):
            self._replace_row_without_reset(row, prepared)

    def _can_append_without_reset(self, prepared_messages: list[dict[str, Any]]) -> bool:
        if not self._messages or len(prepared_messages) <= len(self._messages):
            return False
        head = prepared_messages[: len(self._messages)]
        return self._render_sequences_match(self._messages, head)

    def _can_reconcile_transient_tail_without_reset(
        self, prepared_messages: list[dict[str, Any]]
    ) -> bool:
        assistant_tail = self._trailing_assistant_block()
        if not assistant_tail:
            return False
        stable_prefix_count = len(self._messages) - len(assistant_tail)
        if len(prepared_messages) < stable_prefix_count:
            return False
        stable_prefix = self._messages[:stable_prefix_count]
        if not self._render_sequences_match(
            stable_prefix,
            prepared_messages[:stable_prefix_count],
            ignore_user_status=True,
        ):
            return False
        next_tail = self._split_reconciled_tail(prepared_messages[stable_prefix_count:])[1]
        return all(msg.get("role") == "assistant" for msg in next_tail)

    @staticmethod
    def _split_reconciled_tail(
        remainder: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        split = 0
        while split < len(remainder) and remainder[split].get("role") == "system":
            split += 1
        return remainder[:split], remainder[split:]

    def _reconcile_transient_tail_without_reset(
        self, prepared_messages: list[dict[str, Any]]
    ) -> None:
        assistant_tail = self._trailing_assistant_block()
        stable_prefix_count = len(self._messages) - len(assistant_tail)
        inserted_rows, next_tail = self._split_reconciled_tail(prepared_messages[stable_prefix_count:])
        self._insert_reconciled_rows(stable_prefix_count, inserted_rows)
        self._reconcile_assistant_tail(stable_prefix_count + len(inserted_rows), assistant_tail, next_tail)
        self._next_id = len(prepared_messages) + 1

    def _insert_reconciled_rows(
        self, stable_prefix_count: int, inserted_rows: list[dict[str, Any]]
    ) -> None:
        if not inserted_rows:
            return
        self.beginInsertRows(
            QModelIndex(), stable_prefix_count, stable_prefix_count + len(inserted_rows) - 1
        )
        self._messages[stable_prefix_count:stable_prefix_count] = [dict(msg) for msg in inserted_rows]
        self.endInsertRows()

    def _reconcile_assistant_tail(
        self,
        tail_start: int,
        assistant_tail: list[dict[str, Any]],
        next_tail: list[dict[str, Any]],
    ) -> None:
        common_tail_count = min(len(assistant_tail), len(next_tail))
        for offset in range(common_tail_count):
            self._replace_row_without_reset(tail_start + offset, next_tail[offset])
        if len(next_tail) < len(assistant_tail):
            self._remove_tail_rows(tail_start + len(next_tail), len(assistant_tail) - len(next_tail))
            return
        if len(next_tail) > len(assistant_tail):
            self._insert_tail_rows(tail_start + len(assistant_tail), next_tail[len(assistant_tail) :])

    def _remove_tail_rows(self, remove_start: int, remove_count: int) -> None:
        remove_end = remove_start + remove_count - 1
        self.beginRemoveRows(QModelIndex(), remove_start, remove_end)
        del self._messages[remove_start : remove_end + 1]
        self.endRemoveRows()

    def _insert_tail_rows(self, insert_start: int, insert_rows: list[dict[str, Any]]) -> None:
        self.beginInsertRows(QModelIndex(), insert_start, insert_start + len(insert_rows) - 1)
        self._messages[insert_start:insert_start] = [dict(msg) for msg in insert_rows]
        self.endInsertRows()

    def _replace_row_without_reset(self, row: int, prepared: dict[str, Any]) -> None:
        current = self._messages[row]
        if self._render_tuple(current) == self._render_tuple(prepared):
            return
        self._messages[row] = {
            **current,
            **prepared,
            "id": current.get("id", prepared.get("id", row + 1)),
            "createdat": current.get("createdat", prepared.get("createdat", 0)),
        }
        idx = self.index(row)
        self.dataChanged.emit(idx, idx, self._UPDATE_ROLES)

    def _messages_for_prepared_load(
        self, prepared_messages: list[dict[str, Any]], *, preserve_transient_tail: bool
    ) -> list[dict[str, Any]]:
        if not preserve_transient_tail:
            return self._apply_divider_texts(prepared_messages)
        return self._apply_divider_texts(self._merge_transient_assistant_tail(prepared_messages))

    def _merge_transient_assistant_tail(
        self, prepared_messages: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        transient_tail = self._trailing_transient_assistant_tail()
        if not transient_tail:
            return prepared_messages
        stable_prefix_count = len(self._messages) - len(transient_tail)
        if len(prepared_messages) < stable_prefix_count:
            return prepared_messages
        stable_prefix = self._messages[:stable_prefix_count]
        prepared_prefix = prepared_messages[:stable_prefix_count]
        if not self._render_sequences_match(
            stable_prefix,
            prepared_prefix,
            ignore_user_status=True,
        ):
            return prepared_messages
        remaining_tail = self._remaining_transient_tail(
            prepared_messages[stable_prefix_count:], transient_tail
        )
        if remaining_tail is None:
            return prepared_messages
        return prepared_messages + remaining_tail

    def _trailing_transient_assistant_tail(self) -> list[dict[str, Any]]:
        assistant_tail = self._trailing_assistant_block()
        if not assistant_tail or assistant_tail[-1].get("status") != "typing":
            return []
        return assistant_tail

    def _trailing_assistant_block(self) -> list[dict[str, Any]]:
        if not self._messages or self._messages[-1].get("role") != "assistant":
            return []
        tail_start = len(self._messages) - 1
        while tail_start > 0 and self._messages[tail_start - 1].get("role") == "assistant":
            tail_start -= 1
        return self._messages[tail_start:]

    def _remaining_transient_tail(
        self, prepared_remainder: list[dict[str, Any]], transient_tail: list[dict[str, Any]]
    ) -> list[dict[str, Any]] | None:
        for inserted_count in range(len(prepared_remainder) + 1):
            inserted_rows = prepared_remainder[:inserted_count]
            tail_prefix = prepared_remainder[inserted_count:]
            if any(msg.get("role") != "system" for msg in inserted_rows):
                continue
            if len(tail_prefix) > len(transient_tail):
                continue
            if not self._render_sequences_match(
                transient_tail[: len(tail_prefix)],
                tail_prefix,
                ignore_user_status=True,
            ):
                continue
            return [dict(msg) for msg in transient_tail[len(tail_prefix) :]]
        return None

    @classmethod
    def _render_sequences_match(
        cls,
        left_messages: list[dict[str, Any]],
        right_messages: list[dict[str, Any]],
        *,
        ignore_user_status: bool = False,
    ) -> bool:
        if len(left_messages) != len(right_messages):
            return False
        for left, right in zip(left_messages, right_messages):
            if cls._render_tuple(left, ignore_user_status=ignore_user_status) != cls._render_tuple(
                right, ignore_user_status=ignore_user_status
            ):
                return False
        return True

    @staticmethod
    def _render_tuple(
        message: dict[str, Any], *, ignore_user_status: bool = False
    ) -> tuple[str, str, str, str, str, str, str, str]:
        role = message.get("role", "")
        content = message.get("content", "")
        fmt = message.get("format", "")
        status = message.get("status", "")
        entrance_style = message.get("entrancestyle", "none")
        divider_text = message.get("dividertext", "")
        attachments = message.get("attachments", [])
        references = message.get("references", {})
        role_s = role if isinstance(role, str) else str(role)
        fmt_s = fmt if isinstance(fmt, str) else str(fmt)
        status_s = status if isinstance(status, str) else str(status)
        if ignore_user_status and role_s == "user":
            status_s = ""
        entrance_s = ""
        if role_s == "system":
            entrance_s = entrance_style if isinstance(entrance_style, str) else str(entrance_style)
        return (
            role_s,
            content if isinstance(content, str) else str(content),
            fmt_s,
            status_s,
            entrance_s,
            divider_text if isinstance(divider_text, str) else str(divider_text),
            repr(attachments),
            repr(references),
        )

    def load_history(self, messages: list[dict[str, Any]]) -> None:
        self.load_prepared(self.prepare_history(messages))
