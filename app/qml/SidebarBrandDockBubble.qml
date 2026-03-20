import QtQuick 2.15

Item {
    id: root

    required property var dockRoot
    required property var appIconButton

    property real liftOffset: dockRoot.iconHovered ? 0 : 5

    width: speechBubble.width
    height: speechBubble.height
    x: Math.max(2, appIconButton.x + appIconButton.width / 2 - width / 2)
    anchors.bottom: appIconButton.top
    anchors.bottomMargin: 12
    opacity: dockRoot.bubbleVisible ? 1.0 : 0.0
    transform: Translate { y: root.liftOffset }
    visible: opacity > 0.01

    Behavior on opacity { NumberAnimation { duration: dockRoot.motionUi; easing.type: dockRoot.easeStandard } }
    Behavior on liftOffset { NumberAnimation { duration: dockRoot.motionUi; easing.type: dockRoot.easeEmphasis } }

    Rectangle {
        id: speechBubble
        readonly property real fittedWidth: Math.max(108, Math.min(156, bubbleLabel.implicitWidth + 28))
        width: fittedWidth
        height: bubbleLabel.implicitHeight + 14
        radius: 14
        anchors.horizontalCenter: parent.horizontalCenter
        color: dockRoot.isDark ? "#1B1511" : "#FFFDF9"
        border.width: 1
        border.color: dockRoot.isDark ? "#30241C" : "#E2D6CB"
        antialiasing: true

        Text {
            id: bubbleLabel
            anchors.centerIn: parent
            width: speechBubble.width - 24
            text: dockRoot.currentBubbleText
            color: dockRoot.isDark ? "#E8D8C8" : "#6B5B4C"
            font.pixelSize: dockRoot.typeMeta - 1
            font.weight: dockRoot.weightDemiBold
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            maximumLineCount: 2
            elide: Text.ElideRight
            renderType: Text.NativeRendering
        }
    }
}
