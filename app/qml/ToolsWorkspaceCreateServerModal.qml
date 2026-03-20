import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

AppModal {
    id: root

    property var workspace

    readonly property color textPrimary: workspace ? workspace.textPrimary : "transparent"
    readonly property color textSecondary: workspace ? workspace.textSecondary : "transparent"
    readonly property color accent: workspace ? workspace.accent : "transparent"
    readonly property color accentHover: workspace ? workspace.accentHover : "transparent"
    readonly property color bgCardHover: workspace ? workspace.bgCardHover : "transparent"
    readonly property color borderSubtle: workspace ? workspace.borderSubtle : "transparent"
    readonly property color borderDefault: workspace ? workspace.borderDefault : "transparent"
    readonly property int typeBody: workspace ? workspace.typeBody : 14
    readonly property int typeMeta: workspace ? workspace.typeMeta : 12

    title: workspace.tr("新增 MCP 服务", "Create MCP server")
    closeText: workspace.tr("关闭", "Close")
    darkMode: workspace.isDark
    maxModalWidth: 620
    maxModalHeight: 680

    function draftPayload() {
        return {
            name: nameField.text,
            transport: transportCombo.currentText,
            command: commandField.text,
            argsText: argsField.text,
            envText: envField.text,
            url: urlField.text,
            headersText: headersField.text,
            toolTimeoutSeconds: timeoutField.text,
            maxTools: maxToolsField.text,
            slimSchema: slimSchemaSwitch.checked
        }
    }

    onOpened: {
        nameField.text = ""
        transportCombo.currentIndex = 0
        commandField.text = ""
        argsField.text = ""
        envField.text = ""
        urlField.text = ""
        headersField.text = ""
        timeoutField.text = "30"
        maxToolsField.text = "0"
        slimSchemaSwitch.checked = false
        nameField.forceActiveFocus()
    }

    ColumnLayout {
        width: parent.width
        spacing: 12

        Text {
            Layout.fillWidth: true
            text: workspace.tr("支持 stdio 和 HTTP 两种传输方式。创建后会写入 `tools.mcpServers`。", "Both stdio and HTTP transports are supported. Bao writes the result into `tools.mcpServers`.")
            color: root.textSecondary
            font.pixelSize: root.typeMeta
            wrapMode: Text.WordWrap
        }

        Text { text: workspace.tr("名称", "Name"); color: root.textSecondary; font.pixelSize: root.typeMeta }
        TextField { id: nameField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; color: root.textPrimary }

        Text { text: workspace.tr("传输方式", "Transport"); color: root.textSecondary; font.pixelSize: root.typeMeta }
        ComboBox { id: transportCombo; Layout.fillWidth: true; model: ["stdio", "http"] }

        ColumnLayout {
            visible: transportCombo.currentText === "stdio"
            Layout.fillWidth: true
            spacing: 10

            Text { text: workspace.tr("命令", "Command"); color: root.textSecondary; font.pixelSize: root.typeMeta }
            TextField { id: commandField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; color: root.textPrimary; placeholderText: "npx" }

            Text { text: workspace.tr("参数（每行一个）", "Args (one per line)"); color: root.textSecondary; font.pixelSize: root.typeMeta }
            TextArea { id: argsField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; Layout.preferredHeight: 86; color: root.textPrimary; wrapMode: TextArea.Wrap }

            Text { text: workspace.tr("环境变量（KEY=VALUE）", "Environment (KEY=VALUE)"); color: root.textSecondary; font.pixelSize: root.typeMeta }
            TextArea { id: envField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; Layout.preferredHeight: 76; color: root.textPrimary; wrapMode: TextArea.Wrap }
        }

        ColumnLayout {
            visible: transportCombo.currentText === "http"
            Layout.fillWidth: true
            spacing: 10

            Text { text: workspace.tr("URL", "URL"); color: root.textSecondary; font.pixelSize: root.typeMeta }
            TextField { id: urlField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; color: root.textPrimary; placeholderText: "https://example.com/mcp" }

            Text { text: workspace.tr("请求头（Header: Value）", "Headers (Header: Value)"); color: root.textSecondary; font.pixelSize: root.typeMeta }
            TextArea { id: headersField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; Layout.preferredHeight: 76; color: root.textPrimary; wrapMode: TextArea.Wrap }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            TextField { id: timeoutField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; color: root.textPrimary; placeholderText: workspace.tr("超时秒数", "Timeout seconds") }
            TextField { id: maxToolsField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; color: root.textPrimary; placeholderText: workspace.tr("最大工具数（0=不限）", "Max tools (0=unlimited)") }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Switch { id: slimSchemaSwitch }

            Text {
                Layout.fillWidth: true
                text: workspace.tr("覆盖全局精简结构设置", "Override the global slim schema setting")
                color: root.textPrimary
                font.pixelSize: root.typeBody
                wrapMode: Text.WordWrap
            }
        }
    }

    footer: [
        PillActionButton {
            text: workspace.tr("测试", "Test")
            iconSource: workspace.icon("activity")
            outlined: true
            fillColor: "transparent"
            hoverFillColor: root.bgCardHover
            outlineColor: root.borderSubtle
            hoverOutlineColor: root.borderDefault
            textColor: root.textPrimary
            onClicked: if (workspace.hasToolsService) workspace.toolsService.probeMcpServerPayload(root.draftPayload())
        },
        PillActionButton {
            text: workspace.tr("创建服务", "Create server")
            iconSource: workspace.icon("circle-spark")
            fillColor: root.accent
            hoverFillColor: root.accentHover
            onClicked: {
                if (!workspace.hasToolsService)
                    return
                if (workspace.toolsService.saveMcpServer(root.draftPayload()))
                    root.close()
            }
        }
    ]
}
