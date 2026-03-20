pragma ComponentBehavior: Bound

import QtQuick 2.15

WorkspaceAdaptiveHeader {
    required property var workspace
    property var createSkillModal: null

    compactLayout: workspace.compactLayout
    panelColor: isDark ? "#15100D" : "#FFF7F0"
    panelBorderColor: isDark ? "#22FFFFFF" : "#14000000"
    overlayColor: isDark ? "#0BFFFFFF" : "#08FFFFFF"
    overlayVisible: true
    sideGlowVisible: false
    accentBlobVisible: false
    padding: 14

    introContent: Component {
        Item {
            objectName: "skillsWorkspaceHeaderIntro"
            implicitHeight: introRow.implicitHeight

            Row {
                id: introRow
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                spacing: 10

                WorkspaceHeroIcon { iconSource: workspace.icon("book-stack") }

                Column {
                    anchors.verticalCenter: parent.verticalCenter
                    width: Math.max(0, introRow.width - 44)
                    spacing: 2

                    Text {
                        width: parent.width
                        text: workspace.workspaceString("workspace_skills_title", "技能", "Skills")
                        color: textPrimary
                        font.pixelSize: typeTitle - 1
                        font.weight: weightBold
                        elide: Text.ElideRight
                    }

                    Text {
                        width: parent.width
                        text: workspace.workspaceString(
                            "workspace_skills_caption",
                            "管理 AI 拓展技能",
                            "Manage AI extension skills"
                        )
                        color: textSecondary
                        font.pixelSize: typeMeta
                        maximumLineCount: 1
                        elide: Text.ElideRight
                    }
                }
            }
        }
    }

    centerContent: Component {
        Item {
            objectName: "skillsWorkspaceHeaderTabs"
            implicitWidth: modeTabBar.implicitWidth
            implicitHeight: modeTabBar.implicitHeight

            SegmentedTabs {
                id: modeTabBar
                anchors.centerIn: parent
                currentValue: workspace.currentMode
                items: [
                    { value: "installed", label: workspace.tr("已安装", "Installed"), icon: workspace.icon("book-stack") },
                    { value: "discover", label: workspace.tr("发现", "Discover"), icon: workspace.icon("page-search") }
                ]
                onSelected: function(value) { workspace.currentMode = value }
            }
        }
    }

    trailingContent: Component {
        Item {
            objectName: "skillsWorkspaceHeaderActions"
            implicitWidth: actionRow.implicitWidth
            implicitHeight: actionRow.implicitHeight

            Row {
                id: actionRow
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                spacing: 8

                PillActionButton {
                    text: workspace.tr("目录地址", "Folder path")
                    iconSource: workspace.labIcon("copy-file-path")
                    minHeight: 34
                    horizontalPadding: 18
                    outlined: true
                    fillColor: "transparent"
                    hoverFillColor: bgCardHover
                    outlineColor: borderSubtle
                    hoverOutlineColor: borderDefault
                    textColor: textPrimary
                    onClicked: if (workspace.hasSkillsService) workspace.skillsService.openUserSkillsFolder()
                }

                PillActionButton {
                    visible: workspace.currentMode === "installed"
                    text: workspace.tr("新建技能", "New skill")
                    iconSource: workspace.icon("circle-spark")
                    minHeight: 34
                    horizontalPadding: 18
                    fillColor: accent
                    hoverFillColor: accentHover
                    onClicked: if (createSkillModal) createSkillModal.open()
                }
            }
        }
    }
}
