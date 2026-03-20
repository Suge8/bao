import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

WorkspaceAdaptiveHeader {
    id: panel

    required property var workspaceRoot

    compactLayout: workspaceRoot.compactLayout
    panelColor: isDark ? "#15100D" : "#FFF7F0"
    panelBorderColor: isDark ? "#22FFFFFF" : "#14000000"
    overlayColor: isDark ? "#0BFFFFFF" : "#08FFFFFF"
    overlayVisible: true
    sideGlowVisible: false
    accentBlobVisible: false
    padding: 14

    introContent: Component {
        Item {
            objectName: "memoryWorkspaceHeaderIntro"
            implicitHeight: introRow.implicitHeight

            Row {
                id: introRow
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                spacing: 10

                WorkspaceHeroIcon {
                    iconSource: workspaceRoot.currentScope === "memory"
                        ? workspaceRoot.memoryIconSource
                        : workspaceRoot.experienceIconSource
                }

                Column {
                    anchors.verticalCenter: parent.verticalCenter
                    width: Math.max(0, introRow.width - 44)
                    spacing: 2

                    Text {
                        width: parent.width
                        text: workspaceRoot.currentHeaderTitle()
                        color: textPrimary
                        font.pixelSize: typeTitle - 1
                        font.weight: weightBold
                        elide: Text.ElideRight
                    }

                    Text {
                        width: parent.width
                        text: workspaceRoot.currentHeaderCaption()
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
            objectName: "memoryWorkspaceHeaderTabs"
            implicitWidth: memoryScopeTabs.implicitWidth
            implicitHeight: memoryScopeTabs.implicitHeight

            SegmentedTabs {
                id: memoryScopeTabs
                anchors.centerIn: parent
                preferredTrackWidth: 232
                fillSegments: true
                currentValue: workspaceRoot.currentScope
                items: [
                    { value: "memory", label: workspaceRoot.tr("长期记忆", "Memory"), icon: workspaceRoot.memoryIconSource },
                    { value: "experience", label: workspaceRoot.tr("经验", "Experiences"), icon: workspaceRoot.experienceIconSource }
                ]
                onSelected: function(value) {
                    workspaceRoot.currentScope = value
                    if (value === "memory")
                        workspaceRoot.syncEditorFromSelection(false)
                    else
                        workspaceRoot.applyExperienceFilters()
                }
            }
        }
    }

    trailingContent: Component {
        Item {
            objectName: "memoryWorkspaceHeaderActions"
            implicitWidth: refreshButton.implicitWidth
            implicitHeight: refreshButton.implicitHeight

            AsyncActionButton {
                id: refreshButton
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                text: workspaceRoot.hasMemoryService && workspaceRoot.memoryService.blockingBusy
                    ? workspaceRoot.tr("处理中", "Working")
                    : workspaceRoot.tr("刷新", "Refresh")
                busy: workspaceRoot.hasMemoryService && workspaceRoot.memoryService.blockingBusy
                iconSource: workspaceRoot.refreshIconSource
                fillColor: isDark ? "#2A1B11" : "#E7D5C7"
                hoverFillColor: isDark ? "#342116" : "#DDC7B6"
                textColor: textPrimary
                spinnerColor: textPrimary
                spinnerSecondaryColor: isDark ? "#A0F7EFE7" : "#886B5649"
                spinnerHaloColor: isDark ? "#24FFFFFF" : "#186B5649"
                minHeight: 36
                horizontalPadding: 18
                onClicked: {
                    if (workspaceRoot.currentScope === "memory")
                        workspaceRoot.memoryService.refreshMemoryCategories()
                    else
                        workspaceRoot.applyExperienceFilters()
                }
            }
        }
    }
}
