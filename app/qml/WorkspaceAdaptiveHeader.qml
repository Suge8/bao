import QtQuick 2.15
import QtQuick.Layouts 1.15

CalloutPanel {
    id: root

    property bool compactLayout: false
    property Component introContent: null
    property Component centerContent: null
    property Component trailingContent: null
    property Component supportingContent: null
    property real rowSpacing: 12
    property real sectionSpacing: 10

    readonly property bool hasCenterContent: centerContent !== null
    readonly property bool hasTrailingContent: trailingContent !== null
    readonly property bool hasSupportingContent: supportingContent !== null

    ColumnLayout {
        width: parent.width
        spacing: root.sectionSpacing

        RowLayout {
            Layout.fillWidth: true
            spacing: root.rowSpacing

            Item {
                Layout.fillWidth: true
                Layout.minimumWidth: 0
                implicitHeight: introLoader.implicitHeight

                Loader {
                    id: introLoader
                    anchors.fill: parent
                    active: root.introContent !== null
                    sourceComponent: root.introContent
                }
            }

            Item {
                visible: !root.compactLayout && root.hasCenterContent
                implicitWidth: centerLoaderWide.implicitWidth
                implicitHeight: centerLoaderWide.implicitHeight

                Loader {
                    id: centerLoaderWide
                    anchors.centerIn: parent
                    active: parent.visible
                    sourceComponent: root.centerContent
                }
            }

            Item {
                visible: !root.compactLayout && root.hasTrailingContent
                implicitWidth: trailingLoaderWide.implicitWidth
                implicitHeight: trailingLoaderWide.implicitHeight

                Loader {
                    id: trailingLoaderWide
                    anchors.fill: parent
                    active: parent.visible
                    sourceComponent: root.trailingContent
                }
            }
        }

        Item {
            visible: root.compactLayout && root.hasCenterContent
            Layout.fillWidth: true
            implicitHeight: centerLoaderCompact.implicitHeight

            Loader {
                id: centerLoaderCompact
                anchors.horizontalCenter: parent.horizontalCenter
                active: parent.visible
                sourceComponent: root.centerContent
            }
        }

        Item {
            visible: root.compactLayout && root.hasTrailingContent
            Layout.fillWidth: true
            implicitHeight: trailingLoaderCompact.implicitHeight

            Loader {
                id: trailingLoaderCompact
                anchors.fill: parent
                active: parent.visible
                sourceComponent: root.trailingContent
            }
        }

        Item {
            visible: root.hasSupportingContent
            Layout.fillWidth: true
            implicitHeight: supportingLoader.implicitHeight

            Loader {
                id: supportingLoader
                anchors.fill: parent
                active: parent.visible
                sourceComponent: root.supportingContent
            }
        }
    }
}
