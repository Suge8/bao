# ruff: noqa: E402, N802, N815, F401
from __future__ import annotations

import importlib
from pathlib import Path
from typing import cast

from tests.desktop_ui_testkit import assert_item_within_window as _assert_item_within_window
from tests.desktop_ui_testkit import center_point as _center_point
from tests.desktop_ui_testkit import process_events as _process
from tests.desktop_ui_testkit import qapp as _shared_qapp
from tests.desktop_ui_testkit import scroll_item_into_view as _scroll_item_into_view
from tests.desktop_ui_testkit import wait_until as _wait_until

pytest = importlib.import_module("pytest")

QtCore = pytest.importorskip("PySide6.QtCore")
QtGui = pytest.importorskip("PySide6.QtGui")
QtQml = pytest.importorskip("PySide6.QtQml")
QtQuick = pytest.importorskip("PySide6.QtQuick")
QtTest = pytest.importorskip("PySide6.QtTest")

QAbstractListModel = QtCore.QAbstractListModel
QByteArray = QtCore.QByteArray
QMetaObject = QtCore.QMetaObject
QModelIndex = QtCore.QModelIndex
QObject = QtCore.QObject
QPoint = QtCore.QPoint
QPointF = QtCore.QPointF
Property = QtCore.Property
QQuickItem = QtQuick.QQuickItem
QUrl = QtCore.QUrl
Qt = QtCore.Qt
Signal = QtCore.Signal
Slot = QtCore.Slot
QQmlApplicationEngine = QtQml.QQmlApplicationEngine
QTest = QtTest.QTest

from app.backend.cron import CronTasksModel
from app.main import WindowFocusDismissFilter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAIN_QML_PATH = PROJECT_ROOT / "app" / "qml" / "Main.qml"
qapp = _shared_qapp



__all__ = [name for name in globals() if name != "__all__" and not (name.startswith("__") and name.endswith("__"))]
