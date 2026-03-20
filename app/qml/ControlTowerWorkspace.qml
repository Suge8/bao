import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "ControlTowerWorkspaceLogic.js" as Logic

Item {
    id: root
    objectName: "controlTowerWorkspaceRoot"

    property bool active: false
    property var supervisorService: null
    property var appRoot: null

    readonly property bool hasSupervisorService: supervisorService !== null
    readonly property var overview: hasSupervisorService ? (supervisorService.overview || {}) : ({})
    readonly property var profilesModel: hasSupervisorService ? supervisorService.profilesModel : null
    readonly property var workingModel: hasSupervisorService ? supervisorService.workingModel : null
    readonly property var completedModel: hasSupervisorService ? supervisorService.completedModel : null
    readonly property var automationModel: hasSupervisorService ? supervisorService.automationModel : null
    readonly property var attentionModel: hasSupervisorService ? supervisorService.attentionModel : null
    readonly property int profileCount: hasSupervisorService ? Number(supervisorService.profileCount || 0) : 0
    readonly property int workingCount: hasSupervisorService ? Number(supervisorService.workingCount || 0) : 0
    readonly property int completedCount: hasSupervisorService ? Number(supervisorService.completedCount || 0) : 0
    readonly property int automationCount: hasSupervisorService ? Number(supervisorService.automationCount || 0) : 0
    readonly property int attentionCount: hasSupervisorService ? Number(supervisorService.attentionCount || 0) : 0
    readonly property var selectedProfile: hasSupervisorService ? (supervisorService.selectedProfile || {}) : ({})
    readonly property string selectedProfileId: String((selectedProfile || {}).id || "")
    readonly property bool hasSelectedProfile: selectedProfileId !== ""
    readonly property var overviewSectionKinds: ["working", "completed", "attention", "automation"]
    readonly property bool isChinese: typeof effectiveLang === "string" ? effectiveLang === "zh" : uiLanguage === "zh"
    readonly property bool workspaceIsDark: isDark
    readonly property color workspaceTextPrimary: textPrimary
    readonly property color workspaceTextSecondary: textSecondary
    readonly property color workspaceTextTertiary: textTertiary
    readonly property color workspaceBorderSubtle: borderSubtle
    readonly property int workspaceTypeTitle: typeTitle
    readonly property int workspaceTypeBody: typeBody
    readonly property int workspaceTypeMeta: typeMeta
    readonly property int workspaceTypeCaption: typeCaption
    readonly property int workspaceTypeLabel: typeLabel
    readonly property int workspaceWeightBold: weightBold
    readonly property int workspaceWeightMedium: weightMedium
    readonly property real workspaceMotionFast: motionFast
    readonly property int workspaceEaseStandard: easeStandard
    readonly property color workspaceActionAccent: accent
    readonly property color workspaceActionCurrentHoverFill: bgCardHover
    readonly property color workspaceStatusSuccess: statusSuccess
    readonly property color workspaceStatusError: statusError
    readonly property color panelFill: bgCard
    readonly property color panelBorder: isDark ? "#20FFFFFF" : "#12000000"
    readonly property color sectionFill: isDark ? "#130E0B" : "#FFFCF8"
    readonly property color sectionBorder: isDark ? "#16FFFFFF" : "#14000000"
    readonly property color tileFill: isDark ? "#17110D" : "#FFFAF5"
    readonly property color tileHover: isDark ? "#1E1511" : "#FFF3E8"
    readonly property color tileActive: isDark ? "#241913" : "#FFEEDC"
    readonly property int compactLayoutBreakpoint: 720
    readonly property int wideProfilesPaneWidth: 328
    readonly property int overviewMinimumWidth: 320
    readonly property int compactOverviewMinimumHeight: 220
    readonly property bool compactLayout: width < compactLayoutBreakpoint
    function hydrateIfNeeded() {
        if (!active || !hasSupervisorService)
            return
        if (supervisorService.hydrateIfNeeded)
            supervisorService.hydrateIfNeeded()
    }

    function accentColor(key) { return Logic.accentColor(root, key) }
    function channelLabel(key) { return Logic.channelLabel(root, key) }
    function channelIconSource(key) { return Logic.channelIconSource(root, key) }
    function icon(path) { return Logic.icon(root, path) }
    function labIcon(path) { return Logic.labIcon(root, path) }
    function workspaceString(key, fallbackZh, fallbackEn) { return Logic.workspaceString(root, key, fallbackZh, fallbackEn) }
    function solidIcon(path) { return Logic.solidIcon(root, path) }
    function sectionTitle(kind) { return Logic.sectionTitle(root, kind) }
    function sectionAccentKey(kind) { return Logic.sectionAccentKey(root, kind) }
    function sectionItems(kind) { return Logic.sectionItems(root, kind) }
    function sectionCount(kind) { return Logic.sectionCount(root, kind) }
    function profileIsCurrent(profile) { return Logic.profileIsCurrent(root, profile) }
    function profileIsSelected(profile) { return Logic.profileIsSelected(root, profile) }
    function profileAccentKey(profile) { return Logic.profileAccentKey(root, profile) }
    function profileTimeLabel(profile) { return Logic.profileTimeLabel(root, profile) }
    function profileActionText(profile) { return Logic.profileActionText(root, profile) }
    function sharedHubLive() { return Logic.sharedHubLive(root) }
    function scopeTitle() { return Logic.scopeTitle(root) }
    function scopeCaption() { return Logic.scopeCaption(root) }
    function totalSessionCount() { return Logic.totalSessionCount(root) }
    function itemTimeLabel(item) { return Logic.itemTimeLabel(root, item) }
    function loaderItemHeight(item) { return Logic.loaderItemHeight(root, item) }
    function itemGlyphSources(item) { return Logic.itemGlyphSources(root, item) }
    function emptyTitle(kind) { return Logic.emptyTitle(root, kind) }
    function selectProfile(profileId) { if (hasSupervisorService) supervisorService.selectProfile(profileId) }
    function activateProfile(profileId) { if (hasSupervisorService) supervisorService.activateProfile(profileId) }
    function openItem(item) { if (hasSupervisorService && Boolean((item || {}).canOpen)) { supervisorService.selectItem(String(item.id || "")); supervisorService.openSelectedTarget() } }

    onActiveChanged: hydrateIfNeeded()

    Rectangle {
        anchors.fill: parent
        anchors.margins: 16
        radius: 30
        color: panelFill
        border.width: 1
        border.color: panelBorder
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 18

        ControlTowerHeroPanel {
            workspaceRoot: root
            compactLayout: root.compactLayout
            isDark: root.workspaceIsDark
            textPrimary: root.workspaceTextPrimary
            textSecondary: root.workspaceTextSecondary
            borderSubtle: root.workspaceBorderSubtle
            typeTitle: root.workspaceTypeTitle
            typeMeta: root.workspaceTypeMeta
            typeCaption: root.workspaceTypeCaption
            weightBold: root.workspaceWeightBold
            weightMedium: root.workspaceWeightMedium
        }

        SplitView {
            id: mainSplit
            objectName: "controlTowerMainSplit"
            Layout.fillWidth: true
            Layout.fillHeight: true
            orientation: root.compactLayout ? Qt.Vertical : Qt.Horizontal
            spacing: root.compactLayout ? 12 : 14

            handle: WorkspaceSplitHandle {}

            ControlTowerProfilesPane {
                workspaceRoot: root
                profilesModel: root.profilesModel
                profileCount: root.profileCount
                compactLayout: root.compactLayout
                isDark: root.workspaceIsDark
                textPrimary: root.workspaceTextPrimary
                textSecondary: root.workspaceTextSecondary
                textTertiary: root.workspaceTextTertiary
                tileFill: root.tileFill
                tileHover: root.tileHover
                tileActive: root.tileActive
                actionAccent: root.workspaceActionAccent
                actionCurrentHoverFill: root.workspaceActionCurrentHoverFill
                statusSuccess: root.workspaceStatusSuccess
                statusError: root.workspaceStatusError
                motionFast: root.workspaceMotionFast
                easeStandard: root.workspaceEaseStandard
                typeBody: root.workspaceTypeBody
                typeCaption: root.workspaceTypeCaption
                weightBold: root.workspaceWeightBold
                weightMedium: root.workspaceWeightMedium
            }

            Item {
                objectName: "controlTowerOverviewPane"
                SplitView.fillWidth: true
                SplitView.fillHeight: true
                SplitView.preferredWidth: root.compactLayout
                    ? mainSplit.width
                    : Math.max(root.overviewMinimumWidth, mainSplit.width - root.wideProfilesPaneWidth - mainSplit.spacing)
                SplitView.minimumWidth: root.overviewMinimumWidth
                SplitView.minimumHeight: root.compactLayout ? root.compactOverviewMinimumHeight : 0

                Flickable {
                    id: overviewScroll
                    objectName: "controlTowerOverviewScroll"
                    anchors.fill: parent
                    clip: true
                    contentWidth: width
                    contentHeight: overviewGrid.implicitHeight
                    interactive: contentHeight > height
                    boundsBehavior: Flickable.StopAtBounds
                    ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

                    GridLayout {
                        id: overviewGrid
                        width: overviewScroll.width
                        columns: width >= 860 ? 2 : 1
                        rowSpacing: 14
                        columnSpacing: 14
                        readonly property real laneColumnWidth: columns <= 1
                            ? width
                            : Math.max(0, (width - columnSpacing * (columns - 1)) / columns)

                        Repeater {
                            model: root.overviewSectionKinds

                            delegate: Item {
                                required property var modelData
                                readonly property string sectionKey: String(modelData || "")
                                Layout.fillWidth: true
                                Layout.preferredWidth: overviewGrid.laneColumnWidth
                                Layout.preferredHeight: lanePanel.implicitHeight
                                implicitWidth: overviewGrid.laneColumnWidth
                                implicitHeight: lanePanel.implicitHeight

                                ControlTowerLanePanel {
                                    id: lanePanel
                                    anchors.fill: parent
                                    workspaceRoot: root
                                    sectionKind: sectionKey
                                    sectionModel: root.sectionItems(sectionKey)
                                    sectionItemCount: root.sectionCount(sectionKey)
                                    isDark: root.workspaceIsDark
                                    textPrimary: root.workspaceTextPrimary
                                    textSecondary: root.workspaceTextSecondary
                                    textTertiary: root.workspaceTextTertiary
                                    sectionFill: root.sectionFill
                                    sectionBorder: root.sectionBorder
                                    tileActive: root.tileActive
                                    tileHover: root.tileHover
                                    motionFast: root.workspaceMotionFast
                                    easeStandard: root.workspaceEaseStandard
                                    typeBody: root.workspaceTypeBody
                                    typeMeta: root.workspaceTypeMeta
                                    typeCaption: root.workspaceTypeCaption
                                    typeLabel: root.workspaceTypeLabel
                                    weightBold: root.workspaceWeightBold
                                    weightMedium: root.workspaceWeightMedium
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
