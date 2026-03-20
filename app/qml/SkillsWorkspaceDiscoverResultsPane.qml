pragma ComponentBehavior: Bound

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    required property var workspace
    property bool compactLayout: false
    objectName: "skillsDiscoverResultsPane"

    SplitView.preferredWidth: compactLayout ? 0 : 520
    SplitView.minimumWidth: compactLayout ? 0 : 360
    SplitView.preferredHeight: compactLayout ? 156 : 0
    SplitView.minimumHeight: compactLayout ? 124 : 0
    SplitView.fillWidth: true
    SplitView.fillHeight: true
    radius: 24
    color: "transparent"
    border.width: 0

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 14
        spacing: 12

        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 42
            radius: 16
            color: bgInput
            border.width: 1
            border.color: borderSubtle

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 14
                anchors.rightMargin: 8
                spacing: 8

                TextField {
                    property bool baoClickAwayEditor: true

                    Layout.fillWidth: true
                    hoverEnabled: true
                    leftPadding: 0
                    rightPadding: 0
                    background: null
                    color: textPrimary
                    placeholderText: workspace.tr("输入关键词搜索技能", "Search skills by keyword")
                    placeholderTextColor: textPlaceholder
                    selectionColor: textSelectionBg
                    selectedTextColor: textSelectionFg
                    font.pixelSize: typeBody
                    text: workspace.discoverQueryValue
                    onTextEdited: if (workspace.hasSkillsService) workspace.skillsService.setDiscoverQuery(text)
                }

                AsyncActionButton {
                    text: workspace.tr("搜索", "Search")
                    iconSource: workspace.icon("page-search")
                    minHeight: 32
                    horizontalPadding: 16
                    busy: workspace.serviceBusy
                    buttonEnabled: workspace.discoverQueryValue.trim().length > 0
                    onClicked: if (workspace.hasSkillsService) workspace.skillsService.searchRemote()
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 42
            radius: 16
            color: bgInput
            border.width: 1
            border.color: borderSubtle

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 14
                anchors.rightMargin: 8
                spacing: 8

                TextField {
                    property bool baoClickAwayEditor: true

                    Layout.fillWidth: true
                    hoverEnabled: true
                    leftPadding: 0
                    rightPadding: 0
                    background: null
                    color: textPrimary
                    placeholderText: "vercel-labs/agent-skills@frontend-design"
                    placeholderTextColor: textPlaceholder
                    selectionColor: textSelectionBg
                    selectedTextColor: textSelectionFg
                    font.pixelSize: typeBody
                    text: workspace.discoverReferenceValue
                    onTextEdited: if (workspace.hasSkillsService) workspace.skillsService.setDiscoverReference(text)
                }

                AsyncActionButton {
                    text: workspace.tr("导入", "Import")
                    iconSource: workspace.icon("circle-spark")
                    minHeight: 32
                    horizontalPadding: 16
                    busy: workspace.serviceBusy
                    buttonEnabled: workspace.discoverReferenceValue.trim().length > 0
                    onClicked: if (workspace.hasSkillsService) workspace.skillsService.installDiscoverReference()
                }

                IconCircleButton {
                    buttonSize: 30
                    iconSource: workspace.icon("page-search")
                    glyphSize: 15
                    fillColor: "transparent"
                    hoverFillColor: bgCardHover
                    outlineColor: borderSubtle
                    glyphColor: textSecondary
                    onClicked: if (workspace.hasSkillsService) workspace.skillsService.openSkillsRegistry()
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true

            Text {
                Layout.fillWidth: true
                text: workspace.tr("搜索结果", "Search results")
                color: textPrimary
                font.pixelSize: typeLabel
                font.weight: weightBold
            }

            Rectangle {
                radius: 11
                color: isDark ? "#20FFFFFF" : "#14000000"
                implicitHeight: 22
                implicitWidth: discoverCountLabel.implicitWidth + 16

                Text {
                    id: discoverCountLabel
                    anchors.centerIn: parent
                    text: String(workspace.discoverResultCount)
                    color: textSecondary
                    font.pixelSize: typeMeta
                    font.weight: weightBold
                }
            }
        }

        ListView {
            id: discoverList
            objectName: "skillsDiscoverList"
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
            model: workspace.discoverResultsModel

            delegate: SkillsWorkspaceDiscoverCard {
                width: discoverList.width
                workspace: root.workspace
                itemData: modelData
            }

            footer: Item {
                width: discoverList.width
                height: workspace.discoverResultCount === 0 ? 180 : 0

                SkillsWorkspaceEmptyState {
                    anchors.fill: parent
                    title: workspace.tr("还没有结果", "No results yet")
                    description: workspace.tr(
                        "输入关键词，或直接填写技能引用。",
                        "Search by keyword, or provide a direct skill reference."
                    )
                }
            }
        }
    }
}
