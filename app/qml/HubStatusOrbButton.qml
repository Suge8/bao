import QtQuick 2.15

Rectangle {
    id: orb

    required property var workspaceRoot
    readonly property alias hoverArea: orbHover

    objectName: "hubDetailOrb"
    width: Math.max(workspaceRoot.orbMinWidth, orbContent.implicitWidth + workspaceRoot.orbPaddingX * 2)
    height: 28
    radius: height / 2
    anchors.right: parent.right
    anchors.rightMargin: -18
    anchors.top: parent.top
    anchors.topMargin: -8
    color: workspaceRoot.orbSurface
    border.width: 0
    opacity: workspaceRoot.hasDetail ? 1.0 : 0.0
    scale: orbHover.containsMouse ? 1.06 : 1.0

    Behavior on opacity { NumberAnimation { duration: workspaceRoot.motionFast; easing.type: Easing.OutCubic } }
    Behavior on scale { NumberAnimation { duration: workspaceRoot.motionFast; easing.type: Easing.OutCubic } }

    Row {
        id: orbContent
        anchors.centerIn: parent
        spacing: 1

        Repeater {
            model: workspaceRoot.orbChannels.length > 0 ? workspaceRoot.orbChannels : [null]

            Rectangle {
                width: modelData && workspaceRoot.orbChannels.length > 1 ? 15 : 18
                height: width
                radius: width / 2
                color: modelData ? workspaceRoot.chipSurface : "transparent"

                AppIcon {
                    visible: modelData !== null
                    anchors.centerIn: parent
                    width: parent.width - 1
                    height: width
                    source: modelData ? workspaceRoot.iconSource(modelData.channel) : ""
                    sourceSize: Qt.size(width, height)
                    opacity: 0.96
                }

                Rectangle {
                    visible: modelData !== null
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    width: 8
                    height: width
                    radius: width / 2
                    color: modelData ? workspaceRoot.iconAccent(modelData.channel, modelData.state) : "transparent"
                    border.width: 1
                    border.color: orb.color
                }
            }
        }
    }

    Text {
        anchors.centerIn: parent
        visible: workspaceRoot.orbChannels.length === 0
        text: workspaceRoot.hasErrorState ? "!" : "✓"
        color: workspaceRoot.hasErrorState ? workspaceRoot.statusError : workspaceRoot.statusSuccess
        font.pixelSize: 16
        font.weight: workspaceRoot.weightBold
    }

    Rectangle {
        objectName: "hubDetailOrbOverflow"
        visible: workspaceRoot.overflowCount > 0
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.rightMargin: -4
        anchors.bottomMargin: -2
        width: 15
        height: width
        radius: width / 2
        color: workspaceRoot.isDark ? "#FF201A17" : "#FFF3E7DB"
        border.width: 0

        Text {
            anchors.centerIn: parent
            text: "+" + workspaceRoot.overflowCount
            color: workspaceRoot.textPrimary
            font.pixelSize: 9
            font.weight: workspaceRoot.weightBold
        }
    }

    MouseArea {
        id: orbHover
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: function(mouse) { mouse.accepted = true }
    }
}
