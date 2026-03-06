import QtQuick 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root

    property string title: ""
    property bool expanded: false
    property bool clickable: true
    property bool showArrow: true
    property real reservedRightMargin: 0
    readonly property real effectiveRightMargin: Math.max(root.reservedRightMargin, trailingRow.implicitWidth > 0 ? trailingRow.implicitWidth + 8 : 0)
    property int headerHeight: 36
    property int titlePixelSize: typeLabel
    property int titleWeight: weightMedium
    property color titleColor: textSecondary
    default property alias trailing: trailingRow.data
    signal clicked()

    Layout.fillWidth: true
    implicitHeight: root.headerHeight
    radius: radiusSm
    color: headerArea.pressed
           ? (isDark ? "#12FFFFFF" : "#10000000")
           : (headerArea.containsMouse ? (isDark ? "#0AFFFFFF" : "#08000000") : "transparent")
    scale: headerArea.pressed ? 0.992 : 1.0

    Behavior on color { ColorAnimation { duration: motionFast; easing.type: easeStandard } }
    Behavior on scale { NumberAnimation { duration: motionFast; easing.type: easeStandard } }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 4
        anchors.rightMargin: 4
        spacing: 8

        Text {
            visible: root.showArrow
            text: "▸"
            color: textTertiary
            font.pixelSize: typeMeta
            rotation: root.expanded ? 90 : 0
            Behavior on rotation { NumberAnimation { duration: motionPanel; easing.type: easeEmphasis } }
        }

        Text {
            text: root.title
            color: root.titleColor
            font.pixelSize: root.titlePixelSize
            font.weight: root.titleWeight
            font.letterSpacing: letterTight
            Layout.fillWidth: true
            elide: Text.ElideRight
            verticalAlignment: Text.AlignVCenter
        }

        RowLayout {
            id: trailingRow
            Layout.alignment: Qt.AlignVCenter
            spacing: 8
        }
    }

    MouseArea {
        id: headerArea
        anchors.fill: parent
        anchors.rightMargin: root.effectiveRightMargin
        enabled: root.clickable
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton
        scrollGestureEnabled: false
        cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
        onClicked: root.clicked()
    }
}
