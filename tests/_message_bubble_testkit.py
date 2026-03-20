from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

pytest = importlib.import_module("pytest")

QtCore = pytest.importorskip("PySide6.QtCore")
QtGui = pytest.importorskip("PySide6.QtGui")
QtQml = pytest.importorskip("PySide6.QtQml")

QEventLoop = QtCore.QEventLoop
QMetaObject = QtCore.QMetaObject
QObject = QtCore.QObject
QTimer = QtCore.QTimer
QUrl = QtCore.QUrl
Qt = QtCore.Qt
QGuiApplication = QtGui.QGuiApplication
QQmlComponent = QtQml.QQmlComponent
QQmlEngine = QtQml.QQmlEngine


@dataclass(frozen=True, slots=True)
class WrapperOptions:
    role: str
    entrance_style: str
    content: str = "收到，杰哥。"
    dark: bool = True
    status: str = "done"
    entrance_pending: bool = False
    show_date_divider: bool = False
    date_divider_text: str = ""
    attachments_qml: str = "[]"
    references_qml: str = "({})"


@pytest.fixture(scope="session")
def qapp():
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
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


def _qml_import_header() -> str:
    qml_dir = (Path(__file__).resolve().parents[1] / "app" / "qml").as_uri()
    return f"""
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "{qml_dir}"
"""


def _greeting_palette(dark: bool) -> dict[str, str]:
    if dark:
        return {
            "greeting_aura_far": "#22FFD6A1",
            "greeting_aura_near": "#34FFE7C2",
            "greeting_bubble_bg_start": "#FF2B2118",
            "greeting_bubble_bg_end": "#FF201812",
            "greeting_bubble_border": "#50FFD19A",
            "greeting_bubble_overlay": "#10FFFFFF",
            "greeting_bubble_highlight": "#88FFF5DF",
            "greeting_sweep": "#16FFFFFF",
            "greeting_accent": "#F6C889",
            "greeting_text": "#FFF6EA",
            "greeting_icon_source": "../resources/icons/ignite-dark.svg",
        }
    return {
        "greeting_aura_far": "#0EE0BE93",
        "greeting_aura_near": "#18E8C79F",
        "greeting_bubble_bg_start": "#FFF7F3EC",
        "greeting_bubble_bg_end": "#FFF7F3EC",
        "greeting_bubble_border": "#1F8F6A47",
        "greeting_bubble_overlay": "#06FFFFFF",
        "greeting_bubble_highlight": "#42FFFFFF",
        "greeting_sweep": "#10FFFFFF",
        "greeting_accent": "#A8641F",
        "greeting_text": "#402715",
        "greeting_icon_source": "../resources/icons/ignite-light.svg",
    }


_WRAPPER_TEMPLATE = """{qml_header}
Item {{
    width: 420
    height: 220

    property int motionMicro: 120
    property int motionFast: 180
    property int motionUi: 220
    property int motionPanel: 320
    property int motionAmbient: 500
    property int motionBreath: 1100
    property int motionStatusPulse: 600
    property int motionTrackVelocity: 220
    property int easeStandard: Easing.OutCubic
    property int easeEmphasis: Easing.OutBack
    property int easeSoft: Easing.InOutSine
    property int easeLinear: Easing.Linear
    property real motionCopyFlashPeak: 0.42
    property real motionAuraNearPeak: 0.34
    property real motionAuraFarPeak: 0.2
    property real motionGreetingSweepPeak: 0.26
    property real motionTypingPulseMinOpacity: 0.28
    property int motionEnterOffsetY: 10
    property color statusError: "#F05A5A"
    property color accent: "#FFA11A"
    property color accentGlow: "#88FFF5DF"
    property color accentMuted: "#22FFA11A"
    property color accentHover: "#FFB444"
    property color borderSubtle: "#30FFFFFF"
    property color textPrimary: "#FFF6EA"
    property color textSecondary: "#C8B09A"
    property color bgCard: "#1A120D"
    property color bgCardHover: "#23170F"
    property int sizeBubbleRadius: 18
    property int sizeSystemBubbleRadius: 11
    property int typeBody: 15
    property int typeMeta: 12
    property real lineHeightBody: 1.4
    property real letterTight: 0.2
    property int weightMedium: Font.Medium
    property color chatSystemAuraFar: "#46FFA11A"
    property color chatSystemAuraNear: "#36FFA11A"
    property color chatSystemAuraErrorFar: "#2EF05A5A"
    property color chatSystemAuraErrorNear: "#44F05A5A"
    property color chatSystemBubbleBg: "#28FFB33D"
    property color chatSystemBubbleBorder: "#58FFCB7A"
    property color chatSystemBubbleErrorBg: "#20F05A5A"
    property color chatSystemBubbleErrorBorder: "#58F05A5A"
    property color chatSystemBubbleOverlay: "#22FFA11A"
    property color chatSystemBubbleErrorOverlay: "#08F05A5A"
    property color chatSystemText: "#F6DEBA"
    property color chatGreetingAuraFar: "{greeting_aura_far}"
    property color chatGreetingAuraNear: "{greeting_aura_near}"
    property color chatGreetingBubbleBgStart: "{greeting_bubble_bg_start}"
    property color chatGreetingBubbleBgEnd: "{greeting_bubble_bg_end}"
    property color chatGreetingBubbleBorder: "{greeting_bubble_border}"
    property color chatGreetingBubbleOverlay: "{greeting_bubble_overlay}"
    property color chatGreetingBubbleHighlight: "{greeting_bubble_highlight}"
    property color chatGreetingSweep: "{greeting_sweep}"
    property color chatGreetingAccent: "{greeting_accent}"
    property color chatGreetingText: "{greeting_text}"
    property string chatGreetingIconSource: "{greeting_icon_source}"
    property color chatBubbleCopyFlashUser: "#40FFFFFF"
    property color chatBubbleErrorTint: "#15F05A5A"

    MessageBubble {{
        id: bubble
        objectName: "bubble"
        anchors.fill: parent
        role: "{role}"
        content: "{content}"
        format: "plain"
        status: "{status}"
        attachments: {attachments_qml}
        references: {references_qml}
        entranceStyle: "{entrance_style}"
        entrancePending: {entrance_pending}
        showDateDivider: {show_date_divider}
        dateDividerText: "{date_divider_text}"
        toastFunc: function() {{}}
    }}
}}
"""


def build_wrapper(options: WrapperOptions) -> str:
    palette = _greeting_palette(options.dark)
    return _WRAPPER_TEMPLATE.format(
        qml_header=_qml_import_header(),
        role=options.role,
        entrance_style=options.entrance_style,
        content=options.content,
        status=options.status,
        attachments_qml=options.attachments_qml,
        references_qml=options.references_qml,
        entrance_pending=str(options.entrance_pending).lower(),
        show_date_divider=str(options.show_date_divider).lower(),
        date_divider_text=options.date_divider_text,
        **palette,
    )


def create_component(qml_str: str, source: str) -> Tuple[QQmlEngine, QQmlComponent, QObject]:
    engine = QQmlEngine()
    component = QQmlComponent(engine)
    component.setData(qml_str.encode("utf-8"), QUrl(source))
    _wait_until_ready(component)
    assert component.status() == QQmlComponent.Ready, component.errors()
    root = component.create()
    assert root is not None, component.errors()
    return engine, component, root


__all__ = [
    "QQmlComponent",
    "QQmlEngine",
    "QMetaObject",
    "QObject",
    "QUrl",
    "Qt",
    "QGuiApplication",
    "WrapperOptions",
    "_process",
    "_wait_until_ready",
    "build_wrapper",
    "create_component",
    "qapp",
]
