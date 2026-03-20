pragma ComponentBehavior: Bound

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    required property var workspace
    required property var skill

    property bool selected: workspace && workspace.selectedSkillId === skill.id

    implicitHeight: skillCard.implicitHeight + (sectionHeader.visible ? sectionHeader.implicitHeight + 8 : 0)

    Column {
        anchors.fill: parent
        spacing: 8

        Item {
            id: sectionHeader
            width: parent.width
            implicitHeight: sectionHeaderText.implicitHeight
            visible: !!root.skill.showSectionHeader

            Text {
                id: sectionHeaderText
                anchors.left: parent.left
                anchors.right: parent.right
                text: workspace ? workspace.localizedText(root.skill.sectionTitle, "") : ""
                color: textSecondary
                font.pixelSize: typeMeta
                font.weight: weightBold
            }
        }

        Rectangle {
            id: skillCard
            width: parent.width
            implicitHeight: 120
            radius: 22
            color: skillArea.containsMouse
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
                            source: workspace.skillIconSource(root.skill)
                            sourceSize: Qt.size(width, height)
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        Text {
                            Layout.fillWidth: true
                            text: workspace.localizedSkillName(root.skill)
                            color: textPrimary
                            font.pixelSize: typeBody
                            font.weight: weightBold
                            elide: Text.ElideRight
                        }

                        Text {
                            Layout.fillWidth: true
                            text: workspace.localizedSkillDescription(root.skill)
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
                        onClicked: if (workspace.hasSkillsService) workspace.skillsService.selectSkill(root.skill.id)
                    }
                }

                Row {
                    Layout.fillWidth: true
                    spacing: 8
                    clip: true

                    SkillsWorkspaceBadge {
                        labelText: workspace.sourceLabel(root.skill)
                        tone: root.skill.source === "user" ? "#22C55E" : "#60A5FA"
                    }

                    SkillsWorkspaceBadge {
                        labelText: workspace.primaryStatusLabel(root.skill)
                        tone: workspace.primaryStatusColor(root.skill)
                    }
                }
            }

            MouseArea {
                id: skillArea
                anchors.fill: parent
                hoverEnabled: true
                acceptedButtons: Qt.LeftButton
                cursorShape: Qt.PointingHandCursor
                onClicked: if (workspace.hasSkillsService) workspace.skillsService.selectSkill(root.skill.id)
            }
        }
    }
}
