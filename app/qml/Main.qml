import QtQuick 2.15
import QtQuick.Controls 2.15

import "MainDiagnostics.js" as MainDiagnostics
import "MainStringsEn.js" as MainStringsEn
import "MainStringsZh.js" as MainStringsZh

ApplicationWindow {
    id: root
    visible: true

    readonly property int defaultWindowWidth: 1100
    readonly property int defaultWindowHeight: 720
    readonly property int minimumWindowWidth: 640
    readonly property int minimumWindowHeight: 600
    readonly property int chromeRadius: 20

    width: defaultWindowWidth
    height: defaultWindowHeight
    minimumWidth: minimumWindowWidth
    minimumHeight: minimumWindowHeight
    title: ""

    property bool useNativeTitleBar: true
    readonly property bool useMacTransparentTitleBar: useNativeTitleBar && Qt.platform.os === "osx"

    flags: useNativeTitleBar
           ? (Qt.Window
              | (useMacTransparentTitleBar ? Qt.NoTitleBarBackgroundHint : 0)
              | (useMacTransparentTitleBar ? Qt.ExpandedClientAreaHint : 0))
           : (Qt.Window | Qt.FramelessWindowHint)

    required property var chatService
    required property var configService
    required property var profileService
    required property var sessionService
    required property var profileSupervisorService
    required property var cronService
    required property var heartbeatService
    required property var memoryService
    required property var skillsService
    required property var toolsService
    required property var diagnosticsService
    required property var desktopPreferences
    required property var updateService
    required property var updateBridge
    required property string systemUiLanguage

    readonly property bool hasDesktopPreferences: desktopPreferences !== null
    readonly property bool hasConfigService: configService !== null
    readonly property bool hasSessionService: sessionService !== null
    readonly property bool hasChatService: chatService !== null
    readonly property bool hasDiagnosticsService: diagnosticsService !== null
    readonly property bool isDark: hasDesktopPreferences ? desktopPreferences.isDark : true
    readonly property string uiLanguage: hasDesktopPreferences ? desktopPreferences.uiLanguage : "auto"
    readonly property string autoLanguage: {
        if (typeof systemUiLanguage === "string") {
            var sys = systemUiLanguage.toLowerCase()
            if (sys.startsWith("zh")) return "zh"
            if (sys.startsWith("en")) return "en"
        }
        return String(Qt.locale().name || "").toLowerCase().startsWith("zh") ? "zh" : "en"
    }
    readonly property string effectiveLang: uiLanguage === "zh" || uiLanguage === "en" ? uiLanguage : autoLanguage
    readonly property var stringsZh: MainStringsZh.data()
    readonly property var stringsEn: MainStringsEn.data()
    readonly property var strings: uiLanguage === "zh" ? stringsZh : (uiLanguage === "en" ? stringsEn : (autoLanguage === "zh" ? stringsZh : stringsEn))
    readonly property var workspaceOrder: ["sessions", "control_tower", "memory", "skills", "tools", "cron"]
    readonly property bool setupMode: hasConfigService ? (!configService.isValid || configService.needsSetup) : true
    readonly property bool showingSettings: setupMode || startView === "settings"
    readonly property int currentPageIndex: showingSettings ? 1 : 0
    readonly property string sidebarSelectionTarget: showingSettings ? "settings" : activeWorkspace
    readonly property int activeWorkspaceIndex: Math.max(0, workspaceOrder.indexOf(activeWorkspace))

    property string startView: "chat"
    property string activeWorkspace: "sessions"
    property bool _previousSetupMode: true
    property int setupCompletionToken: 0
    property int _lastActiveWorkspaceIndex: 0

    MainDesignTokens {
        id: designTokens
        isDark: root.isDark
        useMacTransparentTitleBar: root.useMacTransparentTitleBar
    }

    readonly property var design: designTokens
    property alias bgBase: designTokens.bgBase
    property alias bgSidebar: designTokens.bgSidebar
    property alias bgCard: designTokens.bgCard
    property alias bgCardHover: designTokens.bgCardHover
    property alias bgInput: designTokens.bgInput
    property alias bgInputHover: designTokens.bgInputHover
    property alias bgInputFocus: designTokens.bgInputFocus
    property alias bgElevated: designTokens.bgElevated
    property alias textPrimary: designTokens.textPrimary
    property alias textSecondary: designTokens.textSecondary
    property alias textTertiary: designTokens.textTertiary
    property alias textPlaceholder: designTokens.textPlaceholder
    property alias borderSubtle: designTokens.borderSubtle
    property alias borderDefault: designTokens.borderDefault
    property alias borderFocus: designTokens.borderFocus
    property alias accent: designTokens.accent
    property alias accentHover: designTokens.accentHover
    property alias accentMuted: designTokens.accentMuted
    property alias accentGlow: designTokens.accentGlow
    property alias statusSuccess: designTokens.statusSuccess
    property alias statusWarning: designTokens.statusWarning
    property alias statusError: designTokens.statusError
    property alias textSelectionBg: designTokens.textSelectionBg
    property alias textSelectionFg: designTokens.textSelectionFg
    property alias spacingXs: designTokens.spacingXs
    property alias spacingSm: designTokens.spacingSm
    property alias spacingMd: designTokens.spacingMd
    property alias spacingLg: designTokens.spacingLg
    property alias spacingXl: designTokens.spacingXl
    property alias radiusSm: designTokens.radiusSm
    property alias radiusMd: designTokens.radiusMd
    property alias radiusLg: designTokens.radiusLg
    property alias typeTitle: designTokens.typeTitle
    property alias typeBody: designTokens.typeBody
    property alias typeButton: designTokens.typeButton
    property alias typeLabel: designTokens.typeLabel
    property alias typeMeta: designTokens.typeMeta
    property alias typeCaption: designTokens.typeCaption
    property alias lineHeightBody: designTokens.lineHeightBody
    property alias letterTight: designTokens.letterTight
    property alias letterWide: designTokens.letterWide
    property alias weightMedium: designTokens.weightMedium
    property alias weightDemiBold: designTokens.weightDemiBold
    property alias weightBold: designTokens.weightBold
    property alias motionMicro: designTokens.motionMicro
    property alias motionFast: designTokens.motionFast
    property alias motionUi: designTokens.motionUi
    property alias motionPanel: designTokens.motionPanel
    property alias motionAmbient: designTokens.motionAmbient
    property alias motionBreath: designTokens.motionBreath
    property alias motionFloat: designTokens.motionFloat
    property alias motionStagger: designTokens.motionStagger
    property alias motionStatusPulse: designTokens.motionStatusPulse
    property alias motionTrackVelocity: designTokens.motionTrackVelocity
    property alias toastDuration: designTokens.toastDuration
    property alias toastDurationLong: designTokens.toastDurationLong
    property alias easeStandard: designTokens.easeStandard
    property alias easeEmphasis: designTokens.easeEmphasis
    property alias easeSoft: designTokens.easeSoft
    property alias easeLinear: designTokens.easeLinear
    property alias motionDotPulseMinOpacity: designTokens.motionDotPulseMinOpacity
    property alias motionDotPulseScaleMax: designTokens.motionDotPulseScaleMax
    property alias motionPressScaleStrong: designTokens.motionPressScaleStrong
    property alias motionHoverScaleMedium: designTokens.motionHoverScaleMedium
    property alias motionHoverScaleSubtle: designTokens.motionHoverScaleSubtle
    property alias motionToastHiddenScale: designTokens.motionToastHiddenScale
    property alias motionDeleteHiddenScale: designTokens.motionDeleteHiddenScale
    property alias motionCopyFlashPeak: designTokens.motionCopyFlashPeak
    property alias motionAuraNearPeak: designTokens.motionAuraNearPeak
    property alias motionAuraFarPeak: designTokens.motionAuraFarPeak
    property alias motionGreetingSweepPeak: designTokens.motionGreetingSweepPeak
    property alias motionTypingPulseMinOpacity: designTokens.motionTypingPulseMinOpacity
    property alias motionEnterOffsetY: designTokens.motionEnterOffsetY
    property alias motionPageShiftSubtle: designTokens.motionPageShiftSubtle
    property alias motionPageRevealStartScale: designTokens.motionPageRevealStartScale
    property alias motionPageRevealStartOpacity: designTokens.motionPageRevealStartOpacity
    property alias motionSelectionScaleActive: designTokens.motionSelectionScaleActive
    property alias motionSelectionScaleHover: designTokens.motionSelectionScaleHover
    property alias opacityShadowSoft: designTokens.opacityShadowSoft
    property alias opacityDimmedActive: designTokens.opacityDimmedActive
    property alias opacityDimmedIdle: designTokens.opacityDimmedIdle
    property alias sizeControlHeight: designTokens.sizeControlHeight
    property alias sizeButton: designTokens.sizeButton
    property alias sizeFieldPaddingX: designTokens.sizeFieldPaddingX
    property alias sizeOptionHeight: designTokens.sizeOptionHeight
    property alias sizeDropdownMaxHeight: designTokens.sizeDropdownMaxHeight
    property alias sizeSidebarHeader: designTokens.sizeSidebarHeader
    property alias sizeSessionRow: designTokens.sizeSessionRow
    property alias sizeSidebarGroupGap: designTokens.sizeSidebarGroupGap
    property alias sizeSidebarHeaderToRowGap: designTokens.sizeSidebarHeaderToRowGap
    property alias sizeSidebarGroupInnerGap: designTokens.sizeSidebarGroupInnerGap
    property alias sizeCapsuleHeight: designTokens.sizeCapsuleHeight
    property alias sizeBubbleRadius: designTokens.sizeBubbleRadius
    property alias sizeSystemBubbleRadius: designTokens.sizeSystemBubbleRadius
    property alias sizeHubAction: designTokens.sizeHubAction
    property alias sizeHubActionIcon: designTokens.sizeHubActionIcon
    property alias windowContentInsetTop: designTokens.windowContentInsetTop
    property alias windowContentInsetSide: designTokens.windowContentInsetSide
    property alias windowContentInsetBottom: designTokens.windowContentInsetBottom
    property alias hubTextRunning: designTokens.hubTextRunning
    property alias hubTextStarting: designTokens.hubTextStarting
    property alias hubTextIdle: designTokens.hubTextIdle
    property alias hubSurfaceIdleTop: designTokens.hubSurfaceIdleTop
    property alias hubSurfaceStartingTop: designTokens.hubSurfaceStartingTop
    property alias hubSurfaceRunningTop: designTokens.hubSurfaceRunningTop
    property alias hubSurfaceErrorTop: designTokens.hubSurfaceErrorTop
    property alias sidebarListPanelBg: designTokens.sidebarListPanelBg
    property alias sidebarListPanelBorder: designTokens.sidebarListPanelBorder
    property alias sidebarListPanelOverlay: designTokens.sidebarListPanelOverlay
    property alias sidebarGroupBg: designTokens.sidebarGroupBg
    property alias sidebarGroupHoverBg: designTokens.sidebarGroupHoverBg
    property alias sidebarGroupExpandedBg: designTokens.sidebarGroupExpandedBg
    property alias sidebarGroupChevronBg: designTokens.sidebarGroupChevronBg
    property alias sidebarGroupChevronBorder: designTokens.sidebarGroupChevronBorder
    property alias sidebarGroupCountBg: designTokens.sidebarGroupCountBg
    property alias sidebarGroupCountText: designTokens.sidebarGroupCountText
    property alias sidebarScrollbarThumb: designTokens.sidebarScrollbarThumb
    property alias sidebarHeaderBadgeBg: designTokens.sidebarHeaderBadgeBg
    property alias sidebarHeaderBadgeText: designTokens.sidebarHeaderBadgeText
    property alias sessionRowIdleBg: designTokens.sessionRowIdleBg
    property alias sessionRowHoverBg: designTokens.sessionRowHoverBg
    property alias sessionRowActiveBg: designTokens.sessionRowActiveBg
    property alias sessionRowIdleBorder: designTokens.sessionRowIdleBorder
    property alias sessionRowHoverBorder: designTokens.sessionRowHoverBorder
    property alias sessionRowActiveBorder: designTokens.sessionRowActiveBorder
    property alias sessionDeleteHoverBg: designTokens.sessionDeleteHoverBg
    property alias sessionDeleteIdleBg: designTokens.sessionDeleteIdleBg
    property alias sessionDeleteHoverBorder: designTokens.sessionDeleteHoverBorder
    property alias sessionDeleteIdleBorder: designTokens.sessionDeleteIdleBorder
    property alias sessionDeleteIcon: designTokens.sessionDeleteIcon
    property alias sessionUnreadDot: designTokens.sessionUnreadDot
    property alias chatSystemAuraFar: designTokens.chatSystemAuraFar
    property alias chatSystemAuraNear: designTokens.chatSystemAuraNear
    property alias chatSystemAuraErrorFar: designTokens.chatSystemAuraErrorFar
    property alias chatSystemAuraErrorNear: designTokens.chatSystemAuraErrorNear
    property alias chatSystemBubbleBg: designTokens.chatSystemBubbleBg
    property alias chatSystemBubbleBorder: designTokens.chatSystemBubbleBorder
    property alias chatSystemBubbleErrorBg: designTokens.chatSystemBubbleErrorBg
    property alias chatSystemBubbleErrorBorder: designTokens.chatSystemBubbleErrorBorder
    property alias chatSystemBubbleOverlay: designTokens.chatSystemBubbleOverlay
    property alias chatSystemBubbleErrorOverlay: designTokens.chatSystemBubbleErrorOverlay
    property alias chatSystemText: designTokens.chatSystemText
    property alias chatGreetingAuraFar: designTokens.chatGreetingAuraFar
    property alias chatGreetingAuraNear: designTokens.chatGreetingAuraNear
    property alias chatGreetingBubbleBgStart: designTokens.chatGreetingBubbleBgStart
    property alias chatGreetingBubbleBgEnd: designTokens.chatGreetingBubbleBgEnd
    property alias chatGreetingBubbleBorder: designTokens.chatGreetingBubbleBorder
    property alias chatGreetingBubbleOverlay: designTokens.chatGreetingBubbleOverlay
    property alias chatGreetingBubbleHighlight: designTokens.chatGreetingBubbleHighlight
    property alias chatGreetingSweep: designTokens.chatGreetingSweep
    property alias chatGreetingAccent: designTokens.chatGreetingAccent
    property alias chatGreetingText: designTokens.chatGreetingText
    property alias chatGreetingIconSource: designTokens.chatGreetingIconSource
    property alias chatBubbleCopyFlashUser: designTokens.chatBubbleCopyFlashUser
    property alias chatBubbleErrorTint: designTokens.chatBubbleErrorTint
    property alias chatEmptyIconBg: designTokens.chatEmptyIconBg
    property alias chatEmptyIconBorder: designTokens.chatEmptyIconBorder
    property alias chatErrorBadgeBg: designTokens.chatErrorBadgeBg
    property alias chatComposerSendHighlight: designTokens.chatComposerSendHighlight
    property alias chatComposerSendDisabled: designTokens.chatComposerSendDisabled
    color: useNativeTitleBar ? design.bgBase : "transparent"

    onSetupModeChanged: {
        if (_previousSetupMode && !setupMode)
            setupCompletionToken += 1
        _previousSetupMode = setupMode
    }

    Component.onCompleted: _lastActiveWorkspaceIndex = activeWorkspaceIndex

    function copyPlainText(text) {
        diagnosticsClipHelper.text = text || ""
        diagnosticsClipHelper.selectAll()
        diagnosticsClipHelper.copy()
        diagnosticsClipHelper.deselect()
    }

    function themedIconSource(name, darkSuffix) { return design.themedIconSource(name, darkSuffix) }
    function diagnosticsHubState() { return MainDiagnostics.hubState(chatService) }
    function diagnosticsHubLabel() { return MainDiagnostics.hubLabel(strings, chatService) }
    function diagnosticsHubIcon() { return MainDiagnostics.hubIcon(chatService) }
    function diagnosticsHubBadgeColor() { return MainDiagnostics.hubBadgeColor(chatService, isDark) }
    function diagnosticsObservabilityItemsSafe() { return MainDiagnostics.observabilityItems(diagnosticsService) }
    function diagnosticsEventsSafe() { return MainDiagnostics.events(diagnosticsService) }
    function diagnosticsEventCountSafe() { return MainDiagnostics.eventCount(diagnosticsService) }
    function diagnosticsLogFilePathSafe() { return MainDiagnostics.logFilePath(diagnosticsService) }
    function diagnosticsRecentLogTextSafe() { return MainDiagnostics.recentLogText(diagnosticsService) }
    function diagnosticsSectionIcon(section) { return MainDiagnostics.sectionIcon(section, isDark) }
    function diagnosticsObservabilitySummary() { return MainDiagnostics.observabilitySummary(diagnosticsService) }
    function openDiagnostics() { diagnosticsModal.open() }

    Connections {
        target: hasSessionService ? sessionService : null

        function onDeleteCompleted(_key, ok, error) {
            if (ok)
                globalToast.show(strings.session_delete_ok, true)
            else
                globalToast.show(strings.session_delete_fail + (error ? (": " + error) : ""), false)
        }
    }

    MainWindowChrome {
        appRoot: root
    }

    AppToast {
        id: globalToast
        objectName: "globalToast"
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.topMargin: 14
        anchors.rightMargin: 14
        z: 999
        successBg: isDark ? "#1F7A4D" : "#16A34A"
        errorBg: isDark ? "#B84040" : "#DC2626"
        textColor: "#FFFFFF"
        duration: design.toastDuration
    }

    TextEdit {
        id: diagnosticsClipHelper
        visible: false
        textFormat: TextEdit.PlainText
    }

    MainDiagnosticsModal {
        id: diagnosticsModal
        appRoot: root
        toastTarget: globalToast
    }
}
