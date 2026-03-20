import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "ToolsWorkspaceLogic.js" as ToolsWorkspaceLogic

Rectangle {
    id: root

    property var workspace
    property bool compactLayout: false
    property int reloadToken: 0
    objectName: "toolsInstalledDetailPane"

    readonly property color textPrimary: workspace ? workspace.textPrimary : "transparent"
    readonly property color textSecondary: workspace ? workspace.textSecondary : "transparent"
    readonly property int typeLabel: workspace ? workspace.typeLabel : 14
    readonly property int typeCaption: workspace ? workspace.typeCaption : 12
    readonly property int weightBold: workspace ? workspace.weightBold : Font.Normal

    function currentDetailComponent() {
        switch (String(workspace.selectedItem.formKind || "overview")) {
        case "exec":
            return execDetailComponent
        case "web":
            return webDetailComponent
        case "embedding":
            return embeddingDetailComponent
        case "image_generation":
            return imageGenerationDetailComponent
        case "desktop":
            return desktopDetailComponent
        case "coding":
            return codingDetailComponent
        default:
            return overviewDetailComponent
        }
    }

    onReloadTokenChanged: {
        detailLoader.active = false
        detailLoader.active = true
    }

    SplitView.preferredWidth: compactLayout ? 0 : 468
    SplitView.minimumWidth: compactLayout ? 0 : 320
    SplitView.preferredHeight: compactLayout ? workspace.compactDetailPaneMinHeight : 0
    SplitView.minimumHeight: compactLayout ? workspace.compactDetailPaneMinHeight : 0
    SplitView.fillWidth: true
    SplitView.fillHeight: true
    radius: 24
    color: "transparent"
    border.width: 0
    border.color: "transparent"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 8

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 4

            Text {
                Layout.fillWidth: true
                text: workspace.itemDisplayName(workspace.selectedItem) || workspace.tr("选择一个能力族", "Choose a capability family")
                color: root.textPrimary
                font.pixelSize: root.typeLabel
                font.weight: root.weightBold
                elide: Text.ElideRight
            }

            Text {
                Layout.fillWidth: true
                text: workspace.itemDisplayDetail(workspace.selectedItem)
                    || ToolsWorkspaceLogic.installedDetailFallback(workspace)
                color: root.textSecondary
                font.pixelSize: root.typeCaption
                maximumLineCount: 2
                elide: Text.ElideRight
                wrapMode: Text.WordWrap
            }
        }

        ToolsWorkspaceSummaryCard { workspace: root.workspace; item: workspace.selectedItem }

        Loader {
            id: detailLoader
            Layout.fillWidth: true
            Layout.fillHeight: true
            active: true
            sourceComponent: currentDetailComponent()
        }
    }

    Component { id: overviewDetailComponent; ToolsBuiltinOverviewDetail { workspace: root.workspace } }
    Component { id: execDetailComponent; ToolsBuiltinExecDetail { workspace: root.workspace } }
    Component { id: webDetailComponent; ToolsBuiltinWebDetail { workspace: root.workspace } }
    Component { id: embeddingDetailComponent; ToolsBuiltinEmbeddingDetail { workspace: root.workspace } }
    Component { id: imageGenerationDetailComponent; ToolsBuiltinImageDetail { workspace: root.workspace } }
    Component { id: desktopDetailComponent; ToolsBuiltinDesktopDetail { workspace: root.workspace } }
    Component { id: codingDetailComponent; ToolsBuiltinCodingDetail { workspace: root.workspace } }
}
