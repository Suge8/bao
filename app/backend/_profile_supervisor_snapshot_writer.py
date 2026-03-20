from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject

from app.backend._profile_supervisor_storage import _write_snapshot
from app.backend.asyncio_runner import AsyncioRunner


class SnapshotWriter(QObject):
    def __init__(self, runner: AsyncioRunner, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._runner = runner

    def write(self, path: Path, payload: dict[str, Any]) -> None:
        future = self._submit_safe(self._runner.run_bg_io(_write_snapshot, path, dict(payload)))
        if future is not None:
            future.add_done_callback(lambda _future: None)

    def _submit_safe(self, coro: Any) -> Any:
        try:
            return self._runner.submit(coro)
        except RuntimeError:
            close = getattr(coro, "close", None)
            if callable(close):
                close()
            return None
