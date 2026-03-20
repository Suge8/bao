pragma ComponentBehavior: Bound

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "SkillsWorkspaceLogic.js" as SkillsWorkspaceLogic

Item {
    id: root
    objectName: "skillsWorkspaceRoot"

    property bool active: false
    property var skillsService: null
    property string currentMode: "installed"
    property string draftSkillId: ""
    property bool draftDirty: false
    property bool syncingDraft: false
    property var editorRef: null
    property real revealOpacity: 1.0
    property real revealScale: 1.0
    property real revealShift: 0.0
    readonly property int compactLayoutBreakpoint: 860
    readonly property bool compactLayout: width < compactLayoutBreakpoint
    readonly property int compactBrowserPaneHeight: 220
    readonly property int compactFilterPaneHeight: 126
    readonly property int compactListPaneHeight: 104
    readonly property int compactDetailPaneMinHeight: 116
    readonly property int listCacheBuffer: 720

    readonly property bool hasSkillsService: skillsService !== null
    readonly property bool hasSkillsSignals: hasSkillsService
        && typeof skillsService.changed !== "undefined"
        && typeof skillsService.operationFinished !== "undefined"
    readonly property var overview: hasSkillsService ? (skillsService.overview || {}) : ({})
    readonly property var installedSkillsModel: hasSkillsService ? skillsService.skillsModel : null
    readonly property int installedSkillCount: hasSkillsService ? Number(skillsService.totalCount || 0) : 0
    readonly property var selectedSkill: hasSkillsService ? (skillsService.selectedSkill || {}) : ({})
    readonly property string selectedSkillId: hasSkillsService ? String(skillsService.selectedSkillId || "") : ""
    readonly property string selectedContent: hasSkillsService ? String(skillsService.selectedContent || "") : ""
    readonly property string skillQueryValue: hasSkillsService ? String(skillsService.query || "") : ""
    readonly property string sourceFilterValue: hasSkillsService ? String(skillsService.sourceFilter || "all") : "all"
    readonly property bool serviceBusy: hasSkillsService
        && typeof skillsService.busy !== "undefined"
        && skillsService.busy
    readonly property var discoverResultsModel: hasSkillsService ? skillsService.discoverResultsModel : null
    readonly property int discoverResultCount: hasSkillsService ? Number(skillsService.discoverResultCount || 0) : 0
    readonly property var selectedDiscoverItem: hasSkillsService ? (skillsService.selectedDiscoverItem || {}) : ({})
    readonly property string selectedDiscoverId: hasSkillsService ? String(skillsService.selectedDiscoverId || "") : ""
    readonly property string discoverQueryValue: hasSkillsService ? String(skillsService.discoverQuery || "") : ""
    readonly property string discoverReferenceValue: hasSkillsService ? String(skillsService.discoverReference || "") : ""
    readonly property var discoverTask: hasSkillsService
        ? (skillsService.discoverTask || {})
        : ({ state: "idle", kind: "", message: "", reference: "" })
    readonly property var installedFilterOptions: [
        { value: "all", zh: "全部", en: "All" },
        { value: "ready", zh: "现在可用", en: "Ready now" },
        { value: "needs_setup", zh: "需设置", en: "Needs setup" },
        { value: "instruction_only", zh: "仅指导", en: "Instruction only" },
        { value: "user", zh: "用户技能", en: "User skills" },
        { value: "shadowed", zh: "已覆盖", en: "Overridden" }
    ]
    readonly property string effectiveUiLanguage: {
        if (typeof uiLanguage === "string" && uiLanguage !== "auto")
            return uiLanguage
        if (typeof autoLanguage === "string")
            return autoLanguage
        return "en"
    }
    readonly property bool isZhLang: effectiveUiLanguage === "zh"

    function tr(zh, en) { return isZhLang ? zh : en }
    function icon(path) { return SkillsWorkspaceLogic.icon(path) }
    function labIcon(path) { return SkillsWorkspaceLogic.labIcon(path) }
    function workspaceString(key, fallbackZh, fallbackEn) { return SkillsWorkspaceLogic.workspaceString(root, key, fallbackZh, fallbackEn) }
    function localizedText(value, fallback) { return SkillsWorkspaceLogic.localizedText(root, value, fallback) }
    function localizedSkillName(skill) { return SkillsWorkspaceLogic.localizedSkillName(root, skill) }
    function localizedSkillDescription(skill) { return SkillsWorkspaceLogic.localizedSkillDescription(root, skill) }
    function skillIconSource(skill) { return SkillsWorkspaceLogic.skillIconSource(root, skill) }
    function sourceLabel(skill) { return SkillsWorkspaceLogic.sourceLabel(root, skill) }
    function primaryStatusLabel(skill) { return SkillsWorkspaceLogic.primaryStatusLabel(root, skill) }
    function primaryStatusColor(skill) { return SkillsWorkspaceLogic.primaryStatusColor(root, skill) }
    function selectedSkillValue(key, fallbackValue) { return SkillsWorkspaceLogic.selectedValue(root.selectedSkill, key, fallbackValue) }
    function selectedSkillFlag(key) { return SkillsWorkspaceLogic.selectedFlag(root.selectedSkill, key) }
    function selectedDiscoverValue(key, fallbackValue) { return SkillsWorkspaceLogic.selectedValue(root.selectedDiscoverItem, key, fallbackValue) }
    function discoverTaskTone(state) { return SkillsWorkspaceLogic.discoverTaskTone(root, state) }
    function discoverTaskLabel(state) { return SkillsWorkspaceLogic.discoverTaskLabel(root, state) }
    function toastMessage(code, ok) { return SkillsWorkspaceLogic.toastMessage(root, code, ok) }
    function installedCountSummary() { return SkillsWorkspaceLogic.installedCountSummary(root) }
    function discoverPublisherVersion(item) { return SkillsWorkspaceLogic.discoverPublisherVersion(item) }

    function playReveal() {
        revealOpacity = motionPageRevealStartOpacity
        revealScale = motionPageRevealStartScale
        revealShift = motionPageShiftSubtle
        revealAnimation.restart()
    }

    function syncDraft(force) {
        SkillsWorkspaceLogic.syncDraft(root, force)
    }

    onActiveChanged: if (active) playReveal()
    onSelectedSkillIdChanged: syncDraft(true)
    onSelectedContentChanged: syncDraft(false)
    Component.onCompleted: syncDraft(true)

    Connections {
        target: root.hasSkillsSignals ? skillsService : null

        function onOperationFinished(message, ok) {
            globalToast.show(root.toastMessage(message, ok), ok)
            if (ok && (message === "deleted" || message === "installed"))
                root.syncDraft(true)
        }
    }

    Item {
        anchors.fill: parent
        opacity: root.revealOpacity
        scale: root.revealScale
        transform: Translate { x: root.revealShift }

        Rectangle {
            anchors.fill: parent
            anchors.margins: 16
            radius: 30
            color: bgCard
            border.width: 1
            border.color: isDark ? "#20FFFFFF" : "#146E4B2A"

            Rectangle {
                anchors.fill: parent
                radius: parent.radius
                color: isDark ? "#08FFFFFF" : "#0DFFF7EF"
            }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: root.compactLayout ? 18 : 22
                spacing: root.compactLayout ? 14 : 18

                SkillsWorkspaceHeader {
                    workspace: root
                    createSkillModal: createSkillModal
                }

                StackLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    currentIndex: root.currentMode === "installed" ? 0 : 1

                    SkillsWorkspaceInstalledPane { workspace: root }
                    SkillsWorkspaceDiscoverPane { workspace: root }
                }
            }
        }
    }

    SkillsWorkspaceCreateSkillModal {
        id: createSkillModal
        workspace: root
    }

    SequentialAnimation {
        id: revealAnimation

        ParallelAnimation {
            NumberAnimation { target: root; property: "revealOpacity"; to: 1.0; duration: motionUi; easing.type: easeStandard }
            NumberAnimation { target: root; property: "revealScale"; to: 1.0; duration: motionPanel; easing.type: easeEmphasis }
            NumberAnimation { target: root; property: "revealShift"; to: 0.0; duration: motionPanel; easing.type: easeEmphasis }
        }
    }
}
