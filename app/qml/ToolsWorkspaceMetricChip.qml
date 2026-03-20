import QtQuick 2.15

Rectangle {
    id: root

    property var workspace
    property string label: ""
    property string value: ""
    property color tone: "#F97316"
    property bool showIndicator: true

    readonly property bool isDark: workspace ? workspace.isDark : false
    readonly property color textPrimary: workspace ? workspace.textPrimary : "transparent"
    readonly property color textSecondary: workspace ? workspace.textSecondary : "transparent"
    readonly property int typeCaption: workspace ? workspace.typeCaption : 12
    readonly property int typeLabel: workspace ? workspace.typeLabel : 14
    readonly property int weightBold: workspace ? workspace.weightBold : Font.Normal

    implicitWidth: metricRow.implicitWidth + 18
    implicitHeight: 38
    radius: 14
    color: root.isDark ? "#181310" : "#FFFDFC"
    border.width: 1
    border.color: root.isDark ? "#12FFFFFF" : "#0E000000"

    Row {
        id: metricRow
        anchors.centerIn: parent
        spacing: root.showIndicator ? 8 : 0

        Rectangle {
            width: root.showIndicator ? 7 : 0
            height: 7
            radius: 3.5
            color: root.tone
            anchors.verticalCenter: parent.verticalCenter
            visible: root.showIndicator
        }

        Text {
            text: root.label
            color: root.textSecondary
            font.pixelSize: root.typeCaption
            font.weight: root.weightBold
            anchors.verticalCenter: parent.verticalCenter
        }

        Text {
            text: root.value
            color: root.textPrimary
            font.pixelSize: root.typeLabel
            font.weight: root.weightBold
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}
