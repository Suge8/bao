import QtQuick 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    property var workspace

    Layout.fillWidth: true
    implicitHeight: basicsColumn.implicitHeight

    ColumnLayout {
        id: basicsColumn
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        spacing: 10

        Text {
            text: workspace.tr("任务名称", "Task name")
            color: workspace.textPrimary
            font.pixelSize: workspace.typeBody + 1
            font.weight: workspace.weightBold
        }

        CronWorkspaceInputField {
            Layout.fillWidth: true
            workspace: root.workspace
            text: workspace.draftString("name", "")
            placeholderText: workspace.tr("任务名称", "Task name")
            onTextEdited: function(value) { workspace.setDraft("name", value) }
        }
    }
}
