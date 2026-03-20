import QtQuick 2.15
import QtQuick.Layouts 1.15

ToolsWorkspaceFormScroll {
    id: root

    property var workspace

    ToolsWorkspaceDetailCard {
        workspace: root.workspace
        Text { text: workspace.tr("可用后端", "Available backends"); color: root.textPrimary; font.pixelSize: root.typeLabel; font.weight: root.weightBold }

        Text {
            Layout.fillWidth: true
            text: workspace.tr("这里不配置具体参数，只展示当前环境里可用的编程后端。", "This panel does not configure per-backend settings; it only shows the coding backends available in the current environment.")
            color: root.textSecondary
            font.pixelSize: root.typeMeta
            maximumLineCount: 2
            elide: Text.ElideRight
            wrapMode: Text.WordWrap
        }

        Flow {
            Layout.fillWidth: true
            spacing: 8

            Repeater {
                model: (workspace.selectedItem.configValues.backends || []).length ? workspace.selectedItem.configValues.backends : [workspace.tr("当前未检测到后端", "No backend detected")]

                delegate: Rectangle {
                    required property var modelData
                    radius: 12
                    height: 26
                    color: root.isDark ? "#1D1713" : "#FFFFFF"
                    border.width: 1
                    border.color: root.isDark ? "#16FFFFFF" : "#10000000"
                    width: backendLabel.implicitWidth + 18

                    Text {
                        id: backendLabel
                        anchors.centerIn: parent
                        text: String(modelData)
                        color: root.textPrimary
                        font.pixelSize: root.typeCaption
                        font.weight: root.weightBold
                    }
                }
            }
        }
    }
}
