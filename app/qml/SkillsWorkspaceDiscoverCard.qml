pragma ComponentBehavior: Bound

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    required property var workspace
    required property var itemData

    property bool selected: workspace && workspace.selectedDiscoverId === itemData.id

    implicitHeight: 112

    Rectangle {
        anchors.fill: parent
        radius: 22
        color: discoverArea.containsMouse
            ? (root.selected ? (isDark ? "#241914" : "#FFF1E2") : bgCardHover)
            : (root.selected ? (isDark ? "#201612" : "#FFF7F0") : (isDark ? "#17120F" : "#FFFFFF"))
        border.width: root.selected ? 1.5 : 1
        border.color: root.selected ? accent : (isDark ? "#14FFFFFF" : "#10000000")

        Behavior on color { ColorAnimation { duration: motionFast; easing.type: easeStandard } }
        Behavior on border.color { ColorAnimation { duration: motionFast; easing.type: easeStandard } }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 12
            anchors.bottomMargin: 16
            spacing: 8

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Rectangle {
                    Layout.alignment: Qt.AlignTop
                    implicitWidth: 36
                    implicitHeight: 36
                    Layout.preferredWidth: implicitWidth
                    Layout.preferredHeight: implicitHeight
                    radius: 12
                    color: root.selected ? (isDark ? "#302015" : "#F1D8BE") : (isDark ? "#211915" : "#F2E6D9")
                    border.width: root.selected ? 1 : 0
                    border.color: root.selected ? accent : "transparent"

                    AppIcon {
                        anchors.centerIn: parent
                        width: 18
                        height: 18
                        source: workspace.icon("circle-spark")
                        sourceSize: Qt.size(width, height)
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2

                    Text {
                        Layout.fillWidth: true
                        text: String(root.itemData.title || root.itemData.name || "")
                        color: textPrimary
                        font.pixelSize: typeBody
                        font.weight: weightBold
                        elide: Text.ElideRight
                    }

                    Text {
                        Layout.fillWidth: true
                        text: root.itemData.summary
                        color: isDark ? textSecondary : "#5A4537"
                        font.pixelSize: typeMeta
                        wrapMode: Text.WordWrap
                        maximumLineCount: 2
                        elide: Text.ElideRight
                    }
                }

                IconCircleButton {
                    buttonSize: 30
                    glyphText: "→"
                    glyphSize: typeLabel
                    fillColor: "transparent"
                    hoverFillColor: bgCardHover
                    outlineColor: root.selected ? accent : borderSubtle
                    glyphColor: root.selected ? accent : textSecondary
                    onClicked: if (workspace.hasSkillsService) workspace.skillsService.selectDiscoverItem(root.itemData.id)
                }
            }

            Text {
                Layout.fillWidth: true
                text: workspace.discoverPublisherVersion(root.itemData)
                color: textSecondary
                font.pixelSize: typeMeta
                visible: text.length > 0
            }

            Text {
                Layout.fillWidth: true
                text: root.itemData.reference
                color: accent
                font.pixelSize: typeMeta
                elide: Text.ElideRight
            }
        }

        MouseArea {
            id: discoverArea
            anchors.fill: parent
            hoverEnabled: true
            acceptedButtons: Qt.LeftButton
            cursorShape: Qt.PointingHandCursor
            onClicked: if (workspace.hasSkillsService) workspace.skillsService.selectDiscoverItem(root.itemData.id)
        }
    }
}
