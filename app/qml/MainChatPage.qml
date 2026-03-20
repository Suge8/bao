import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    required property var appRoot
    required property real cornerRadius

    property bool active: !appRoot.showingSettings
    property real revealOpacity: 1.0
    property real revealScale: 1.0
    property real revealShift: 0.0
    property real revealAuraOpacity: 0.0
    property real completionFlashOpacity: 0.0
    property real completionFlashScale: 0.94
    property real workspaceSwitchOpacity: 1.0
    property real workspaceSwitchScale: 1.0
    property real workspaceSwitchShift: 0.0
    property real workspaceSwitchAuraOpacity: 0.0
    property real workspaceSwitchSweepOpacity: 0.0
    property real workspaceSwitchSweepX: -0.22

    function playReveal(direction, distance) {
        revealOpacity = appRoot.design.motionPageRevealStartOpacity
        revealScale = appRoot.design.motionPageRevealStartScale
        revealShift = direction * distance
        revealAuraOpacity = appRoot.design.motionPageAuraPeak
        chatPageReveal.restart()
    }

    function playSetupCompletionReveal() {
        playReveal(-1, appRoot.design.motionPageShift + 8)
        completionFlashOpacity = 0.24
        completionFlashScale = 0.94
        setupCompletionReveal.restart()
    }

    function playWorkspaceSwitch(direction) {
        workspaceSwitchOpacity = 0.78
        workspaceSwitchScale = 0.992
        workspaceSwitchShift = direction * appRoot.design.motionPageShiftSubtle
        workspaceSwitchAuraOpacity = appRoot.design.motionPageAuraPeak * 1.2
        workspaceSwitchSweepOpacity = 0.24
        workspaceSwitchSweepX = direction > 0 ? -0.22 : 0.22
        workspaceSwitchReveal.restart()
    }

    onActiveChanged: {
        if (active)
            playReveal(-1, appRoot.design.motionPageShift)
    }

    Connections {
        target: appRoot

        function onSetupCompletionTokenChanged() {
            if (root.active)
                root.playSetupCompletionReveal()
        }

        function onActiveWorkspaceChanged() {
            if (!root.active)
                return
            var nextIndex = appRoot.activeWorkspaceIndex
            var direction = nextIndex >= appRoot._lastActiveWorkspaceIndex ? 1 : -1
            appRoot._lastActiveWorkspaceIndex = nextIndex
            root.playWorkspaceSwitch(direction)
        }
    }

    Rectangle {
        anchors.fill: parent
        anchors.margins: 8
        radius: root.cornerRadius - 8
        color: appRoot.isDark ? "#14FFA11A" : "#0FFFF1DE"
        opacity: root.revealAuraOpacity
        visible: opacity > 0.01
    }

    Rectangle {
        anchors.fill: parent
        anchors.margins: 8
        radius: root.cornerRadius - 8
        color: appRoot.isDark ? "#20FFD699" : "#1FD0892C"
        opacity: root.completionFlashOpacity
        scale: root.completionFlashScale
        visible: opacity > 0.01
    }

    Rectangle {
        anchors.fill: parent
        anchors.margins: 8
        radius: root.cornerRadius - 8
        color: appRoot.isDark ? "#16FFB33D" : "#10FFB33D"
        opacity: root.workspaceSwitchAuraOpacity
        visible: opacity > 0.01
    }

    Item {
        anchors.fill: parent
        opacity: root.revealOpacity
        scale: root.revealScale
        transform: Translate { x: root.revealShift }

        Item {
            anchors.fill: parent
            opacity: root.workspaceSwitchOpacity
            scale: root.workspaceSwitchScale
            transform: Translate { x: root.workspaceSwitchShift }

            Rectangle {
                width: parent.width * 0.30
                height: parent.height
                radius: root.cornerRadius - 8
                x: root.workspaceSwitchSweepX * parent.width
                color: appRoot.isDark ? "#18FFF0D1" : "#12FFFFFF"
                opacity: root.workspaceSwitchSweepOpacity
                rotation: 7
                visible: opacity > 0.01
            }

            MainWorkspaceStack {
                anchors.fill: parent
                appRoot: root.appRoot
            }
        }
    }

    SequentialAnimation {
        id: chatPageReveal

        ParallelAnimation {
            NumberAnimation {
                target: root
                property: "revealOpacity"
                to: 1.0
                duration: appRoot.design.motionUi
                easing.type: appRoot.design.easeStandard
            }
            NumberAnimation {
                target: root
                property: "revealScale"
                to: 1.0
                duration: appRoot.design.motionPanel
                easing.type: appRoot.design.easeEmphasis
            }
            NumberAnimation {
                target: root
                property: "revealShift"
                to: 0.0
                duration: appRoot.design.motionPanel
                easing.type: appRoot.design.easeEmphasis
            }
            NumberAnimation {
                target: root
                property: "revealAuraOpacity"
                to: 0.0
                duration: appRoot.design.motionPanel
                easing.type: appRoot.design.easeStandard
            }
        }
    }

    SequentialAnimation {
        id: setupCompletionReveal

        ParallelAnimation {
            NumberAnimation {
                target: root
                property: "completionFlashOpacity"
                to: 0.0
                duration: appRoot.design.motionAmbient
                easing.type: appRoot.design.easeStandard
            }
            NumberAnimation {
                target: root
                property: "completionFlashScale"
                to: 1.02
                duration: appRoot.design.motionUi
                easing.type: appRoot.design.easeEmphasis
            }
        }

        NumberAnimation {
            target: root
            property: "completionFlashScale"
            to: 1.0
            duration: appRoot.design.motionPanel
            easing.type: appRoot.design.easeSoft
        }
    }

    SequentialAnimation {
        id: workspaceSwitchReveal

        ParallelAnimation {
            NumberAnimation {
                target: root
                property: "workspaceSwitchOpacity"
                to: 1.0
                duration: appRoot.design.motionUi
                easing.type: appRoot.design.easeStandard
            }
            NumberAnimation {
                target: root
                property: "workspaceSwitchScale"
                to: 1.0
                duration: appRoot.design.motionPanel
                easing.type: appRoot.design.easeEmphasis
            }
            NumberAnimation {
                target: root
                property: "workspaceSwitchShift"
                to: 0.0
                duration: appRoot.design.motionPanel
                easing.type: appRoot.design.easeEmphasis
            }
            NumberAnimation {
                target: root
                property: "workspaceSwitchAuraOpacity"
                to: 0.0
                duration: appRoot.design.motionPanel
                easing.type: appRoot.design.easeStandard
            }
            NumberAnimation {
                target: root
                property: "workspaceSwitchSweepOpacity"
                to: 0.0
                duration: appRoot.design.motionUi
                easing.type: appRoot.design.easeStandard
            }
            NumberAnimation {
                target: root
                property: "workspaceSwitchSweepX"
                to: 0.82
                duration: appRoot.design.motionPanel
                easing.type: appRoot.design.easeEmphasis
            }
        }
    }
}
