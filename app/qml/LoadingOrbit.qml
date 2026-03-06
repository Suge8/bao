pragma ComponentBehavior: Bound

import QtQuick 2.15

Item {
    id: root
    property bool running: true
    property color color: "#FFB33D"
    property color secondaryColor: "#34FFB33D"
    property color haloColor: "#A8FFB33D"
    property real haloOpacity: 0.18
    property bool showCore: root.width >= 18 && root.height >= 18

    width: 40
    height: 40
    opacity: root.running ? 1.0 : 0.0

    readonly property real loaderSize: Math.min(root.width, root.height)
    readonly property real orbitRadius: Math.max(3, root.loaderSize * 0.26)
    readonly property real dotSize: Math.max(4, root.loaderSize * 0.16)
    readonly property real coreSize: Math.max(3, root.loaderSize * 0.18)
    readonly property real orbitOpacityValue: 0.96
    readonly property real coreOpacityValue: 0.34
    readonly property bool hasHalo: root.haloOpacity > 0.0
    readonly property bool haloActive: root.running && root.hasHalo
    readonly property bool coreActive: root.running && root.showCore
    readonly property bool orbitActive: root.running
    readonly property int motionMicroMs: typeof motionMicro === "number" ? motionMicro : 120
    readonly property int motionFastMs: typeof motionFast === "number" ? motionFast : 180
    readonly property int motionUiMs: typeof motionUi === "number" ? motionUi : 220
    readonly property int motionAmbientMs: typeof motionAmbient === "number" ? motionAmbient : 500
    readonly property int motionFloatMs: typeof motionFloat === "number" ? motionFloat : 1700
    readonly property int motionPanelMs: typeof motionPanel === "number" ? motionPanel : 320
    readonly property int motionStaggerMs: typeof motionStagger === "number" ? motionStagger : 80
    readonly property int easeStandardType: typeof easeStandard === "number" ? easeStandard : Easing.OutCubic
    readonly property int easeEmphasisType: typeof easeEmphasis === "number" ? easeEmphasis : Easing.OutBack
    readonly property int easeSoftType: typeof easeSoft === "number" ? easeSoft : Easing.InOutSine
    readonly property int easeLinearType: typeof easeLinear === "number" ? easeLinear : Easing.Linear

    Behavior on opacity { NumberAnimation { duration: root.motionFastMs; easing.type: root.easeStandardType } }

    Rectangle {
        id: halo
        anchors.centerIn: parent
        width: root.loaderSize * 0.76
        height: halo.width
        radius: halo.width / 2
        color: root.haloColor
        opacity: root.haloActive ? root.haloOpacity : 0.0
        scale: 0.9

        SequentialAnimation on opacity {
            running: root.haloActive
            loops: Animation.Infinite
            NumberAnimation { from: root.haloOpacity * 0.45; to: root.haloOpacity; duration: root.motionAmbientMs; easing.type: root.easeSoftType }
            NumberAnimation { from: root.haloOpacity; to: root.haloOpacity * 0.45; duration: root.motionAmbientMs; easing.type: root.easeSoftType }
        }

        SequentialAnimation on scale {
            running: root.haloActive
            loops: Animation.Infinite
            NumberAnimation { from: 0.88; to: 1.04; duration: root.motionAmbientMs; easing.type: root.easeEmphasisType }
            NumberAnimation { from: 1.04; to: 0.88; duration: root.motionAmbientMs; easing.type: root.easeSoftType }
        }
    }

    Rectangle {
        id: core
        anchors.centerIn: parent
        width: root.coreSize
        height: core.width
        radius: core.width / 2
        color: root.color
        opacity: root.coreActive ? root.coreOpacityValue : 0.0
        scale: 0.92

        SequentialAnimation on opacity {
            running: root.coreActive
            loops: Animation.Infinite
            NumberAnimation { from: root.coreOpacityValue * 0.7; to: root.coreOpacityValue; duration: root.motionAmbientMs; easing.type: root.easeSoftType }
            NumberAnimation { from: root.coreOpacityValue; to: root.coreOpacityValue * 0.7; duration: root.motionAmbientMs; easing.type: root.easeSoftType }
        }

        SequentialAnimation on scale {
            running: root.coreActive
            loops: Animation.Infinite
            NumberAnimation { from: 0.9; to: 1.06; duration: root.motionAmbientMs; easing.type: root.easeEmphasisType }
            NumberAnimation { from: 1.06; to: 0.9; duration: root.motionAmbientMs; easing.type: root.easeSoftType }
        }
    }

    Item {
        id: orbit
        anchors.fill: parent
        rotation: 0

        NumberAnimation on rotation {
            running: root.orbitActive
            from: 0
            to: 360
            duration: root.motionFloatMs + root.motionPanelMs
            loops: Animation.Infinite
            easing.type: root.easeLinearType
        }

        Repeater {
            model: 3

            delegate: Item {
                required property int index
                id: orbitSlot
                width: orbit.width
                height: orbit.height
                rotation: orbitSlot.index * 120

                Rectangle {
                    id: orbitDot
                    width: root.dotSize
                    height: orbitDot.width
                    radius: orbitDot.width / 2
                    x: (orbitSlot.width - orbitDot.width) / 2
                    y: orbitSlot.height / 2 - root.orbitRadius - orbitDot.height / 2
                    color: orbitSlot.index === 1 ? root.secondaryColor : root.color
                    opacity: root.orbitOpacityValue
                    scale: 0.82

                    SequentialAnimation on opacity {
                        running: root.orbitActive
                        loops: Animation.Infinite
                        PauseAnimation { duration: orbitSlot.index * root.motionStaggerMs }
                        NumberAnimation { from: root.orbitOpacityValue * 0.46; to: root.orbitOpacityValue; duration: root.motionUiMs; easing.type: root.easeStandardType }
                        NumberAnimation { from: root.orbitOpacityValue; to: root.orbitOpacityValue * 0.46; duration: root.motionUiMs; easing.type: root.easeSoftType }
                        PauseAnimation { duration: root.motionMicroMs + orbitSlot.index * 20 }
                    }

                    SequentialAnimation on scale {
                        running: root.orbitActive
                        loops: Animation.Infinite
                        PauseAnimation { duration: orbitSlot.index * root.motionStaggerMs }
                        NumberAnimation { from: 0.8; to: 1.0; duration: root.motionUiMs; easing.type: root.easeEmphasisType }
                        NumberAnimation { from: 1.0; to: 0.8; duration: root.motionUiMs; easing.type: root.easeSoftType }
                        PauseAnimation { duration: root.motionMicroMs + orbitSlot.index * 20 }
                    }
                }
            }
        }
    }
}
