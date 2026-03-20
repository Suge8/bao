function alphaColor(color, alpha) {
    return Qt.rgba(color.r, color.g, color.b, Math.max(0.0, Math.min(1.0, alpha)))
}

function clamp01(value) {
    return Math.max(0.0, Math.min(1.0, value))
}

function uiLangCode(root) {
    if (root.uiEffectiveLang === "zh" || root.uiEffectiveLang === "en")
        return root.uiEffectiveLang
    if (root.uiLanguageCode === "zh")
        return "zh"
    return "en"
}

function tr(root, zh, en) {
    return uiLangCode(root) === "zh" ? zh : en
}

function referenceCategoryLabel(root, category) {
    switch (String(category || "")) {
    case "preference":
        return tr(root, "偏好记忆", "Preference memory")
    case "personal":
        return tr(root, "个人记忆", "Personal memory")
    case "project":
        return tr(root, "项目记忆", "Project memory")
    case "general":
        return tr(root, "通用记忆", "General memory")
    default:
        return String(category || "")
    }
}

function buildReferenceSummary(root) {
    var data = root.references || {}
    var segments = []
    var categories = Array.isArray(data.longTermCategories) ? data.longTermCategories : []
    if (categories.length > 0) {
        var labels = []
        for (var i = 0; i < categories.length; ++i)
            labels.push(referenceCategoryLabel(root, categories[i]))
        segments.push(labels.join(" / "))
    }
    var relatedMemoryCount = Number(data.relatedMemoryCount || 0)
    if (relatedMemoryCount > 0)
        segments.push(tr(root, "相关记忆 " + relatedMemoryCount + " 条", relatedMemoryCount + " memories"))
    var experienceCount = Number(data.experienceCount || 0)
    if (experienceCount > 0)
        segments.push(tr(root, "经验 " + experienceCount + " 条", experienceCount + " experiences"))
    if (segments.length === 0)
        return ""
    return tr(root, "参考：", "Referenced: ") + segments.join(" · ")
}

function entranceProfileData(root, profile) {
    switch (profile) {
    case "greeting":
        return { opacityDuration: root.uiMotionUi + 40, moveDuration: root.uiMotionUi + 44, settleDuration: root.uiMotionPanel + 42, glowFadeDuration: root.uiMotionAmbient, startScale: 0.962, peakScale: 1.016, startX: 0, settleX: 0, startY: 16, settleY: -1.4, glowPeak: root.uiMotionAuraNearPeak * 0.44, glowStartScale: 0.95, glowPeakScale: 1.058 }
    case "system":
        return { opacityDuration: root.uiMotionUi + 24, moveDuration: root.uiMotionUi + 20, settleDuration: root.uiMotionPanel + 16, glowFadeDuration: root.uiMotionPanel + 60, startScale: 0.932, peakScale: 1.014, startX: 0, settleX: 0, startY: -26, settleY: 1.2, glowPeak: root.uiMotionAuraNearPeak * 0.43, glowStartScale: 0.95, glowPeakScale: 1.046 }
    case "userSent":
        return { opacityDuration: root.uiMotionFast + 40, moveDuration: root.uiMotionFast + 50, settleDuration: root.uiMotionUi + 44, glowFadeDuration: root.uiMotionPanel + 20, startScale: 0.981, peakScale: 1.02, startX: root.uiMotionEnterOffsetY * 2.65, settleX: -1.05, startY: root.uiMotionEnterOffsetY * 0.58, settleY: -0.58, glowPeak: root.uiMotionAuraNearPeak * 0.68, glowStartScale: 0.938, glowPeakScale: 1.045 }
    case "assistantReceived":
        return { opacityDuration: root.uiMotionUi + 22, moveDuration: root.uiMotionUi + 18, settleDuration: root.uiMotionUi + 52, glowFadeDuration: root.uiMotionPanel + 20, startScale: 0.972, peakScale: 1.015, startX: -root.uiMotionEnterOffsetY * 2.25, settleX: 0.82, startY: root.uiMotionEnterOffsetY * 0.84, settleY: -0.78, glowPeak: root.uiMotionAuraNearPeak * 0.55, glowStartScale: 0.95, glowPeakScale: 1.044 }
    case "user":
        return { opacityDuration: root.uiMotionFast + 28, moveDuration: root.uiMotionFast + 32, settleDuration: root.uiMotionUi + 36, glowFadeDuration: root.uiMotionPanel + 20, startScale: 0.975, peakScale: 1.017, startX: root.uiMotionEnterOffsetY * 1.95, settleX: -0.82, startY: root.uiMotionEnterOffsetY * 0.4, settleY: -0.46, glowPeak: root.uiMotionAuraNearPeak * 0.53, glowStartScale: 0.938, glowPeakScale: 1.044 }
    default:
        return { opacityDuration: root.uiMotionUi + 6, moveDuration: root.uiMotionUi + 14, settleDuration: root.uiMotionUi + 42, glowFadeDuration: root.uiMotionPanel + 20, startScale: 0.971, peakScale: 1.014, startX: -root.uiMotionEnterOffsetY * 1.65, settleX: 0.62, startY: root.uiMotionEnterOffsetY * 0.68, settleY: -0.56, glowPeak: root.uiMotionAuraNearPeak * 0.44, glowStartScale: 0.95, glowPeakScale: 1.043 }
    }
}

