import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "ToolsWorkspaceLogic.js" as ToolsWorkspaceLogic

SplitView {
    id: root

    property var workspace
    property int reloadToken: 0
    objectName: "toolsWorkspaceServersSplit"

    Layout.fillWidth: true
    Layout.fillHeight: true
    orientation: workspace.compactLayout ? Qt.Vertical : Qt.Horizontal
    spacing: workspace.compactLayout ? 10 : 10
    handle: WorkspaceSplitHandle {}

    Item {
        visible: workspace.compactLayout
        SplitView.preferredWidth: 0
        SplitView.fillWidth: true
        SplitView.preferredHeight: workspace.compactBrowserPaneHeight
        SplitView.minimumHeight: workspace.compactBrowserPaneHeight

        ColumnLayout {
            anchors.fill: parent
            spacing: 10

            ToolsWorkspaceFilterRail {
                Layout.fillWidth: true
                Layout.preferredHeight: workspace.compactFilterPaneHeight
                Layout.minimumHeight: workspace.compactFilterPaneHeight
                workspace: root.workspace
                compactLayout: true
                title: workspace.tr("MCP 筛选", "MCP filters")
                placeholderText: workspace.tr("搜索服务或工具…", "Search servers…")
                queryText: workspace.hasToolsService && typeof workspace.toolsService.query !== "undefined" ? String(workspace.toolsService.query || "") : ""
                selectedFilter: workspace.hasToolsService ? workspace.toolsService.sourceFilter : "all"
                filters: [
                    { value: "all", zh: "全部", en: "All" },
                    { value: "mcp", zh: "仅 MCP", en: "Only MCP" },
                    { value: "attention", zh: "异常/待配", en: "Errors / setup" }
                ]
            }

            ToolsWorkspaceCatalogPanel {
                Layout.fillWidth: true
                Layout.fillHeight: true
                workspace: root.workspace
                compactLayout: true
                serverMode: true
                title: workspace.tr("已配置服务", "Configured servers")
                itemCount: workspace.serverCount
                model: workspace.serverModel
                emptyTitle: workspace.tr("还没有 MCP 服务", "No MCP servers yet")
                emptyDescription: ToolsWorkspaceLogic.serversEmptyDescription(workspace)
            }
        }
    }

    ToolsWorkspaceFilterRail {
        visible: !workspace.compactLayout
        workspace: root.workspace
        compactLayout: false
        title: workspace.tr("MCP 筛选", "MCP filters")
        placeholderText: workspace.tr("搜索服务或工具…", "Search servers…")
        queryText: workspace.hasToolsService && typeof workspace.toolsService.query !== "undefined" ? String(workspace.toolsService.query || "") : ""
        selectedFilter: workspace.hasToolsService ? workspace.toolsService.sourceFilter : "all"
        filters: [
            { value: "all", zh: "全部", en: "All" },
            { value: "mcp", zh: "仅 MCP", en: "Only MCP" },
            { value: "attention", zh: "异常/待配", en: "Errors / setup" }
        ]
    }

    ToolsWorkspaceCatalogPanel {
        visible: !workspace.compactLayout
        workspace: root.workspace
        compactLayout: false
        serverMode: true
        title: workspace.tr("已配置服务", "Configured servers")
        itemCount: workspace.serverCount
        model: workspace.serverModel
        emptyTitle: workspace.tr("还没有 MCP 服务", "No MCP servers yet")
        emptyDescription: ToolsWorkspaceLogic.serversEmptyDescription(workspace)
    }

    ToolsWorkspaceServerDetailPane {
        workspace: root.workspace
        compactLayout: root.workspace.compactLayout
        reloadToken: root.reloadToken
    }
}
