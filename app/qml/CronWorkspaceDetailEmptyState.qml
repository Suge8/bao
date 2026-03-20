import QtQuick 2.15

Item {
    id: root

    property var workspace

    Column {
        anchors.centerIn: parent
        width: Math.min(parent.width - 40, 320)
        spacing: 10

        Text {
            objectName: "cronDetailEmptyTitle"
            width: parent.width
            text: workspace.hasCronService && workspace.cronService.totalTaskCount === 0
                ? workspace.tr("从右上角创建第一个任务", "Create your first task from the top right")
                : workspace.taskSelectionPrompt()
            color: workspace.textPrimary
            font.pixelSize: workspace.typeTitle
            font.weight: workspace.weightBold
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
        }

        Text {
            objectName: "cronDetailEmptyDescription"
            width: parent.width
            text: workspace.hasCronService && workspace.cronService.totalTaskCount === 0
                ? workspace.tr(
                    "创建后，这里会一步步引导你设置执行时间和消息内容。",
                    "After you create one, this area guides you through the time and message setup."
                )
                : workspace.tr(
                    "选中后，这里会一步步引导你完成设置。",
                    "After you select one, this area guides you through the setup step by step."
                )
            color: workspace.textSecondary
            font.pixelSize: workspace.typeBody
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
        }
    }
}
