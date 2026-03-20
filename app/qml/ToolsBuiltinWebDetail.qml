import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ToolsWorkspaceFormScroll {
    id: root

    property var workspace

    ToolsWorkspaceDetailCard {
        workspace: root.workspace
        Text { text: workspace.tr("搜索与抓取", "Search and retrieval"); color: root.textPrimary; font.pixelSize: root.typeLabel; font.weight: root.weightBold }

        Text { text: workspace.tr("搜索服务提供方", "Search provider"); color: root.textSecondary; font.pixelSize: root.typeMeta }
        TextField { id: providerField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; text: String(workspace.selectedItem.configValues.provider || ""); color: root.textPrimary; placeholderText: "tavily / brave / exa" }

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6
                Text { text: "Tavily"; color: root.textSecondary; font.pixelSize: root.typeMeta }
                TextField { id: tavilyField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; echoMode: TextInput.Password; text: String(workspace.selectedItem.configValues.tavilyApiKey || ""); color: root.textPrimary; placeholderText: "tvly-..." }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6
                Text { text: "Brave"; color: root.textSecondary; font.pixelSize: root.typeMeta }
                TextField { id: braveField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; echoMode: TextInput.Password; text: String(workspace.selectedItem.configValues.braveApiKey || ""); color: root.textPrimary; placeholderText: "BSA..." }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6
                Text { text: "Exa"; color: root.textSecondary; font.pixelSize: root.typeMeta }
                TextField { id: exaField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; echoMode: TextInput.Password; text: String(workspace.selectedItem.configValues.exaApiKey || ""); color: root.textPrimary; placeholderText: "exa_..." }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6
                Text { text: workspace.tr("最大结果数", "Max results"); color: root.textSecondary; font.pixelSize: root.typeMeta }
                TextField { id: maxResultsField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; text: String(workspace.selectedItem.configValues.maxResults || 5); color: root.textPrimary; placeholderText: "5" }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Switch { id: browserEnabledSwitch; checked: Boolean(workspace.selectedItem.configValues.browserEnabled) }

            Text {
                Layout.fillWidth: true
                text: workspace.tr("启用托管浏览器自动化。Bao 只在需要交互页面、登录流或反爬回退时按需启动。", "Enable managed browser automation. Bao only starts it on demand for interactive pages, login flows, or anti-bot fallback.")
                color: root.textPrimary
                font.pixelSize: root.typeBody
                wrapMode: Text.WordWrap
            }
        }

        Text { text: workspace.tr("运行时状态", "Runtime status"); color: root.textSecondary; font.pixelSize: root.typeMeta }
        Text {
            Layout.fillWidth: true
            text: Boolean(workspace.selectedItem.configValues.browserAvailable)
                ? workspace.tr("托管浏览器运行时已就绪。", "Managed browser runtime is ready.")
                : String(workspace.selectedItem.configValues.browserStatusDetail || workspace.tr("托管浏览器运行时尚未就绪。", "Managed browser runtime is not ready yet."))
            color: root.textPrimary
            font.pixelSize: root.typeBody
            wrapMode: Text.WordWrap
        }

        Text {
            Layout.fillWidth: true
            visible: String(workspace.selectedItem.configValues.browserProfilePath || "").length > 0
            text: workspace.tr("托管配置目录", "Managed profile") + ": " + String(workspace.selectedItem.configValues.browserProfilePath || "")
            color: root.textSecondary
            font.pixelSize: root.typeMeta
            wrapMode: Text.WrapAnywhere
        }

        Text {
            Layout.fillWidth: true
            visible: String(workspace.selectedItem.configValues.browserRuntimeRoot || "").length > 0
            text: workspace.tr("运行时目录", "Runtime root") + ": " + String(workspace.selectedItem.configValues.browserRuntimeRoot || "")
            color: root.textSecondary
            font.pixelSize: root.typeMeta
            wrapMode: Text.WrapAnywhere
        }

        RowLayout {
            Layout.fillWidth: true
            Item { Layout.fillWidth: true }

            PillActionButton {
                text: workspace.tr("保存网页配置", "Save web settings")
                iconSource: workspace.icon("circle-spark")
                fillColor: root.accent
                hoverFillColor: root.accentHover
                onClicked: if (workspace.hasToolsService) workspace.toolsService.saveConfig({
                    "tools.web.search.provider": providerField.text,
                    "tools.web.search.tavilyApiKey": tavilyField.text,
                    "tools.web.search.braveApiKey": braveField.text,
                    "tools.web.search.exaApiKey": exaField.text,
                    "tools.web.search.maxResults": parseInt(maxResultsField.text || "5"),
                    "tools.web.browser.enabled": browserEnabledSwitch.checked
                })
            }
        }
    }
}
