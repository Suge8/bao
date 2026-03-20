from __future__ import annotations

from pathlib import Path
from typing import Callable


def report_invalid_qml(qml_url: object, report_startup_failure: Callable[..., None]) -> int | None:
    from PySide6.QtCore import QUrl

    if not isinstance(qml_url, QUrl) or not qml_url.isValid():
        report_startup_failure(
            "QML load failed: desktop_qml.rcc is required in frozen builds",
            code="qml_resource_missing",
        )
        return 1
    if qml_url.isLocalFile() and not Path(qml_url.toLocalFile()).exists():
        report_startup_failure(
            f"QML load failed: file not found: {qml_url.toLocalFile()}",
            code="qml_missing",
            details={"qml_path": qml_url.toString()},
        )
        return 1
    return None
