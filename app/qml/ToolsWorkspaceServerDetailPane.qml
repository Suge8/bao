import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root

    property var workspace
    property bool compactLayout: false
    property int reloadToken: 0
    objectName: "toolsServerDetailPane"

    onReloadTokenChanged: {
        detailLoader.active = false
        detailLoader.active = true
    }

    SplitView.preferredWidth: compactLayout ? 0 : 492
    SplitView.minimumWidth: compactLayout ? 0 : 340
    SplitView.preferredHeight: compactLayout ? workspace.compactDetailPaneMinHeight : 0
    SplitView.minimumHeight: compactLayout ? workspace.compactDetailPaneMinHeight : 0
    SplitView.fillWidth: true
    SplitView.fillHeight: true
    radius: 24
    color: "transparent"
    border.width: 0
    border.color: "transparent"

    Loader {
        id: detailLoader
        anchors.fill: parent
        anchors.margins: 16
        active: true
        sourceComponent: root.workspace.selectedItem.kind === "mcp_server" ? serverDetailComponent : emptyDetailComponent
    }

    Component { id: emptyDetailComponent; ToolsWorkspaceEmptyServerDetail { workspace: root.workspace } }
    Component { id: serverDetailComponent; ToolsMcpServerDetail { workspace: root.workspace } }
}
