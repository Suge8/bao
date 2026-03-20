import QtQuick 2.15

Item {
    id: root
    objectName: "sidebarBrandDock"

    property bool active: false
    property bool isDark: false
    property bool hasDiagnostics: false
    property int diagnosticsCount: 0
    property string diagnosticsLabel: ""
    property string diagnosticsHint: ""
    property var bubbleMessages: []
    property color accent: "#FFB33D"
    property int typeMeta: 12
    property int weightMedium: Font.Medium
    property int weightDemiBold: Font.DemiBold
    property int weightBold: Font.Bold
    property int motionFast: 180
    property int motionUi: 220
    property int motionPanel: 320
    property int easeStandard: Easing.OutCubic
    property int easeEmphasis: Easing.OutBack
    property int easeSoft: Easing.InOutSine
    property real motionPressScaleStrong: 0.94
    property real motionSelectionScaleActive: 1.015
    readonly property bool iconHovered: appIconButton.hovered
    readonly property bool appIconPressed: appIconButton.pressed
    readonly property bool diagnosticsHovered: diagnosticsPill.hovered
    readonly property int visibleDiagnosticsCount: Math.max(0, diagnosticsCount)
    readonly property bool bubbleVisible: iconHovered && currentBubbleText.length > 0
    readonly property color primaryInk: isDark ? "#F7EFE7" : "#261A12"
    readonly property color secondaryInk: isDark ? "#C5AF9E" : "#6B5649"
    readonly property url brandImageSource: "../resources/logo-circle.png"
    readonly property real appIconRestScale: iconHovered ? 1.015 : 1.0
    readonly property real appIconInteractiveScale: active ? motionSelectionScaleActive : appIconRestScale
    readonly property real appIconScale: appIconPressed ? motionPressScaleStrong : appIconInteractiveScale
    readonly property int idleMotionDuration: 860
    readonly property real idleLiftTravel: 3.6
    readonly property real idleScalePeak: 1.055
    readonly property real hoverLiftTravel: 5.2
    readonly property real hoverTiltAngle: -6.5
    readonly property real hoverScalePeak: 1.14
    readonly property real brandAuraRestOpacity: iconHovered ? 0.26 : 0.10
    readonly property real brandAuraOpacity: active ? 0.34 : brandAuraRestOpacity
    readonly property real brandAuraRestScale: active ? 1.02 : 0.94
    readonly property real brandAuraScale: iconHovered ? 1.08 : brandAuraRestScale
    readonly property real brandPlateOpacity: iconHovered ? 0.92 : 0.76
    readonly property real brandPlateScale: iconHovered ? 1.02 : 0.98
    readonly property real diagnosticsHoverScale: diagnosticsHovered ? 1.03 : 1.0
    readonly property color diagnosticsBorderColor: diagnosticsHovered ? (isDark ? "#C29C6A" : "#D8A66A") : (isDark ? "#2AFFFFFF" : "#DCC4A7")
    readonly property color diagnosticsFillColor: diagnosticsHovered ? (isDark ? "#221712" : "#F6EBDD") : (isDark ? "#16110E" : "#FCF6F0")
    readonly property color diagnosticsOverlayColor: diagnosticsHovered ? (isDark ? "#12FFFFFF" : "#16FFFFFF") : (isDark ? "#07FFFFFF" : "#0CFFFFFF")
    readonly property real diagnosticsIconScale: diagnosticsHovered ? 1.06 : 1.0
    readonly property real diagnosticsIconOpacity: diagnosticsHovered ? 1.0 : 0.88
    readonly property real diagnosticsLabelOpacity: diagnosticsHovered ? 1.0 : 0.94
    readonly property color diagnosticsHintColor: diagnosticsHovered ? primaryInk : secondaryInk
    readonly property int diagnosticsHintWeight: diagnosticsHovered ? weightDemiBold : weightMedium
    readonly property real diagnosticsBadgeScale: diagnosticsHovered ? 1.04 : 1.0
    readonly property string diagnosticsCountLabel: visibleDiagnosticsCount > 9 ? "9+" : String(visibleDiagnosticsCount)
    property string currentBubbleText: ""

    signal settingsRequested()
    signal diagnosticsRequested()

    implicitWidth: 188
    implicitHeight: 72

    function pickBubbleText() {
        if (!bubbleMessages || bubbleMessages.length === 0)
            return ""
        return bubbleMessages[Math.floor(Math.random() * bubbleMessages.length)] || ""
    }

    onIconHoveredChanged: {
        if (iconHovered)
            currentBubbleText = pickBubbleText()
    }

    SidebarBrandDockAppIcon {
        id: appIconButton
        dockRoot: root
        onClicked: root.settingsRequested()
    }

    SidebarBrandDockDiagnosticsPill {
        id: diagnosticsPill
        dockRoot: root
        appIconButton: appIconButton
        onClicked: root.diagnosticsRequested()
    }

    SidebarBrandDockBubble {
        dockRoot: root
        appIconButton: appIconButton
    }
}
