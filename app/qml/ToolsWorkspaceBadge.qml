import QtQuick 2.15

Rectangle {
    id: root

    property var workspace
    property string text: ""
    property color tone: "#60A5FA"
    property bool prominent: false

    readonly property bool isDark: workspace ? workspace.isDark : false
    readonly property color textPrimary: workspace ? workspace.textPrimary : "transparent"
    readonly property int typeCaption: workspace ? workspace.typeCaption : 12
    readonly property int weightBold: workspace ? workspace.weightBold : Font.Normal

    radius: prominent ? 11 : 10
    height: prominent ? 22 : 20
    color: prominent
        ? Qt.rgba(Qt.color(tone).r, Qt.color(tone).g, Qt.color(tone).b, root.isDark ? 0.18 : 0.10)
        : (root.isDark ? "#1D1713" : "#FFFFFF")
    border.width: 1
    border.color: prominent
        ? Qt.rgba(Qt.color(tone).r, Qt.color(tone).g, Qt.color(tone).b, root.isDark ? 0.34 : 0.24)
        : (root.isDark ? "#16FFFFFF" : "#10000000")
    width: label.implicitWidth + (prominent ? 16 : 14)

    Text {
        id: label
        anchors.centerIn: parent
        text: root.text
        color: root.textPrimary
        font.pixelSize: prominent ? root.typeCaption : 11
        font.weight: root.weightBold
    }
}
