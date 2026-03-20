import QtQuick 2.15

Rectangle {
    id: root

    property int count: 0
    property string labelText: ""
    property bool isDark: false
    property color fillColor: isDark ? "#18110D" : "#FFF7EE"
    property color borderColor: isDark ? "#2D221C" : "#E7D6C2"
    property color textColor: isDark ? "#C8B09A" : "#7F5F45"
    property int fontPixelSize: 11
    property int fontWeight: Font.Medium

    implicitWidth: badgeText.implicitWidth + 16
    implicitHeight: 26
    radius: 13
    color: root.fillColor
    border.width: 1
    border.color: root.borderColor

    Text {
        id: badgeText
        anchors.centerIn: parent
        text: root.labelText.length > 0 ? root.labelText : String(root.count)
        color: root.textColor
        font.pixelSize: root.fontPixelSize
        font.weight: root.fontWeight
    }
}
