import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    property var workspace
    property var deleteModal: null

    objectName: "automationTasksPanel"
    anchors.fill: parent

    ColumnLayout {
        anchors.fill: parent
        spacing: 12

        Rectangle {
            Layout.fillWidth: true
            visible: workspace.hasCronService && workspace.cronService.noticeText !== ""
            radius: 18
            color: workspace.cronService.noticeSuccess ? (workspace.isDark ? "#132015" : "#ECF8EF") : (workspace.isDark ? "#2A1513" : "#FFF1EE")
            border.width: 1
            border.color: workspace.cronService.noticeSuccess ? (workspace.isDark ? "#245A37" : "#AED9B6") : (workspace.isDark ? "#6B2A22" : "#F0B2A8")
            implicitHeight: noticeLabel.implicitHeight + 18

            Text {
                id: noticeLabel
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.margins: 14
                text: workspace.cronService.noticeText
                color: workspace.cronService.noticeSuccess ? workspace.textPrimary : workspace.statusError
                font.pixelSize: workspace.typeLabel
                font.weight: workspace.weightMedium
                wrapMode: Text.WordWrap
            }
        }

        SplitView {
            id: mainSplit
            objectName: "cronWorkspaceMainSplit"
            Layout.fillWidth: true
            Layout.fillHeight: true
            orientation: workspace.compactLayout ? Qt.Vertical : Qt.Horizontal
            spacing: workspace.compactLayout ? 12 : 10
            handle: WorkspaceSplitHandle {}

            CronWorkspaceListPanel { workspace: root.workspace; compactLayout: root.workspace.compactLayout }
            CronWorkspaceTaskDetailPane {
                workspace: root.workspace
                compactLayout: root.workspace.compactLayout
                deleteModal: root.deleteModal
            }
        }
    }
}
