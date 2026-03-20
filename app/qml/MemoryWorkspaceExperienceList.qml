import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    required property var workspaceRoot

    ListView {
        id: memoryExperienceList
        objectName: "memoryExperienceList"
        anchors.fill: parent
        model: workspaceRoot.experienceModel
        spacing: 10
        clip: true
        reuseItems: true
        cacheBuffer: workspaceRoot.listCacheBuffer
        boundsBehavior: Flickable.StopAtBounds

        delegate: Rectangle {
            required property var modelData
            width: ListView.view.width
            implicitHeight: 156
            radius: radiusLg
            color: String(workspaceRoot.selectedExperience.key || "") === String(modelData.key || "")
                ? sessionRowActiveBg
                : (expMouse.containsMouse ? bgCardHover : (isDark ? "#1A1411" : "#FFFFFF"))
            border.width: 1
            border.color: String(workspaceRoot.selectedExperience.key || "") === String(modelData.key || "")
                ? "#D8A23C"
                : borderSubtle

            Behavior on color { ColorAnimation { duration: motionUi; easing.type: easeStandard } }
            Behavior on border.color { ColorAnimation { duration: motionUi; easing.type: easeStandard } }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 14
                spacing: 8

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Text {
                        Layout.fillWidth: true
                        text: modelData.task || workspaceRoot.tr("未命名经验", "Untitled experience")
                        color: textPrimary
                        font.pixelSize: typeButton
                        font.weight: weightBold
                        elide: Text.ElideRight
                    }

                    Rectangle {
                        radius: 10
                        color: modelData.deprecated ? (isDark ? "#24F05A5A" : "#14F05A5A") : (isDark ? "#1CFFFFFF" : "#12000000")
                        implicitWidth: stateBadge.implicitWidth + 12
                        implicitHeight: stateBadge.implicitHeight + 6

                        Text {
                            id: stateBadge
                            anchors.centerIn: parent
                            text: modelData.deprecated ? workspaceRoot.tr("已停用", "Deprecated") : (modelData.outcome || workspaceRoot.tr("成功", "success"))
                            color: modelData.deprecated ? statusError : textSecondary
                            font.pixelSize: typeCaption
                            font.weight: weightDemiBold
                        }
                    }
                }

                Text {
                    Layout.fillWidth: true
                    text: modelData.preview || modelData.lessons || ""
                    color: textPrimary
                    font.pixelSize: typeLabel
                    wrapMode: Text.WordWrap
                    maximumLineCount: 3
                    elide: Text.ElideRight
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Repeater {
                        model: [
                            workspaceRoot.tr("质量 " + Number(modelData.quality || 0), "Q " + Number(modelData.quality || 0)),
                            workspaceRoot.tr("复用 " + Number(modelData.uses || 0), "Reuse " + Number(modelData.uses || 0)),
                            workspaceRoot.tr("命中 " + Number(modelData.hit_count || 0), "Used " + Number(modelData.hit_count || 0))
                        ]

                        delegate: Rectangle {
                            required property var modelData
                            radius: 9
                            color: isDark ? "#18FFFFFF" : "#12000000"
                            implicitWidth: badgeText.implicitWidth + 12
                            implicitHeight: badgeText.implicitHeight + 6

                            Text {
                                id: badgeText
                                anchors.centerIn: parent
                                text: modelData
                                color: textSecondary
                                font.pixelSize: typeCaption
                                font.weight: weightDemiBold
                            }
                        }
                    }

                    Item { Layout.fillWidth: true }

                    Text {
                        text: modelData.updated_label || ""
                        color: textSecondary
                        font.pixelSize: typeMeta
                    }
                }
            }

            MouseArea {
                id: expMouse
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: workspaceRoot.memoryService.selectExperience(modelData.key)
            }
        }

        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
    }

    Item {
        anchors.fill: parent
        visible: workspaceRoot.hasMemoryService && workspaceRoot.experienceCount === 0

        Column {
            anchors.centerIn: parent
            width: Math.min(parent.width - 40, 300)
            spacing: 10

            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                implicitWidth: 56
                implicitHeight: 56
                radius: 28
                color: isDark ? "#1D1613" : "#FFF4EA"
                border.width: 1
                border.color: borderSubtle

                Text {
                    anchors.centerIn: parent
                    text: "✦"
                    color: "#D8A23C"
                    font.pixelSize: 24
                    font.weight: weightBold
                }
            }

            Text {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                text: workspaceRoot.tr("当前筛选下没有经验", "No experiences for this filter")
                color: textPrimary
                font.pixelSize: typeButton
                font.weight: weightBold
                wrapMode: Text.WordWrap
            }

            Text {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                text: workspaceRoot.tr(
                    "试试放宽筛选，或继续使用 Bao，新的经验会在这里慢慢积累。",
                    "Relax the filters or keep using Bao — new experiences will accumulate here over time."
                )
                color: textSecondary
                font.pixelSize: typeLabel
                wrapMode: Text.WordWrap
            }
        }
    }
}
