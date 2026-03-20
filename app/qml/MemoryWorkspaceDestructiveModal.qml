import QtQuick 2.15

AppModal {
    id: modal

    required property var workspaceRoot

    title: workspaceRoot.destructiveAction === "clearMemory"
        ? workspaceRoot.tr("清空该类记忆？", "Clear this memory category?")
        : workspaceRoot.tr("删除这条经验？", "Delete this experience?")
    closeText: workspaceRoot.tr("取消", "Cancel")
    showDefaultCloseAction: true
    maxModalWidth: 460
    maxModalHeight: 280
    Component.onCompleted: workspaceRoot.destructiveModalRef = modal

    Text {
        width: parent.width
        text: workspaceRoot.destructiveAction === "clearMemory"
            ? workspaceRoot.tr(
                "这会清空当前分类下的聚合记忆内容，但不会影响其他分类。",
                "This clears the aggregated content in the current category without touching other categories."
            )
            : workspaceRoot.tr(
                "删除后这条经验将不再出现在经验工作台中。",
                "After deletion, this experience will no longer appear in the experience workspace."
            )
        color: textPrimary
        wrapMode: Text.WordWrap
        font.pixelSize: typeBody
    }

    footer: [
        PillActionButton {
            text: workspaceRoot.tr("确认", "Confirm")
            onClicked: workspaceRoot.confirmDestructiveAction()
        }
    ]
}
