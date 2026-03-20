import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ToolsWorkspaceFormScroll {
    id: root

    property var workspace
    readonly property color detailFillColor: root.isDark ? "#15100D" : "#FFF9F2"

    function saveDomainSelection(domainKey, locked) {
        if (!workspace.hasToolsService || locked)
            return
        var domains = (workspace.overview.toolExposureDomains || []).slice(0)
        var index = domains.indexOf(domainKey)
        if (index === -1)
            domains.push(domainKey)
        else
            domains.splice(index, 1)
        if (domains.indexOf("core") === -1)
            domains.unshift("core")
        workspace.toolsService.saveConfig({"tools.toolExposure.domains": domains})
    }

    Layout.fillWidth: true
    Layout.fillHeight: true

    ToolsWorkspaceDetailCard {
        workspace: root.workspace
        fillColor: root.detailFillColor

        Text {
            Layout.fillWidth: true
            text: workspace.tr("暴露模式", "Exposure mode")
            color: root.textPrimary
            font.pixelSize: root.typeLabel
            font.weight: root.weightBold
        }

        Text {
            Layout.fillWidth: true
            text: workspace.tr("Bao 每轮只暴露必要工具。这里控制默认暴露模式，以及允许参与自动选择的任务域闭环。", "Bao only exposes the tools needed for the current turn. Control the default exposure mode and the task-closure domains eligible for automatic selection here.")
            color: root.textSecondary
            font.pixelSize: root.typeBody
            wrapMode: Text.WordWrap
        }

        RowLayout {
            spacing: 10
            Layout.fillWidth: true

            Repeater {
                model: [
                    { value: "off", zh: "全量暴露", en: "Full exposure" },
                    { value: "auto", zh: "BM25 自动", en: "BM25 auto" }
                ]

                delegate: PillActionButton {
                    required property var modelData
                    readonly property bool activeMode: String(workspace.overview.toolExposureMode || "off") === modelData.value
                    text: workspace.tr(modelData.zh, modelData.en)
                    fillColor: activeMode ? root.accent : "transparent"
                    hoverFillColor: activeMode ? root.accentHover : root.bgCardHover
                    outlineColor: activeMode ? root.accent : root.borderSubtle
                    textColor: activeMode ? "#FFFFFFFF" : root.textSecondary
                    outlined: !activeMode
                    onClicked: if (workspace.hasToolsService) workspace.toolsService.saveConfig({"tools.toolExposure.mode": modelData.value})
                }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 10

            Repeater {
                model: workspace.exposureDomainOptions

                delegate: ToolsWorkspaceDomainCard {
                    required property var modelData
                    readonly property bool enabledDomain: (workspace.overview.toolExposureDomains || []).indexOf(modelData.key) !== -1
                    workspace: root.workspace
                    title: workspace.localizedText(modelData.displayLabel, modelData.key)
                    summary: workspace.localizedText(modelData.descriptionDisplay, "")
                    detail: workspace.localizedText(modelData.closureSummaryDisplay, "")
                    active: enabledDomain
                    locked: Boolean(modelData.locked)
                    onPressed: root.saveDomainSelection(modelData.key, locked)
                }
            }
        }

        Text {
            Layout.fillWidth: true
            text: workspace.tr("core 域会始终保留。off 模式直接全量暴露；auto 模式才会使用 BM25 域路由，并按这里勾选的 domain 参与筛选。", "The core domain always stays enabled. Off mode exposes everything directly; auto mode uses BM25 domain routing and only considers the domains enabled here.")
            color: root.textSecondary
            font.pixelSize: root.typeMeta
            wrapMode: Text.WordWrap
        }
    }

    ToolsWorkspaceDetailCard {
        workspace: root.workspace
        fillColor: root.detailFillColor

        Text {
            Layout.fillWidth: true
            text: workspace.tr("工作区限制", "Workspace restrictions")
            color: root.textPrimary
            font.pixelSize: root.typeLabel
            font.weight: root.weightBold
        }

        Text {
            Layout.fillWidth: true
            text: workspace.tr("当你需要更强的本地安全边界时，可以把文件与命令的作用范围收束到当前工作区。", "When you want a stricter local safety boundary, keep file and command access scoped to the current workspace.")
            color: root.textSecondary
            font.pixelSize: root.typeBody
            wrapMode: Text.WordWrap
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Switch {
                checked: Boolean(workspace.overview.restrictToWorkspace)
                onToggled: if (workspace.hasToolsService) workspace.toolsService.saveConfig({"tools.restrictToWorkspace": checked})
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 2

                Text {
                    text: workspace.tr("限制到工作区", "Restrict to workspace")
                    color: root.textPrimary
                    font.pixelSize: root.typeBody
                    font.weight: root.weightBold
                }

                Text {
                    Layout.fillWidth: true
                    text: workspace.tr("开启后，文件和命令工具默认只在工作区目录内操作。", "When enabled, file and command tools stay scoped to the workspace directory by default.")
                    color: root.textSecondary
                    font.pixelSize: root.typeMeta
                    wrapMode: Text.WordWrap
                }
            }
        }
    }

    ToolsWorkspaceDetailCard {
        workspace: root.workspace
        fillColor: root.detailFillColor

        Text {
            Layout.fillWidth: true
            text: workspace.tr("最近一次工具观测", "Latest tool observability")
            color: root.textPrimary
            font.pixelSize: root.typeLabel
            font.weight: root.weightBold
        }

        Text {
            Layout.fillWidth: true
            text: workspace.tr("这里显示最近一次运行的工具调用摘要，用来判断自动暴露是否真的有帮助。", "This shows the latest tool-call summary so you can tell whether auto exposure is actually helping.")
            color: root.textSecondary
            font.pixelSize: root.typeBody
            wrapMode: Text.WordWrap
        }

        Flow {
            Layout.fillWidth: true
            spacing: 10

            Repeater {
                model: workspace.observabilityItems

                delegate: ToolsWorkspaceMetricChip {
                    required property var modelData
                    workspace: root.workspace
                    label: String(modelData.label || "")
                    value: String(modelData.value || "")
                    showIndicator: false
                    visible: label.length > 0
                }
            }
        }
    }
}
