import QtQuick 2.15
import QtQuick.Layouts 1.15
import "ToolsWorkspaceLogic.js" as ToolsWorkspaceLogic

Rectangle {
    id: root

    property var workspace
    property var item

    readonly property bool isDark: workspace ? workspace.isDark : false
    readonly property color accent: workspace ? workspace.accent : "transparent"
    readonly property color textSecondary: workspace ? workspace.textSecondary : "transparent"
    readonly property int typeCaption: workspace ? workspace.typeCaption : 12
    readonly property int weightBold: workspace ? workspace.weightBold : Font.Normal

    Layout.fillWidth: true
    implicitHeight: summaryColumn.implicitHeight + 16
    radius: 16
    color: root.isDark ? "#181310" : "#FFF9F3"
    border.width: 1
    border.color: root.isDark ? "#12FFFFFF" : "#10000000"

    Column {
        id: summaryColumn
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 10
        spacing: 6

        Flow {
            width: parent.width
            spacing: 8

            Repeater {
                model: ToolsWorkspaceLogic.listBadges(root.workspace, root.item)

                delegate: ToolsWorkspaceBadge {
                    required property var modelData
                    workspace: root.workspace
                    text: modelData.text
                    tone: modelData.tone
                }
            }
        }

        Text {
            width: parent.width
            visible: text.length > 0
            text: ToolsWorkspaceLogic.detailStatusNote(root.workspace, root.item)
            color: ToolsWorkspaceLogic.statusTone(root.workspace, root.item)
            font.pixelSize: root.typeCaption
            font.weight: root.weightBold
            wrapMode: Text.WordWrap
        }

        Text {
            width: parent.width
            text: ToolsWorkspaceLogic.includesSummary(root.workspace, root.item)
            color: root.textSecondary
            font.pixelSize: root.typeCaption
            wrapMode: Text.WordWrap
        }

        Text {
            width: parent.width
            visible: text.length > 0
            text: ToolsWorkspaceLogic.exposureNote(root.workspace, root.item)
            color: root.textSecondary
            font.pixelSize: root.typeCaption
            wrapMode: Text.WordWrap
        }

        Text {
            width: parent.width
            visible: text.length > 0
            text: ToolsWorkspaceLogic.attentionAction(root.workspace, root.item)
            color: root.accent
            font.pixelSize: root.typeCaption
            font.weight: root.weightBold
            wrapMode: Text.WordWrap
        }
    }
}
