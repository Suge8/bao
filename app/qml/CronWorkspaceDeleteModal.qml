import QtQuick 2.15
import QtQuick.Layouts 1.15

AppModal {
    id: root

    property var workspace

    darkMode: workspace.isDark
    title: workspace.tr("删除这个任务？", "Delete this task?")
    closeText: workspace.tr("取消", "Cancel")
    maxModalWidth: 460
    maxModalHeight: 260

    ColumnLayout {
        width: parent.width
        spacing: 12

        Text {
            Layout.fillWidth: true
            text: workspace.tr("这会删除调度定义，但不会删除已经产生的 定时任务会话历史。", "This deletes the scheduled definition, but keeps any existing cron session history.")
            color: workspace.textSecondary
            font.pixelSize: workspace.typeBody
            wrapMode: Text.WordWrap
        }

        RowLayout {
            Layout.fillWidth: true

            Item { Layout.fillWidth: true }

            PillActionButton {
                text: workspace.tr("确认删除", "Delete task")
                fillColor: workspace.statusError
                hoverFillColor: Qt.darker(workspace.statusError, 1.06)
                onClicked: {
                    root.close()
                    if (workspace.hasCronService)
                        workspace.cronService.deleteSelected()
                }
            }
        }
    }
}
