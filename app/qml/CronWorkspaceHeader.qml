import QtQuick 2.15

WorkspaceAdaptiveHeader {
    id: root

    property var workspace

    compactLayout: workspace.compactLayout
    panelColor: workspace.isDark ? "#15100D" : "#FFF7F0"
    panelBorderColor: workspace.isDark ? "#22FFFFFF" : "#14000000"
    overlayColor: workspace.isDark ? "#0BFFFFFF" : "#08FFFFFF"
    overlayVisible: true
    sideGlowVisible: false
    accentBlobVisible: false
    padding: 14

    introContent: Component {
        Item {
            objectName: "cronWorkspaceHeaderIntro"
            implicitHeight: introRow.implicitHeight

            Row {
                id: introRow
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                spacing: 10

                WorkspaceHeroIcon { iconSource: workspace.icon("calendar-rotate") }

                Column {
                    anchors.verticalCenter: parent.verticalCenter
                    width: Math.max(0, introRow.width - 50)
                    spacing: 2

                    Text {
                        width: parent.width
                        text: workspace.workspaceString("workspace_cron_title", "自动任务", "Automation")
                        color: workspace.textPrimary
                        font.pixelSize: workspace.typeTitle - 1
                        font.weight: workspace.weightBold
                        elide: Text.ElideRight
                    }

                    Text {
                        width: parent.width
                        text: workspace.automationHeaderCaption()
                        color: workspace.textSecondary
                        font.pixelSize: workspace.typeMeta
                        maximumLineCount: 1
                        elide: Text.ElideRight
                    }
                }
            }
        }
    }

    centerContent: Component {
        Item {
            objectName: "cronWorkspaceHeaderTabs"
            implicitWidth: automationTabBar.implicitWidth
            implicitHeight: automationTabBar.implicitHeight

            SegmentedTabs {
                id: automationTabBar
                objectName: "automationTabBar"
                anchors.centerIn: parent
                preferredTrackWidth: 214
                fillSegments: true
                currentValue: workspace.currentPane
                accentColor: workspace.cronAccent
                items: [
                    { value: "tasks", label: workspace.tr("计划任务", "Tasks"), icon: workspace.icon("calendar-rotate") },
                    { value: "checks", label: workspace.tr("自动检查", "Checks"), icon: workspace.labIcon("watch-activity") }
                ]
                onSelected: function(value) { workspace.switchPane(value) }
            }
        }
    }

    trailingContent: Component {
        Item {
            objectName: "cronWorkspaceHeaderActions"
            implicitWidth: actionRow.implicitWidth
            implicitHeight: actionRow.implicitHeight

            Row {
                id: actionRow
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                spacing: 8

                PillActionButton {
                    visible: workspace.currentPane === "tasks"
                    text: workspace.tr("新建任务", "New task")
                    iconSource: workspace.icon("circle-spark")
                    fillColor: workspace.cronAccent
                    hoverFillColor: workspace.cronAccentHover
                    onClicked: if (workspace.hasCronService) workspace.cronService.newDraft()
                }

                PillActionButton {
                    text: workspace.tr("刷新", "Refresh")
                    iconSource: workspace.labIcon("watch-loader")
                    fillColor: "transparent"
                    hoverFillColor: workspace.bgCardHover
                    outlineColor: workspace.borderSubtle
                    hoverOutlineColor: workspace.borderDefault
                    textColor: workspace.textPrimary
                    outlined: true
                    onClicked: workspace.refreshCurrentPane()
                }
            }
        }
    }
}
