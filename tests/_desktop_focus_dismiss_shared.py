# ruff: noqa: E402, N802

from __future__ import annotations

import importlib
import sys

pytest = importlib.import_module("pytest")

QtCore = pytest.importorskip("PySide6.QtCore")
QtGui = pytest.importorskip("PySide6.QtGui")
QtQml = pytest.importorskip("PySide6.QtQml")
QtQuick = pytest.importorskip("PySide6.QtQuick")
QtQuickControls2 = pytest.importorskip("PySide6.QtQuickControls2")
QtTest = pytest.importorskip("PySide6.QtTest")

QEvent = QtCore.QEvent
QCoreApplication = QtCore.QCoreApplication
QEventLoop = QtCore.QEventLoop
QObject = QtCore.QObject
QPoint = QtCore.QPoint
QPointF = QtCore.QPointF
QTimer = QtCore.QTimer
QUrl = QtCore.QUrl
Qt = QtCore.Qt
QGuiApplication = QtGui.QGuiApplication
QFont = QtGui.QFont
QMouseEvent = QtGui.QMouseEvent
QQmlComponent = QtQml.QQmlComponent
QQmlEngine = QtQml.QQmlEngine
QQuickWindow = QtQuick.QQuickWindow
QQuickStyle = QtQuickControls2.QQuickStyle
QTest = QtTest.QTest


@pytest.fixture(scope="session")
def qapp():
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    yield app


def _process(ms: int) -> None:
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def _install_focus_filter(root: QObject, focus_filter_cls):
    focus_filter = focus_filter_cls(root)
    if hasattr(root, "installEventFilter"):
        root.installEventFilter(focus_filter)
    return focus_filter


def _remove_focus_filter(root: QObject, focus_filter) -> None:
    if focus_filter is None:
        return
    if hasattr(root, "removeEventFilter"):
        root.removeEventFilter(focus_filter)


def _wait_until_ready(component: QQmlComponent, timeout_ms: int = 500) -> None:
    remaining = timeout_ms
    while component.status() == QQmlComponent.Loading and remaining > 0:
        _process(25)
        remaining -= 25


def _mouse_release(x: float, y: float) -> QMouseEvent:
    return QMouseEvent(
        QEvent.Type.MouseButtonRelease,
        QPointF(x, y),
        QPointF(x, y),
        QPointF(x, y),
        Qt.LeftButton,
        Qt.LeftButton,
        Qt.NoModifier,
    )


class _MouseMoveRecorder(QObject):
    def __init__(self) -> None:
        super().__init__()
        self.moves = 0

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # pragma: no cover - Qt hook
        if watched is not None and event.type() == QEvent.Type.MouseMove:
            self.moves += 1
        return False


__all__ = [
    "QCoreApplication",
    "QEvent",
    "QEventLoop",
    "QFont",
    "QGuiApplication",
    "QMouseEvent",
    "QObject",
    "QPoint",
    "QPointF",
    "QUrl",
    "QQmlComponent",
    "QQmlEngine",
    "QQuickWindow",
    "QTest",
    "Qt",
    "_MouseMoveRecorder",
    "_install_focus_filter",
    "_mouse_release",
    "_process",
    "_remove_focus_filter",
    "_wait_until_ready",
    "qapp",
]
