pragma ComponentBehavior: Bound

import QtQuick 2.15

Rectangle {
    required property var workspace

    implicitHeight: taskSummaryColumn.implicitHeight + 16
    radius: 16
    color: isDark ? "#181310" : "#FFF9F3"
    border.width: 1
    border.color: isDark ? "#12FFFFFF" : "#10000000"

    Column {
        id: taskSummaryColumn
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 10
        spacing: 6

        Row {
            width: parent.width
            spacing: 8

            SkillsWorkspaceBadge {
                labelText: workspace.discoverTaskLabel(workspace.discoverTask.state)
                tone: workspace.discoverTaskTone(workspace.discoverTask.state)
            }

            Text {
                text: workspace.discoverTask.kind === "install"
                    ? workspace.tr("导入任务", "Import task")
                    : workspace.tr("搜索任务", "Search task")
                color: textSecondary
                font.pixelSize: typeCaption
                visible: workspace.discoverTask.state !== "idle"
            }
        }

        Text {
            width: parent.width
            text: workspace.discoverTask.message
                ? workspace.discoverTask.message
                : workspace.tr(
                    "搜索或导入时，这里会显示当前任务状态。",
                    "Current search/import status will appear here."
                )
            color: workspace.discoverTask.state === "failed" ? statusError : textSecondary
            font.pixelSize: typeCaption
            wrapMode: Text.WordWrap
        }

        Text {
            width: parent.width
            visible: (workspace.discoverTask.reference || "").length > 0
            text: workspace.discoverTask.reference || ""
            color: accent
            font.pixelSize: typeCaption
            wrapMode: Text.WrapAnywhere
        }
    }
}
