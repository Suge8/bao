import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    required property var workspaceRoot

    ListView {
        id: memoryCategoryList
        objectName: "memoryCategoryList"
        anchors.fill: parent
        model: workspaceRoot.memoryCategoryModel
        spacing: 10
        clip: true
        reuseItems: true
        cacheBuffer: workspaceRoot.listCacheBuffer
        boundsBehavior: Flickable.StopAtBounds

        delegate: Rectangle {
            required property var modelData
            width: ListView.view.width
            implicitHeight: 136
            radius: radiusLg
            color: String(workspaceRoot.selectedMemoryCategory.category || "") === String(modelData.category || "")
                ? sessionRowActiveBg
                : (cardMouse.containsMouse ? bgCardHover : (isDark ? "#1A1411" : "#FFFFFF"))
            border.width: 1
            border.color: String(workspaceRoot.selectedMemoryCategory.category || "") === String(modelData.category || "")
                ? accent
                : borderSubtle

            Rectangle {
                anchors.fill: parent
                radius: parent.radius
                color: "transparent"
                border.width: 0
                opacity: String(workspaceRoot.selectedMemoryCategory.category || "") === String(modelData.category || "") ? 0.1 : 0.0
                gradient: Gradient {
                    GradientStop { position: 0.0; color: isDark ? "#18FFD8B0" : "#10FFC58A" }
                    GradientStop { position: 1.0; color: "transparent" }
                }

                Behavior on opacity { NumberAnimation { duration: motionUi; easing.type: easeStandard } }
            }

            Behavior on color { ColorAnimation { duration: motionUi; easing.type: easeStandard } }
            Behavior on border.color { ColorAnimation { duration: motionUi; easing.type: easeStandard } }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 14
                spacing: 8

                RowLayout {
                    Layout.fillWidth: true

                    Text {
                        Layout.fillWidth: true
                        text: modelData.category === "preference" ? workspaceRoot.tr("偏好", "Preference")
                              : modelData.category === "personal" ? workspaceRoot.tr("个人", "Personal")
                              : modelData.category === "project" ? workspaceRoot.tr("项目", "Project")
                              : workspaceRoot.tr("通用", "General")
                        color: textPrimary
                        font.pixelSize: typeButton
                        font.weight: weightBold
                    }

                    Rectangle {
                        radius: 10
                        color: isDark ? "#18FFFFFF" : "#12000000"
                        implicitWidth: badgeText.implicitWidth + 12
                        implicitHeight: badgeText.implicitHeight + 6

                        Text {
                            id: badgeText
                            anchors.centerIn: parent
                            text: modelData.is_empty
                                ? workspaceRoot.tr("空", "Empty")
                                : workspaceRoot.tr(
                                    String(modelData.fact_count || 0) + " 条事实",
                                    String(modelData.fact_count || 0) + " facts"
                                )
                            color: textSecondary
                            font.pixelSize: typeCaption
                            font.weight: weightDemiBold
                        }
                    }
                }

                Text {
                    Layout.fillWidth: true
                    text: modelData.preview || workspaceRoot.tr(
                        "还没有内容，适合在这里保存稳定偏好或项目背景。",
                        "No content yet — use this space for durable preferences or project context."
                    )
                    color: modelData.is_empty ? textSecondary : textPrimary
                    font.pixelSize: typeLabel
                    wrapMode: Text.WordWrap
                    maximumLineCount: 3
                    elide: Text.ElideRight
                }

                Item { Layout.fillHeight: true }

                RowLayout {
                    Layout.fillWidth: true

                    Text {
                        Layout.fillWidth: true
                        text: modelData.updated_label
                            ? workspaceRoot.tr("更新于 " + modelData.updated_label, "Updated " + modelData.updated_label)
                            : workspaceRoot.tr("尚未写入", "Not written yet")
                        color: textSecondary
                        font.pixelSize: typeMeta
                    }

                    IconCircleButton {
                        buttonSize: 28
                        glyphText: "→"
                        glyphSize: typeMeta
                        fillColor: "transparent"
                        hoverFillColor: bgCardHover
                        outlineColor: borderSubtle
                        glyphColor: textSecondary
                        onClicked: workspaceRoot.selectMemory(modelData.category)
                    }
                }
            }

            MouseArea {
                id: cardMouse
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: workspaceRoot.selectMemory(modelData.category)
            }
        }

        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
    }

    Item {
        anchors.fill: parent
        visible: workspaceRoot.memoryCategoryCount === 0

        Column {
            anchors.centerIn: parent
            width: Math.min(parent.width - 40, 280)
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
                    text: "◌"
                    color: accent
                    font.pixelSize: 24
                    font.weight: weightBold
                }
            }

            Text {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                text: workspaceRoot.tr("没有匹配的记忆分类", "No matching memory categories")
                color: textPrimary
                font.pixelSize: typeButton
                font.weight: weightBold
                wrapMode: Text.WordWrap
            }

            Text {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                text: workspaceRoot.tr(
                    "换一个关键词，或者直接在右侧编辑当前分类内容。",
                    "Try another keyword, or edit the current category on the right."
                )
                color: textSecondary
                font.pixelSize: typeLabel
                wrapMode: Text.WordWrap
            }
        }
    }
}
