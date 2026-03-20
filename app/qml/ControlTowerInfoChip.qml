import QtQuick 2.15

Rectangle {
    id: root

    property string chipId: ""
    property string labelText: ""
    property bool isDark: false
    property color fillColor: isDark ? "#18110D" : "#FFF7EE"
    property color borderColor: isDark ? "#2D221C" : "#E7D6C2"
    property color textColor: isDark ? "#C8B09A" : "#7F5F45"
    property int fontPixelSize: 11
    property int fontWeight: Font.Medium
    property real horizontalPadding: 14
    property real minHeight: 24
    property real maximumWidth: -1
    readonly property real contentWidth: chipText.implicitWidth + horizontalPadding
    readonly property real resolvedMaximumWidth: maximumWidth > 0 ? maximumWidth : contentWidth

    objectName: chipId.length > 0 ? "controlTowerInfoChip_" + chipId : ""
    clip: true
    implicitWidth: Math.min(contentWidth, resolvedMaximumWidth)
    implicitHeight: minHeight
    radius: implicitHeight / 2
    color: root.fillColor
    border.width: 1
    border.color: root.borderColor
    visible: root.labelText.length > 0

    Text {
        id: chipText
        anchors.centerIn: parent
        width: Math.max(0, parent.width - horizontalPadding)
        text: root.labelText
        color: root.textColor
        font.pixelSize: root.fontPixelSize
        font.weight: root.fontWeight
        textFormat: Text.PlainText
        elide: Text.ElideRight
        maximumLineCount: 1
        horizontalAlignment: Text.AlignHCenter
    }
}
