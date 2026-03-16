from __future__ import annotations

import os

os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")

try:
    from PySide6.QtQuickControls2 import QQuickStyle

    QQuickStyle.setStyle("Basic")
except ImportError:
    pass
