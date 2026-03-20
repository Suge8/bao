import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "ToolsWorkspaceLogic.js" as ToolsWorkspaceLogic

ToolsWorkspaceFormScroll {
    id: root

    property var workspace
    readonly property var initialDraft: ToolsWorkspaceLogic.serverDraftFromItem(workspace.selectedItem)

    function draftPayload() {
        return {
            previousName: initialDraft.previousName,
            name: nameField.text,
            transport: transportCombo.currentText,
            command: commandField.text,
            argsText: argsField.text,
            envText: envField.text,
            url: urlField.text,
            headersText: headersField.text,
            toolTimeoutSeconds: timeoutField.text,
            maxTools: maxToolsField.text,
            slimSchema: ToolsWorkspaceLogic.slimSchemaValueFromMode(slimSchemaMode.currentText)
        }
    }

    Text {
        Layout.fillWidth: true
        text: String(workspace.selectedItem.name || workspace.tr("MCP 服务", "MCP server"))
        color: root.textPrimary
        font.pixelSize: root.typeTitle
        font.weight: root.weightBold
    }

    Text {
        Layout.fillWidth: true
        text: workspace.statusDetail(workspace.selectedItem) || workspace.tr("编辑服务定义，保存后会写入配置；测试按钮会直接复用 MCP 握手逻辑。", "Edit the server definition and save it to config. The Test action reuses the real MCP handshake path.")
        color: root.textSecondary
        font.pixelSize: root.typeBody
        wrapMode: Text.WordWrap
    }

    ToolsWorkspaceDetailCard {
        workspace: root.workspace
        Text { text: workspace.tr("服务定义", "Server definition"); color: root.textPrimary; font.pixelSize: root.typeLabel; font.weight: root.weightBold }

        Text { text: workspace.tr("名称", "Name"); color: root.textSecondary; font.pixelSize: root.typeMeta }
        TextField { id: nameField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; text: initialDraft.name; color: root.textPrimary }

        Text { text: workspace.tr("传输方式", "Transport"); color: root.textSecondary; font.pixelSize: root.typeMeta }
        ComboBox { id: transportCombo; Layout.fillWidth: true; model: ["stdio", "http"]; currentIndex: Math.max(0, model.indexOf(String(initialDraft.transport || "stdio"))) }

        ColumnLayout {
            visible: transportCombo.currentText === "stdio"
            Layout.fillWidth: true
            spacing: 10

            Text { text: workspace.tr("命令", "Command"); color: root.textSecondary; font.pixelSize: root.typeMeta }
            TextField { id: commandField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; text: initialDraft.command; color: root.textPrimary; placeholderText: "npx" }

            Text { text: workspace.tr("参数（每行一个）", "Args (one per line)"); color: root.textSecondary; font.pixelSize: root.typeMeta }
            TextArea { id: argsField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; Layout.preferredHeight: 96; text: initialDraft.argsText; wrapMode: TextArea.Wrap; color: root.textPrimary }

            Text { text: workspace.tr("环境变量（KEY=VALUE）", "Environment (KEY=VALUE)"); color: root.textSecondary; font.pixelSize: root.typeMeta }
            TextArea { id: envField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; Layout.preferredHeight: 88; text: initialDraft.envText; wrapMode: TextArea.Wrap; color: root.textPrimary }
        }

        ColumnLayout {
            visible: transportCombo.currentText === "http"
            Layout.fillWidth: true
            spacing: 10

            Text { text: workspace.tr("URL", "URL"); color: root.textSecondary; font.pixelSize: root.typeMeta }
            TextField { id: urlField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; text: initialDraft.url; color: root.textPrimary; placeholderText: "https://example.com/mcp" }

            Text { text: workspace.tr("请求头（Header: Value）", "Headers (Header: Value)"); color: root.textSecondary; font.pixelSize: root.typeMeta }
            TextArea { id: headersField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; Layout.preferredHeight: 88; text: initialDraft.headersText; wrapMode: TextArea.Wrap; color: root.textPrimary }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6
                Text { text: workspace.tr("工具超时", "Tool timeout"); color: root.textSecondary; font.pixelSize: root.typeMeta }
                TextField { id: timeoutField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; text: String(initialDraft.toolTimeoutSeconds || 30); color: root.textPrimary }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6
                Text { text: workspace.tr("最大工具数", "Max tools"); color: root.textSecondary; font.pixelSize: root.typeMeta }
                TextField { id: maxToolsField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; text: String(initialDraft.maxTools || 0); color: root.textPrimary }
            }
        }

        Text { text: workspace.tr("精简结构", "Slim schema"); color: root.textSecondary; font.pixelSize: root.typeMeta }
        ComboBox {
            id: slimSchemaMode
            Layout.fillWidth: true
            model: ["inherit", "enabled", "disabled"]
            currentIndex: Math.max(0, model.indexOf(ToolsWorkspaceLogic.slimSchemaModeFromValue(initialDraft.slimSchema)))

            delegate: ItemDelegate {
                width: ListView.view ? ListView.view.width : implicitWidth
                text: modelData === "inherit" ? workspace.tr("继承全局设置", "Inherit global setting") : modelData === "enabled" ? workspace.tr("强制启用", "Force enable") : workspace.tr("强制关闭", "Force disable")
            }

            contentItem: Text {
                leftPadding: 0
                rightPadding: slimSchemaMode.indicator.width + slimSchemaMode.spacing
                text: slimSchemaMode.currentText === "inherit" ? workspace.tr("继承全局设置", "Inherit global setting") : slimSchemaMode.currentText === "enabled" ? workspace.tr("强制启用", "Force enable") : workspace.tr("强制关闭", "Force disable")
                color: root.textPrimary
                font.pixelSize: root.typeBody
                verticalAlignment: Text.AlignVCenter
                elide: Text.ElideRight
            }
        }

        Rectangle {
            Layout.fillWidth: true
            implicitHeight: probeColumn.implicitHeight + 20
            radius: 18
            color: root.isDark ? "#17110E" : "#FFFDFC"
            border.width: 1
            border.color: root.isDark ? "#12FFFFFF" : "#10000000"

            Column {
                id: probeColumn
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 12
                spacing: 8

                Text {
                    width: parent.width
                    text: workspace.tr("最近一次探测", "Latest probe")
                    color: root.textSecondary
                    font.pixelSize: root.typeMeta
                    font.weight: root.weightBold
                    font.letterSpacing: root.letterWide
                }

                Text {
                    width: parent.width
                    text: workspace.selectedItem.probe && workspace.selectedItem.probe.error
                        ? String(workspace.selectedItem.probe.error)
                        : (workspace.selectedItem.probe && workspace.selectedItem.probe.toolNames && workspace.selectedItem.probe.toolNames.length
                            ? workspace.selectedItem.probe.toolNames.join(", ")
                            : workspace.tr("还没有探测结果。", "No probe result yet."))
                    color: workspace.selectedItem.probe && workspace.selectedItem.probe.error ? root.statusError : root.textPrimary
                    font.pixelSize: root.typeMeta
                    wrapMode: Text.WordWrap
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            PillActionButton {
                text: workspace.tr("测试连接", "Test")
                iconSource: workspace.icon("activity")
                outlined: true
                fillColor: "transparent"
                hoverFillColor: root.bgCardHover
                outlineColor: root.borderSubtle
                hoverOutlineColor: root.borderDefault
                textColor: root.textPrimary
                onClicked: if (workspace.hasToolsService) workspace.toolsService.probeMcpServerPayload(root.draftPayload())
            }

            PillActionButton {
                text: workspace.tr("保存服务", "Save server")
                iconSource: workspace.icon("circle-spark")
                fillColor: root.accent
                hoverFillColor: root.accentHover
                onClicked: if (workspace.hasToolsService) workspace.toolsService.saveMcpServer(root.draftPayload())
            }

            Item { Layout.fillWidth: true }

            PillActionButton {
                text: workspace.tr("删除", "Delete")
                fillColor: root.statusError
                hoverFillColor: Qt.darker(root.statusError, 1.06)
                onClicked: if (workspace.hasToolsService) workspace.toolsService.deleteMcpServer(initialDraft.previousName)
            }
        }
    }
}
