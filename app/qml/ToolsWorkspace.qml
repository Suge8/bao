import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import "ToolsWorkspaceLogic.js" as ToolsWorkspaceLogic

Item {
    id: root
    objectName: "toolsWorkspaceRoot"

    property bool active: false
    property string currentScope: "installed"
    property var toolsService: null
    property var configService: null
    property string uiLanguage: "auto"
    property string autoLanguage: "en"
    property real revealOpacity: 1.0
    property real revealScale: 1.0
    property real revealShift: 0.0
    property int detailReloadToken: 0
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
    readonly property color accentMuted: windowRoot ? windowRoot.accentMuted : "transparent"
    readonly property color statusSuccess: windowRoot ? windowRoot.statusSuccess : "transparent"
    readonly property color statusError: windowRoot ? windowRoot.statusError : "transparent"
    readonly property int typeTitle: windowRoot ? Number(windowRoot.typeTitle || 0) : 0
    readonly property int typeBody: windowRoot ? Number(windowRoot.typeBody || 0) : 0
    readonly property int typeLabel: windowRoot ? Number(windowRoot.typeLabel || 0) : 0
    readonly property int typeMeta: windowRoot ? Number(windowRoot.typeMeta || 0) : 0
    readonly property int typeCaption: windowRoot ? Number(windowRoot.typeCaption || 0) : 0
    readonly property int weightBold: windowRoot ? Number(windowRoot.weightBold || 0) : 0
    readonly property int weightDemiBold: windowRoot ? Number(windowRoot.weightDemiBold || 0) : 0
    readonly property int weightMedium: windowRoot ? Number(windowRoot.weightMedium || 0) : 0
    readonly property int motionFast: windowRoot ? Number(windowRoot.motionFast || 0) : 0
    readonly property int easeStandard: windowRoot ? Number(windowRoot.easeStandard || 0) : 0
    readonly property int compactLayoutBreakpoint: 860
    readonly property bool compactLayout: width < compactLayoutBreakpoint
    readonly property int compactBrowserPaneHeight: 208
    readonly property int compactFilterPaneHeight: 124
    readonly property int compactListPaneHeight: 104
    readonly property int compactDetailPaneMinHeight: 116
    readonly property int listCacheBuffer: 720

    readonly property bool hasToolsService: toolsService !== null
    readonly property bool hasToolsSignals: hasToolsService
        && typeof toolsService.changed !== "undefined"
        && typeof toolsService.operationFinished !== "undefined"
    readonly property bool hasConfigService: configService !== null
    readonly property string effectiveUiLanguage: uiLanguage !== "auto" ? uiLanguage : (autoLanguage || "en")
    readonly property bool isZhLang: effectiveUiLanguage === "zh"
    readonly property var catalogModel: hasToolsService && typeof toolsService.catalogModel !== "undefined" ? toolsService.catalogModel : null
    readonly property var serverModel: hasToolsService && typeof toolsService.serverModel !== "undefined" ? toolsService.serverModel : null
    readonly property int catalogCount: hasToolsService && typeof toolsService.catalogCount !== "undefined" ? Number(toolsService.catalogCount || 0) : 0
    readonly property int serverCount: hasToolsService && typeof toolsService.serverCount !== "undefined" ? Number(toolsService.serverCount || 0) : 0
    readonly property string firstCatalogItemId: hasToolsService && typeof toolsService.firstCatalogItemId !== "undefined" ? String(toolsService.firstCatalogItemId || "") : ""
    readonly property string firstServerItemId: hasToolsService && typeof toolsService.firstServerItemId !== "undefined" ? String(toolsService.firstServerItemId || "") : ""
    readonly property var selectedItem: hasToolsService && typeof toolsService.selectedItem !== "undefined" ? (toolsService.selectedItem || ({})) : ({})
    readonly property string selectedItemId: hasToolsService && typeof toolsService.selectedItemId !== "undefined" ? String(toolsService.selectedItemId || "") : ""
    readonly property var overview: hasToolsService && typeof toolsService.overview !== "undefined" ? (toolsService.overview || ({})) : ({})
    readonly property var summaryMetrics: overview.summaryMetrics || []
    readonly property var exposureDomainOptions: overview.exposureDomainOptions || []
    readonly property var observabilityItems: overview.observability || []
    readonly property var selectedRuntimeStateDisplay: selectedItem.runtimeStateDisplay || null
    readonly property Component currentScopePane: currentScope === "installed"
        ? installedPaneComponent
        : (currentScope === "servers" ? serversPaneComponent : policiesPaneComponent)

    function tr(zh, en) { return isZhLang ? zh : en }
    function localizedText(value, fallback) { return ToolsWorkspaceLogic.localizedText(root, value, fallback) }
    function itemDisplayName(item) { return localizedText(item.displayName, item.name || "") }
    function itemDisplaySummary(item) { return localizedText(item.displaySummary, item.summary || "") }
    function itemDisplayDetail(item) { return localizedText(item.displayDetail, item.detail || item.summary || "") }
    function icon(path) { return "../resources/icons/vendor/iconoir/" + path + ".svg" }
    function labIcon(path) { return "../resources/icons/vendor/lucide-lab/" + path + ".svg" }
    function workspaceString(key, fallbackZh, fallbackEn) { return typeof strings === "object" && strings !== null && strings[key] ? String(strings[key]) : tr(fallbackZh, fallbackEn) }
    function itemIconSource(item) { return String(item.iconSource || labIcon("toolbox")) }
    function statusDetail(item) { return localizedText(item.statusDetailDisplay, item.statusDetail || "") }
    function readConfig(path, fallbackValue) {
        if (!hasConfigService)
            return fallbackValue
        var value = configService.getValue(path)
        return value === undefined || value === null ? fallbackValue : value
    }
    function toastMessage(code, ok) { return !ok ? code : (code === "saved" ? tr("工具配置已保存", "Tool settings saved") : code === "deleted" ? tr("MCP 服务已删除", "MCP server deleted") : code === "probe_ok" ? tr("连接测试成功", "Connection test succeeded") : code) }
    function playReveal() { revealOpacity = motionPageRevealStartOpacity; revealScale = motionPageRevealStartScale; revealShift = motionPageShiftSubtle; revealAnimation.restart() }
    function openCreateServerModal() { createServerModal.open() }
    function ensureSelectionForScope() {
        if (!hasToolsService || currentScope === "policies")
            return
        var firstItemId = currentScope === "servers" ? firstServerItemId : firstCatalogItemId
        if (!firstItemId)
            return
        if (!selectedItem.id || (currentScope === "installed" && selectedItem.kind !== "builtin") || (currentScope === "servers" && selectedItem.kind !== "mcp_server"))
            toolsService.selectItem(firstItemId)
    }

    onActiveChanged: if (active) { playReveal(); ensureSelectionForScope() }
    onCurrentScopeChanged: {
        if (hasToolsService && currentScope === "installed" && toolsService.sourceFilter === "mcp")
            toolsService.setSourceFilter("all")
        else if (hasToolsService && currentScope === "servers" && toolsService.sourceFilter === "builtin")
            toolsService.setSourceFilter("mcp")
        ensureSelectionForScope()
    }
    onSelectedItemIdChanged: detailReloadToken += 1
    Component.onCompleted: ensureSelectionForScope()

    Connections {
        target: root.hasToolsSignals ? toolsService : null

        function onChanged() { root.ensureSelectionForScope() }
        function onOperationFinished(message, ok) { globalToast.show(root.toastMessage(message, ok), ok) }
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

            Rectangle { anchors.fill: parent; radius: parent.radius; color: isDark ? "#08FFFFFF" : "#0DFFF7EF" }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: root.compactLayout ? 16 : 18
                spacing: root.compactLayout ? 12 : 14

                ToolsWorkspaceHeader { workspace: root }

                Loader {
                    id: scopePaneLoader
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.preferredWidth: 1
                    Layout.preferredHeight: 1
                    active: true
                    sourceComponent: root.currentScopePane
                }
            }
        }
    }

    Component {
        id: installedPaneComponent
        ToolsWorkspaceInstalledPane {
            workspace: root
            reloadToken: root.detailReloadToken
        }
    }

    Component {
        id: serversPaneComponent
        ToolsWorkspaceServersPane {
            workspace: root
            reloadToken: root.detailReloadToken
        }
    }

    Component {
        id: policiesPaneComponent
        ToolsWorkspacePoliciesPane {
            workspace: root
        }
    }

    ToolsWorkspaceCreateServerModal { id: createServerModal; workspace: root }

    SequentialAnimation {
        id: revealAnimation

        ParallelAnimation {
            NumberAnimation { target: root; property: "revealOpacity"; to: 1.0; duration: motionUi; easing.type: easeStandard }
            NumberAnimation { target: root; property: "revealScale"; to: 1.0; duration: motionPanel; easing.type: easeEmphasis }
            NumberAnimation { target: root; property: "revealShift"; to: 0.0; duration: motionPanel; easing.type: easeEmphasis }
        }
    }
}
