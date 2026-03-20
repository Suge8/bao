import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: panel

    required property var workspaceRoot
    required property string sectionKind
    required property var sectionModel
    required property int sectionItemCount
    required property bool isDark
    required property color textPrimary
    required property color textSecondary
    required property color textTertiary
    required property color sectionFill
    required property color sectionBorder
    required property color tileActive
    required property color tileHover
    required property real motionFast
    required property int easeStandard
    required property int typeBody
    required property int typeMeta
    required property int typeCaption
    required property int typeLabel
    required property int weightBold
    required property int weightMedium

    objectName: "controlTowerLane_" + sectionKind
    Layout.fillWidth: true
    Layout.preferredHeight: implicitHeight
    radius: 24
    color: sectionFill
    border.width: 1
    border.color: sectionBorder
    implicitHeight: Math.max(220, lanePanelContent.implicitHeight + 28)

    ColumnLayout {
        id: lanePanelContent
        anchors.fill: parent
        anchors.margins: 14
        spacing: 12

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Text {
                text: workspaceRoot.sectionTitle(sectionKind)
                color: textPrimary
                font.pixelSize: typeBody
                font.weight: weightBold
            }

            Rectangle {
                implicitWidth: laneCountText.implicitWidth + 14
                implicitHeight: 24
                radius: 12
                color: isDark ? "#18120E" : "#FFF5EA"
                border.width: 1
                border.color: workspaceRoot.accentColor(workspaceRoot.sectionAccentKey(sectionKind))

                Text {
                    id: laneCountText
                    anchors.centerIn: parent
                    text: sectionItemCount
                    color: textPrimary
                    font.pixelSize: typeCaption
                    font.weight: weightBold
                }
            }

            Item { Layout.fillWidth: true }
        }

        Loader {
            id: lanePanelLoader
            property real loadedHeight: workspaceRoot.loaderItemHeight(item)
            Layout.fillWidth: true
            Layout.preferredHeight: loadedHeight
            active: true
            sourceComponent: sectionItemCount > 0 ? laneListComponent : laneEmptyStateComponent
            onLoaded: {
                if (!item)
                    return
                item.workspaceRoot = workspaceRoot
                item.sectionKind = sectionKind
                item.sectionModel = sectionModel
                item.isDark = isDark
                item.textPrimary = textPrimary
                item.textSecondary = textSecondary
                item.textTertiary = textTertiary
                item.tileActive = tileActive
                item.tileHover = tileHover
                item.motionFast = motionFast
                item.easeStandard = easeStandard
                item.typeMeta = typeMeta
                item.typeLabel = typeLabel
                item.typeCaption = typeCaption
                item.weightBold = weightBold
                item.weightMedium = weightMedium
            }
        }
    }

    Component {
        id: laneEmptyStateComponent

        ControlTowerLaneEmpty {}
    }

    Component {
        id: laneListComponent

        ControlTowerLaneList {}
    }
}
