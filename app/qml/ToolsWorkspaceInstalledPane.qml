import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

SplitView {
    id: root

    property var workspace
    property int reloadToken: 0
    objectName: "toolsWorkspaceInstalledSplit"

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
                title: workspace.tr("筛选", "Filters")
                placeholderText: workspace.tr("搜索能力或工具…", "Search tools…")
                queryText: workspace.hasToolsService && typeof workspace.toolsService.query !== "undefined" ? String(workspace.toolsService.query || "") : ""
                selectedFilter: workspace.hasToolsService ? workspace.toolsService.sourceFilter : "all"
                filters: [
                    { value: "all", zh: "全部", en: "All" },
                    { value: "builtin", zh: "内建", en: "Built-in" },
                    { value: "attention", zh: "异常/待配", en: "Errors / setup" }
                ]
            }

            ToolsWorkspaceCatalogPanel {
                Layout.fillWidth: true
                Layout.fillHeight: true
                workspace: root.workspace
                compactLayout: true
                title: workspace.tr("内建能力族", "Built-in families")
                itemCount: workspace.catalogCount
                model: workspace.catalogModel
                emptyTitle: workspace.tr("没有匹配的工具族", "No tool family matches this view")
                emptyDescription: workspace.tr("试试清空搜索，或切到 MCP 页面管理外部服务。", "Try clearing the search, or switch to the MCP page for external servers.")
            }
        }
    }

    ToolsWorkspaceFilterRail {
        visible: !workspace.compactLayout
        workspace: root.workspace
        compactLayout: false
        title: workspace.tr("筛选", "Filters")
        placeholderText: workspace.tr("搜索能力或工具…", "Search tools…")
        queryText: workspace.hasToolsService && typeof workspace.toolsService.query !== "undefined" ? String(workspace.toolsService.query || "") : ""
        selectedFilter: workspace.hasToolsService ? workspace.toolsService.sourceFilter : "all"
        filters: [
            { value: "all", zh: "全部", en: "All" },
            { value: "builtin", zh: "内建", en: "Built-in" },
            { value: "attention", zh: "异常/待配", en: "Errors / setup" }
        ]
    }

    ToolsWorkspaceCatalogPanel {
        visible: !workspace.compactLayout
        workspace: root.workspace
        compactLayout: false
        title: workspace.tr("内建能力族", "Built-in families")
        itemCount: workspace.catalogCount
        model: workspace.catalogModel
        emptyTitle: workspace.tr("没有匹配的工具族", "No tool family matches this view")
        emptyDescription: workspace.tr("试试清空搜索，或切到 MCP 页面管理外部服务。", "Try clearing the search, or switch to the MCP page for external servers.")
    }

    ToolsWorkspaceInstalledDetailPane {
        workspace: root.workspace
        compactLayout: root.workspace.compactLayout
        reloadToken: root.reloadToken
    }
}
