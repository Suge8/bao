import QtQuick 2.15
import QtQuick.Layouts 1.15
import "ToolsWorkspaceLogic.js" as ToolsWorkspaceLogic

WorkspaceAdaptiveHeader {
    id: root

    property var workspace

    compactLayout: workspace.compactLayout
    panelColor: workspace.isDark ? "#15100D" : "#FFF7F0"
    panelBorderColor: workspace.isDark ? "#22FFFFFF" : "#14000000"
    overlayColor: workspace.isDark ? "#0BFFFFFF" : "#08FFFFFF"
    overlayVisible: true
    sideGlowVisible: false
    accentBlobVisible: false
    padding: 14

    introContent: Component {
        Item {
            objectName: "toolsWorkspaceHeaderIntro"
            implicitHeight: introRow.implicitHeight

            Row {
                id: introRow
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                spacing: 10

                WorkspaceHeroIcon { iconSource: workspace.labIcon("toolbox") }

                Column {
                    anchors.verticalCenter: parent.verticalCenter
                    width: Math.max(0, introRow.width - 44)
                    spacing: 2

                    Text {
                        width: parent.width
                        text: ToolsWorkspaceLogic.scopeIntroTitle(workspace)
                        color: workspace.textPrimary
                        font.pixelSize: workspace.typeTitle - 1
                        font.weight: workspace.weightBold
                        elide: Text.ElideRight
                    }

                    Text {
                        width: parent.width
                        text: ToolsWorkspaceLogic.scopeIntroCaption(workspace)
                        color: workspace.textSecondary
                        font.pixelSize: workspace.typeMeta
                        maximumLineCount: 1
                        elide: Text.ElideRight
                    }
                }
            }
        }
    }

    centerContent: Component {
        Item {
            objectName: "toolsWorkspaceHeaderTabs"
            implicitWidth: scopeTabBar.implicitWidth
            implicitHeight: scopeTabBar.implicitHeight

            SegmentedTabs {
                id: scopeTabBar
                anchors.centerIn: parent
                preferredTrackWidth: 250
                fillSegments: true
                currentValue: workspace.currentScope
                items: [
                    { value: "installed", label: workspace.tr("已安装", "Installed"), icon: workspace.labIcon("toolbox") },
                    { value: "servers", label: "MCP", icon: workspace.icon("database-settings") },
                    { value: "policies", label: workspace.tr("策略", "Policies"), icon: workspace.icon("ios-settings") }
                ]
                onSelected: function(value) { workspace.currentScope = value }
            }
        }
    }

    trailingContent: Component {
        Item {
            objectName: "toolsWorkspaceHeaderActions"
            implicitWidth: actionRow.implicitWidth
            implicitHeight: actionRow.implicitHeight

            RowLayout {
                id: actionRow
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                spacing: 8

                AsyncActionButton {
                    visible: workspace.currentScope === "servers"
                    text: workspace.hasToolsService && workspace.toolsService.busy
                        ? workspace.tr("测试中", "Testing")
                        : workspace.tr("新增 MCP 服务", "Add MCP server")
                    iconSource: workspace.icon("circle-spark")
                    busy: workspace.hasToolsService
                        && typeof workspace.toolsService.busy !== "undefined"
                        && workspace.toolsService.busy
                    minHeight: 34
                    horizontalPadding: 18
                    fillColor: workspace.accent
                    hoverFillColor: workspace.accentHover
                    onClicked: workspace.openCreateServerModal()
                }
            }
        }
    }

    supportingContent: Component {
        Flow {
            objectName: "toolsWorkspaceHeaderMetrics"
            width: parent ? parent.width : 0
            spacing: 8

            Repeater {
                model: workspace.summaryMetrics

                delegate: ToolsWorkspaceMetricChip {
                    required property var modelData
                    workspace: root.workspace
                    label: ToolsWorkspaceLogic.summaryMetricLabel(workspace, modelData.displayLabel || modelData.key)
                    value: String(modelData.value)
                    tone: modelData.tone
                }
            }
        }
    }
}
