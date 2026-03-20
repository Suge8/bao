from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from loguru import logger
from PySide6.QtCore import QUrl
from PySide6.QtGui import QImage

from bao.config.paths import get_media_dir
from bao.utils.helpers import safe_filename


class ChatServiceStreamingMixin:
    def _compose_user_display_text(self, text: str, attachment_names: list[str]) -> str:
        if not attachment_names:
            return text
        label = "附件" if self._lang == "zh" else "Attachments"
        attachment_line = f"[{label}] {self._summarize_attachment_names(attachment_names)}"
        return f"{text}\n\n{attachment_line}" if text else attachment_line

    @staticmethod
    def _summarize_attachment_names(names: list[str]) -> str:
        cleaned = [name.strip() for name in names if isinstance(name, str) and name.strip()]
        if not cleaned:
            return ""
        if len(cleaned) <= 3:
            return ", ".join(cleaned)
        preview = ", ".join(cleaned[:3])
        return f"{preview} +{len(cleaned) - 3}"

    @staticmethod
    def _coerce_local_paths(values: Any) -> list[str]:
        raw_items = values if isinstance(values, list) else [values]
        paths: list[str] = []
        seen: set[str] = set()
        for raw in raw_items:
            path = ChatServiceStreamingMixin._coerce_local_path(raw)
            if not path or path in seen:
                continue
            seen.add(path)
            paths.append(path)
        return paths

    @staticmethod
    def _coerce_local_path(value: Any) -> str | None:
        to_local_file = getattr(value, "toLocalFile", None)
        if callable(to_local_file):
            local = to_local_file()
            return local if isinstance(local, str) and local else None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        if raw.startswith("file://"):
            local = QUrl(raw).toLocalFile()
            return local or None
        return raw

    @staticmethod
    def _save_clipboard_image(image: QImage) -> str | None:
        media_dir = get_media_dir("desktop")
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = safe_filename(f"desktop-paste-{timestamp}-{uuid.uuid4().hex[:8]}.png")
        target = media_dir / filename
        try:
            saved = image.save(str(target))
        except Exception as exc:
            logger.warning("Failed to save pasted clipboard image: {}", exc)
            return None
        return str(target) if saved else None

    def _handle_progress_update(self, row: int, content: str) -> None:
        should_render_in_ui = self._should_render_active_stream()
        if row == -2:
            self._pending_split = True
            return
        if row == -1 and self._pending_split:
            self._split_progress_row(should_render_in_ui)
        if row == -1 and should_render_in_ui and self._active_streaming_row < 0:
            self._restore_active_streaming_row(emit_append_signal=True)
        target = self._active_streaming_row if row == -1 else row
        if target >= 0 and should_render_in_ui:
            self._model.update_content(target, content)
            self.incrementalContent.emit(target)
        self._active_has_content = bool(content)

    def _split_progress_row(self, should_render_in_ui: bool) -> None:
        if self._active_has_content:
            current_row = self._active_streaming_row
            if current_row >= 0 and should_render_in_ui:
                self._model.set_status(current_row, "done")
            self._active_streaming_row = (
                self._append_typing_row() if should_render_in_ui else -1
            )
            self._active_has_content = False
        self._pending_split = False

    def _restore_active_streaming_row(self, *, emit_append_signal: bool) -> int:
        if not self._should_render_active_stream():
            return -1
        last_row = self._model.rowCount() - 1
        last_message = self._model.message_at(last_row)
        if last_message is not None and last_message.get("role") == "assistant":
            self._active_streaming_row = last_row
            self._active_has_content = bool(last_message.get("content"))
            return last_row
        new_row = (
            self._append_typing_row()
            if emit_append_signal
            else self._model.append_assistant("", status="typing")
        )
        self._active_streaming_row = new_row
        self._active_has_content = False
        return new_row

    def _rebind_active_streaming_row_after_history(self) -> int:
        if not self._should_render_active_stream():
            self._active_streaming_row = -1
            self._active_has_content = False
            return -1
        last_row = self._model.rowCount() - 1
        last_message = self._model.message_at(last_row)
        if last_message is None or last_message.get("role") != "assistant":
            return self._append_rebound_typing_row()
        if last_message.get("_source") == "assistant-progress":
            return self._append_rebound_typing_row()
        self._active_streaming_row = last_row
        self._active_has_content = bool(last_message.get("content"))
        return last_row

    def _append_rebound_typing_row(self) -> int:
        new_row = self._append_typing_row()
        self._active_streaming_row = new_row
        self._active_has_content = False
        return new_row

    def _append_typing_row(self) -> int:
        row = self._model.append_assistant("", status="typing")
        self.appendAtBottom.emit(row)
        return row

    def _handle_tool_hint_update(self, hint: str) -> None:
        should_render_in_ui = self._should_render_active_stream()
        if self._active_streaming_row < 0 and should_render_in_ui:
            self._restore_active_streaming_row(emit_append_signal=True)
        if self._active_streaming_row < 0:
            return
        if self._active_has_content:
            if not should_render_in_ui:
                self._active_streaming_row = -1
                self._active_has_content = False
                return
            self._model.set_status(self._active_streaming_row, "done")
            self._active_streaming_row = self._append_typing_row()
        clean_hint = hint.strip()
        if should_render_in_ui and clean_hint:
            self._model.update_content(self._active_streaming_row, clean_hint)
            self.incrementalContent.emit(self._active_streaming_row)
            self._model.set_status(self._active_streaming_row, "done")
            self._active_streaming_row = self._append_typing_row()
            self._active_has_content = False
        else:
            self._active_streaming_row = -1
            self._active_has_content = False
        self._pending_split = False

    def _tool_hints_enabled(self) -> bool:
        data = self._config_data or {}
        agents = data.get("agents") if isinstance(data, dict) else None
        defaults = agents.get("defaults") if isinstance(agents, dict) else None
        if not isinstance(defaults, dict):
            return True
        value = defaults.get("sendToolHints", defaults.get("send_tool_hints", True))
        return value if isinstance(value, bool) else True

    def _should_render_active_stream(self) -> bool:
        return self._active_streaming_session_key in (None, self._committed_session_key)
