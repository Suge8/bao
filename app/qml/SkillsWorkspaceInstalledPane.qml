pragma ComponentBehavior: Bound

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

SplitView {
    id: root
    required property var workspace
    objectName: "skillsWorkspaceInstalledSplit"

    orientation: workspace.compactLayout ? Qt.Vertical : Qt.Horizontal
    spacing: workspace.compactLayout ? 10 : 10
    handle: WorkspaceSplitHandle {}

    Item {
        visible: root.workspace.compactLayout
        SplitView.preferredWidth: 0
        SplitView.fillWidth: true
        SplitView.preferredHeight: root.workspace.compactBrowserPaneHeight
        SplitView.minimumHeight: root.workspace.compactBrowserPaneHeight

        ColumnLayout {
            anchors.fill: parent
            spacing: 10

            SkillsWorkspaceFilterRail {
                Layout.fillWidth: true
                Layout.preferredHeight: root.workspace.compactFilterPaneHeight
                Layout.minimumHeight: root.workspace.compactFilterPaneHeight
                workspace: root.workspace
                compactLayout: true
            }

            SkillsWorkspaceInstalledListPane {
                Layout.fillWidth: true
                Layout.fillHeight: true
                workspace: root.workspace
                compactLayout: true
            }
        }
    }

    SkillsWorkspaceFilterRail {
        visible: !root.workspace.compactLayout
        workspace: root.workspace
        compactLayout: false
    }
    SkillsWorkspaceInstalledListPane {
        visible: !root.workspace.compactLayout
        workspace: root.workspace
        compactLayout: false
    }
    SkillsWorkspaceInstalledDetailPane { workspace: root.workspace; compactLayout: root.workspace.compactLayout }
}
