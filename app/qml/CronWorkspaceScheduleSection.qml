import QtQuick 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    property var workspace

    Layout.fillWidth: true
    implicitHeight: scheduleColumn.implicitHeight

    ColumnLayout {
        id: scheduleColumn
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        spacing: 10

        Text {
            text: workspace.tr("执行时间", "Schedule")
            color: workspace.textPrimary
            font.pixelSize: workspace.typeBody + 1
            font.weight: workspace.weightBold
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Repeater {
                model: [
                    { key: "every", label: workspace.tr("重复", "Repeat") },
                    { key: "at", label: workspace.tr("单次", "Once") },
                    { key: "cron", label: workspace.tr("高级", "Advanced") }
                ]

                delegate: PillActionButton {
                    required property var modelData
                    Layout.preferredWidth: 96
                    text: modelData.label
                    horizontalPadding: 12
                    fillColor: workspace.draftString("schedule_kind", "every") === modelData.key ? workspace.cronAccent : "transparent"
                    hoverFillColor: workspace.draftString("schedule_kind", "every") === modelData.key ? workspace.cronAccentHover : workspace.bgCardHover
                    outlineColor: workspace.draftString("schedule_kind", "every") === modelData.key ? workspace.cronAccent : workspace.borderSubtle
                    textColor: workspace.draftString("schedule_kind", "every") === modelData.key ? "#FFFFFFFF" : workspace.textSecondary
                    outlined: workspace.draftString("schedule_kind", "every") !== modelData.key
                    onClicked: workspace.setDraft("schedule_kind", modelData.key)
                }
            }

            Item { Layout.fillWidth: true }
        }

        Text {
            Layout.fillWidth: true
            visible: workspace.scheduleModeHint().length > 0
            text: workspace.scheduleModeHint()
            color: workspace.textSecondary
            font.pixelSize: workspace.typeMeta
            wrapMode: Text.WordWrap
        }

        CronWorkspaceInputField {
            Layout.fillWidth: true
            visible: workspace.draftString("schedule_kind", "every") === "every"
            workspace: root.workspace
            text: workspace.draftString("every_minutes", "60")
            placeholderText: workspace.tr("每隔多少分钟执行一次", "Repeat interval in minutes")
            inputMethodHints: Qt.ImhDigitsOnly
            onTextEdited: function(value) { workspace.setDraft("every_minutes", value) }
        }

        CronWorkspaceInputField {
            Layout.fillWidth: true
            visible: workspace.draftString("schedule_kind", "every") === "at"
            workspace: root.workspace
            text: workspace.draftString("at_input", "")
            placeholderText: workspace.tr("时间，例如 2026-03-12T09:00", "Time, for example 2026-03-12T09:00")
            onTextEdited: function(value) { workspace.setDraft("at_input", value) }
        }

        CronWorkspaceInputField {
            Layout.fillWidth: true
            visible: workspace.draftString("schedule_kind", "every") === "cron"
            workspace: root.workspace
            text: workspace.draftString("cron", "")
            placeholderText: workspace.tr("Cron 表达式，例如 0 9 * * 1-5", "Cron expression, for example 0 9 * * 1-5")
            onTextEdited: function(value) { workspace.setDraft("cron", value) }
        }

        CronWorkspaceInputField {
            Layout.fillWidth: true
            visible: workspace.draftString("schedule_kind", "every") === "cron"
            workspace: root.workspace
            text: workspace.draftString("timezone", "")
            placeholderText: workspace.tr("时区，可留空，例如 Australia/Sydney", "Timezone, optional, for example Australia/Sydney")
            onTextEdited: function(value) { workspace.setDraft("timezone", value) }
        }
    }
}
