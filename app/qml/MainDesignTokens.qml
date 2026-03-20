import QtQuick 2.15

QtObject {
    id: root

    required property bool isDark
    required property bool useMacTransparentTitleBar

    function themedIconSource(name, darkSuffix) {
        var resolvedDarkSuffix = typeof darkSuffix === "string" ? darkSuffix : ""
        return "../resources/icons/" + name + (isDark ? resolvedDarkSuffix : "-light") + ".svg"
    }

    readonly property color bgBase: isDark ? "#130E0B" : "#FCF8F4"
    readonly property color bgSidebar: isDark ? "#0F0B09" : "#F3ECE6"
    readonly property color bgCard: isDark ? "#19120E" : "#FFFFFF"
    readonly property color bgCardHover: isDark ? "#22170F" : "#FFF6EE"
    readonly property color bgInput: isDark ? "#1A120D" : "#FFF4EA"
    readonly property color bgInputHover: isDark ? "#23170F" : "#FFEEDF"
    readonly property color bgInputFocus: isDark ? "#2A1B11" : "#FFFFFF"
    readonly property color bgElevated: isDark ? "#24170F" : "#FFFFFF"

    readonly property color textPrimary: isDark ? "#F7EFE7" : "#261A12"
    readonly property color textSecondary: isDark ? "#C5AF9E" : "#6B5649"
    readonly property color textTertiary: isDark ? "#8B7668" : "#9D8473"
    readonly property color textPlaceholder: isDark ? "#705D51" : "#B89D8A"

    readonly property color borderSubtle: isDark ? "#20FFA11A" : "#14000000"
    readonly property color borderDefault: isDark ? "#40FFA11A" : "#24000000"
    readonly property color borderFocus: "#FFAE38"

    readonly property color accent: "#FFB33D"
    readonly property color accentHover: "#FF971A"
    readonly property color accentMuted: isDark ? "#54FFB33D" : "#34FFB33D"
    readonly property color accentGlow: "#A8FFB33D"

    readonly property color statusSuccess: "#22C55E"
    readonly property color statusWarning: "#F59E0B"
    readonly property color statusError: "#F05A5A"
    readonly property color textSelectionBg: isDark ? "#92FFB33D" : "#70FFB33D"
    readonly property color textSelectionFg: "#1E140E"

    readonly property int spacingXs: 4
    readonly property int spacingSm: 8
    readonly property int spacingMd: 12
    readonly property int spacingLg: 16
    readonly property int spacingXl: 24
    readonly property int spacingXxl: 32

    readonly property int radiusSm: 8
    readonly property int radiusMd: 12
    readonly property int radiusLg: 16

    readonly property int typeDisplay: 30
    readonly property int typeTitle: 22
    readonly property int typeBody: 15
    readonly property int typeButton: 14
    readonly property int typeLabel: 13
    readonly property int typeMeta: 12
    readonly property int typeCaption: 11
    readonly property real lineHeightBody: 1.4
    readonly property real letterTight: 0.2
    readonly property real letterWide: 0.5
    readonly property int weightRegular: Font.Normal
    readonly property int weightMedium: Font.Medium
    readonly property int weightDemiBold: Font.DemiBold
    readonly property int weightBold: Font.Bold

    readonly property int motionMicro: 120
    readonly property int motionFast: 180
    readonly property int motionUi: 220
    readonly property int motionPanel: 320
    readonly property int motionAmbient: 500
    readonly property int motionBreath: 1100
    readonly property int motionFloat: 1700
    readonly property int motionStagger: 80
    readonly property int motionStatusPulse: 600
    readonly property int motionTrackVelocity: 220
    readonly property int toastDuration: 2200
    readonly property int toastDurationLong: 2600
    readonly property int easeStandard: Easing.OutCubic
    readonly property int easeEmphasis: Easing.OutBack
    readonly property int easeSoft: Easing.InOutSine
    readonly property int easeLinear: Easing.Linear
    readonly property real motionStatusMinOpacityStarting: 0.78
    readonly property real motionStatusMinOpacityError: 0.74
    readonly property real motionGlowPeakOpacity: 0.8
    readonly property real motionDotPulseMinOpacity: 0.3
    readonly property real motionDotPulseScaleMax: 1.4
    readonly property real motionRingIdlePeakOpacity: 0.35
    readonly property real motionRingHoverOpacity: 0.6
    readonly property real motionFloatOffset: 2.5
    readonly property real motionPressScaleStrong: 0.88
    readonly property real motionHoverScaleStrong: 1.15
    readonly property real motionHoverScaleMedium: 1.08
    readonly property real motionHoverScaleSubtle: 1.04
    readonly property real motionBubbleHiddenScale: 0.8
    readonly property real motionToastHiddenScale: 0.92
    readonly property real motionDeleteHiddenScale: 0.92
    readonly property real motionCopyFlashPeak: 0.42
    readonly property real motionAuraNearPeak: 0.34
    readonly property real motionAuraFarPeak: 0.2
    readonly property real motionGreetingSweepPeak: 0.26
    readonly property real motionTypingPulseMinOpacity: 0.28
    readonly property int motionEnterOffsetY: 10
    readonly property int motionPageShift: 18
    readonly property int motionPageShiftSubtle: 10
    readonly property real motionPageRevealStartScale: 0.986
    readonly property real motionPageRevealStartOpacity: 0.84
    readonly property real motionPageAuraPeak: 0.11
    readonly property real motionSelectionScaleActive: 1.018
    readonly property real motionSelectionScaleHover: 1.006
    readonly property real motionSelectionAuraOpacity: 0.12
    readonly property real motionSelectionAuraHiddenScale: 0.96
    readonly property real motionSelectionRailHiddenScale: 0.55
    readonly property real opacityShadowSoft: 0.3
    readonly property real opacityInteractionIdle: 0.65
    readonly property real opacityInteractionHover: 0.95
    readonly property real opacityInactive: 0.85
    readonly property real opacityDimmedActive: 0.9
    readonly property real opacityDimmedIdle: 0.6

    readonly property int sizeControlHeight: 42
    readonly property int sizeControlHeightLg: 48
    readonly property int sizeButton: 40
    readonly property int sizeFieldPaddingX: 14
    readonly property int sizeOptionHeight: 34
    readonly property int sizeDropdownMaxHeight: 240
    readonly property int sizeSidebarHeader: 46
    readonly property int sizeSessionRow: 40
    readonly property int sizeSidebarGroupGap: 12
    readonly property int sizeSidebarHeaderToRowGap: 6
    readonly property int sizeSidebarGroupInnerGap: 4
    readonly property int sizeCapsuleHeight: 64
    readonly property int sizeBubbleRadius: 18
    readonly property int sizeSystemBubbleRadius: 11
    readonly property int sizeAppIcon: 46
    readonly property int sizeHubAction: 44
    readonly property int sizeHubActionIcon: 28
    readonly property int windowContentInsetTop: useMacTransparentTitleBar ? 72 : spacingLg
    readonly property int windowContentInsetSide: spacingLg
    readonly property int windowContentInsetBottom: spacingLg

    readonly property color hubTextRunning: isDark ? "#A8EAC3" : "#177C43"
    readonly property color hubTextStarting: isDark ? "#FFE2A2" : "#A85D00"
    readonly property color hubTextIdle: isDark ? "#FFD3A0" : "#A95A00"
    readonly property color hubSurfaceIdleTop: isDark ? "#FF6F3819" : "#FFF6D1A8"
    readonly property color hubSurfaceStartingTop: isDark ? "#FF8B5316" : "#FFF1BC60"
    readonly property color hubSurfaceRunningTop: isDark ? "#FF145B42" : "#FFC4ECD8"
    readonly property color hubSurfaceErrorTop: isDark ? "#FF6B2527" : "#FFF4C8C8"

    readonly property color sidebarListPanelBg: isDark ? "#120A08" : "#FBF2EA"
    readonly property color sidebarListPanelBorder: isDark ? "#14FFFFFF" : "#12000000"
    readonly property color sidebarListPanelOverlay: isDark ? "#06FFFFFF" : "#0AFFFFFF"
    readonly property color sidebarGroupBaseBg: isDark ? "#1A120F" : "#FFF8F1"
    readonly property color sidebarGroupBg: isDark ? "#1A120F" : "#FFF8F1"
    readonly property color sidebarGroupHoverBg: isDark ? "#221714" : "#FFF2E8"
    readonly property color sidebarGroupExpandedBg: isDark ? "#261A16" : "#FFF0E5"
    readonly property color sidebarGroupBorder: "#00000000"
    readonly property color sidebarGroupExpandedBorder: "#00000000"
    readonly property color sidebarGroupHighlight: "#00000000"
    readonly property color sidebarGroupChevronBg: isDark ? "#16FFFFFF" : "#14000000"
    readonly property color sidebarGroupChevronBorder: isDark ? "#18FFFFFF" : "#12000000"
    readonly property color sidebarGroupCountBg: isDark ? "#18FFFFFF" : "#14000000"
    readonly property color sidebarGroupCountText: isDark ? "#F3DCC8" : "#6B4C35"
    readonly property color sidebarScrollbarThumb: isDark ? "#20FFFFFF" : "#16000000"
    readonly property color sidebarHeaderBadgeBg: isDark ? "#26FFD7A8" : "#1CCB8740"
    readonly property color sidebarHeaderBadgeText: isDark ? "#FFF1DE" : "#6D431E"
    readonly property color sessionRowIdleBg: isDark ? "#150E0C" : "#FFF9F4"
    readonly property color sessionRowHoverBg: isDark ? "#1B1311" : "#FFF4EA"
    readonly property color sessionRowActiveBg: isDark ? "#3A2318" : "#FFD9BC"
    readonly property color sessionRowIdleBorder: "#00000000"
    readonly property color sessionRowHoverBorder: "#00000000"
    readonly property color sessionRowActiveBorder: "#00000000"
    readonly property color sessionDeleteHoverBg: isDark ? "#28F87171" : "#22F87171"
    readonly property color sessionDeleteIdleBg: isDark ? "#14FFFFFF" : "#10000000"
    readonly property color sessionDeleteHoverBorder: "#66F87171"
    readonly property color sessionDeleteIdleBorder: isDark ? "#2AFFFFFF" : "#23000000"
    readonly property color sessionDeleteIcon: isDark ? "#F87171" : "#DC2626"
    readonly property color sessionUnreadDot: isDark ? "#F87171" : "#DC2626"

    readonly property color chatSystemAuraFar: isDark ? "#46FFA11A" : "#36FFA11A"
    readonly property color chatSystemAuraNear: isDark ? "#36FFA11A" : "#2AFFA11A"
    readonly property color chatSystemAuraErrorFar: "#2EF05A5A"
    readonly property color chatSystemAuraErrorNear: "#44F05A5A"
    readonly property color chatSystemBubbleBg: isDark ? "#28FFB33D" : "#16FFB33D"
    readonly property color chatSystemBubbleBorder: isDark ? "#58FFCB7A" : "#42D0892C"
    readonly property color chatSystemBubbleErrorBg: isDark ? "#20F05A5A" : "#14F05A5A"
    readonly property color chatSystemBubbleErrorBorder: isDark ? "#58F05A5A" : "#42F05A5A"
    readonly property color chatSystemBubbleOverlay: isDark ? "#22FFA11A" : "#18FFA11A"
    readonly property color chatSystemBubbleErrorOverlay: "#08F05A5A"
    readonly property color chatSystemText: isDark ? "#F6DEBA" : "#77471A"
    readonly property color chatGreetingAuraFar: isDark ? "#22FFD6A1" : "#0EE0BE93"
    readonly property color chatGreetingAuraNear: isDark ? "#34FFE7C2" : "#18E8C79F"
    readonly property color chatGreetingBubbleBgStart: isDark ? "#FF2B2118" : "#FFF7F3EC"
    readonly property color chatGreetingBubbleBgEnd: isDark ? "#FF201812" : "#FFF7F3EC"
    readonly property color chatGreetingBubbleBorder: isDark ? "#50FFD19A" : "#1F8F6A47"
    readonly property color chatGreetingBubbleOverlay: isDark ? "#10FFFFFF" : "#06FFFFFF"
    readonly property color chatGreetingBubbleHighlight: isDark ? "#88FFF5DF" : "#42FFFFFF"
    readonly property color chatGreetingSweep: isDark ? "#16FFFFFF" : "#10FFFFFF"
    readonly property color chatGreetingAccent: isDark ? "#F6C889" : "#A8641F"
    readonly property color chatGreetingText: isDark ? "#FFF6EA" : "#402715"
    readonly property string chatGreetingIconSource: themedIconSource("ignite", "-dark")
    readonly property color chatBubbleCopyFlashUser: "#40FFFFFF"
    readonly property color chatBubbleErrorTint: "#15F05A5A"
    readonly property color chatEmptyIconBg: isDark ? "#10FFFFFF" : "#1C9A6328"
    readonly property color chatEmptyIconBorder: isDark ? "transparent" : "#2E9A6328"
    readonly property color chatErrorBadgeBg: isDark ? "#18F87171" : "#10F87171"
    readonly property color chatComposerSendGlow: isDark ? "#2EFFB33D" : "#24FF971A"
    readonly property color chatComposerSendHighlight: isDark ? "#2CFFFFFF" : "#20FFFFFF"
    readonly property color chatComposerSendDisabled: isDark ? "#1A1A26" : "#E5E7EB"
}
