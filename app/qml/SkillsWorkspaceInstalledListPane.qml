pragma ComponentBehavior: Bound

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    required property var workspace
    property bool compactLayout: false
    objectName: "skillsInstalledListPane"

    SplitView.preferredWidth: compactLayout ? 0 : 356
    SplitView.minimumWidth: compactLayout ? 0 : 280
    SplitView.preferredHeight: compactLayout ? workspace.compactListPaneHeight : 0
    SplitView.minimumHeight: compactLayout ? 108 : 0
    SplitView.fillWidth: true
    SplitView.fillHeight: true
    radius: 24
    color: "transparent"
    border.width: 0

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 14
        spacing: 12

        RowLayout {
            Layout.fillWidth: true

            Text {
                Layout.fillWidth: true
                text: workspace.tr("技能列表", "Skills")
                color: textPrimary
                font.pixelSize: typeLabel
                font.weight: weightBold
            }

            Rectangle {
                radius: 11
                color: isDark ? "#20FFFFFF" : "#14000000"
                implicitHeight: 22
                implicitWidth: listCountLabel.implicitWidth + 16

                Text {
                    id: listCountLabel
                    anchors.centerIn: parent
                    text: workspace.installedCountSummary()
                    color: textSecondary
                    font.pixelSize: typeMeta
                    font.weight: weightBold
                }
            }
        }

        ListView {
            id: skillList
            objectName: "skillsInstalledList"
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: 10
            bottomMargin: 12
            boundsBehavior: Flickable.StopAtBounds
            reuseItems: true
            cacheBuffer: workspace.listCacheBuffer
            ScrollIndicator.vertical: ScrollIndicator {
                visible: false
                width: 4
                contentItem: Rectangle {
                    implicitWidth: 2
                    radius: 1
                    color: isDark ? "#28FFFFFF" : "#22000000"
                }
            }
            model: workspace.installedSkillsModel

            delegate: SkillsWorkspaceInstalledCard {
                width: skillList.width
                workspace: root.workspace
                skill: modelData
            }

            footer: Item {
                width: skillList.width
                height: workspace.installedSkillCount === 0 ? 180 : 0

                SkillsWorkspaceEmptyState {
                    anchors.fill: parent
                    title: workspace.tr("没有匹配的技能", "No matching skills")
                    description: workspace.tr(
                        "试试清空搜索，或切换筛选范围。",
                        "Try clearing the search, or switch the filter scope."
                    )
                }
            }
        }
    }
}
