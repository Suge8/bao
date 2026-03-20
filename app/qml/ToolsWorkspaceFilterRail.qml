import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root

    property var workspace
    property bool compactLayout: false
    property string title: ""
    property string placeholderText: ""
    property string queryText: ""
    property var filters: []
    property string selectedFilter: "all"
    objectName: "toolsFilterRail"

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
    border.color: "transparent"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 14
        spacing: compactLayout ? 8 : 10

        Text {
            text: root.title
            color: workspace.textPrimary
            font.pixelSize: workspace.typeMeta
            font.weight: workspace.weightBold
        }

        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 42
            radius: 16
            color: workspace.bgInput
            border.width: 1
            border.color: workspace.borderSubtle

            TextField {
                property bool baoClickAwayEditor: true
                anchors.fill: parent
                leftPadding: 14
                rightPadding: 14
                background: null
                color: workspace.textPrimary
                placeholderText: root.placeholderText
                placeholderTextColor: workspace.textPlaceholder
                selectionColor: workspace.textSelectionBg
                selectedTextColor: workspace.textSelectionFg
                text: root.queryText
                onTextEdited: if (workspace.hasToolsService) workspace.toolsService.setQuery(text)
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
                model: root.filters

                delegate: PillActionButton {
                    required property var modelData
                    Layout.fillWidth: true
                    text: workspace.tr(modelData.zh, modelData.en)
                    minHeight: 34
                    horizontalPadding: 14
                    outlined: true
                    fillColor: root.selectedFilter === modelData.value ? workspace.accentMuted : "transparent"
                    hoverFillColor: root.selectedFilter === modelData.value ? workspace.accentMuted : workspace.bgCardHover
                    outlineColor: root.selectedFilter === modelData.value ? workspace.accent : workspace.borderSubtle
                    hoverOutlineColor: root.selectedFilter === modelData.value ? workspace.accentHover : workspace.borderDefault
                    textColor: workspace.textPrimary
                    onClicked: if (workspace.hasToolsService) workspace.toolsService.setSourceFilter(modelData.value)
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
                    model: root.filters

                    delegate: PillActionButton {
                        required property var modelData
                        text: workspace.tr(modelData.zh, modelData.en)
                        minHeight: 30
                        horizontalPadding: 12
                        outlined: true
                        fillColor: root.selectedFilter === modelData.value ? workspace.accentMuted : "transparent"
                        hoverFillColor: root.selectedFilter === modelData.value ? workspace.accentMuted : workspace.bgCardHover
                        outlineColor: root.selectedFilter === modelData.value ? workspace.accent : workspace.borderSubtle
                        hoverOutlineColor: root.selectedFilter === modelData.value ? workspace.accentHover : workspace.borderDefault
                        textColor: workspace.textPrimary
                        onClicked: if (workspace.hasToolsService) workspace.toolsService.setSourceFilter(modelData.value)
                    }
                }
            }
        }
    }
}
