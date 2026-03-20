pragma ComponentBehavior: Bound

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    required property var workspace
    property bool compactLayout: false
    objectName: "skillsFilterRail"

    SplitView.preferredWidth: compactLayout ? 0 : 152
    SplitView.minimumWidth: compactLayout ? 0 : 144
    SplitView.maximumWidth: compactLayout ? 0 : 164
    SplitView.preferredHeight: compactLayout ? workspace.compactFilterPaneHeight : 0
    SplitView.minimumHeight: compactLayout ? workspace.compactFilterPaneHeight : 0
    SplitView.fillWidth: compactLayout
    SplitView.fillHeight: !compactLayout
    radius: 24
    color: "transparent"
    border.width: 0

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 14
        spacing: compactLayout ? 8 : 10

        Text {
            text: workspace.tr("筛选", "Filters")
            color: textPrimary
            font.pixelSize: typeMeta
            font.weight: weightBold
        }

        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 42
            radius: 16
            color: bgInput
            border.width: 1
            border.color: borderSubtle

            TextField {
                property bool baoClickAwayEditor: true

                anchors.fill: parent
                hoverEnabled: true
                leftPadding: 14
                rightPadding: 14
                background: null
                color: textPrimary
                placeholderText: workspace.tr("搜索技能…", "Search skills…")
                placeholderTextColor: textPlaceholder
                selectionColor: textSelectionBg
                selectedTextColor: textSelectionFg
                font.pixelSize: typeBody
                text: workspace.skillQueryValue
                onTextEdited: if (workspace.hasSkillsService) workspace.skillsService.setQuery(text)
            }
        }

        Loader {
            Layout.fillWidth: true
            sourceComponent: root.compactLayout ? compactFiltersComponent : wideFiltersComponent
        }

        Item {
            Layout.fillHeight: true
            visible: !root.compactLayout
        }
    }

    Component {
        id: wideFiltersComponent

        ColumnLayout {
            spacing: 6

            Repeater {
                model: workspace.installedFilterOptions

                delegate: PillActionButton {
                    required property var modelData

                    Layout.fillWidth: true
                    text: workspace.isZhLang ? modelData.zh : modelData.en
                    minHeight: 34
                    horizontalPadding: 14
                    outlined: true
                    fillColor: workspace.sourceFilterValue === modelData.value ? accentMuted : "transparent"
                    hoverFillColor: workspace.sourceFilterValue === modelData.value ? accentMuted : bgCardHover
                    outlineColor: workspace.sourceFilterValue === modelData.value ? accent : borderSubtle
                    hoverOutlineColor: workspace.sourceFilterValue === modelData.value ? accentHover : borderDefault
                    textColor: textPrimary
                    onClicked: if (workspace.hasSkillsService) workspace.skillsService.setSourceFilter(modelData.value)
                }
            }
        }
    }

    Component {
        id: compactFiltersComponent

        Flickable {
            width: parent ? parent.width : 0
            implicitHeight: filterChipRow.implicitHeight
            contentWidth: filterChipRow.implicitWidth
            contentHeight: filterChipRow.implicitHeight
            clip: true
            boundsBehavior: Flickable.StopAtBounds
            flickableDirection: Flickable.HorizontalFlick
            interactive: contentWidth > width
            ScrollIndicator.horizontal: ScrollIndicator { visible: false }

            Row {
                id: filterChipRow
                spacing: 8

                Repeater {
                    model: workspace.installedFilterOptions

                    delegate: PillActionButton {
                        required property var modelData

                        text: workspace.isZhLang ? modelData.zh : modelData.en
                        minHeight: 30
                        horizontalPadding: 12
                        outlined: true
                        fillColor: workspace.sourceFilterValue === modelData.value ? accentMuted : "transparent"
                        hoverFillColor: workspace.sourceFilterValue === modelData.value ? accentMuted : bgCardHover
                        outlineColor: workspace.sourceFilterValue === modelData.value ? accent : borderSubtle
                        hoverOutlineColor: workspace.sourceFilterValue === modelData.value ? accentHover : borderDefault
                        textColor: textPrimary
                        onClicked: if (workspace.hasSkillsService) workspace.skillsService.setSourceFilter(modelData.value)
                    }
                }
            }
        }
    }
}
