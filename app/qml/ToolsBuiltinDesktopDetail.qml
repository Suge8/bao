import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ToolsWorkspaceFormScroll {
    id: root

    property var workspace

    ToolsWorkspaceDetailCard {
        workspace: root.workspace
        Text { text: workspace.tr("桌面自动化", "Desktop automation"); color: root.textPrimary; font.pixelSize: root.typeLabel; font.weight: root.weightBold }

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Switch { id: enabledSwitch; checked: Boolean(workspace.selectedItem.configValues.enabled) }

            Text {
                Layout.fillWidth: true
                text: workspace.tr("允许 Bao 通过截图、点击、键盘和滚动操作当前桌面。", "Allow Bao to act on the current desktop with screenshots, clicks, keyboard input, and scrolling.")
                color: root.textPrimary
                font.pixelSize: root.typeBody
                wrapMode: Text.WordWrap
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Item { Layout.fillWidth: true }

            PillActionButton {
                text: workspace.tr("保存桌面权限", "Save desktop access")
                iconSource: workspace.icon("circle-spark")
                fillColor: root.accent
                hoverFillColor: root.accentHover
                onClicked: if (workspace.hasToolsService) workspace.toolsService.saveConfig({"tools.desktop.enabled": enabledSwitch.checked})
            }
        }
    }
}
