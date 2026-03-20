# ruff: noqa: E402, N802, N815, F403, F405, I001
from __future__ import annotations

from tests._chat_view_integration_shared import *

class DummyDiagnosticsService(QObject):
    changed = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._log_file_path = "/tmp/bao-desktop.log"
        self._recent_log_text = "2026-03-08 03:19:15.301 | INFO | boot"
        self._events: list[dict[str, object]] = [
            {
                "code": "provider_error",
                "stage": "chat",
                "message": "provider timeout",
                "source": "provider",
                "timestamp": "2026-03-08T03:19:15",
                "session_key": "desktop:local",
                "level": "error",
            }
        ]
        self._observability_items: list[dict[str, object]] = [
            {"label": "Tool calls", "value": "5"},
            {"label": "Tool errors", "value": "1"},
        ]

    @Property(str, notify=changed)
    def logFilePath(self) -> str:
        return self._log_file_path

    @Property(str, notify=changed)
    def recentLogText(self) -> str:
        return self._recent_log_text

    @Property(list, notify=changed)
    def events(self) -> list[dict[str, object]]:
        return self._events

    @Property(list, notify=changed)
    def observabilityItems(self) -> list[dict[str, object]]:
        return self._observability_items

    @Property(int, notify=changed)
    def eventCount(self) -> int:
        return len(self._events)

    @Slot()
    def refresh(self) -> None:
        self.changed.emit()

    @Slot()
    def openLogDirectory(self) -> None:
        return None

    @Slot(result=str)
    def buildAssistantPrompt(self) -> str:
        return "Diagnostics prompt"

__all__ = [name for name in globals() if name != "__all__" and not (name.startswith("__") and name.endswith("__"))]
