import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ToolsWorkspaceFormScroll {
    id: root

    property var workspace

    ToolsWorkspaceDetailCard {
        workspace: root.workspace
        Text { text: workspace.tr("向量嵌入", "Embeddings"); color: root.textPrimary; font.pixelSize: root.typeLabel; font.weight: root.weightBold }

        Text { text: workspace.tr("模型", "Model"); color: root.textSecondary; font.pixelSize: root.typeMeta }
        TextField { id: modelField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; text: String(workspace.selectedItem.configValues.model || ""); color: root.textPrimary; placeholderText: "text-embedding-3-small" }

        Text { text: workspace.tr("API 密钥", "API Key"); color: root.textSecondary; font.pixelSize: root.typeMeta }
        TextField { id: keyField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; echoMode: TextInput.Password; text: String(workspace.selectedItem.configValues.apiKey || ""); color: root.textPrimary; placeholderText: "sk-..." }

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6
                Text { text: workspace.tr("基础地址", "Base URL"); color: root.textSecondary; font.pixelSize: root.typeMeta }
                TextField { id: baseUrlField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; text: String(workspace.selectedItem.configValues.baseUrl || ""); color: root.textPrimary; placeholderText: "https://api.openai.com/v1" }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6
                Text { text: workspace.tr("维度", "Dimensions"); color: root.textSecondary; font.pixelSize: root.typeMeta }
                TextField { id: dimField; property bool baoClickAwayEditor: true; Layout.fillWidth: true; text: String(workspace.selectedItem.configValues.dim || 0); color: root.textPrimary; placeholderText: "0" }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Item { Layout.fillWidth: true }

            PillActionButton {
                text: workspace.tr("保存嵌入配置", "Save embedding settings")
                iconSource: workspace.icon("circle-spark")
                fillColor: root.accent
                hoverFillColor: root.accentHover
                onClicked: if (workspace.hasToolsService) workspace.toolsService.saveConfig({
                    "tools.embedding.model": modelField.text,
                    "tools.embedding.apiKey": keyField.text,
                    "tools.embedding.baseUrl": baseUrlField.text,
                    "tools.embedding.dim": parseInt(dimField.text || "0")
                })
            }
        }
    }
}
