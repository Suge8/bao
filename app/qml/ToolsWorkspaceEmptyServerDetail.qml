import QtQuick 2.15
import QtQuick.Layouts 1.15
import "ToolsWorkspaceLogic.js" as ToolsWorkspaceLogic

ColumnLayout {
    id: root

    property var workspace

    readonly property color textPrimary: workspace ? workspace.textPrimary : "transparent"
    readonly property color textSecondary: workspace ? workspace.textSecondary : "transparent"
    readonly property int typeTitle: workspace ? workspace.typeTitle : 18
    readonly property int typeBody: workspace ? workspace.typeBody : 14
    readonly property int weightBold: workspace ? workspace.weightBold : Font.Normal

    spacing: 12

    Text {
        objectName: "toolsServerDetailEmptyTitle"
        Layout.fillWidth: true
        text: workspace.tr("选择一个 MCP 服务", "Choose an MCP server")
        color: root.textPrimary
        font.pixelSize: root.typeTitle
        font.weight: root.weightBold
    }

    Text {
        objectName: "toolsServerDetailEmptyDescription"
        Layout.fillWidth: true
        text: ToolsWorkspaceLogic.emptyServerDetailDescription(workspace)
        color: root.textSecondary
        font.pixelSize: root.typeBody
        wrapMode: Text.WordWrap
    }
}
