import QtQuick 2.15
import QtQuick.Layouts 1.15

CalloutPanel {
    id: root

    property var workspace

    objectName: "cronStatusPanel"
    Layout.fillWidth: true
    panelColor: workspace.statusSurface(workspace.taskStatusKey())
    panelBorderColor: workspace.fieldBorder
    sideGlowVisible: workspace.showingExistingTask
    sideGlowColor: workspace.isDark ? "#18FFFFFF" : "#14FFB33D"
    sideGlowWidthFactor: 0.24
    padding: 14

    ColumnLayout {
        Layout.fillWidth: true
        spacing: 10

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Rectangle {
                implicitWidth: 34
                implicitHeight: 34
                Layout.preferredWidth: implicitWidth
                Layout.preferredHeight: implicitHeight
                radius: 17
                color: workspace.isDark ? "#19130F" : "#FFF4E6"

                AppIcon {
                    anchors.centerIn: parent
                    width: 18
                    height: 18
                    source: workspace.labIcon("watch-activity")
                    sourceSize: Qt.size(width, height)
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 2

                Text {
                    text: workspace.tr("任务状态", "Task status")
                    color: workspace.textPrimary
                    font.pixelSize: workspace.typeBody + 1
                    font.weight: workspace.weightBold
                }

                Text {
                    Layout.fillWidth: true
                    text: workspace.showingExistingTask ? workspace.statusLabel(workspace.taskStatusKey()) : workspace.tr("还没有选中任务", "No task selected yet")
                    color: workspace.showingExistingTask ? workspace.statusColor(workspace.taskStatusKey()) : workspace.textSecondary
                    font.pixelSize: workspace.typeBody
                    wrapMode: Text.WordWrap
                }
            }
        }

        Text {
            objectName: "cronStatusSummaryText"
            Layout.fillWidth: true
            text: workspace.showingExistingTask
                ? String(workspace.visibleTask.schedule_summary || "")
                : workspace.emptyTaskStatusHint()
            color: workspace.textSecondary
            font.pixelSize: workspace.typeBody
            wrapMode: Text.WordWrap
        }

        Rectangle {
            Layout.fillWidth: true
            visible: workspace.showingExistingTask
            radius: 16
            color: workspace.isDark ? "#14100D" : "#FAF3EB"
            border.width: 1
            border.color: workspace.fieldBorder
            implicitHeight: metricsGrid.implicitHeight + 24

            GridLayout {
                id: metricsGrid
                anchors.fill: parent
                anchors.margins: 12
                columns: 2
                columnSpacing: 14
                rowSpacing: 10

                Repeater {
                    model: [
                        { label: workspace.tr("下一次执行", "Next run"), icon: workspace.icon("clock-rotate-right"), value: workspace.summaryText(workspace.visibleTask.next_run_text, "未安排", "Not scheduled") },
                        { label: workspace.tr("最近结果", "Last result"), icon: workspace.icon("message-text"), value: workspace.summaryText(workspace.visibleTask.last_result_text, "暂无", "None yet") },
                        { label: workspace.tr("最近执行", "Last run"), icon: workspace.icon("activity"), value: workspace.summaryText(workspace.visibleTask.last_run_text, "从未执行", "Never run") },
                        { label: workspace.tr("任务对话", "Task chat"), icon: workspace.icon("chat-lines"), value: workspace.summaryText(workspace.visibleTask.session_key, "保存后生成", "Created after save") }
                    ]

                    delegate: Item {
                        required property var modelData
                        Layout.fillWidth: true
                        implicitHeight: metricValue.implicitHeight + 24

                        Column {
                            anchors.fill: parent
                            spacing: 4

                            Row {
                                spacing: 8

                                AppIcon {
                                    width: 16
                                    height: 16
                                    source: modelData.icon
                                    sourceSize: Qt.size(width, height)
                                    opacity: 0.72
                                }

                                Text {
                                    text: modelData.label
                                    color: workspace.textTertiary
                                    font.pixelSize: workspace.typeMeta
                                    font.weight: workspace.weightBold
                                }
                            }

                            Text {
                                id: metricValue
                                width: parent.width
                                text: modelData.value
                                color: workspace.textPrimary
                                font.pixelSize: workspace.typeBody
                                wrapMode: Text.WordWrap
                            }
                        }
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            visible: workspace.showingExistingTask && String(workspace.visibleTask.last_error || "") !== ""
            radius: 16
            color: workspace.isDark ? "#2A1513" : "#FFF1EE"
            border.width: 1
            border.color: workspace.isDark ? "#6B2A22" : "#F0B2A8"
            implicitHeight: latestErrorText.implicitHeight + 28

            Column {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 4

                Text {
                    text: workspace.tr("最近错误", "Latest error")
                    color: workspace.statusError
                    font.pixelSize: workspace.typeMeta
                    font.weight: workspace.weightBold
                }

                Text {
                    id: latestErrorText
                    width: parent.width
                    text: String(workspace.visibleTask.last_error || "")
                    color: workspace.textPrimary
                    font.pixelSize: workspace.typeBody
                    wrapMode: Text.WordWrap
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 8
            visible: workspace.showingExistingTask

            AsyncActionButton {
                Layout.preferredWidth: 156
                text: workspace.tr("现在执行一次", "Run now")
                busy: workspace.hasCronService && workspace.cronService.busy
                buttonEnabled: workspace.showingExistingTask && workspace.hasCronService && !workspace.cronService.busy && workspace.cronService.canRunSelectedNow
                fillColor: workspace.cronAccent
                hoverFillColor: workspace.cronAccentHover
                iconSource: workspace.icon("play")
                onClicked: if (workspace.hasCronService) workspace.cronService.runSelectedNow()
            }

            PillActionButton {
                Layout.preferredWidth: 132
                iconSource: workspace.draftBool("enabled", true) ? workspace.icon("bubble-xmark") : workspace.icon("circle-spark")
                text: workspace.draftBool("enabled", true) ? workspace.tr("暂停任务", "Pause task") : workspace.tr("启用任务", "Enable task")
                fillColor: "transparent"
                hoverFillColor: workspace.draftBool("enabled", true) ? (workspace.isDark ? "#311816" : "#FFF0EC") : workspace.bgCardHover
                outlineColor: workspace.draftBool("enabled", true) ? workspace.statusError : workspace.borderSubtle
                hoverOutlineColor: workspace.draftBool("enabled", true) ? workspace.statusError : workspace.borderDefault
                textColor: workspace.draftBool("enabled", true) ? workspace.statusError : workspace.textSecondary
                outlined: true
                buttonEnabled: workspace.showingExistingTask && workspace.hasCronService && !workspace.cronService.busy
                onClicked: if (workspace.hasCronService) workspace.cronService.setSelectedEnabled(!workspace.draftBool("enabled", true))
            }

            PillActionButton {
                Layout.preferredWidth: 144
                text: workspace.tr("查看任务对话", "Open task chat")
                iconSource: workspace.icon("chat-lines")
                fillColor: "transparent"
                hoverFillColor: workspace.bgCardHover
                outlineColor: workspace.borderSubtle
                textColor: workspace.textSecondary
                outlined: true
                buttonEnabled: workspace.showingExistingTask
                onClicked: workspace.openSelectedSession()
            }

            Item { Layout.fillWidth: true }
        }

        Text {
            Layout.fillWidth: true
            visible: workspace.showingExistingTask && workspace.hasCronService && String(workspace.cronService.runNowBlockedReason || "") !== ""
            text: String(workspace.cronService.runNowBlockedReason || "")
            color: workspace.textSecondary
            font.pixelSize: workspace.typeMeta
            wrapMode: Text.WordWrap
        }
    }
}
