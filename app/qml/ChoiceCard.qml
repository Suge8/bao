import QtQuick 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root

    property string badgeText: ""
    property string title: ""
    property string description: ""
    property string trailingText: ""
    property bool selected: false
    property bool clickable: true
    property real pulsePhase: 0.0
    signal clicked()

    radius: radiusMd
    color: selected ? (isDark ? "#18FFB33D" : "#14FFB33D") : (isDark ? "#0DFFFFFF" : "#08000000")
    border.color: selected ? accent : (cardArea.containsMouse ? accent : borderSubtle)
    border.width: selected || cardArea.containsMouse ? 1.2 : 1
    scale: cardArea.pressed
           ? 0.992
           : (selected ? motionSelectionScaleHover : (cardArea.containsMouse ? motionHoverScaleSubtle : 1.0))
    implicitHeight: cardCol.implicitHeight + 24

    Behavior on color { ColorAnimation { duration: motionFast; easing.type: easeStandard } }
    Behavior on border.color { ColorAnimation { duration: motionFast; easing.type: easeStandard } }
    Behavior on border.width { NumberAnimation { duration: motionFast; easing.type: easeStandard } }
    Behavior on scale { NumberAnimation { duration: motionFast; easing.type: easeEmphasis } }

    SequentialAnimation on pulsePhase {
        running: root.selected
        loops: Animation.Infinite
        NumberAnimation { from: 0.0; to: 1.0; duration: motionAmbient + motionMicro; easing.type: easeSoft }
        NumberAnimation { from: 1.0; to: 0.0; duration: motionAmbient + motionMicro; easing.type: easeSoft }
    }

    Rectangle {
        anchors.fill: parent
        radius: parent.radius
        color: accent
        opacity: root.selected
                 ? (0.06 + root.pulsePhase * 0.04)
                 : (cardArea.containsMouse ? 0.04 : 0.0)
        scale: root.selected ? (1.0 + root.pulsePhase * 0.018) : (cardArea.containsMouse ? 1.01 : 0.98)
        visible: opacity > 0.001
        Behavior on opacity { NumberAnimation { duration: motionUi; easing.type: easeStandard } }
        Behavior on scale { NumberAnimation { duration: motionUi; easing.type: easeEmphasis } }
    }

    Rectangle {
        width: Math.max(44, parent.width * 0.26)
        height: parent.height * 0.88
        radius: height / 2
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        anchors.rightMargin: -height * 0.08
        color: accent
        opacity: root.selected ? 0.10 : (cardArea.containsMouse ? 0.06 : 0.0)
        scale: root.selected ? 1.0 : 0.96
        visible: opacity > 0.001
        Behavior on opacity { NumberAnimation { duration: motionUi; easing.type: easeStandard } }
        Behavior on scale { NumberAnimation { duration: motionUi; easing.type: easeEmphasis } }
    }

    ColumnLayout {
        id: cardCol
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 12
        spacing: 8

        RowLayout {
            Layout.fillWidth: true
            visible: badgeText !== "" || trailingText !== ""

            Rectangle {
                visible: badgeText !== ""
                implicitWidth: badgeLabel.implicitWidth + 16
                implicitHeight: 24
                radius: 12
                color: root.selected ? accent : (isDark ? "#14FFFFFF" : "#10FFFFFF")
                scale: root.selected ? 1.0 : (cardArea.containsMouse ? motionHoverScaleSubtle : 1.0)
                Behavior on color { ColorAnimation { duration: motionFast; easing.type: easeStandard } }
                Behavior on scale { NumberAnimation { duration: motionFast; easing.type: easeEmphasis } }

                Text {
                    id: badgeLabel
                    anchors.centerIn: parent
                    text: root.badgeText
                    color: root.selected ? "#FFFFFFFF" : textSecondary
                    font.pixelSize: typeCaption
                    font.weight: Font.DemiBold
                }
            }

            Item { Layout.fillWidth: true }

            Text {
                visible: trailingText !== ""
                text: root.trailingText
                color: root.selected ? accent : textSecondary
                font.pixelSize: typeCaption
                font.weight: Font.DemiBold
            }
        }

        Text {
            Layout.fillWidth: true
            text: root.title
            color: textPrimary
            font.pixelSize: typeBody
            font.weight: Font.DemiBold
            wrapMode: Text.WordWrap
        }

        Text {
            visible: description !== ""
            Layout.fillWidth: true
            text: root.description
            color: textSecondary
            font.pixelSize: typeMeta
            wrapMode: Text.WordWrap
            lineHeight: 1.18
        }
    }

    MouseArea {
        id: cardArea
        anchors.fill: parent
        enabled: root.clickable
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton
        scrollGestureEnabled: false
        cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
        onClicked: root.clicked()
    }
}
