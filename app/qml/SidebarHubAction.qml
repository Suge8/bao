import QtQuick 2.15

Item {
    id: root

    required property var sidebarRoot
    required property var capsule

    width: sidebarRoot.sizeHubAction
    height: sidebarRoot.sizeHubAction

    Rectangle {
        id: actionShell
        anchors.fill: parent
        radius: width / 2
        antialiasing: true
        color: Qt.darker(root.capsule.actionColor, sidebarRoot.isDark ? 1.22 : 1.14)
        scale: (root.capsule.isPressed ? 0.97 : (root.capsule.isHovered ? sidebarRoot.motionHoverScaleSubtle : 1.0))
               + root.capsule.actionPulse * 0.025

        Behavior on color { ColorAnimation { duration: root.capsule.stateTransitionDuration; easing.type: sidebarRoot.easeStandard } }
        Behavior on scale { NumberAnimation { duration: sidebarRoot.motionFast; easing.type: sidebarRoot.easeStandard } }

        Rectangle {
            id: actionFace
            anchors.centerIn: parent
            width: parent.width - 2
            height: width
            radius: width / 2
            color: root.capsule.actionColor
            Behavior on color { ColorAnimation { duration: root.capsule.stateTransitionDuration; easing.type: sidebarRoot.easeStandard } }
        }

        Rectangle {
            anchors.centerIn: actionFace
            width: actionFace.width
            height: width
            radius: width / 2
            color: "transparent"
            border.width: 1.4
            border.color: root.capsule.isError ? "#66FFF7F6" : (root.capsule.isRunning ? "#7AF7FFF9" : "#72FFFFFF")
            opacity: root.capsule.isIdleVisual ? 0.08 : (0.18 + root.capsule.actionPulse * 2.2)
            scale: 1.0 + root.capsule.actionPulse * (root.capsule.isStarting ? 1.25 : 0.9)

            Behavior on opacity { NumberAnimation { duration: sidebarRoot.motionFast; easing.type: sidebarRoot.easeSoft } }
            Behavior on scale { NumberAnimation { duration: sidebarRoot.motionUi; easing.type: sidebarRoot.easeSoft } }
            Behavior on border.color { ColorAnimation { duration: root.capsule.stateTransitionDuration; easing.type: sidebarRoot.easeStandard } }
        }

        Item {
            objectName: "hubActionIconWrap"
            anchors.centerIn: actionFace
            width: sidebarRoot.sizeHubActionIcon
            height: sidebarRoot.sizeHubActionIcon
            transformOrigin: Item.Center
            y: root.capsule.iconLift
            scale: 1.0 + root.capsule.iconPulse
            rotation: root.capsule.iconTurn

            Behavior on y { NumberAnimation { duration: root.capsule.stateTransitionDuration; easing.type: sidebarRoot.easeSoft } }
            Behavior on scale { NumberAnimation { duration: root.capsule.stateTransitionDuration; easing.type: sidebarRoot.easeSoft } }
            Behavior on rotation { NumberAnimation { duration: root.capsule.stateTransitionDuration; easing.type: sidebarRoot.easeSoft } }

            AppIcon {
                anchors.fill: parent
                source: root.capsule.actionIconSource
                sourceSize: Qt.size(sidebarRoot.sizeHubActionIcon, sidebarRoot.sizeHubActionIcon)
                opacity: root.capsule.isHovered ? 1.0 : 0.98
                visible: !root.capsule.useRunningPacman && root.capsule.actionIconSource != ""
                Behavior on opacity { NumberAnimation { duration: sidebarRoot.motionFast; easing.type: sidebarRoot.easeStandard } }
            }

            HubPacmanGlyph {
                anchors.fill: parent
                mouth: root.capsule.pacmanMouth
                phase: root.capsule.pacmanPhase
                visible: root.capsule.useRunningPacman
            }
        }
    }

    SequentialAnimation {
        running: root.capsule.isRunning
        loops: Animation.Infinite
        NumberAnimation { target: root.capsule; property: "actionPulse"; to: 0.075; duration: sidebarRoot.motionBreath; easing.type: sidebarRoot.easeSoft }
        NumberAnimation { target: root.capsule; property: "actionPulse"; to: 0.0; duration: sidebarRoot.motionBreath; easing.type: sidebarRoot.easeSoft }
    }
    SequentialAnimation {
        running: root.capsule.isStarting
        loops: Animation.Infinite
        NumberAnimation { target: root.capsule; property: "actionPulse"; to: 0.14; duration: sidebarRoot.motionAmbient; easing.type: sidebarRoot.easeSoft }
        NumberAnimation { target: root.capsule; property: "actionPulse"; to: 0.0; duration: sidebarRoot.motionAmbient; easing.type: sidebarRoot.easeSoft }
    }
    SequentialAnimation {
        running: root.capsule.isError
        loops: Animation.Infinite
        NumberAnimation { target: root.capsule; property: "actionPulse"; to: 0.09; duration: sidebarRoot.motionStatusPulse; easing.type: sidebarRoot.easeSoft }
        NumberAnimation { target: root.capsule; property: "actionPulse"; to: 0.0; duration: sidebarRoot.motionStatusPulse; easing.type: sidebarRoot.easeSoft }
    }
    SequentialAnimation {
        running: root.capsule.isIdleVisual
        loops: Animation.Infinite
        NumberAnimation { target: root.capsule; property: "iconLift"; to: -0.55; duration: sidebarRoot.motionAmbient; easing.type: sidebarRoot.easeSoft }
        NumberAnimation { target: root.capsule; property: "iconLift"; to: 0.0; duration: sidebarRoot.motionAmbient; easing.type: sidebarRoot.easeSoft }
    }
    SequentialAnimation {
        running: root.capsule.isIdleVisual
        loops: Animation.Infinite
        NumberAnimation { target: root.capsule; property: "iconPulse"; to: 0.045; duration: sidebarRoot.motionAmbient; easing.type: sidebarRoot.easeSoft }
        NumberAnimation { target: root.capsule; property: "iconPulse"; to: 0.0; duration: sidebarRoot.motionAmbient; easing.type: sidebarRoot.easeSoft }
    }
    SequentialAnimation {
        running: root.capsule.isIdleVisual
        loops: Animation.Infinite
        NumberAnimation { target: root.capsule; property: "iconTurn"; to: 3; duration: sidebarRoot.motionAmbient; easing.type: sidebarRoot.easeSoft }
        NumberAnimation { target: root.capsule; property: "iconTurn"; to: 0; duration: sidebarRoot.motionAmbient; easing.type: sidebarRoot.easeSoft }
    }
    SequentialAnimation {
        running: root.capsule.isStarting
        loops: Animation.Infinite
        NumberAnimation { target: root.capsule; property: "iconPulse"; to: 0.13; duration: sidebarRoot.motionAmbient; easing.type: sidebarRoot.easeSoft }
        NumberAnimation { target: root.capsule; property: "iconPulse"; to: 0.0; duration: sidebarRoot.motionAmbient; easing.type: sidebarRoot.easeSoft }
    }
    NumberAnimation {
        target: root.capsule
        property: "iconTurn"
        from: 0
        to: 360
        duration: sidebarRoot.motionFloat
        loops: Animation.Infinite
        easing.type: sidebarRoot.easeLinear
        running: root.capsule.isStarting
    }
    SequentialAnimation {
        running: root.capsule.isRunning
        loops: Animation.Infinite
        NumberAnimation { target: root.capsule; property: "iconLift"; to: -0.45; duration: sidebarRoot.motionBreath; easing.type: sidebarRoot.easeSoft }
        NumberAnimation { target: root.capsule; property: "iconLift"; to: 0.45; duration: sidebarRoot.motionBreath; easing.type: sidebarRoot.easeSoft }
        NumberAnimation { target: root.capsule; property: "iconLift"; to: 0.0; duration: sidebarRoot.motionBreath; easing.type: sidebarRoot.easeSoft }
    }
    SequentialAnimation {
        running: root.capsule.isRunning
        loops: Animation.Infinite
        NumberAnimation { target: root.capsule; property: "iconPulse"; to: 0.085; duration: sidebarRoot.motionBreath; easing.type: sidebarRoot.easeSoft }
        NumberAnimation { target: root.capsule; property: "iconPulse"; to: 0.02; duration: sidebarRoot.motionBreath; easing.type: sidebarRoot.easeSoft }
    }
    SequentialAnimation {
        running: root.capsule.isRunning
        loops: Animation.Infinite
        NumberAnimation { target: root.capsule; property: "pacmanMouth"; to: root.capsule.pacmanMouthWide; duration: 220; easing.type: sidebarRoot.easeSoft }
        NumberAnimation { target: root.capsule; property: "pacmanMouth"; to: root.capsule.pacmanMouthClosed; duration: 140; easing.type: sidebarRoot.easeSoft }
        NumberAnimation { target: root.capsule; property: "pacmanMouth"; to: root.capsule.pacmanMouthRest; duration: 120; easing.type: sidebarRoot.easeSoft }
    }
    NumberAnimation {
        target: root.capsule
        property: "pacmanPhase"
        from: 0.0
        to: 1.0
        duration: 480
        loops: Animation.Infinite
        easing.type: sidebarRoot.easeLinear
        running: root.capsule.isRunning
    }
    SequentialAnimation {
        running: root.capsule.isError
        loops: Animation.Infinite
        NumberAnimation { target: root.capsule; property: "iconPulse"; to: 0.07; duration: sidebarRoot.motionStatusPulse; easing.type: sidebarRoot.easeSoft }
        NumberAnimation { target: root.capsule; property: "iconPulse"; to: 0.0; duration: sidebarRoot.motionStatusPulse; easing.type: sidebarRoot.easeSoft }
    }
    SequentialAnimation {
        running: root.capsule.isError
        loops: Animation.Infinite
        NumberAnimation { target: root.capsule; property: "iconTurn"; to: 4; duration: sidebarRoot.motionStatusPulse; easing.type: sidebarRoot.easeSoft }
        NumberAnimation { target: root.capsule; property: "iconTurn"; to: -4; duration: sidebarRoot.motionStatusPulse; easing.type: sidebarRoot.easeSoft }
        NumberAnimation { target: root.capsule; property: "iconTurn"; to: 0; duration: sidebarRoot.motionStatusPulse; easing.type: sidebarRoot.easeSoft }
    }
    NumberAnimation {
        target: root.capsule
        property: "iconTurn"
        to: 0
        duration: sidebarRoot.motionUi
        easing.type: sidebarRoot.easeSoft
        running: root.capsule.isRunning && Math.abs(root.capsule.iconTurn) > 0.01
    }
}
