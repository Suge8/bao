pragma ComponentBehavior: Bound

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    required property var workspace
    property bool compactLayout: false
    objectName: "skillsDiscoverDetailPane"

    SplitView.preferredWidth: compactLayout ? 0 : 468
    SplitView.minimumWidth: compactLayout ? 0 : 320
    SplitView.preferredHeight: compactLayout ? workspace.compactDetailPaneMinHeight : 0
    SplitView.minimumHeight: compactLayout ? workspace.compactDetailPaneMinHeight : 0
    SplitView.fillWidth: true
    SplitView.fillHeight: true
    radius: 24
    color: "transparent"
    border.width: 0

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 8

        SkillsWorkspaceDiscoverSummaryCard {
            Layout.fillWidth: true
            workspace: root.workspace
        }

        SkillsWorkspaceDiscoverTaskCard {
            Layout.fillWidth: true
            workspace: root.workspace
        }
    }
}
