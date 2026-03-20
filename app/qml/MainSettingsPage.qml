import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    required property var appRoot
    required property real cornerRadius

    property bool active: appRoot.showingSettings
    property bool preloadReady: false
    property real revealOpacity: 1.0
    property real revealScale: 1.0
    property real revealShift: 0.0
    property real revealAuraOpacity: 0.0

    function playReveal(direction, distance) {
        revealOpacity = appRoot.design.motionPageRevealStartOpacity
        revealScale = appRoot.design.motionPageRevealStartScale
        revealShift = direction * distance
        revealAuraOpacity = appRoot.design.motionPageAuraPeak
        settingsPageReveal.restart()
    }

    onActiveChanged: {
        if (active)
            playReveal(1, appRoot.design.motionPageShift)
    }

    Component.onCompleted: {
        Qt.callLater(function() {
            if (!root.active)
                root.preloadReady = true
        })
    }

    Rectangle {
        anchors.fill: parent
        anchors.margins: 8
        radius: root.cornerRadius - 8
        color: appRoot.isDark ? "#12FFFFFF" : "#10FFFFFF"
        opacity: root.revealAuraOpacity
        visible: opacity > 0.01
    }

    Component {
        id: settingsViewComponent

        SettingsView {
            objectName: "settingsView"
            appRoot: root.appRoot
            onboardingMode: root.appRoot.setupMode
            configService: root.appRoot.configService
            updateService: root.appRoot.updateService
            updateBridge: root.appRoot.updateBridge
            desktopPreferences: root.appRoot.desktopPreferences
        }
    }

    Loader {
        id: settingsPageLoader
        anchors.fill: parent
        active: root.active || root.preloadReady
        opacity: root.revealOpacity
        scale: root.revealScale
        transform: Translate { x: root.revealShift }
        sourceComponent: settingsViewComponent
    }

    SequentialAnimation {
        id: settingsPageReveal

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
}
