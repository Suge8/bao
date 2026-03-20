import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import "CronWorkspaceLogic.js" as CronWorkspaceLogic

Item {
    id: root
    objectName: "cronWorkspaceRoot"

    property bool active: false
    property var appRoot: null
    property var cronService: null
    property var heartbeatService: null
    property string currentPane: "tasks"
    property real revealOpacity: 1.0
    property real contentRevealOpacity: 1.0
    property real contentRevealShift: 0.0
    readonly property var windowRoot: Window.window
    readonly property bool isDark: windowRoot ? Boolean(windowRoot.isDark) : false
    readonly property color bgInput: windowRoot ? windowRoot.bgInput : "transparent"
    readonly property color bgCardHover: windowRoot ? windowRoot.bgCardHover : "transparent"
    readonly property color textPrimary: windowRoot ? windowRoot.textPrimary : "transparent"
    readonly property color textSecondary: windowRoot ? windowRoot.textSecondary : "transparent"
    readonly property color textTertiary: windowRoot ? windowRoot.textTertiary : "transparent"
    readonly property color textPlaceholder: windowRoot ? windowRoot.textPlaceholder : "transparent"
    readonly property color textSelectionBg: windowRoot ? windowRoot.textSelectionBg : "transparent"
    readonly property color textSelectionFg: windowRoot ? windowRoot.textSelectionFg : "transparent"
    readonly property color borderSubtle: windowRoot ? windowRoot.borderSubtle : "transparent"
    readonly property color borderDefault: windowRoot ? windowRoot.borderDefault : "transparent"
    readonly property color accent: windowRoot ? windowRoot.accent : "transparent"
    readonly property color accentHover: windowRoot ? windowRoot.accentHover : "transparent"
    readonly property color statusSuccess: windowRoot ? windowRoot.statusSuccess : "transparent"
    readonly property color statusError: windowRoot ? windowRoot.statusError : "transparent"
    readonly property color statusWarning: windowRoot ? windowRoot.statusWarning : "transparent"
    readonly property int typeTitle: windowRoot ? Number(windowRoot.typeTitle || 0) : 0
    readonly property int typeBody: windowRoot ? Number(windowRoot.typeBody || 0) : 0
    readonly property int typeLabel: windowRoot ? Number(windowRoot.typeLabel || 0) : 0
    readonly property int typeMeta: windowRoot ? Number(windowRoot.typeMeta || 0) : 0
    readonly property int typeCaption: windowRoot ? Number(windowRoot.typeCaption || 0) : 0
    readonly property int weightBold: windowRoot ? Number(windowRoot.weightBold || 0) : 0
    readonly property int weightDemiBold: windowRoot ? Number(windowRoot.weightDemiBold || 0) : 0
    readonly property int weightMedium: windowRoot ? Number(windowRoot.weightMedium || 0) : 0
    readonly property real letterWide: windowRoot ? Number(windowRoot.letterWide || 0) : 0
    readonly property int motionFast: windowRoot ? Number(windowRoot.motionFast || 0) : 0
    readonly property int easeStandard: windowRoot ? Number(windowRoot.easeStandard || 0) : 0
    readonly property int compactLayoutBreakpoint: 840
    readonly property bool compactLayout: width < compactLayoutBreakpoint
    readonly property int compactListPaneHeight: 164
    readonly property int compactDetailPaneMinHeight: 190
    readonly property int listCacheBuffer: 720

    readonly property bool hasCronService: cronService !== null
    readonly property bool hasHeartbeatService: heartbeatService !== null && typeof heartbeatService.heartbeatFileExists !== "undefined"
    readonly property var draft: hasCronService ? cronService.draft : ({})
    readonly property var selectedTask: hasCronService ? cronService.selectedTask : ({})
    readonly property bool hasDraft: hasCronService ? cronService.hasDraft : false
    readonly property bool editingNewTask: hasCronService ? cronService.editingNewTask : false
    readonly property bool showingExistingTask: draftString("id", "") !== ""
    readonly property var visibleTask: showingExistingTask ? selectedTask : ({})
    readonly property string resolvedLang: CronWorkspaceLogic.resolveLang(root)
    readonly property color cronAccent: accent
    readonly property color cronAccentHover: accentHover
    readonly property color panelFill: bgCard
    readonly property color panelBorder: isDark ? "#20FFFFFF" : "#126E4B2A"
    readonly property color sectionFill: isDark ? "#16110E" : "#FCF8F3"
    readonly property color fieldFill: isDark ? "#120E0C" : "#F7EFE6"
    readonly property color fieldHoverFill: isDark ? "#171210" : "#F9F3EB"
    readonly property color fieldBorder: isDark ? "#18FFFFFF" : "#14000000"
    readonly property color selectedRowFill: isDark ? "#211813" : "#FFF1E3"
    readonly property color selectedRowBorder: cronAccent

    function tr(zh, en) { return resolvedLang === "zh" ? zh : en }
    function workspaceString(key, fallbackZh, fallbackEn) { return CronWorkspaceLogic.workspaceString(root, key, fallbackZh, fallbackEn) }
    function automationHeaderCaption() { return CronWorkspaceLogic.automationHeaderCaption(root) }
    function statusItems() { return CronWorkspaceLogic.statusItems(root) }
    function statusLabel(statusKey) { return CronWorkspaceLogic.statusLabel(root, statusKey) }
    function statusColor(statusKey) { return CronWorkspaceLogic.statusColor(root, statusKey) }
    function statusSurface(statusKey) { return CronWorkspaceLogic.statusSurface(root, statusKey) }
    function summaryText(value, fallbackZh, fallbackEn) { return CronWorkspaceLogic.summaryText(root, value, fallbackZh, fallbackEn) }
    function icon(path) { return CronWorkspaceLogic.icon(path) }
    function labIcon(path) { return CronWorkspaceLogic.labIcon(path) }
    function scheduleModeHint() { return CronWorkspaceLogic.scheduleModeHint(root) }
    function deliveryHint() { return CronWorkspaceLogic.deliveryHint(root) }
    function taskStatusKey() { return CronWorkspaceLogic.taskStatusKey(root) }
    function taskSelectionPrompt() { return CronWorkspaceLogic.taskSelectionPrompt(root) }
    function emptyTaskStatusHint() { return CronWorkspaceLogic.emptyTaskStatusHint(root) }

    function playReveal() {
        revealOpacity = motionPageRevealStartOpacity
        revealAnimation.restart()
    }

    function playContentReveal() {
        contentRevealOpacity = motionPageRevealStartOpacity
        contentRevealShift = CronWorkspaceLogic.currentPaneDirection(root) >= 0 ? motionPageShiftSubtle : -motionPageShiftSubtle
        contentRevealAnimation.restart()
    }

    function switchPane(nextPane) {
        if (currentPane === nextPane)
            return
        currentPane = nextPane
    }

    function setDraft(path, value) {
        if (hasCronService)
            cronService.updateDraftField(path, value)
    }

    function chooseTask(taskId) {
        if (hasCronService)
            cronService.selectTask(taskId)
    }

    function openSelectedSession() {
        if (appRoot)
            appRoot.activeWorkspace = "sessions"
        if (hasCronService)
            cronService.openSelectedSession()
    }

    function openHeartbeatSession() {
        if (appRoot)
            appRoot.activeWorkspace = "sessions"
        if (hasHeartbeatService)
            heartbeatService.openHeartbeatSession()
    }

    function refreshCurrentPane() {
        if (currentPane === "checks" && hasHeartbeatService)
            heartbeatService.refresh()
        else if (hasCronService)
            cronService.refresh()
    }

    function draftString(key, fallbackValue) {
        var value = draft[key]
        return value === undefined || value === null ? String(fallbackValue || "") : String(value)
    }

    function draftBool(key, fallbackValue) {
        var value = draft[key]
        return value === undefined || value === null ? !!fallbackValue : Boolean(value)
    }

    onActiveChanged: {
        if (!active)
            return
        playReveal()
        if (hasCronService)
            cronService.refresh()
    }

    onCurrentPaneChanged: playContentReveal()

    Item {
        anchors.fill: parent
        opacity: root.revealOpacity

        Rectangle {
            anchors.fill: parent
            anchors.margins: 16
            radius: 30
            color: bgCard
            border.width: 1
            border.color: isDark ? "#20FFFFFF" : "#146E4B2A"

            Rectangle { anchors.fill: parent; radius: parent.radius; color: isDark ? "#08FFFFFF" : "#0DFFF7EF" }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 18
                spacing: 14

                CronWorkspaceHeader { workspace: root }

                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    opacity: root.contentRevealOpacity
                    transform: Translate { x: root.contentRevealShift }

                    CronWorkspaceTasksPane { workspace: root; deleteModal: deleteModal; visible: root.currentPane === "tasks" }
                    CronWorkspaceChecksPane { workspace: root; visible: root.currentPane === "checks" }
                }
            }
        }
    }

    CronWorkspaceDeleteModal { id: deleteModal; workspace: root }

    SequentialAnimation {
        id: revealAnimation

        NumberAnimation { target: root; property: "revealOpacity"; to: 1.0; duration: motionUi; easing.type: easeStandard }
    }

    SequentialAnimation {
        id: contentRevealAnimation

        ParallelAnimation {
            NumberAnimation { target: root; property: "contentRevealOpacity"; to: 1.0; duration: motionUi; easing.type: easeStandard }
            NumberAnimation { target: root; property: "contentRevealShift"; to: 0.0; duration: motionPanel; easing.type: easeEmphasis }
        }
    }
}
