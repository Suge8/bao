import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: emptyState

    property var workspaceRoot: null
    property string sectionKind: ""
    property var sectionModel: null
    property bool isDark: false
    property color textPrimary: "transparent"
    property color textSecondary: "transparent"
    property color textTertiary: "transparent"
    property color tileActive: "transparent"
    property color tileHover: "transparent"
    property real motionFast: 0
    property int easeStandard: 0
    property int typeMeta: 12
    property int typeLabel: 14
    property int typeCaption: 11
    property int weightBold: Font.Bold
    property int weightMedium: Font.Medium

    implicitHeight: 160

    Rectangle {
        anchors.fill: parent
        radius: 16
        color: isDark ? "#140E0B" : "#FFF8F2"
        border.width: 1
        border.color: isDark ? "#14FFFFFF" : "#12000000"

        Text {
            anchors.centerIn: parent
            width: parent.width - 28
            text: workspaceRoot.emptyTitle(sectionKind)
            color: textPrimary
            font.pixelSize: typeLabel
            font.weight: weightBold
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
        }
    }
}
