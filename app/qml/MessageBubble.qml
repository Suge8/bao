import QtQuick 2.15
import "MessageBubbleLogic.js" as Logic

Item {
    id: root

    property string role: "assistant"
    property string content: ""
    property string format: "plain"
    property string status: "done"
    property int messageId: -1
    property int messageRow: -1
    property string entranceStyle: "none"
    property bool entrancePending: false
    property bool showDateDivider: false
    property string dateDividerText: ""
    property var toastFunc: null
    property var attachments: []
    property var references: ({})
    property var systemBubbleRef: null
    property var standardBubbleRef: null

    readonly property string uiEffectiveLang: typeof effectiveLang === "string" ? effectiveLang : ""
    readonly property string uiLanguageCode: typeof uiLanguage === "string" ? uiLanguage : ""
    readonly property color uiAccent: accent
    readonly property color uiAccentGlow: accentGlow
    readonly property color uiAccentHover: accentHover
    readonly property color uiBgCard: bgCard
    readonly property color uiBgCardHover: bgCardHover
    readonly property color uiBorderSubtle: borderSubtle
    readonly property color uiStatusError: statusError
    readonly property color uiTextPrimary: textPrimary
    readonly property color uiTextSecondary: textSecondary
    readonly property int uiTypeBody: typeBody
    readonly property int uiTypeMeta: typeMeta
    readonly property real uiLineHeightBody: lineHeightBody
    readonly property real uiLetterTight: letterTight
    readonly property int uiWeightMedium: weightMedium
    readonly property int uiEaseStandard: easeStandard
    readonly property int uiEaseEmphasis: easeEmphasis
    readonly property int uiEaseSoft: easeSoft
    readonly property int uiMotionMicro: motionMicro
    readonly property int uiMotionFast: motionFast
    readonly property int uiMotionUi: motionUi
    readonly property int uiMotionPanel: motionPanel
    readonly property int uiMotionAmbient: motionAmbient
    readonly property real uiMotionCopyFlashPeak: motionCopyFlashPeak
    readonly property real uiMotionAuraNearPeak: motionAuraNearPeak
    readonly property real uiMotionAuraFarPeak: motionAuraFarPeak
    readonly property real uiMotionGreetingSweepPeak: motionGreetingSweepPeak
    readonly property real uiMotionTypingPulseMinOpacity: motionTypingPulseMinOpacity
    readonly property int uiMotionEnterOffsetY: motionEnterOffsetY
    readonly property int uiSizeBubbleRadius: sizeBubbleRadius
    readonly property int uiSizeSystemBubbleRadius: sizeSystemBubbleRadius
    readonly property color uiChatSystemAuraFar: chatSystemAuraFar
    readonly property color uiChatSystemAuraNear: chatSystemAuraNear
    readonly property color uiChatSystemAuraErrorFar: chatSystemAuraErrorFar
    readonly property color uiChatSystemAuraErrorNear: chatSystemAuraErrorNear
    readonly property color uiChatSystemBubbleBg: chatSystemBubbleBg
    readonly property color uiChatSystemBubbleBorder: chatSystemBubbleBorder
    readonly property color uiChatSystemBubbleErrorBg: chatSystemBubbleErrorBg
    readonly property color uiChatSystemBubbleErrorBorder: chatSystemBubbleErrorBorder
    readonly property color uiChatSystemBubbleOverlay: chatSystemBubbleOverlay
    readonly property color uiChatSystemBubbleErrorOverlay: chatSystemBubbleErrorOverlay
    readonly property color uiChatSystemText: chatSystemText
    readonly property color uiChatGreetingAuraFar: chatGreetingAuraFar
    readonly property color uiChatGreetingAuraNear: chatGreetingAuraNear
    readonly property color uiChatGreetingBubbleBgStart: chatGreetingBubbleBgStart
    readonly property color uiChatGreetingBubbleBgEnd: chatGreetingBubbleBgEnd
    readonly property color uiChatGreetingBubbleBorder: chatGreetingBubbleBorder
    readonly property color uiChatGreetingBubbleOverlay: chatGreetingBubbleOverlay
    readonly property color uiChatGreetingBubbleHighlight: chatGreetingBubbleHighlight
    readonly property color uiChatGreetingSweep: chatGreetingSweep
    readonly property color uiChatGreetingAccent: chatGreetingAccent
    readonly property color uiChatGreetingText: chatGreetingText
    readonly property string uiChatGreetingIconSource: chatGreetingIconSource
    readonly property color uiChatBubbleCopyFlashUser: chatBubbleCopyFlashUser
    readonly property color uiChatBubbleErrorTint: chatBubbleErrorTint

    property bool isGreeting: entranceStyle === "greeting"
    property bool isUser: role === "user"
    property bool isSystem: role === "system" || isGreeting
    property bool isSystemError: role === "system" && status === "error"
    property bool isPending: status === "pending"
    property bool isMarkdown: format === "markdown"
    property bool isTypingBubble: status === "typing" && content === ""
    property bool isAssistantEntrance: !isSystem && entranceStyle === "assistantReceived"
    property bool isUserEntrance: !isSystem && entranceStyle === "userSent"
    property bool _entranceStarted: false
    readonly property bool hasAttachments: Array.isArray(attachments) && attachments.length > 0
    readonly property string referenceSummaryText: Logic.buildReferenceSummary(root)
    readonly property bool showsReferenceSummary: role === "assistant" && status !== "typing" && referenceSummaryText !== ""
    readonly property bool shouldAnimateEntrance: entranceStyle !== "none" && entrancePending
    readonly property bool showGreetingDecoration: isGreeting && !isSystemError
    readonly property real greetingAuraFarPeak: uiMotionAuraFarPeak * 0.45
    readonly property real greetingAuraNearPeak: uiMotionAuraNearPeak * 0.5
    readonly property real feedbackProgressStart: -0.3
    readonly property real feedbackProgressEnd: 1.3
    readonly property real feedbackBandOuterOffset: 0.24
    readonly property real feedbackBandInnerOffset: 0.08
    readonly property int systemContentPaddingX: isGreeting ? 11 : 12
    readonly property int systemContentPaddingY: isGreeting ? 7 : 8
    readonly property int systemIconSize: isGreeting ? 22 : 10
    readonly property int systemIconSlotWidth: isGreeting ? systemIconSize : 12
    readonly property int systemIconGap: isGreeting ? 5 : 8
    readonly property int systemTextStartX: systemContentPaddingX + systemIconSlotWidth + systemIconGap
    readonly property bool useGreetingGradient: showGreetingDecoration && uiChatGreetingBubbleBgStart !== uiChatGreetingBubbleBgEnd
    readonly property string entranceMotionProfile: resolveEntranceMotionProfile()
    readonly property string contentMorphProfile: isTypingBubble ? "typing" : "content"
    readonly property string pendingSurfaceProfile: isPending ? "pending" : "settled"
    readonly property var entranceMotion: Logic.entranceProfileData(root, entranceMotionProfile)
    readonly property var contentMorphMotion: Logic.contentMorphProfileData(root, contentMorphProfile)
    readonly property var pendingSurfaceMotion: Logic.pendingSurfaceProfileData(root, pendingSurfaceProfile)
    readonly property color systemIconColor: Logic.systemIconColor(root)
    readonly property int entranceOpacityDuration: entranceMotion.opacityDuration
    readonly property int entranceMoveDuration: entranceMotion.moveDuration
    readonly property int entranceSettleDuration: entranceMotion.settleDuration
    readonly property int entranceGlowFadeDuration: entranceMotion.glowFadeDuration
    readonly property real entranceStartScale: entranceMotion.startScale
    readonly property real entrancePeakScale: entranceMotion.peakScale
    readonly property real entranceStartX: entranceMotion.startX
    readonly property real entranceSettleX: entranceMotion.settleX
    readonly property real entranceStartY: entranceMotion.startY
    readonly property real entranceSettleY: entranceMotion.settleY
    readonly property color systemAuraFarColor: Logic.systemAuraFarColor(root)
    readonly property color systemAuraNearColor: Logic.systemAuraNearColor(root)
    readonly property color systemBubbleFillColor: Logic.systemBubbleFillColor(root)
    readonly property color systemBubbleBorderColor: Logic.systemBubbleBorderColor(root)
    readonly property color systemOverlayColor: Logic.systemOverlayColor(root)
    readonly property color systemAccentColor: Logic.systemAccentColor(root)
    readonly property color systemTextColor: Logic.systemTextColor(root)
    readonly property int bubblePaddingX: 16
    readonly property int bubblePaddingTop: 12
    readonly property int bubblePaddingBottom: 16
    readonly property real bubbleMaxWidth: root.width * 0.75
    readonly property real bubbleAttachmentContentWidth: Logic.bubbleAttachmentContentWidth(root)
    readonly property real bubbleAttachmentViewportWidth: Math.min(Math.max(0, bubbleMaxWidth - (bubblePaddingX * 2)), bubbleAttachmentContentWidth)
    readonly property real contentColumnSpacing: Logic.contentColumnSpacing(root)
    readonly property int dividerBlockHeight: showDateDivider && dateDividerText !== "" ? 28 : 0
    readonly property color dividerLineColor: Logic.alphaColor(uiTextSecondary, isSystem ? 0.18 : 0.14)
    readonly property real bubbleEntranceGlowPeak: entranceMotion.glowPeak
    readonly property color bubbleEntranceGlowColor: Logic.bubbleEntranceGlowColor(root)
    readonly property real bubbleEntranceGlowStartScale: entranceMotion.glowStartScale
    readonly property real bubbleEntranceGlowPeakScale: entranceMotion.glowPeakScale
    readonly property bool showsTypingIndicator: contentMorphMotion.showsTypingIndicator
    readonly property bool showsContentBody: contentMorphMotion.showsContentBody
    readonly property real contentMorphOffsetY: contentMorphMotion.contentOffsetY
    readonly property real contentMorphScale: contentMorphMotion.contentScale
    readonly property real typingMorphOffsetY: contentMorphMotion.typingOffsetY
    readonly property real typingMorphScale: contentMorphMotion.typingScale
    readonly property int contentMorphDuration: contentMorphMotion.contentDuration
    readonly property int typingMorphDuration: contentMorphMotion.typingDuration
    readonly property bool canCopyFeedback: root.content !== ""
    readonly property color copyFeedbackOverlayColor: Logic.copyFeedbackOverlayColor(root)
    readonly property color copyFeedbackSheenColor: Logic.copyFeedbackSheenColor(root)
    readonly property real copyFeedbackOverlayPeak: Logic.copyFeedbackOverlayPeak(root)
    readonly property real copyFeedbackSheenPeak: Logic.copyFeedbackSheenPeak(root)

    width: parent ? parent.width : 600
    height: isSystem
        ? (systemBubbleRef ? systemBubbleRef.implicitHeight : 0)
        : (standardBubbleRef ? standardBubbleRef.implicitHeight : 0)

    function tr(zh, en) { return Logic.tr(root, zh, en) }
    function clamp01(value) { return Logic.clamp01(value) }

    function resolveEntranceMotionProfile() {
        if (isGreeting)
            return "greeting"
        if (isSystem)
            return "system"
        if (isUserEntrance)
            return "userSent"
        if (isAssistantEntrance)
            return "assistantReceived"
        if (isUser)
            return "user"
        return "assistant"
    }

    function currentBubbleItem() { return root.isSystem ? root.systemBubbleRef : root.standardBubbleRef }

    function playEntrance() {
        if (_entranceStarted || !shouldAnimateEntrance)
            return
        entranceStartTimer.restart()
    }

    function consumeEntrance() {
        var view = ListView.view
        if (!view || !view.model)
            return
        if (messageId >= 0 && view.model.consumeEntranceById) {
            view.model.consumeEntranceById(messageId)
            return
        }
        if (messageRow >= 0 && view.model.consumeEntrance)
            view.model.consumeEntrance(messageRow)
    }

    function copyToClipboard(text) {
        if (!text)
            return
        clipHelper.text = text
        clipHelper.selectAll()
        clipHelper.copy()
        clipHelper.deselect()
        var toast = root.toastFunc
        if (typeof toast === "function")
            toast()
    }

    function copyCurrentMessage() {
        var bubbleItem = currentBubbleItem()
        if (!canCopyFeedback || !bubbleItem)
            return
        copyToClipboard(root.content)
        bubbleItem.playCopyFeedback()
    }

    Component.onCompleted: playEntrance()
    onShouldAnimateEntranceChanged: if (shouldAnimateEntrance) playEntrance()

    Timer {
        id: entranceStartTimer
        interval: 0
        repeat: false
        onTriggered: {
            var bubbleItem = root.currentBubbleItem()
            if (root._entranceStarted || !root.shouldAnimateEntrance || !bubbleItem)
                return
            root._entranceStarted = true
            root.consumeEntrance()
            bubbleItem.playEntrance()
        }
    }

    MessageBubbleDateDivider { workspaceRoot: root }
    MessageBubbleSystemBubble { workspaceRoot: root }
    MessageBubbleStandardBubble { workspaceRoot: root }
    TextEdit { id: clipHelper; visible: false }
}
