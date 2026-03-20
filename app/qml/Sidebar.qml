import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

import "SidebarLogic.js" as SidebarLogic

Rectangle {
    id: root
    objectName: "sidebarRoot"

    readonly property var windowRoot: Window.window
    property var chatService: null
    property var profileService: null
    property var sessionService: null
    property var supervisorService: null
    property var diagnosticsService: null
    property string selectionTarget: "sessions"
    readonly property var strings: windowRoot ? windowRoot.strings : ({})
    readonly property bool isDark: windowRoot ? Boolean(windowRoot.isDark) : false
    readonly property color accent: windowRoot ? windowRoot.accent : "#FFB33D"
    readonly property color accentHover: windowRoot ? windowRoot.accentHover : "#E39F38"
    readonly property color textPrimary: windowRoot ? windowRoot.textPrimary : "#F7EFE7"
    readonly property color textSecondary: windowRoot ? windowRoot.textSecondary : "#C5AF9E"
    readonly property color bgSidebar: windowRoot ? windowRoot.bgSidebar : "#120C09"
    readonly property color bgCardHover: windowRoot ? windowRoot.bgCardHover : "#241A15"
    readonly property color borderFocus: windowRoot ? windowRoot.borderFocus : "#FFB33D"
    readonly property color hubSurfaceRunningTop: windowRoot ? windowRoot.hubSurfaceRunningTop : "#1E1A15"
    readonly property color hubSurfaceErrorTop: windowRoot ? windowRoot.hubSurfaceErrorTop : "#261513"
    readonly property color hubSurfaceStartingTop: windowRoot ? windowRoot.hubSurfaceStartingTop : "#231A14"
    readonly property color hubSurfaceIdleTop: windowRoot ? windowRoot.hubSurfaceIdleTop : "#1D1712"
    readonly property color hubTextRunning: windowRoot ? windowRoot.hubTextRunning : textPrimary
    readonly property color hubTextStarting: windowRoot ? windowRoot.hubTextStarting : textPrimary
    readonly property color hubTextIdle: windowRoot ? windowRoot.hubTextIdle : textPrimary
    readonly property color statusSuccess: windowRoot ? windowRoot.statusSuccess : "#56D88D"
    readonly property color statusError: windowRoot ? windowRoot.statusError : "#FF7A70"
    readonly property color statusWarning: windowRoot ? windowRoot.statusWarning : "#FFC45C"
    readonly property int sizeCapsuleHeight: windowRoot ? Number(windowRoot.sizeCapsuleHeight || 54) : 54
    readonly property int sizeHubAction: windowRoot ? Number(windowRoot.sizeHubAction || 34) : 34
    readonly property int sizeHubActionIcon: windowRoot ? Number(windowRoot.sizeHubActionIcon || 18) : 18
    readonly property int typeCaption: windowRoot ? Number(windowRoot.typeCaption || 12) : 12
    readonly property int typeMeta: windowRoot ? Number(windowRoot.typeMeta || 11) : 11
    readonly property int typeBody: windowRoot ? Number(windowRoot.typeBody || 14) : 14
    readonly property int typeButton: windowRoot ? Number(windowRoot.typeButton || 14) : 14
    readonly property int typeLabel: windowRoot ? Number(windowRoot.typeLabel || 13) : 13
    readonly property int weightBold: windowRoot ? Number(windowRoot.weightBold || Font.Bold) : Font.Bold
    readonly property int weightDemiBold: windowRoot ? Number(windowRoot.weightDemiBold || Font.DemiBold) : Font.DemiBold
    readonly property int weightMedium: windowRoot ? Number(windowRoot.weightMedium || Font.Medium) : Font.Medium
    readonly property real letterWide: windowRoot ? Number(windowRoot.letterWide || 0.8) : 0.8
    readonly property real letterTight: windowRoot ? Number(windowRoot.letterTight || 0.1) : 0.1
    readonly property int motionFast: windowRoot ? Number(windowRoot.motionFast || 180) : 180
    readonly property int motionUi: windowRoot ? Number(windowRoot.motionUi || 220) : 220
    readonly property int motionPanel: windowRoot ? Number(windowRoot.motionPanel || 320) : 320
    readonly property int motionBreath: windowRoot ? Number(windowRoot.motionBreath || 1200) : 1200
    readonly property int motionAmbient: windowRoot ? Number(windowRoot.motionAmbient || 1100) : 1100
    readonly property int motionStatusPulse: windowRoot ? Number(windowRoot.motionStatusPulse || 760) : 760
    readonly property int motionFloat: windowRoot ? Number(windowRoot.motionFloat || 900) : 900
    readonly property int motionMicro: windowRoot ? Number(windowRoot.motionMicro || 120) : 120
    readonly property real motionHoverScaleSubtle: windowRoot ? Number(windowRoot.motionHoverScaleSubtle || 1.01) : 1.01
    readonly property real motionDotPulseScaleMax: windowRoot ? Number(windowRoot.motionDotPulseScaleMax || 1.45) : 1.45
    readonly property real motionDotPulseMinOpacity: windowRoot ? Number(windowRoot.motionDotPulseMinOpacity || 0.35) : 0.35
    readonly property int easeStandard: windowRoot ? Number(windowRoot.easeStandard || Easing.OutCubic) : Easing.OutCubic
    readonly property int easeEmphasis: windowRoot ? Number(windowRoot.easeEmphasis || Easing.OutBack) : Easing.OutBack
    readonly property int easeSoft: windowRoot ? Number(windowRoot.easeSoft || Easing.InOutSine) : Easing.InOutSine
    readonly property int easeLinear: Easing.Linear
    readonly property bool settingsActive: selectionTarget === "settings"
    readonly property bool hasChatService: chatService !== null
    readonly property bool hasProfileService: profileService !== null && typeof profileService.activeProfileId !== "undefined"
    readonly property bool hasSessionService: sessionService !== null
    readonly property bool hasSupervisorService: supervisorService !== null
    readonly property bool hasDiagnosticsService: diagnosticsService !== null
    readonly property bool hasDiagnosticsCount: hasDiagnosticsService && typeof diagnosticsService.eventCount !== "undefined"
    readonly property var supervisorOverview: hasSupervisorService ? (supervisorService.overview || {}) : ({})
    readonly property string currentState: resolvedHubState()
    readonly property bool isRunning: currentState === "running"
    readonly property bool isStarting: currentState === "starting"
    readonly property bool isError: currentState === "error"
    readonly property bool isChinese: typeof effectiveLang === "string" ? effectiveLang === "zh" : uiLanguage === "zh"
    readonly property bool uiIsDark: isDark
    readonly property color uiBgCanvas: "transparent"
    readonly property color uiTextPrimary: textPrimary
    readonly property color uiTextSecondary: textSecondary
    readonly property color uiStatusSuccess: statusSuccess
    readonly property color uiStatusError: statusError
    readonly property color uiStatusWarning: statusWarning
    property string editingProfileId: ""
    property string editingProfileName: ""
    property var pendingDeleteProfile: ({ "id": "", "displayName": "", "avatarKey": "mochi" })
    property real navHighlightY: 0.0
    property real navHighlightHeight: 50
    property real navHighlightOpacity: 0.0

    signal settingsRequested()
    signal diagnosticsRequested()
    signal newSessionRequested()
    signal sessionSelected(string key)
    signal sessionDeleteRequested(string key)
    signal sectionRequested(string section)

    color: "transparent"

    function sectionIconSource(section) { return SidebarLogic.sectionIconSource(root, section) }
    function channelIconSource(channel) { return SidebarLogic.channelVisualSource(root, channel, false) }
    function channelFilledIconSource(channel) { return SidebarLogic.channelVisualSource(root, channel, true) }
    function resolvedHubState() { return SidebarLogic.resolvedHubState(root) }
    function channelAccent(channel) { return SidebarLogic.channelAccent(root, channel) }
    function profileAvatarSource(key) { return "../resources/profile-avatars/" + String(key || "mochi") + ".svg" }
    function containsItemPoint(item, x, y) { return SidebarLogic.containsItemPoint(root, item, x, y) }
    function themedIconSource(name) { return windowRoot ? windowRoot.themedIconSource(name) : "" }
    function updateNavHighlight() { SidebarLogic.updateNavHighlight(root, workspaceNav.navContentItem, { "sessions": workspaceNav.sessionsItem, "memory": workspaceNav.memoryItem, "skills": workspaceNav.skillsItem, "tools": workspaceNav.toolsItem, "cron": workspaceNav.cronItem }) }
    function beginRenameProfile(profileId, displayName) { var nextId = String(profileId || "").trim(); if (!nextId.length) return; if (editingProfileId === nextId) { cancelRenameProfile(); return } editingProfileId = nextId; editingProfileName = String(displayName || "").trim() }
    function cancelRenameProfile() { editingProfileId = ""; editingProfileName = "" }
    function submitRenameProfile() { var profileId = String(editingProfileId || "").trim(); var displayName = String(editingProfileName || "").trim(); if (!profileId.length || !displayName.length || !hasProfileService) return false; profileService.renameProfile(profileId, displayName); cancelRenameProfile(); return true }
    function closeProfilePopup() { profilePopup.close() }
    function toggleProfilePopup() { if (profilePopup.opened) profilePopup.close(); else profilePopup.open() }
    function activateProfile(profileId) {
        var nextId = String(profileId || "").trim()
        if (!nextId.length || !hasProfileService)
            return false
        closeProfilePopup()
        if (String(profileService.activeProfileId || "") === nextId)
            return true
        profileService.activateProfile(nextId)
        return true
    }
    function focusProfileRenameEditor(editor) { if (!editor) return; editor.forceActiveFocus(); editor.selectAll() }
    function clearPendingDeleteProfile() { pendingDeleteProfile = { "id": "", "displayName": "", "avatarKey": "mochi" } }
    function requestDeleteProfile(profileId, displayName, avatarKey) { var nextId = String(profileId || "").trim(); if (!nextId.length) return; cancelRenameProfile(); pendingDeleteProfile = { "id": nextId, "displayName": String(displayName || nextId), "avatarKey": String(avatarKey || "mochi") }; closeProfilePopup(); deleteProfileModal.open() }
    function confirmDeleteProfile() { var profileId = String((pendingDeleteProfile || {}).id || "").trim(); if (!profileId.length || !hasProfileService) return; profileService.deleteProfile(profileId); deleteProfileModal.close() }
    function createProfile(name) { var nextName = String(name || "").trim(); if (!nextName.length || !hasProfileService) return false; profileService.createProfile(nextName); closeProfilePopup(); return true }

    onSelectionTargetChanged: Qt.callLater(function() { root.updateNavHighlight(); root.cancelRenameProfile(); root.closeProfilePopup(); deleteProfileModal.close() })
    Component.onCompleted: Qt.callLater(function() { root.updateNavHighlight() })

    Rectangle {
        anchors.fill: parent
        radius: 24
        color: bgSidebar
        antialiasing: true
        Rectangle { anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right; height: parent.radius; color: parent.color }
        Rectangle { anchors.top: parent.top; anchors.bottom: parent.bottom; anchors.right: parent.right; width: parent.radius; color: parent.color }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        SidebarHubCapsule { sidebarRoot: root }
        SidebarProfileBar { id: profileBar; sidebarRoot: root; popupOpened: profilePopup.opened; onToggled: root.toggleProfilePopup() }
        SidebarControlTowerCard { sidebarRoot: root; onClicked: root.sectionRequested("control_tower") }
        SidebarWorkspaceNav { id: workspaceNav; sidebarRoot: root; onSectionRequested: function(section) { root.sectionRequested(section) } }
        Item { Layout.fillHeight: true }

        SidebarBrandDock {
            Layout.fillWidth: true
            Layout.preferredHeight: implicitHeight
            Layout.bottomMargin: 6
            active: root.settingsActive
            isDark: isDark
            hasDiagnostics: root.hasDiagnosticsCount
            diagnosticsCount: root.hasDiagnosticsCount ? diagnosticsService.eventCount : 0
            diagnosticsLabel: strings.sidebar_diagnostics
            diagnosticsHint: strings.sidebar_diagnostics_hint
            bubbleMessages: [strings.bubble_0, strings.bubble_1, strings.bubble_2, strings.bubble_3, strings.bubble_4]
            accent: accent
            typeMeta: typeMeta
            weightMedium: weightMedium
            weightDemiBold: weightDemiBold
            weightBold: weightBold
            motionFast: motionFast
            motionUi: motionUi
            motionPanel: motionPanel
            easeStandard: easeStandard
            easeEmphasis: easeEmphasis
            easeSoft: easeSoft
            motionPressScaleStrong: 0.94
            motionSelectionScaleActive: motionSelectionScaleActive
            onSettingsRequested: root.settingsRequested()
            onDiagnosticsRequested: root.diagnosticsRequested()
        }
    }

    SidebarProfilePopup { id: profilePopup; sidebarRoot: root; profileBar: profileBar }
    SidebarDeleteProfileModal { id: deleteProfileModal; sidebarRoot: root }

    TapHandler {
        enabled: profilePopup.opened
        onTapped: function(eventPoint) {
            if (root.containsItemPoint(profileBar, eventPoint.position.x, eventPoint.position.y)) return
            if (root.containsItemPoint(profilePopup.contentItem, eventPoint.position.x, eventPoint.position.y)) return
            if (root.containsItemPoint(profilePopup.background, eventPoint.position.x, eventPoint.position.y)) return
            root.closeProfilePopup()
        }
    }
}