function contentMorphProfileData(root, profile) {
    if (profile === "typing")
        return { showsTypingIndicator: true, showsContentBody: false, contentOffsetY: 5, contentScale: 0.992, typingOffsetY: 0, typingScale: 1.0, contentDuration: root.uiMotionUi + 20, typingDuration: root.uiMotionUi }
    return { showsTypingIndicator: false, showsContentBody: root.content !== "", contentOffsetY: 0, contentScale: 1.0, typingOffsetY: -4, typingScale: 0.92, contentDuration: root.uiMotionUi + 20, typingDuration: root.uiMotionUi }
}

function pendingSurfaceProfileData(root, profile) {
    if (profile === "pending")
        return { opacity: root.isUser ? 1.0 : 0.84, scale: 1.016, color: root.isUser ? "#12FFFFFF" : alphaColor(root.uiAccent, 0.08), duration: root.uiMotionUi + 60 }
    return { opacity: 0.0, scale: 1.0, color: root.isUser ? "#12FFFFFF" : alphaColor(root.uiAccent, 0.08), duration: root.uiMotionUi + 60 }
}

function systemIconColor(root) {
    if (root.isSystemError) return root.uiStatusError
    if (root.isGreeting) return root.uiChatGreetingAccent
    return root.systemAccentColor
}

function systemAuraFarColor(root) {
    if (root.isSystemError) return root.uiChatSystemAuraErrorFar
    if (root.isGreeting) return root.uiChatGreetingAuraFar
    return root.uiChatSystemAuraFar
}

function systemAuraNearColor(root) {
    if (root.isSystemError) return root.uiChatSystemAuraErrorNear
    if (root.isGreeting) return root.uiChatGreetingAuraNear
    return root.uiChatSystemAuraNear
}

function systemBubbleFillColor(root) {
    if (root.isSystemError) return root.uiChatSystemBubbleErrorBg
    if (root.isGreeting) return root.uiChatGreetingBubbleBgStart
    return root.uiChatSystemBubbleBg
}

function systemBubbleBorderColor(root) {
    if (root.isSystemError) return root.uiChatSystemBubbleErrorBorder
    if (root.isGreeting) return root.uiChatGreetingBubbleBorder
    return root.uiChatSystemBubbleBorder
}

function systemOverlayColor(root) {
    if (root.isSystemError) return root.uiChatSystemBubbleErrorOverlay
    if (root.isGreeting) return root.uiChatGreetingBubbleOverlay
    return root.uiChatSystemBubbleOverlay
}

function systemAccentColor(root) {
    if (root.isSystemError) return root.uiStatusError
    if (root.isGreeting) return root.uiChatGreetingAccent
    return root.uiAccent
}

function systemTextColor(root) {
    if (root.isSystemError) return root.uiStatusError
    if (root.isGreeting) return root.uiChatGreetingText
    return root.uiChatSystemText
}

function bubbleAttachmentContentWidth(root) {
    if (!root.hasAttachments)
        return 0
    var total = 0
    for (var i = 0; i < root.attachments.length; ++i) {
        var item = root.attachments[i]
        total += item && item.isImage ? 72 : 164
        if (i > 0)
            total += 8
    }
    return total
}

function contentColumnSpacing(root) {
    var visibleBlocks = 0
    if (root.showsContentBody) visibleBlocks += 1
    if (root.hasAttachments) visibleBlocks += 1
    if (root.showsReferenceSummary) visibleBlocks += 1
    return visibleBlocks > 1 ? 8 : 0
}

function bubbleEntranceGlowColor(root) {
    return root.isUserEntrance ? alphaColor(root.uiAccent, 0.34) : alphaColor(root.uiAccentGlow, 0.52)
}

function copyFeedbackOverlayColor(root) {
    if (root.isSystemError) return root.uiChatSystemBubbleErrorOverlay
    if (root.isGreeting) return root.uiChatGreetingBubbleHighlight
    if (root.isSystem) return root.uiChatSystemBubbleOverlay
    if (root.isUser) return root.uiChatBubbleCopyFlashUser
    return root.uiAccentGlow
}

function copyFeedbackSheenColor(root) {
    if (root.isSystemError) return "#12FFFFFF"
    if (root.isGreeting) return root.uiChatGreetingBubbleHighlight
    if (root.isSystem) return "#18FFFFFF"
    if (root.isUser) return "#24FFFFFF"
    return "#1CFFFFFF"
}

function copyFeedbackOverlayPeak(root) {
    if (root.isGreeting) return root.uiMotionCopyFlashPeak * 0.82
    if (root.isSystem) return root.uiMotionCopyFlashPeak * 0.64
    if (root.isUser) return root.uiMotionCopyFlashPeak * 0.9
    return root.uiMotionCopyFlashPeak * 0.72
}

function copyFeedbackSheenPeak(root) {
    if (root.isGreeting) return root.uiMotionGreetingSweepPeak * 0.82
    if (root.isSystem) return root.uiMotionGreetingSweepPeak * 0.94
    if (root.isUser) return root.uiMotionGreetingSweepPeak * 0.68
    return root.uiMotionGreetingSweepPeak * 0.54
}
