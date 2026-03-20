import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    property var workspace

    Layout.fillWidth: true
    implicitHeight: deliveryColumn.implicitHeight

    ColumnLayout {
        id: deliveryColumn
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        spacing: 10

        Text {
            text: workspace.tr("消息与投递", "Message and delivery")
            color: workspace.textPrimary
            font.pixelSize: workspace.typeBody + 1
            font.weight: workspace.weightBold
        }

        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 154
            radius: 18
            color: messageInput.activeFocus ? workspace.fieldHoverFill : workspace.fieldFill
            border.width: messageInput.activeFocus ? 1.5 : 1
            border.color: messageInput.activeFocus ? workspace.borderFocus : workspace.fieldBorder

            TextArea {
                id: messageInput
                property bool baoClickAwayEditor: true
                anchors.fill: parent
                anchors.margins: 12
                text: workspace.draftString("message", "")
                color: workspace.textPrimary
                placeholderText: workspace.tr("任务执行时要发送给 Bao 的消息或指令", "The message or instruction Bao should receive when the task runs")
                placeholderTextColor: workspace.textPlaceholder
                wrapMode: TextArea.Wrap
                selectByMouse: true
                background: null
                selectionColor: workspace.textSelectionBg
                selectedTextColor: workspace.textSelectionFg
                onTextChanged: if (activeFocus) workspace.setDraft("message", text)
            }
        }

        PillActionButton {
            text: workspace.draftBool("deliver", false) ? workspace.tr("发送结果到渠道", "Send result to channel") : workspace.tr("只在 Bao 内运行", "Run inside Bao only")
            fillColor: workspace.draftBool("deliver", false) ? workspace.cronAccent : "transparent"
            hoverFillColor: workspace.draftBool("deliver", false) ? workspace.cronAccentHover : workspace.bgCardHover
            outlineColor: workspace.draftBool("deliver", false) ? workspace.cronAccent : workspace.borderSubtle
            textColor: workspace.draftBool("deliver", false) ? "#FFFFFFFF" : workspace.textSecondary
            outlined: !workspace.draftBool("deliver", false)
            onClicked: workspace.setDraft("deliver", !workspace.draftBool("deliver", false))
        }

        Text {
            Layout.fillWidth: true
            visible: workspace.deliveryHint().length > 0
            text: workspace.tr("任务完成后会自动发到下面的渠道和目标。", "When finished, Bao sends the result to the channel and target below.")
            color: workspace.textSecondary
            font.pixelSize: workspace.typeMeta
            wrapMode: Text.WordWrap
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            CronWorkspaceInputField {
                Layout.fillWidth: true
                workspace: root.workspace
                fieldEnabled: workspace.draftBool("deliver", false)
                text: workspace.draftString("channel", "")
                placeholderText: workspace.tr("渠道，例如 telegram", "Channel, for example telegram")
                onTextEdited: function(value) { workspace.setDraft("channel", value) }
            }

            CronWorkspaceInputField {
                Layout.fillWidth: true
                workspace: root.workspace
                fieldEnabled: workspace.draftBool("deliver", false)
                text: workspace.draftString("target", "")
                placeholderText: workspace.tr("目标，例如 chat id / 电话", "Target, for example chat id / phone")
                onTextEdited: function(value) { workspace.setDraft("target", value) }
            }
        }
    }
}
