import QtQuick 2.15

Rectangle {
    id: bubble

    required property var workspaceRoot
    readonly property alias hoverArea: bubbleHover
    readonly property alias headingMeasure: headingMeasure

    objectName: "hubDetailBubble"
    z: 20
    property real maxContentHeight: 116
    width: Math.max(156, Math.min(280, workspaceRoot.bubbleBodyWidth + 24))
    x: workspaceRoot.orbItem.x + workspaceRoot.orbItem.width - 2
    y: Math.max(2, workspaceRoot.orbItem.y + 2)
    visible: workspaceRoot.showBubble
    color: workspaceRoot.bubbleSurface
    radius: 14
    border.width: 1
    border.color: workspaceRoot.bubbleBorder
    opacity: visible ? 1.0 : 0.0
    implicitHeight: Math.min(maxContentHeight, bubbleContent.implicitHeight) + 16
    clip: true
    transformOrigin: Item.Left
    scale: visible ? 1.0 : 0.92

    Behavior on scale { NumberAnimation { duration: workspaceRoot.motionFast; easing.type: Easing.OutCubic } }
    Behavior on opacity { NumberAnimation { duration: workspaceRoot.motionFast; easing.type: Easing.OutCubic } }

    Canvas {
        visible: false
        anchors.bottom: parent.top
        width: 12
        height: 8
        x: Math.max(0, Math.min(parent.width - width, workspaceRoot.orbItem.x + workspaceRoot.orbItem.width / 2 - bubble.x - width / 2))
        onPaint: {
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)
            ctx.beginPath()
            ctx.moveTo(width / 2, 0)
            ctx.lineTo(0, height)
            ctx.lineTo(width, height)
            ctx.closePath()
            ctx.fillStyle = bubble.color
            ctx.fill()
        }
    }

    Flickable {
        objectName: "hubDetailViewport"
        anchors.fill: parent
        anchors.margins: 7
        clip: true
        contentWidth: width
        contentHeight: bubbleContent.implicitHeight
        boundsBehavior: Flickable.StopAtBounds
        interactive: contentHeight > height

        Column {
            id: bubbleContent
            width: parent.width
            spacing: 6

            Text {
                objectName: "hubDetailText"
                width: parent.width
                text: workspaceRoot.bubbleHeading
                color: workspaceRoot.bubbleHeadingColor
                font.pixelSize: workspaceRoot.bubbleHeadingSize
                font.weight: workspaceRoot.bubbleHeadingWeight
                opacity: workspaceRoot.bubbleHeadingOpacity
                wrapMode: Text.WordWrap
                textFormat: Text.PlainText
            }

            Text {
                id: headingMeasure
                visible: false
                text: workspaceRoot.bubbleHeading
                font.pixelSize: workspaceRoot.bubbleHeadingSize
                font.weight: workspaceRoot.bubbleHeadingWeight
            }

            Column {
                width: parent.width
                spacing: 5
                visible: workspaceRoot.hasChannels

                Repeater {
                    model: workspaceRoot.channels

                    Row {
                        width: bubbleContent.width
                        spacing: 7

                        Rectangle {
                            width: 22
                            height: width
                            radius: width / 2
                            color: workspaceRoot.rowIconSurface

                            AppIcon {
                                anchors.centerIn: parent
                                width: 16
                                height: width
                                source: modelData ? workspaceRoot.iconSource(modelData.channel) : ""
                                sourceSize: Qt.size(width, height)
                            }

                            Rectangle {
                                anchors.right: parent.right
                                anchors.bottom: parent.bottom
                                width: 8
                                height: width
                                radius: width / 2
                                color: modelData ? workspaceRoot.iconAccent(modelData.channel, modelData.state) : "transparent"
                                border.width: 1
                                border.color: bubble.color
                            }
                        }

                        Column {
                            width: parent.width - 26
                            spacing: 2

                            Row {
                                width: parent.width
                                spacing: 6

                                Text {
                                    text: workspaceRoot.channelLabel(modelData.channel)
                                    color: workspaceRoot.textPrimary
                                    font.pixelSize: workspaceRoot.typeCaption
                                    font.weight: workspaceRoot.weightMedium
                                }

                                Text {
                                    text: workspaceRoot.channelStateText(modelData.state)
                                    color: workspaceRoot.iconAccent(modelData.channel, modelData.state)
                                    font.pixelSize: workspaceRoot.typeCaption - 1
                                    font.weight: workspaceRoot.weightMedium
                                    opacity: 0.86
                                }
                            }

                            Text {
                                visible: Boolean(modelData.detail)
                                width: parent.width
                                text: modelData.detail || ""
                                color: workspaceRoot.isDark ? workspaceRoot.textSecondary : "#7A5F52"
                                font.pixelSize: workspaceRoot.typeCaption - 1
                                font.weight: workspaceRoot.weightMedium
                                wrapMode: Text.WordWrap
                                textFormat: Text.PlainText
                                opacity: 0.9
                            }
                        }
                    }
                }
            }
        }
    }

    MouseArea {
        id: bubbleHover
        anchors.fill: parent
        anchors.leftMargin: -10
        anchors.topMargin: -8
        hoverEnabled: true
        acceptedButtons: Qt.NoButton
    }
}
