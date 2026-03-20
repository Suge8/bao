import QtQuick 2.15
import QtQuick.Layouts 1.15
import "ToolsWorkspaceLogic.js" as ToolsWorkspaceLogic

ToolsWorkspaceFormScroll {
    id: root

    property var workspace

    ToolsWorkspaceDetailCard {
        workspace: root.workspace
        Text {
            Layout.fillWidth: true
            text: workspace.tr("当前状态", "Current state")
            color: root.textPrimary
            font.pixelSize: root.typeLabel
            font.weight: root.weightBold
        }

        Text {
            Layout.fillWidth: true
            text: workspace.statusDetail(workspace.selectedItem) || ""
            color: root.textSecondary
            font.pixelSize: root.typeBody
            wrapMode: Text.WordWrap
        }

        Text {
            Layout.fillWidth: true
            visible: text.length > 0
            text: ToolsWorkspaceLogic.runtimeStateText(workspace, workspace.selectedItem)
            color: root.textSecondary
            font.pixelSize: root.typeCaption
            font.weight: root.weightBold
            wrapMode: Text.WordWrap
        }

        Text {
            Layout.fillWidth: true
            visible: text.length > 0
            text: ToolsWorkspaceLogic.exposureNote(workspace, workspace.selectedItem)
            color: root.textSecondary
            font.pixelSize: root.typeCaption
            wrapMode: Text.WordWrap
        }

        Text {
            Layout.fillWidth: true
            visible: text.length > 0
            text: ToolsWorkspaceLogic.attentionAction(workspace, workspace.selectedItem)
            color: root.accent
            font.pixelSize: root.typeCaption
            font.weight: root.weightBold
            wrapMode: Text.WordWrap
        }

        Repeater {
            model: workspace.selectedItem.metaLines || []

            delegate: Text {
                required property var modelData
                Layout.fillWidth: true
                text: "• " + String(modelData)
                color: root.textSecondary
                font.pixelSize: root.typeMeta
                wrapMode: Text.WordWrap
            }
        }
    }
}
