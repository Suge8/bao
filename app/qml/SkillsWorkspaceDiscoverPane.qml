pragma ComponentBehavior: Bound

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

SplitView {
    id: root
    required property var workspace
    objectName: "skillsWorkspaceDiscoverSplit"

    orientation: workspace.compactLayout ? Qt.Vertical : Qt.Horizontal
    spacing: workspace.compactLayout ? 12 : 10
    handle: WorkspaceSplitHandle {}

    SkillsWorkspaceDiscoverResultsPane { workspace: root.workspace; compactLayout: root.workspace.compactLayout }
    SkillsWorkspaceDiscoverDetailPane { workspace: root.workspace; compactLayout: root.workspace.compactLayout }
}
