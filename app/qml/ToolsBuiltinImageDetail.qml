import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ToolsWorkspaceFormScroll {
    id: root

    property var workspace

    ToolsWorkspaceDetailCard {
        workspace: root.workspace
        Text { text: workspace.tr("图像生成", "Image generation"); color: root.textPrimary; font.pixelSize: root.typeLabel; font.weight: root.weightBold }

        Text { text: workspace.tr("API 密钥", "API Key"); color: root.textSecondary; font.pixelSize: root.typeMeta }
        TextField { id: keyField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; echoMode: TextInput.Password; text: String(workspace.selectedItem.configValues.apiKey || ""); color: root.textPrimary; placeholderText: "AIza..." }

        Text { text: workspace.tr("模型", "Model"); color: root.textSecondary; font.pixelSize: root.typeMeta }
        TextField { id: modelField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; text: String(workspace.selectedItem.configValues.model || ""); color: root.textPrimary; placeholderText: "gemini-2.0-flash-exp-image-generation" }

        Text { text: workspace.tr("基础地址", "Base URL"); color: root.textSecondary; font.pixelSize: root.typeMeta }
        TextField { id: baseUrlField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; text: String(workspace.selectedItem.configValues.baseUrl || ""); color: root.textPrimary; placeholderText: "https://generativelanguage.googleapis.com/v1beta" }

        RowLayout {
            Layout.fillWidth: true
            Item { Layout.fillWidth: true }

            PillActionButton {
                text: workspace.tr("保存图像配置", "Save image settings")
                iconSource: workspace.icon("circle-spark")
                fillColor: root.accent
                hoverFillColor: root.accentHover
                onClicked: if (workspace.hasToolsService) workspace.toolsService.saveConfig({
                    "tools.imageGeneration.apiKey": keyField.text,
                    "tools.imageGeneration.model": modelField.text,
                    "tools.imageGeneration.baseUrl": baseUrlField.text
                })
            }
        }
    }
}
