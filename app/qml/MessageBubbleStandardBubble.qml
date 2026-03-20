import QtQuick 2.15
import "MessageBubbleLogic.js" as Logic

Item {
    id: panel

    required property var workspaceRoot

    visible: !workspaceRoot.isSystem
    anchors.top: parent.top
    anchors.left: parent.left
    anchors.right: parent.right
    implicitHeight: workspaceRoot.dividerBlockHeight + bubble.height + 5
    Component.onCompleted: workspaceRoot.standardBubbleRef = panel
    function resetFeedbackSheen(sheen) {
        sheen.opacity = 0.0
        sheen.progress = workspaceRoot.feedbackProgressStart
    }
    function resetFeedbackRipple(ripple) {
        ripple.opacity = 0.0
        ripple.scale = 0.92
    }
    function resetCopyFeedback() {
        copyFlash.opacity = 0.0
        resetFeedbackRipple(copyRipple)
        resetFeedbackSheen(copySheen)
    }
    function playCopyFeedback() {
        if (!workspaceRoot.canCopyFeedback)
            return
        resetCopyFeedback()
        copyFeedbackAnim.restart()
    }
    function playEntrance() {
        enterTranslate.x = workspaceRoot.entranceStartX
        enterTranslate.y = workspaceRoot.entranceStartY
        bubble.scale = workspaceRoot.entranceStartScale
        bubbleEntranceGlow.scale = workspaceRoot.bubbleEntranceGlowStartScale
        entranceAnim.restart()
    }
    Rectangle {
        id: bubbleEntranceGlow
        objectName: "bubbleEntranceGlow"
        anchors.fill: bubble
        anchors.margins: -6
        radius: bubble.radius + 6
        color: workspaceRoot.bubbleEntranceGlowColor
        opacity: 0.0
        scale: 0.96
        z: -1
    }

    Rectangle {
        id: bubble
        objectName: "bubbleBody"
        anchors.right: workspaceRoot.isUser ? parent.right : undefined
        anchors.left: workspaceRoot.isUser ? undefined : parent.left
        anchors.rightMargin: workspaceRoot.isUser ? 20 : 0
        anchors.leftMargin: workspaceRoot.isUser ? 0 : 20
        anchors.top: parent.top
        anchors.topMargin: workspaceRoot.dividerBlockHeight + 5
        property bool isTyping: workspaceRoot.isTypingBubble
        width: isTyping ? 72 : Math.min(Math.ceil(bubbleContent.implicitWidth) + (workspaceRoot.bubblePaddingX * 2), workspaceRoot.bubbleMaxWidth)
        height: isTyping ? 42 : bubbleContent.implicitHeight + workspaceRoot.bubblePaddingTop + workspaceRoot.bubblePaddingBottom
        radius: workspaceRoot.uiSizeBubbleRadius
        clip: true
        opacity: workspaceRoot.shouldAnimateEntrance && !workspaceRoot._entranceStarted ? 0.0 : 1.0
        scale: workspaceRoot.shouldAnimateEntrance && !workspaceRoot._entranceStarted ? workspaceRoot.entranceStartScale : 1.0
        transformOrigin: Item.Center
        transform: Translate { id: enterTranslate; objectName: "bubbleEntranceShift"; x: 0; y: 0 }
        color: workspaceRoot.isUser ? (clickArea.containsMouse ? workspaceRoot.uiAccentHover : workspaceRoot.uiAccent) : (clickArea.containsMouse ? workspaceRoot.uiBgCardHover : workspaceRoot.uiBgCard)
        border.color: workspaceRoot.isUser ? "transparent" : workspaceRoot.uiBorderSubtle
        border.width: workspaceRoot.isUser ? 0 : 1
        Behavior on color { ColorAnimation { duration: workspaceRoot.uiMotionFast; easing.type: workspaceRoot.uiEaseStandard } }
        MouseArea {
            id: clickArea
            anchors.fill: parent
            hoverEnabled: true
            preventStealing: true
            cursorShape: Qt.PointingHandCursor
            onClicked: function(mouse) {
                if (bubble.isTyping || workspaceRoot.content === "")
                    return
                if (workspaceRoot.isMarkdown) {
                    var localPt = clickArea.mapToItem(contentText, mouse.x, mouse.y)
                    var link = contentText.linkAt(localPt.x, localPt.y)
                    if (link) {
                        Qt.openUrlExternally(link)
                        return
                    }
                }
                workspaceRoot.copyCurrentMessage()
            }
        }
        Rectangle { id: copyFlash; objectName: "copyFlash"; anchors.fill: parent; radius: parent.radius; z: 1; color: workspaceRoot.copyFeedbackOverlayColor; opacity: 0.0 }
        Rectangle {
            id: copyRipple
            objectName: "copyRipple"
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
        Rectangle {
            id: copySheen
            objectName: "copySheen"
            visible: workspaceRoot.canCopyFeedback
            property real progress: workspaceRoot.feedbackProgressStart
            anchors.fill: parent
            radius: parent.radius
            color: "transparent"
            gradient: Gradient {
                GradientStop { position: 0.0; color: Logic.alphaColor(workspaceRoot.copyFeedbackSheenColor, 0.0) }
                GradientStop { position: workspaceRoot.clamp01(copySheen.progress - workspaceRoot.feedbackBandOuterOffset); color: Logic.alphaColor(workspaceRoot.copyFeedbackSheenColor, 0.0) }
                GradientStop { position: workspaceRoot.clamp01(copySheen.progress - workspaceRoot.feedbackBandInnerOffset); color: Logic.alphaColor(workspaceRoot.copyFeedbackSheenColor, 0.1) }
                GradientStop { position: workspaceRoot.clamp01(copySheen.progress); color: Logic.alphaColor(workspaceRoot.copyFeedbackSheenColor, 0.32) }
                GradientStop { position: workspaceRoot.clamp01(copySheen.progress + workspaceRoot.feedbackBandInnerOffset); color: Logic.alphaColor(workspaceRoot.copyFeedbackSheenColor, 0.12) }
                GradientStop { position: workspaceRoot.clamp01(copySheen.progress + workspaceRoot.feedbackBandOuterOffset); color: Logic.alphaColor(workspaceRoot.copyFeedbackSheenColor, 0.0) }
                GradientStop { position: 1.0; color: Logic.alphaColor(workspaceRoot.copyFeedbackSheenColor, 0.0) }
            }
            opacity: 0.0
        }
        ParallelAnimation {
            id: entranceAnim
            NumberAnimation { target: bubble; property: "opacity"; from: 0.0; to: 1.0; duration: workspaceRoot.entranceOpacityDuration; easing.type: workspaceRoot.uiEaseStandard }
            SequentialAnimation {
                NumberAnimation { target: bubble; property: "scale"; from: workspaceRoot.entranceStartScale; to: workspaceRoot.entrancePeakScale; duration: workspaceRoot.entranceMoveDuration; easing.type: workspaceRoot.uiEaseEmphasis }
                NumberAnimation { target: bubble; property: "scale"; to: 1.0; duration: workspaceRoot.entranceSettleDuration; easing.type: workspaceRoot.uiEaseSoft }
            }
            SequentialAnimation {
                NumberAnimation { target: enterTranslate; property: "x"; from: workspaceRoot.entranceStartX; to: workspaceRoot.entranceSettleX; duration: workspaceRoot.entranceMoveDuration; easing.type: workspaceRoot.uiEaseEmphasis }
                NumberAnimation { target: enterTranslate; property: "x"; to: 0; duration: workspaceRoot.entranceSettleDuration; easing.type: workspaceRoot.uiEaseSoft }
            }
            SequentialAnimation {
                NumberAnimation { target: enterTranslate; property: "y"; from: workspaceRoot.entranceStartY; to: workspaceRoot.entranceSettleY; duration: workspaceRoot.entranceMoveDuration; easing.type: workspaceRoot.uiEaseEmphasis }
                NumberAnimation { target: enterTranslate; property: "y"; to: 0; duration: workspaceRoot.entranceSettleDuration; easing.type: workspaceRoot.uiEaseSoft }
            }
            SequentialAnimation {
                NumberAnimation { target: bubbleEntranceGlow; property: "opacity"; from: 0.0; to: workspaceRoot.bubbleEntranceGlowPeak; duration: workspaceRoot.uiMotionUi; easing.type: workspaceRoot.uiEaseStandard }
                NumberAnimation { target: bubbleEntranceGlow; property: "opacity"; to: 0.0; duration: workspaceRoot.entranceGlowFadeDuration; easing.type: workspaceRoot.uiEaseSoft }
            }
            SequentialAnimation {
                NumberAnimation { target: bubbleEntranceGlow; property: "scale"; from: workspaceRoot.bubbleEntranceGlowStartScale; to: workspaceRoot.bubbleEntranceGlowPeakScale; duration: workspaceRoot.entranceMoveDuration; easing.type: workspaceRoot.uiEaseEmphasis }
                NumberAnimation { target: bubbleEntranceGlow; property: "scale"; to: 1.0; duration: workspaceRoot.entranceSettleDuration; easing.type: workspaceRoot.uiEaseSoft }
            }
        }
        Item {
            id: bubbleContent
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.topMargin: workspaceRoot.bubblePaddingTop
            anchors.leftMargin: workspaceRoot.bubblePaddingX
            anchors.rightMargin: workspaceRoot.bubblePaddingX
            implicitWidth: Math.max(contentText.implicitWidth, attachmentStrip.width, referenceText.implicitWidth)
            implicitHeight: contentColumn.implicitHeight
            Column {
                id: contentColumn
                width: parent.width
                spacing: workspaceRoot.contentColumnSpacing
                Text {
                    id: contentText
                    objectName: "contentText"
                    width: parent.width
                    text: workspaceRoot.content
                    visible: workspaceRoot.showsContentBody || opacity > 0.01
                    color: workspaceRoot.isUser ? "#FFFFFF" : workspaceRoot.uiTextPrimary
                    font.pixelSize: workspaceRoot.uiTypeBody
                    wrapMode: Text.Wrap
                    textFormat: workspaceRoot.isMarkdown ? Text.MarkdownText : Text.PlainText
                    lineHeight: workspaceRoot.uiLineHeightBody
                    opacity: workspaceRoot.showsContentBody ? 1.0 : 0.0
                    y: workspaceRoot.contentMorphOffsetY
                    scale: workspaceRoot.contentMorphScale
                    transformOrigin: Item.Center
                    Behavior on opacity { NumberAnimation { duration: workspaceRoot.contentMorphDuration; easing.type: workspaceRoot.uiEaseStandard } }
                    Behavior on y { NumberAnimation { duration: workspaceRoot.contentMorphDuration; easing.type: workspaceRoot.uiEaseSoft } }
                    Behavior on scale { NumberAnimation { duration: workspaceRoot.contentMorphDuration; easing.type: workspaceRoot.uiEaseSoft } }
                }
                Flickable {
                    id: attachmentStrip
                    objectName: "attachmentStrip"
                    width: workspaceRoot.bubbleAttachmentViewportWidth
                    height: workspaceRoot.hasAttachments ? 56 : 0
                    visible: workspaceRoot.hasAttachments
                    contentWidth: attachmentRow.implicitWidth
                    contentHeight: attachmentRow.implicitHeight
                    clip: true
                    boundsBehavior: Flickable.StopAtBounds
                    interactive: contentWidth > width
                    Row {
                        id: attachmentRow
                        spacing: 8
                        Repeater {
                            model: workspaceRoot.attachments
                            delegate: AttachmentChip {
                                fileName: modelData.fileName ?? ""
                                fileSizeLabel: modelData.fileSizeLabel ?? ""
                                previewUrl: modelData.previewUrl ?? ""
                                isImage: Boolean(modelData.isImage)
                                extensionLabel: modelData.extensionLabel ?? "FILE"
                                openOnClick: true
                            }
                        }
                    }
                }
                Text {
                    id: referenceText
                    objectName: "referenceText"
                    width: parent.width
                    visible: workspaceRoot.showsReferenceSummary
                    text: workspaceRoot.referenceSummaryText
                    color: workspaceRoot.uiTextSecondary
                    font.pixelSize: workspaceRoot.uiTypeMeta
                    wrapMode: Text.Wrap
                    opacity: 0.84
                }
            }
        }
        Item {
            id: typingIndicator
            objectName: "typingIndicator"
            anchors.centerIn: parent
            visible: workspaceRoot.showsTypingIndicator || opacity > 0.01
            width: 32
            height: 10
            opacity: workspaceRoot.showsTypingIndicator ? 1.0 : 0.0
            y: workspaceRoot.typingMorphOffsetY
            scale: workspaceRoot.typingMorphScale
            transformOrigin: Item.Center
            Behavior on opacity { NumberAnimation { duration: workspaceRoot.typingMorphDuration; easing.type: workspaceRoot.uiEaseStandard } }
            Behavior on y { NumberAnimation { duration: workspaceRoot.typingMorphDuration; easing.type: workspaceRoot.uiEaseSoft } }
            Behavior on scale { NumberAnimation { duration: workspaceRoot.typingMorphDuration; easing.type: workspaceRoot.uiEaseSoft } }
            Row {
                anchors.centerIn: parent
                spacing: 5
                Repeater {
                    model: 3
                    delegate: Rectangle {
                        width: 6
                        height: 6
                        radius: 3
                        color: workspaceRoot.isUser ? "#FFFFFF" : workspaceRoot.uiTextSecondary
                        opacity: workspaceRoot.uiMotionTypingPulseMinOpacity
                        SequentialAnimation on opacity {
                            running: workspaceRoot.showsTypingIndicator
                            loops: Animation.Infinite
                            PauseAnimation { duration: index * 120 }
                            NumberAnimation { to: 1.0; duration: workspaceRoot.uiMotionUi; easing.type: workspaceRoot.uiEaseStandard }
                            NumberAnimation { to: workspaceRoot.uiMotionTypingPulseMinOpacity; duration: workspaceRoot.uiMotionUi; easing.type: workspaceRoot.uiEaseStandard }
                            PauseAnimation { duration: workspaceRoot.uiMotionUi }
                        }
                    }
                }
            }
        }
        Rectangle {
            id: pendingOverlay
            objectName: "pendingOverlay"
            anchors.fill: parent
            radius: parent.radius
            color: workspaceRoot.pendingSurfaceMotion.color
            visible: workspaceRoot.isPending || opacity > 0.01
            opacity: workspaceRoot.pendingSurfaceMotion.opacity
            scale: workspaceRoot.pendingSurfaceMotion.scale
            transformOrigin: Item.Center
            Behavior on opacity { NumberAnimation { duration: workspaceRoot.pendingSurfaceMotion.duration; easing.type: workspaceRoot.uiEaseSoft } }
            Behavior on scale { NumberAnimation { duration: workspaceRoot.pendingSurfaceMotion.duration; easing.type: workspaceRoot.uiEaseSoft } }
        }
        Rectangle {
            anchors.fill: parent
            radius: parent.radius
            color: workspaceRoot.uiChatBubbleErrorTint
            visible: workspaceRoot.status === "error"
        }
    }
    ParallelAnimation {
        id: copyFeedbackAnim
        SequentialAnimation { NumberAnimation { target: copyFlash; property: "opacity"; from: 0.0; to: workspaceRoot.copyFeedbackOverlayPeak; duration: workspaceRoot.uiMotionMicro; easing.type: workspaceRoot.uiEaseStandard } NumberAnimation { target: copyFlash; property: "opacity"; to: 0.0; duration: workspaceRoot.uiMotionUi; easing.type: workspaceRoot.uiEaseSoft } }
        SequentialAnimation { NumberAnimation { target: copyRipple; property: "opacity"; from: 0.0; to: 0.24; duration: workspaceRoot.uiMotionFast; easing.type: workspaceRoot.uiEaseStandard } NumberAnimation { target: copyRipple; property: "opacity"; to: 0.0; duration: workspaceRoot.uiMotionPanel; easing.type: workspaceRoot.uiEaseSoft } }
        NumberAnimation { target: copyRipple; property: "scale"; from: 0.92; to: 1.02; duration: workspaceRoot.uiMotionPanel; easing.type: workspaceRoot.uiEaseEmphasis }
        SequentialAnimation { NumberAnimation { target: copySheen; property: "opacity"; from: 0.0; to: workspaceRoot.copyFeedbackSheenPeak; duration: workspaceRoot.uiMotionFast; easing.type: workspaceRoot.uiEaseStandard } PauseAnimation { duration: workspaceRoot.uiMotionMicro } NumberAnimation { target: copySheen; property: "opacity"; to: 0.0; duration: workspaceRoot.uiMotionPanel; easing.type: workspaceRoot.uiEaseSoft } }
        NumberAnimation { target: copySheen; property: "progress"; from: workspaceRoot.feedbackProgressStart; to: workspaceRoot.feedbackProgressEnd; duration: workspaceRoot.uiMotionAmbient + 100; easing.type: workspaceRoot.uiEaseSoft }
    }
}
