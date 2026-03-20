import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    property var workspace

    objectName: "automationChecksPanel"
    anchors.fill: parent

    ScrollView {
        id: checksScroll
        anchors.fill: parent
        clip: true
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

        ColumnLayout {
            width: Math.max(0, checksScroll.availableWidth)
            spacing: 12

            CronWorkspaceSectionCard {
                workspace: root.workspace

                Text {
                    text: workspace.tr("适合写进自动检查的内容", "Good automatic check prompts")
                    color: workspace.textPrimary
                    font.pixelSize: workspace.typeBody + 1
                    font.weight: workspace.weightBold
                }

                Repeater {
                    model: [
                        workspace.tr("每天查看收件箱，把需要跟进的事项整理出来。", "Review the inbox every day and surface anything that needs a follow-up."),
                        workspace.tr("定期检查项目里的阻塞项，发现卡点就开始处理。", "Check projects for blockers on a schedule and start work when something is stuck."),
                        workspace.tr("每周检查固定来源，例如 GitHub、任务板或文档目录。", "Review fixed sources each week, such as GitHub, task boards, or document folders.")
                    ]

                    delegate: Text {
                        required property string modelData
                        Layout.fillWidth: true
                        text: modelData
                        color: workspace.textSecondary
                        font.pixelSize: workspace.typeMeta
                        wrapMode: Text.WordWrap
                    }
                }
            }

            CronWorkspaceSectionCard {
                workspace: root.workspace

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 4

                        Text {
                            text: workspace.tr("自动检查", "Automatic Checks")
                            color: workspace.textPrimary
                            font.pixelSize: workspace.typeLabel
                            font.weight: workspace.weightBold
                        }

                        Text {
                            Layout.fillWidth: true
                            text: workspace.hasHeartbeatService && workspace.heartbeatService.heartbeatFileExists
                                ? workspace.tr("Bao 会按你的检查说明定期查看是否有新任务，发现需要处理的事项就会开始执行。", "Bao follows these instructions on schedule and starts working when something needs attention.")
                                : workspace.tr("还没有检查说明。点“编辑检查说明”会先创建模板，再打开当前空间的检查说明文件。", "No instructions yet. Edit instructions will create the template first, then open the instructions for this space.")
                            color: workspace.textSecondary
                            font.pixelSize: workspace.typeMeta
                            wrapMode: Text.WordWrap
                        }
                    }

                    AsyncActionButton {
                        Layout.preferredWidth: 152
                        text: workspace.tr("立即检查", "Run check")
                        busy: workspace.hasHeartbeatService && workspace.heartbeatService.busy
                        buttonEnabled: workspace.hasHeartbeatService && !workspace.heartbeatService.busy && workspace.heartbeatService.canRunNow
                        fillColor: workspace.cronAccent
                        hoverFillColor: workspace.cronAccentHover
                        iconSource: workspace.labIcon("watch-activity")
                        onClicked: if (workspace.hasHeartbeatService) workspace.heartbeatService.runNow()
                    }

                    PillActionButton {
                        Layout.preferredWidth: 154
                        text: workspace.tr("打开检查会话", "Open check chat")
                        iconSource: workspace.icon("chat-lines")
                        fillColor: "transparent"
                        hoverFillColor: workspace.bgCardHover
                        outlineColor: workspace.borderSubtle
                        hoverOutlineColor: workspace.borderDefault
                        textColor: workspace.textPrimary
                        outlined: true
                        buttonEnabled: workspace.hasHeartbeatService
                        onClicked: workspace.openHeartbeatSession()
                    }
                }

                Flow {
                    id: heartbeatStatsFlow
                    Layout.fillWidth: true
                    spacing: 12

                    Repeater {
                        model: [
                            { label: workspace.tr("检查说明", "Instructions"), value: workspace.hasHeartbeatService && workspace.heartbeatService.heartbeatFileExists ? workspace.tr("已设置", "Ready") : workspace.tr("未设置", "Not set") },
                            { label: workspace.tr("检查频率", "Frequency"), value: workspace.hasHeartbeatService ? String(workspace.heartbeatService.intervalText || workspace.tr("等待开始", "Waiting to start")) : "" },
                            { label: workspace.tr("上次检查", "Last check"), value: workspace.hasHeartbeatService ? String(workspace.heartbeatService.lastCheckedText || workspace.tr("尚未检查", "Never checked")) : "" },
                            { label: workspace.tr("上次结果", "Last result"), value: workspace.hasHeartbeatService ? String(workspace.heartbeatService.lastDecisionLabel || workspace.tr("暂无", "None")) : "" }
                        ]

                        delegate: Rectangle {
                            required property var modelData
                            width: heartbeatStatsFlow.width >= 920 ? (heartbeatStatsFlow.width - heartbeatStatsFlow.spacing * 3) / 4 : (heartbeatStatsFlow.width >= 520 ? (heartbeatStatsFlow.width - heartbeatStatsFlow.spacing) / 2 : heartbeatStatsFlow.width)
                            radius: 14
                            color: workspace.fieldFill
                            border.width: 1
                            border.color: workspace.fieldBorder
                            implicitHeight: statColumn.implicitHeight + 18

                            Column {
                                id: statColumn
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 4

                                Text {
                                    text: modelData.label
                                    color: workspace.textSecondary
                                    font.pixelSize: workspace.typeMeta
                                    font.weight: workspace.weightBold
                                }

                                Text {
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

                Text {
                    Layout.fillWidth: true
                    visible: workspace.hasHeartbeatService && String(workspace.heartbeatService.heartbeatPreview || "") !== ""
                    text: workspace.tr("当前会检查：", "What Bao will review: ") + String(workspace.heartbeatService.heartbeatPreview || "")
                    color: workspace.textSecondary
                    font.pixelSize: workspace.typeMeta
                    wrapMode: Text.WordWrap
                    maximumLineCount: 3
                    elide: Text.ElideRight
                }

                Text {
                    Layout.fillWidth: true
                    visible: workspace.hasHeartbeatService && String(workspace.heartbeatService.runNowBlockedReason || "") !== ""
                    text: String(workspace.heartbeatService.runNowBlockedReason || "")
                    color: workspace.textSecondary
                    font.pixelSize: workspace.typeMeta
                    wrapMode: Text.WordWrap
                }

                Text {
                    Layout.fillWidth: true
                    visible: workspace.hasHeartbeatService && String(workspace.heartbeatService.lastError || "") !== ""
                    text: String(workspace.heartbeatService.lastError || "")
                    color: workspace.statusError
                    font.pixelSize: workspace.typeMeta
                    wrapMode: Text.WordWrap
                }

                Rectangle {
                    Layout.fillWidth: true
                    visible: workspace.hasHeartbeatService && String(workspace.heartbeatService.noticeText || "") !== ""
                    radius: 14
                    color: workspace.heartbeatService.noticeSuccess ? (workspace.isDark ? "#132015" : "#ECF8EF") : (workspace.isDark ? "#2A1513" : "#FFF1EE")
                    border.width: 1
                    border.color: workspace.heartbeatService.noticeSuccess ? (workspace.isDark ? "#245A37" : "#AED9B6") : (workspace.isDark ? "#6B2A22" : "#F0B2A8")
                    implicitHeight: heartbeatNotice.implicitHeight + 18

                    Text {
                        id: heartbeatNotice
                        anchors.fill: parent
                        anchors.margins: 10
                        text: String(workspace.heartbeatService.noticeText || "")
                        color: workspace.heartbeatService.noticeSuccess ? workspace.textPrimary : workspace.statusError
                        font.pixelSize: workspace.typeMeta
                        wrapMode: Text.WordWrap
                    }
                }
            }

            CronWorkspaceSectionCard {
                workspace: root.workspace

                Text {
                    text: workspace.tr("添加检查内容", "Add checks")
                    color: workspace.textPrimary
                    font.pixelSize: workspace.typeBody + 1
                    font.weight: workspace.weightBold
                }

                Text {
                    Layout.fillWidth: true
                    text: workspace.tr("你可以直接编辑检查说明，也可以先在对话里告诉 Bao 想定期查看什么，再回来整理说明。", "You can edit the instructions directly, or tell Bao in chat what should be reviewed on a schedule and refine the instructions here.")
                    color: workspace.textSecondary
                    font.pixelSize: workspace.typeMeta
                    wrapMode: Text.WordWrap
                }

                PillActionButton {
                    objectName: "heartbeatInlineEditButton"
                    text: workspace.tr("编辑检查说明", "Edit instructions")
                    iconSource: workspace.labIcon("copy-file-path")
                    fillColor: workspace.cronAccent
                    hoverFillColor: workspace.cronAccentHover
                    buttonEnabled: workspace.hasHeartbeatService
                    onClicked: if (workspace.hasHeartbeatService) workspace.heartbeatService.openHeartbeatFile()
                }

                Text {
                    Layout.fillWidth: true
                    text: workspace.tr("如果还没有说明，点击上面的“编辑检查说明”会先创建模板，再直接打开当前空间的文件。", "If no instructions exist yet, Edit instructions creates the template first, then opens the file for this space.")
                    color: workspace.textSecondary
                    font.pixelSize: workspace.typeMeta
                    wrapMode: Text.WordWrap
                }
            }
        }
    }
}
