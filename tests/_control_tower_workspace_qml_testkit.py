# ruff: noqa: E402
from __future__ import annotations

import importlib
import sys
from pathlib import Path

pytest = importlib.import_module("pytest")
from tests._control_tower_workspace_qml_fragments import (
    attention_lane_block,
    automation_lane_block,
    completed_lane_block,
    supervisor_actions_block,
    supervisor_overview_block,
    supervisor_profiles_block,
    working_lane_block,
    wrapper_footer,
    wrapper_header,
)
from tests._desktop_ui_testkit_base import QQuickStyle, apply_test_app_font

QtCore = pytest.importorskip("PySide6.QtCore")
QtGui = pytest.importorskip("PySide6.QtGui")
QtQml = pytest.importorskip("PySide6.QtQml")
QtQuick = pytest.importorskip("PySide6.QtQuick")
QtTest = pytest.importorskip("PySide6.QtTest")

QEventLoop = QtCore.QEventLoop
QPoint = QtCore.QPoint
QPointF = QtCore.QPointF
Qt = QtCore.Qt
QTimer = QtCore.QTimer
QUrl = QtCore.QUrl
QGuiApplication = QtGui.QGuiApplication
QQmlComponent = QtQml.QQmlComponent
QQmlEngine = QtQml.QQmlEngine
QQuickItem = QtQuick.QQuickItem
QQuickView = QtQuick.QQuickView
QTest = QtTest.QTest


@pytest.fixture(scope="session")
def qapp():
    app = QGuiApplication.instance()
    if app is None:
        QQuickStyle.setStyle("Basic")
        app = QGuiApplication(sys.argv)
    apply_test_app_font(app)
    yield app


def _process(ms: int) -> None:
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def _wait_until_ready(component: QQmlComponent, timeout_ms: int = 500) -> None:
    remaining = timeout_ms
    while component.status() == QQmlComponent.Loading and remaining > 0:
        _process(25)
        remaining -= 25


def _qml_dir_uri() -> str:
    return (Path(__file__).resolve().parents[1] / "app" / "qml").as_uri()


def _wrapper_supervisor(selected_profile_qml: str) -> str:
    return (
        supervisor_overview_block()
        + supervisor_profiles_block()
        + working_lane_block()
        + completed_lane_block()
        + automation_lane_block()
        + attention_lane_block()
        + supervisor_actions_block(selected_profile_qml)
    )


def _build_wrapper(*, selected_profile_qml: str, expected_title: str) -> str:
    del expected_title
    qml_dir = _qml_dir_uri()
    return (
        wrapper_header(qml_dir)
        + _wrapper_supervisor(selected_profile_qml)
        + wrapper_footer()
    )


def _build_segmented_tabs_wrapper(current_value: str = "installed") -> str:
    qml_dir = _qml_dir_uri()
    return f'''
import QtQuick 2.15
import QtQuick.Controls 2.15
import "{qml_dir}"

Item {{
    width: 360
    height: 120

    property bool isDark: false
    property color accent: "#FFA11A"
    property color borderSubtle: "#14000000"
    property color textSecondary: "#6F5A4B"
    property int typeLabel: 14
    property int motionFast: 180
    property int easeStandard: Easing.OutCubic
    property int easeEmphasis: Easing.OutBack

    SegmentedTabs {{
        anchors.centerIn: parent
        currentValue: "{current_value}"
        items: [
            {{ value: "installed", label: "已安装", icon: "../resources/icons/vendor/iconoir/book-stack.svg" }},
            {{ value: "discover", label: "发现", icon: "../resources/icons/vendor/iconoir/page-search.svg" }}
        ]
    }}
}}
'''


def _build_split_handle_wrapper(handle_height: int = 28) -> str:
    qml_dir = _qml_dir_uri()
    return f'''
import QtQuick 2.15
import "{qml_dir}"

Item {{
    width: 24
    height: {handle_height}

    property bool isDark: false

    WorkspaceSplitHandle {{
        id: handle
        objectName: "workspaceSplitHandle"
        anchors.centerIn: parent
        width: 10
        height: parent.height
    }}
}}
'''


__all__ = [name for name in globals() if not (name.startswith("__") and name.endswith("__"))]
