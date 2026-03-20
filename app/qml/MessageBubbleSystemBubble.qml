import QtQuick 2.15
import "MessageBubbleLogic.js" as Logic

Item {
    id: panel

    required property var workspaceRoot

    visible: workspaceRoot.isSystem
    anchors.top: parent.top
    anchors.left: parent.left
    anchors.right: parent.right
    implicitHeight: workspaceRoot.dividerBlockHeight + systemBubble.height + 7
    Component.onCompleted: workspaceRoot.systemBubbleRef = panel

    function resetFeedbackSheen(sheen) {
        sheen.opacity = 0.0
        sheen.progress = workspaceRoot.feedbackProgressStart
    }

    function resetFeedbackRipple(ripple) {
        ripple.opacity = 0.0
        ripple.scale = 0.92
    }

    function resetCopyFeedback() {
        systemCopyFlash.opacity = 0.0
        resetFeedbackRipple(systemCopyRipple)
        resetFeedbackSheen(systemCopySheen)
    }

    function playCopyFeedback() {
        if (!workspaceRoot.canCopyFeedback)
            return
        resetCopyFeedback()
        copyFeedbackAnim.restart()
    }

    function playEntrance() {
        systemAuraNear.opacity = 0.0
        systemAuraFar.opacity = 0.0
        resetFeedbackSheen(greetingSweep)
        systemShift.y = workspaceRoot.entranceStartY
        systemBubble.scale = workspaceRoot.entranceStartScale
        systemEntranceAnim.restart()
    }

    Rectangle {
        id: systemAuraFar
        visible: workspaceRoot.isSystemError
        anchors.fill: systemBubble
        anchors.leftMargin: -12
        anchors.rightMargin: -12
        anchors.topMargin: -12
        anchors.bottomMargin: -12
        radius: systemBubble.radius + (workspaceRoot.isGreeting ? 10 : 12)
        color: workspaceRoot.systemAuraFarColor
        opacity: 0.0
    }

    Rectangle {
        id: systemAuraNear
        objectName: "systemAuraNear"
        visible: workspaceRoot.isSystem
        anchors.fill: systemBubble
        radius: systemBubble.radius
        color: workspaceRoot.systemAuraNearColor
        opacity: 0.0
    }

    Rectangle {
        id: systemBubble
        objectName: "systemBubble"
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: workspaceRoot.dividerBlockHeight + (workspaceRoot.isGreeting ? 8 : 7)
        width: workspaceRoot.isGreeting
            ? Math.max(228, Math.min(workspaceRoot.width * 0.64, systemText.implicitWidth + workspaceRoot.systemTextStartX + workspaceRoot.systemContentPaddingX + 2))
            : Math.max(98, Math.min(workspaceRoot.width * 0.9, systemText.implicitWidth + workspaceRoot.systemTextStartX + workspaceRoot.systemContentPaddingX))
        height: Math.max(systemText.contentHeight, workspaceRoot.systemIconSize) + (workspaceRoot.systemContentPaddingY * 2)
        radius: workspaceRoot.isGreeting ? height / 2 : workspaceRoot.uiSizeSystemBubbleRadius
        color: workspaceRoot.systemBubbleFillColor
        border.width: 1
        border.color: workspaceRoot.systemBubbleBorderColor
        clip: true
        opacity: workspaceRoot.shouldAnimateEntrance && !workspaceRoot._entranceStarted ? 0.0 : 1.0
        scale: workspaceRoot.shouldAnimateEntrance && !workspaceRoot._entranceStarted ? workspaceRoot.entranceStartScale : 1.0
        transformOrigin: Item.Center
        transform: Translate { id: systemShift; y: 0 }

        Behavior on color { ColorAnimation { duration: workspaceRoot.uiMotionUi; easing.type: workspaceRoot.uiEaseStandard } }
        Behavior on border.color { ColorAnimation { duration: workspaceRoot.uiMotionUi; easing.type: workspaceRoot.uiEaseStandard } }

        Rectangle { anchors.fill: parent; radius: parent.radius; color: workspaceRoot.systemOverlayColor }

        Rectangle {
            objectName: "greetingGradient"
            anchors.fill: parent
            radius: parent.radius
            visible: workspaceRoot.useGreetingGradient
            gradient: Gradient {
                GradientStop { position: 0.0; color: workspaceRoot.uiChatGreetingBubbleBgStart }
                GradientStop { position: 1.0; color: workspaceRoot.uiChatGreetingBubbleBgEnd }
            }
            opacity: 0.92
        }

        Rectangle { id: systemCopyFlash; objectName: "systemCopyFlash"; anchors.fill: parent; radius: parent.radius; color: workspaceRoot.copyFeedbackOverlayColor; opacity: 0.0 }
        Rectangle {
            id: systemCopyRipple
            objectName: "systemCopyRipple"
            anchors.fill: parent
            anchors.margins: 2
            radius: Math.max(1, parent.radius - 2)
            color: "transparent"
            border.width: 1
            border.color: Logic.alphaColor(workspaceRoot.copyFeedbackSheenColor, 0.52)
            opacity: 0.0
            scale: 0.92
            transformOrigin: Item.Center
        }

        Item {
            width: workspaceRoot.systemIconSlotWidth
            height: workspaceRoot.systemIconSize
            anchors.left: parent.left
            anchors.leftMargin: workspaceRoot.systemContentPaddingX
            anchors.verticalCenter: parent.verticalCenter

            Item {
                anchors.centerIn: parent
                width: workspaceRoot.systemIconSize
                height: workspaceRoot.systemIconSize

                Image {
                    objectName: "greetingIcon"
                    visible: workspaceRoot.isGreeting
                    anchors.centerIn: parent
                    width: workspaceRoot.systemIconSize
                    height: workspaceRoot.systemIconSize
                    source: workspaceRoot.uiChatGreetingIconSource
                    sourceSize: Qt.size(workspaceRoot.systemIconSize, workspaceRoot.systemIconSize)
                    fillMode: Image.PreserveAspectFit
                    smooth: true
                }

                Repeater {
                    model: workspaceRoot.isGreeting ? [] : [
                        { "margin": 0, "width": parent.width, "opacity": 1.0 },
                        { "margin": 4, "width": Math.max(4, parent.width - 3), "opacity": 0.9 },
                        { "margin": 8, "width": Math.max(6, parent.width - 1), "opacity": 0.78 }
                    ]

                    delegate: Rectangle {
                        required property var modelData
                        anchors.top: parent.top
                        anchors.topMargin: modelData.margin
                        anchors.left: parent.left
                        width: modelData.width
                        height: 2
                        radius: 1
                        color: workspaceRoot.systemIconColor
                        opacity: modelData.opacity
                    }
                }
            }
        }

        Rectangle {
            id: greetingSweep
            objectName: "greetingSweep"
            visible: workspaceRoot.useGreetingGradient
            property real progress: workspaceRoot.feedbackProgressStart
            anchors.fill: parent
            radius: parent.radius
            color: "transparent"
            gradient: Gradient {
                GradientStop { position: 0.0; color: Logic.alphaColor(workspaceRoot.uiChatGreetingSweep, 0.0) }
                GradientStop { position: workspaceRoot.clamp01(greetingSweep.progress - workspaceRoot.feedbackBandOuterOffset); color: Logic.alphaColor(workspaceRoot.uiChatGreetingSweep, 0.0) }
                GradientStop { position: workspaceRoot.clamp01(greetingSweep.progress - workspaceRoot.feedbackBandInnerOffset); color: Logic.alphaColor(workspaceRoot.uiChatGreetingSweep, 0.08) }
                GradientStop { position: workspaceRoot.clamp01(greetingSweep.progress); color: Logic.alphaColor(workspaceRoot.uiChatGreetingSweep, 0.28) }
                GradientStop { position: workspaceRoot.clamp01(greetingSweep.progress + workspaceRoot.feedbackBandInnerOffset); color: Logic.alphaColor(workspaceRoot.uiChatGreetingSweep, 0.1) }
                GradientStop { position: workspaceRoot.clamp01(greetingSweep.progress + workspaceRoot.feedbackBandOuterOffset); color: Logic.alphaColor(workspaceRoot.uiChatGreetingSweep, 0.0) }
                GradientStop { position: 1.0; color: Logic.alphaColor(workspaceRoot.uiChatGreetingSweep, 0.0) }
            }
            opacity: 0.0
        }

        Rectangle {
            id: systemCopySheen
            objectName: "systemCopySheen"
            visible: workspaceRoot.canCopyFeedback
            property real progress: workspaceRoot.feedbackProgressStart
            anchors.fill: parent
            radius: parent.radius
            color: "transparent"
            gradient: Gradient {
                GradientStop { position: 0.0; color: Logic.alphaColor(workspaceRoot.copyFeedbackSheenColor, 0.0) }
                GradientStop { position: workspaceRoot.clamp01(systemCopySheen.progress - workspaceRoot.feedbackBandOuterOffset); color: Logic.alphaColor(workspaceRoot.copyFeedbackSheenColor, 0.0) }
                GradientStop { position: workspaceRoot.clamp01(systemCopySheen.progress - workspaceRoot.feedbackBandInnerOffset); color: Logic.alphaColor(workspaceRoot.copyFeedbackSheenColor, 0.1) }
                GradientStop { position: workspaceRoot.clamp01(systemCopySheen.progress); color: Logic.alphaColor(workspaceRoot.copyFeedbackSheenColor, 0.32) }
                GradientStop { position: workspaceRoot.clamp01(systemCopySheen.progress + workspaceRoot.feedbackBandInnerOffset); color: Logic.alphaColor(workspaceRoot.copyFeedbackSheenColor, 0.12) }
                GradientStop { position: workspaceRoot.clamp01(systemCopySheen.progress + workspaceRoot.feedbackBandOuterOffset); color: Logic.alphaColor(workspaceRoot.copyFeedbackSheenColor, 0.0) }
                GradientStop { position: 1.0; color: Logic.alphaColor(workspaceRoot.copyFeedbackSheenColor, 0.0) }
            }
            opacity: 0.0
        }

        Text {
            id: systemText
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.leftMargin: workspaceRoot.systemTextStartX
            anchors.rightMargin: workspaceRoot.systemContentPaddingX
            anchors.verticalCenter: parent.verticalCenter
            text: workspaceRoot.content
            color: workspaceRoot.systemTextColor
            font.pixelSize: workspaceRoot.isGreeting ? Math.max(workspaceRoot.uiTypeMeta + 2, workspaceRoot.uiTypeBody - 1) : workspaceRoot.uiTypeMeta
            font.weight: workspaceRoot.isGreeting ? Font.DemiBold : workspaceRoot.uiWeightMedium
            font.letterSpacing: workspaceRoot.isGreeting ? 0.1 : workspaceRoot.uiLetterTight
            wrapMode: Text.Wrap
            horizontalAlignment: Text.AlignLeft
            verticalAlignment: Text.AlignVCenter
            lineHeight: workspaceRoot.isGreeting ? 1.2 : 1.35
            textFormat: Text.PlainText
        }

        MouseArea {
            id: systemClickArea
            anchors.fill: parent
            z: 10
            hoverEnabled: true
            preventStealing: true
            cursorShape: Qt.PointingHandCursor
            onClicked: workspaceRoot.copyCurrentMessage()
        }
    }

    ParallelAnimation {
        id: systemEntranceAnim
        NumberAnimation { target: systemBubble; property: "opacity"; from: 0.0; to: 1.0; duration: workspaceRoot.entranceOpacityDuration; easing.type: workspaceRoot.uiEaseStandard }
        SequentialAnimation {
            NumberAnimation { target: systemBubble; property: "scale"; from: workspaceRoot.entranceStartScale; to: workspaceRoot.entrancePeakScale; duration: workspaceRoot.entranceMoveDuration; easing.type: workspaceRoot.uiEaseEmphasis }
            NumberAnimation { target: systemBubble; property: "scale"; to: 1.0; duration: workspaceRoot.entranceSettleDuration; easing.type: workspaceRoot.uiEaseSoft }
        }
        SequentialAnimation {
            NumberAnimation { target: systemShift; property: "y"; from: workspaceRoot.entranceStartY; to: workspaceRoot.entranceSettleY; duration: workspaceRoot.entranceMoveDuration; easing.type: workspaceRoot.uiEaseEmphasis }
            NumberAnimation { target: systemShift; property: "y"; to: 0; duration: workspaceRoot.entranceSettleDuration; easing.type: workspaceRoot.uiEaseSoft }
        }
        SequentialAnimation {
            NumberAnimation { target: systemAuraNear; property: "opacity"; from: 0.0; to: workspaceRoot.isGreeting ? workspaceRoot.greetingAuraNearPeak * 0.72 : (workspaceRoot.isSystemError ? workspaceRoot.uiMotionAuraNearPeak * 0.78 : workspaceRoot.uiMotionAuraNearPeak * 0.46); duration: workspaceRoot.uiMotionUi; easing.type: workspaceRoot.uiEaseStandard }
            NumberAnimation { target: systemAuraNear; property: "opacity"; to: 0.0; duration: workspaceRoot.uiMotionAmbient; easing.type: workspaceRoot.uiEaseSoft }
        }
        SequentialAnimation {
            NumberAnimation { target: systemAuraFar; property: "opacity"; from: 0.0; to: workspaceRoot.isGreeting ? workspaceRoot.greetingAuraFarPeak * 0.92 : workspaceRoot.uiMotionAuraFarPeak * 0.8; duration: workspaceRoot.uiMotionUi; easing.type: workspaceRoot.uiEaseStandard }
            NumberAnimation { target: systemAuraFar; property: "opacity"; to: 0.0; duration: workspaceRoot.uiMotionAmbient + 120; easing.type: workspaceRoot.uiEaseSoft }
        }
        SequentialAnimation {
            NumberAnimation { target: greetingSweep; property: "opacity"; from: 0.0; to: workspaceRoot.uiMotionGreetingSweepPeak * 0.78; duration: workspaceRoot.uiMotionUi; easing.type: workspaceRoot.uiEaseStandard }
            PauseAnimation { duration: workspaceRoot.uiMotionFast }
            NumberAnimation { target: greetingSweep; property: "opacity"; to: 0.0; duration: workspaceRoot.uiMotionPanel; easing.type: workspaceRoot.uiEaseSoft }
        }
        NumberAnimation { target: greetingSweep; property: "progress"; from: workspaceRoot.feedbackProgressStart; to: workspaceRoot.feedbackProgressEnd; duration: workspaceRoot.uiMotionAmbient + 200; easing.type: workspaceRoot.uiEaseSoft }
    }

    ParallelAnimation {
        id: copyFeedbackAnim
        SequentialAnimation { NumberAnimation { target: systemCopyFlash; property: "opacity"; from: 0.0; to: workspaceRoot.copyFeedbackOverlayPeak; duration: workspaceRoot.uiMotionMicro; easing.type: workspaceRoot.uiEaseStandard } NumberAnimation { target: systemCopyFlash; property: "opacity"; to: 0.0; duration: workspaceRoot.uiMotionUi; easing.type: workspaceRoot.uiEaseSoft } }
        SequentialAnimation { NumberAnimation { target: systemCopyRipple; property: "opacity"; from: 0.0; to: 0.24; duration: workspaceRoot.uiMotionFast; easing.type: workspaceRoot.uiEaseStandard } NumberAnimation { target: systemCopyRipple; property: "opacity"; to: 0.0; duration: workspaceRoot.uiMotionPanel; easing.type: workspaceRoot.uiEaseSoft } }
        NumberAnimation { target: systemCopyRipple; property: "scale"; from: 0.92; to: 1.02; duration: workspaceRoot.uiMotionPanel; easing.type: workspaceRoot.uiEaseEmphasis }
        SequentialAnimation { NumberAnimation { target: systemCopySheen; property: "opacity"; from: 0.0; to: workspaceRoot.copyFeedbackSheenPeak; duration: workspaceRoot.uiMotionFast; easing.type: workspaceRoot.uiEaseStandard } PauseAnimation { duration: workspaceRoot.uiMotionMicro } NumberAnimation { target: systemCopySheen; property: "opacity"; to: 0.0; duration: workspaceRoot.uiMotionPanel; easing.type: workspaceRoot.uiEaseSoft } }
        NumberAnimation { target: systemCopySheen; property: "progress"; from: workspaceRoot.feedbackProgressStart; to: workspaceRoot.feedbackProgressEnd; duration: workspaceRoot.uiMotionAmbient + 100; easing.type: workspaceRoot.uiEaseSoft }
    }
}
