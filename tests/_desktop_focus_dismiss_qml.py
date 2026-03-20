# ruff: noqa: E402

from __future__ import annotations

from pathlib import Path


def _qml_import_header() -> str:
    qml_import = (Path(__file__).resolve().parents[1] / "app" / "qml").as_uri()
    return f"""
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "{qml_import}"
"""


def _build_window() -> bytes:
    return b"""
import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    width: 400
    height: 240
    visible: true
    Item {
        anchors.fill: parent
        Rectangle {
            anchors.fill: parent
            color: "white"
        }
        TextArea {
            id: editor
            objectName: "editor"
            property bool baoClickAwayEditor: true
            x: 40
            y: 40
            width: 200
            height: 80
            focus: true
            text: "hello bao"
        }
    }
}
"""


def _build_two_editor_window() -> bytes:
    return b"""
import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    width: 500
    height: 240
    visible: true
    Item {
        anchors.fill: parent
        Rectangle {
            anchors.fill: parent
            color: "white"
        }
        TextArea {
            id: editorA
            objectName: "editorA"
            property bool baoClickAwayEditor: true
            x: 40
            y: 40
            width: 160
            height: 80
            text: "hello a"
        }
        TextArea {
            id: editorB
            objectName: "editorB"
            property bool baoClickAwayEditor: true
            x: 240
            y: 40
            width: 160
            height: 80
            text: "hello b"
        }
    }
}
"""


def _build_editor_and_button_window() -> bytes:
    return b"""
import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    width: 520
    height: 240
    visible: true
    Item {
        anchors.fill: parent
        TextArea {
            id: editor
            objectName: "editor"
            property bool baoClickAwayEditor: true
            x: 40
            y: 40
            width: 200
            height: 80
            text: "hello bao"
        }
        Button {
            id: button
            objectName: "button"
            x: 300
            y: 40
            width: 100
            height: 40
            text: "Go"
            focusPolicy: Qt.StrongFocus
        }
    }
}
"""


def _build_editor_and_mouse_area_window() -> bytes:
    return b"""
import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    id: root
    width: 520
    height: 260
    visible: true
    property bool clicked: false

    Item {
        anchors.fill: parent

        TextArea {
            id: editor
            objectName: "editor"
            property bool baoClickAwayEditor: true
            x: 40
            y: 40
            width: 200
            height: 80
            text: "hello bao"
        }

        Rectangle {
            id: clickTarget
            objectName: "clickTarget"
            x: 300
            y: 40
            width: 140
            height: 44
            radius: 10
            color: "#dddddd"

            MouseArea {
                anchors.fill: parent
                onClicked: root.clicked = true
            }
        }
    }
}
"""


def _build_editor_and_expand_header_window() -> bytes:
    return f"""
{_qml_import_header()}

ApplicationWindow {{
    id: root
    width: 520
    height: 260
    visible: true
    property bool expanded: false
    property int radiusSm: 8
    property color textTertiary: "#666666"
    property int typeMeta: 12
    property color textSecondary: "#444444"
    property real letterTight: 0.2
    property int weightMedium: 500
    property int typeLabel: 13
    property bool isDark: false
    property int motionFast: 180
    property int motionPanel: 320
    property int easeStandard: Easing.OutCubic
    property int easeEmphasis: Easing.OutBack

    ColumnLayout {{
        anchors.fill: parent
        anchors.margins: 24
        spacing: 16

        TextArea {{
            id: editor
            objectName: "editor"
            property bool baoClickAwayEditor: true
            Layout.fillWidth: true
            Layout.preferredHeight: 80
            text: "hello bao"
        }}

        ExpandHeader {{
            id: header
            objectName: "expandHeader"
            Layout.fillWidth: true
            title: "Provider"
            expanded: root.expanded
            onClicked: root.expanded = !root.expanded
        }}
    }}
}}
""".encode("utf-8")


def _settings_select_root_properties() -> str:
    return """
    property bool clicked: false
    property int radiusSm: 8; property color textTertiary: "#666666"; property color textSecondary: "#444444"
    property color textPrimary: "#111111"; property color textPlaceholder: "#777777"; property color bgInput: "#f2f2f2"
    property color bgInputHover: "#e9e9e9"; property color bgInputFocus: "#dddddd"; property color borderSubtle: "#cccccc"; property color borderFocus: "#ff8800"
    property bool isDark: false; property int typeLabel: 13; property int typeButton: 14; property int typeCaption: 12; property int typeMeta: 12; property int weightMedium: 500; property real letterTight: 0.2
    property int sizeControlHeight: 40; property int sizeDropdownMaxHeight: 220; property int sizeOptionHeight: 36; property int sizeFieldPaddingX: 12; property int spacingSm: 8; property int spacingMd: 12
    property int motionUi: 120; property int motionFast: 120; property int motionMicro: 80; property int motionPanel: 180; property int easeStandard: Easing.OutCubic; property int easeEmphasis: Easing.OutBack
"""


def _build_settings_select_and_mouse_area_window() -> bytes:
    return f"""
{_qml_import_header()}

ApplicationWindow {{
    id: root
    width: 420
    height: 320
    visible: true
{_settings_select_root_properties()}

    SettingsSelect {{
        id: settingsSelect
        objectName: "settingsSelect"
        x: 20
        y: 20
        width: root.width - 40
        label: "Context"
        dotpath: ""
        initialValue: "auto"
        options: [
            {{"label": "auto", "value": "auto"}},
            {{"label": "off", "value": "off"}}
        ]
    }}

    Rectangle {{
        id: hitTarget
        objectName: "hitTarget"
        x: 120
        y: 220
        width: 180
        height: 48
        color: "#cccccc"

        MouseArea {{
            anchors.fill: parent
            onClicked: root.clicked = true
        }}
    }}
}}
""".encode("utf-8")


__all__ = [
    "_build_editor_and_button_window",
    "_build_editor_and_expand_header_window",
    "_build_editor_and_mouse_area_window",
    "_build_settings_select_and_mouse_area_window",
    "_build_two_editor_window",
    "_build_window",
]
