import QtQuick 2.15

Rectangle {
    id: root
    objectName: "sidebarAppIconButton"

    required property var dockRoot
    readonly property bool hovered: appIconArea.containsMouse
    readonly property bool pressed: appIconArea.pressed
    signal clicked()

    readonly property bool active: dockRoot.active

    width: 68
    height: 68
    radius: 34
    anchors.left: parent.left
    anchors.leftMargin: 8
    anchors.bottom: parent.bottom
    anchors.bottomMargin: 2
    antialiasing: true
    color: "transparent"
    border.width: dockRoot.active ? 1.5 : 0
    border.color: dockRoot.active ? dockRoot.accent : "transparent"
    scale: dockRoot.appIconScale

    Behavior on border.color { ColorAnimation { duration: dockRoot.motionUi; easing.type: dockRoot.easeStandard } }
    Behavior on border.width { NumberAnimation { duration: dockRoot.motionFast; easing.type: dockRoot.easeStandard } }
    Behavior on color { ColorAnimation { duration: dockRoot.motionUi; easing.type: dockRoot.easeStandard } }
    Behavior on scale { NumberAnimation { duration: dockRoot.motionUi; easing.type: dockRoot.easeEmphasis } }

    Rectangle {
        anchors.centerIn: parent
        width: 78
        height: 78
        radius: width / 2
        color: dockRoot.isDark ? "#26F4BF6A" : "#2FE4A45D"
        opacity: dockRoot.brandAuraOpacity
        scale: dockRoot.brandAuraScale
        Behavior on opacity { NumberAnimation { duration: dockRoot.motionUi; easing.type: dockRoot.easeSoft } }
        Behavior on scale { NumberAnimation { duration: dockRoot.motionPanel; easing.type: dockRoot.easeEmphasis } }
    }

    Rectangle {
        anchors.centerIn: parent
        width: 66
        height: 66
        radius: width / 2
        color: dockRoot.isDark ? "#12000000" : "#120A0603"
        opacity: dockRoot.brandPlateOpacity
        scale: dockRoot.brandPlateScale
        Behavior on opacity { NumberAnimation { duration: dockRoot.motionFast; easing.type: dockRoot.easeStandard } }
        Behavior on scale { NumberAnimation { duration: dockRoot.motionUi; easing.type: dockRoot.easeEmphasis } }
    }

    Item {
        id: brandMarkMotion
        objectName: "sidebarBrandMarkMotion"
        property real restY: (parent.height - height) / 2
        width: 58
        height: 58
        x: (parent.width - width) / 2
        y: restY
        rotation: 0
        scale: 1.0
        transformOrigin: Item.Center

        states: [
            State {
                name: "hovered"
                when: dockRoot.iconHovered
                PropertyChanges {
                    brandMarkMotion.y: brandMarkMotion.restY - dockRoot.hoverLiftTravel
                    brandMarkMotion.rotation: dockRoot.hoverTiltAngle
                    brandMarkMotion.x: (root.width - brandMarkMotion.width) / 2 - 0.6
                    brandMarkMotion.scale: dockRoot.appIconPressed ? 0.965 : dockRoot.hoverScalePeak
                }
            },
            State {
                name: "active"
                when: dockRoot.active
                PropertyChanges {
                    brandMarkMotion.y: brandMarkMotion.restY - 1.2
                    brandMarkMotion.rotation: 0
                    brandMarkMotion.x: (root.width - brandMarkMotion.width) / 2
                    brandMarkMotion.scale: 1.04
                }
            }
        ]
        transitions: Transition {
            NumberAnimation {
                properties: "x,y,rotation,scale"
                duration: dockRoot.motionPanel
                easing.type: dockRoot.easeSoft
            }
        }

        SequentialAnimation on y {
            running: dockRoot.visible && !dockRoot.iconHovered && !dockRoot.active
            loops: Animation.Infinite
            NumberAnimation { to: brandMarkMotion.restY - dockRoot.idleLiftTravel; duration: dockRoot.idleMotionDuration; easing.type: dockRoot.easeSoft }
            NumberAnimation { to: brandMarkMotion.restY; duration: dockRoot.idleMotionDuration - 110; easing.type: dockRoot.easeSoft }
        }
        SequentialAnimation on scale {
            running: dockRoot.visible && !dockRoot.iconHovered && !dockRoot.active
            loops: Animation.Infinite
            NumberAnimation { to: dockRoot.idleScalePeak; duration: dockRoot.idleMotionDuration; easing.type: dockRoot.easeSoft }
            NumberAnimation { to: 1.0; duration: dockRoot.idleMotionDuration - 110; easing.type: dockRoot.easeSoft }
        }

        AppIcon {
            id: brandMarkIcon
            objectName: "sidebarBrandMarkIcon"
            anchors.fill: parent
            source: dockRoot.brandImageSource
            sourceSize: Qt.size(116, 116)
        }

        Rectangle {
            width: 22
            height: 9
            radius: 4.5
            anchors.top: parent.top
            anchors.topMargin: 8
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.horizontalCenterOffset: -8
            rotation: -18
            color: "#24FFFFFF"
            opacity: dockRoot.iconHovered ? 0.42 : 0.20
            Behavior on opacity { NumberAnimation { duration: dockRoot.motionFast; easing.type: dockRoot.easeStandard } }
            SequentialAnimation on opacity {
                running: dockRoot.visible && !dockRoot.iconHovered && !dockRoot.active
                loops: Animation.Infinite
                NumberAnimation { to: 0.30; duration: dockRoot.idleMotionDuration; easing.type: dockRoot.easeSoft }
                NumberAnimation { to: 0.18; duration: dockRoot.idleMotionDuration - 110; easing.type: dockRoot.easeSoft }
            }
        }
    }

    MouseArea {
        id: appIconArea
        anchors.fill: parent
        anchors.margins: -8
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.clicked()
    }
}
