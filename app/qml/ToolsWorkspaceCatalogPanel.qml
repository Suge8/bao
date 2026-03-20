import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root

    property var workspace
    property bool compactLayout: false
    property bool serverMode: false
    property string title: ""
    property int itemCount: 0
    property var model: null
    property string emptyTitle: ""
    property string emptyDescription: ""
    objectName: serverMode ? "toolsServerCatalogPanel" : "toolsCatalogPanel"

    readonly property bool isDark: workspace ? workspace.isDark : false
    readonly property color textSecondary: workspace ? workspace.textSecondary : "transparent"
    readonly property int typeMeta: workspace ? workspace.typeMeta : 12
    readonly property int weightBold: workspace ? workspace.weightBold : Font.Normal

    SplitView.preferredWidth: compactLayout ? 0 : (serverMode ? 348 : 356)
    SplitView.minimumWidth: compactLayout ? 0 : 280
    SplitView.preferredHeight: compactLayout ? workspace.compactListPaneHeight : 0
    SplitView.minimumHeight: compactLayout ? workspace.compactListPaneHeight : 0
    SplitView.fillWidth: true
    SplitView.fillHeight: true
    radius: 24
    color: "transparent"
    border.width: 0
    border.color: "transparent"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 14
        spacing: 12

        RowLayout {
            Layout.fillWidth: true

            Text {
                Layout.fillWidth: true
                text: root.title
                color: root.workspace.textPrimary
                font.pixelSize: root.workspace.typeLabel
                font.weight: root.workspace.weightBold
            }

            Rectangle {
                radius: 11
                color: root.isDark ? "#20FFFFFF" : "#14000000"
                implicitHeight: 22
                implicitWidth: countLabel.implicitWidth + 16

                Text {
                    id: countLabel
                    anchors.centerIn: parent
                    text: String(root.itemCount)
                    color: root.textSecondary
                    font.pixelSize: root.typeMeta
                    font.weight: root.weightBold
                }
            }
        }

        ListView {
            id: catalogList
            objectName: root.serverMode ? "toolsServerList" : "toolsCatalogList"
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: 10
            bottomMargin: 12
            model: root.model
            reuseItems: true
            cacheBuffer: workspace.listCacheBuffer
            boundsBehavior: Flickable.StopAtBounds
            ScrollIndicator.vertical: ScrollIndicator {
                visible: false
                width: 4
                contentItem: Rectangle {
                    implicitWidth: 2
                    radius: 1
                    color: root.isDark ? "#28FFFFFF" : "#22000000"
                }
            }

            delegate: ToolsWorkspaceCatalogCard {
                required property var modelData
                workspace: root.workspace
                itemData: modelData
                selected: root.workspace.hasToolsService && root.workspace.toolsService.selectedItemId === modelData.id
                serverMode: root.serverMode
                onClicked: if (root.workspace.hasToolsService) root.workspace.toolsService.selectItem(modelData.id)
            }

            footer: Item {
                width: parent.width
                height: root.itemCount === 0 ? 180 : 0

                ToolsWorkspaceEmptyState {
                    anchors.centerIn: parent
                    visible: parent.height > 0
                    workspace: root.workspace
                    title: root.emptyTitle
                    description: root.emptyDescription
                    titleObjectName: root.serverMode ? "toolsServerCatalogEmptyTitle" : "toolsCatalogEmptyTitle"
                    descriptionObjectName: root.serverMode ? "toolsServerCatalogEmptyDescription" : "toolsCatalogEmptyDescription"
                }
            }
        }
    }
}
