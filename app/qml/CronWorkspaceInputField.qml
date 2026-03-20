import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root

    property var workspace
    property bool fieldEnabled: true
    property alias text: field.text
    property alias placeholderText: field.placeholderText
    property alias inputMethodHints: field.inputMethodHints
    signal textEdited(string value)

    implicitHeight: 44
    radius: 16
    color: hoverRegion.containsMouse ? workspace.fieldHoverFill : workspace.fieldFill
    border.width: field.activeFocus ? 1.5 : 1
    border.color: field.activeFocus ? workspace.borderFocus : workspace.fieldBorder
    opacity: fieldEnabled ? 1.0 : 0.6

    MouseArea {
        id: hoverRegion
        anchors.fill: parent
        hoverEnabled: true
        acceptedButtons: Qt.NoButton
    }

    TextField {
        id: field
        property bool baoClickAwayEditor: true
        anchors.fill: parent
        anchors.leftMargin: 14
        anchors.rightMargin: 14
        enabled: root.fieldEnabled
        hoverEnabled: true
        color: workspace.textPrimary
        placeholderTextColor: workspace.textPlaceholder
        background: null
        leftPadding: 0
        rightPadding: 0
        topPadding: 0
        bottomPadding: 0
        verticalAlignment: TextInput.AlignVCenter
        selectionColor: workspace.textSelectionBg
        selectedTextColor: workspace.textSelectionFg
        onTextEdited: root.textEdited(text)
    }
}
