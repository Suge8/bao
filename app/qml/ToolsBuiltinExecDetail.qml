import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ToolsWorkspaceFormScroll {
    id: root

    property var workspace
    property string selectedSandboxMode: String(workspace.selectedItem.configValues.sandboxMode || "semi-auto")
    readonly property bool readOnlyMode: selectedSandboxMode === "read-only"
    readonly property bool restrictEnabledByConfig: Boolean(workspace.selectedItem.configValues.restrictToWorkspace)
    readonly property bool effectiveRestrictToWorkspace: readOnlyMode || restrictEnabledByConfig

    function sandboxTitle(mode) {
        switch (String(mode)) {
        case "full-auto":
            return workspace.tr("完全放开", "Full auto")
        case "read-only":
            return workspace.tr("只读审计", "Read only")
        default:
            return workspace.tr("默认平衡", "Semi auto")
        }
    }

    function sandboxIcon(mode) {
        switch (String(mode)) {
        case "full-auto":
            return workspace.icon("play")
        case "read-only":
            return workspace.icon("page-search")
        default:
            return workspace.icon("activity")
        }
    }

    function sandboxSummary(mode) {
        switch (String(mode)) {
        case "full-auto":
            return workspace.tr("不拦危险命令模式，也不自动锁到工作区。", "No dangerous-command pattern guard and no automatic workspace restriction.")
        case "read-only":
            return workspace.tr("阻止写操作，并始终限制在当前工作区。", "Blocks write operations and always keeps execution inside the current workspace.")
        default:
            return workspace.tr("只拦明显危险命令，适合大多数本机开发场景。", "Blocks obviously dangerous commands only, which fits most local development workflows.")
        }
    }

    function sandboxDetail(mode) {
        switch (String(mode)) {
        case "full-auto":
            return workspace.tr("给最熟悉当前环境的 owner 模式使用。", "Best reserved for owner-mode sessions on a trusted machine.")
        case "read-only":
            return workspace.tr("适合排障、审计或只看不改的任务。", "Best for audits, debugging, or look-without-changing sessions.")
        default:
            return workspace.tr("默认推荐，不会自动启用工作区限制。", "Recommended default. Workspace restriction stays a separate switch.")
        }
    }

    ToolsWorkspaceDetailCard {
        workspace: root.workspace

        Text {
            Layout.fillWidth: true
            text: workspace.tr("执行策略", "Execution policy")
            color: root.textPrimary
            font.pixelSize: root.typeLabel
            font.weight: root.weightBold
        }

        Text {
            Layout.fillWidth: true
            text: workspace.tr(
                "把危险命令拦截和工作区限制拆开：默认模式保持轻量，只有你显式选择时才进一步收紧。",
                "Keep dangerous-command guarding and workspace restriction separate: the default stays lightweight, and tighter boundaries only apply when you explicitly opt in."
            )
            color: root.textSecondary
            font.pixelSize: root.typeMeta
            wrapMode: Text.WordWrap
        }

        Flow {
            id: modeFlow
            objectName: "execModeFlow"
            Layout.fillWidth: true
            spacing: 10

            Repeater {
                model: ["semi-auto", "full-auto", "read-only"]

                delegate: ToolsWorkspaceModeCard {
                    required property string modelData
                    objectName: "execModeCard-" + modelData
                    width: modeFlow.width >= 720 ? (modeFlow.width - modeFlow.spacing * 2) / 3 : modeFlow.width
                    workspace: root.workspace
                    iconSource: root.sandboxIcon(modelData)
                    modeKey: modelData
                    title: root.sandboxTitle(modelData)
                    summary: root.sandboxSummary(modelData)
                    detail: root.sandboxDetail(modelData)
                    selected: root.selectedSandboxMode === modelData
                    onPressed: root.selectedSandboxMode = modelData
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6

                Text {
                    text: workspace.tr("超时（秒）", "Timeout (s)")
                    color: root.textSecondary
                    font.pixelSize: root.typeMeta
                }

                TextField {
                    id: timeoutField
                    property bool baoClickAwayEditor: true
                    Layout.fillWidth: true
                    text: String(workspace.selectedItem.configValues.timeout || 60)
                    color: root.textPrimary
                    placeholderText: "60"
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6

                Text {
                    text: workspace.tr("当前模式摘要", "Selected mode")
                    color: root.textSecondary
                    font.pixelSize: root.typeMeta
                }

                Rectangle {
                    objectName: "execModeSummaryCard"
                    Layout.fillWidth: true
                    implicitHeight: 44
                    radius: 14
                    color: root.isDark ? "#14100C" : "#FFF7EF"
                    border.width: 1
                    border.color: root.readOnlyMode ? root.accent : (root.isDark ? "#18FFFFFF" : "#14000000")

                    Text {
                        anchors.fill: parent
                        anchors.margins: 12
                        verticalAlignment: Text.AlignVCenter
                        text: root.sandboxTitle(root.selectedSandboxMode) + " · " + root.sandboxDetail(root.selectedSandboxMode)
                        color: root.textPrimary
                        font.pixelSize: root.typeMeta
                        wrapMode: Text.WordWrap
                    }
                }
            }
        }

        Text {
            text: workspace.tr("附加 PATH", "PATH append")
            color: root.textSecondary
            font.pixelSize: root.typeMeta
        }

        TextField {
            id: pathField
            property bool baoClickAwayEditor: true
            Layout.fillWidth: true
            text: String(workspace.selectedItem.configValues.pathAppend || "")
            color: root.textPrimary
            placeholderText: workspace.tr("可选路径，用冒号分隔", "Optional path list, colon-separated")
        }

        Rectangle {
            objectName: "execRestrictCard"
            Layout.fillWidth: true
            radius: 18
            color: root.isDark ? "#15110D" : "#FFF9F2"
            border.width: 1
            border.color: root.effectiveRestrictToWorkspace ? root.accent : (root.isDark ? "#18FFFFFF" : "#10000000")
            implicitHeight: restrictContent.implicitHeight + 24

            ColumnLayout {
                id: restrictContent
                anchors.fill: parent
                anchors.margins: 12
                spacing: 8

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    Switch {
                        id: restrictSwitch
                        enabled: !root.readOnlyMode
                        checked: root.effectiveRestrictToWorkspace
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        Text {
                            Layout.fillWidth: true
                            text: workspace.tr("限制到当前工作区", "Restrict to current workspace")
                            color: root.textPrimary
                            font.pixelSize: root.typeBody
                            font.weight: root.weightBold
                            wrapMode: Text.WordWrap
                        }

                        Text {
                            Layout.fillWidth: true
                            text: root.readOnlyMode
                                ? workspace.tr("当前选择了只读模式，所以这里会自动开启。", "Read-only is selected, so workspace restriction stays enabled automatically.")
                                : workspace.tr("这个开关和 sandbox mode 独立：默认模式不会替你自动打开。", "This switch stays separate from sandbox mode: the default mode does not turn it on for you.")
                            color: root.textSecondary
                            font.pixelSize: root.typeMeta
                            wrapMode: Text.WordWrap
                        }
                    }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Item { Layout.fillWidth: true }

            PillActionButton {
                text: workspace.tr("保存执行策略", "Save exec settings")
                iconSource: workspace.icon("circle-spark")
                fillColor: root.accent
                hoverFillColor: root.accentHover
                onClicked: if (workspace.hasToolsService) workspace.toolsService.saveConfig({
                    "tools.exec.timeout": parseInt(timeoutField.text || "60"),
                    "tools.exec.pathAppend": pathField.text,
                    "tools.exec.sandboxMode": root.selectedSandboxMode,
                    "tools.restrictToWorkspace": root.readOnlyMode ? true : restrictSwitch.checked
                })
            }
        }
    }
}
