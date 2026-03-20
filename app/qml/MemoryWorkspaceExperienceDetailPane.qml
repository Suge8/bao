import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: pane

    required property var workspaceRoot

    ColumnLayout {
        anchors.fill: parent
        spacing: 12
        visible: workspaceRoot.hasSelectedExperience

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Rectangle {
                implicitWidth: 34
                implicitHeight: 34
                radius: 17
                color: isDark ? "#1D1713" : "#F3E7DA"
                border.width: 1
                border.color: borderSubtle

                Image {
                    anchors.centerIn: parent
                    width: 18
                    height: 18
                    source: workspaceRoot.experienceIconSource
                    fillMode: Image.PreserveAspectFit
                    smooth: true
                }
            }

            Text {
                Layout.fillWidth: true
                text: workspaceRoot.selectedExperience.task || workspaceRoot.tr("选择一条经验", "Choose an experience")
                color: textPrimary
                font.pixelSize: typeTitle - 3
                font.weight: weightBold
                wrapMode: Text.WordWrap
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Repeater {
                model: [
                    {
                        "text": workspaceRoot.selectedExperience.deprecated
                            ? workspaceRoot.tr("已停用", "Deprecated")
                            : (workspaceRoot.selectedExperience.outcome || workspaceRoot.tr("成功", "Success")),
                        "color": workspaceRoot.selectedExperience.deprecated ? statusError : textSecondary,
                        "fill": workspaceRoot.selectedExperience.deprecated ? (isDark ? "#24F05A5A" : "#14F05A5A") : (isDark ? "#18FFFFFF" : "#12000000")
                    },
                    {
                        "text": workspaceRoot.tr("质量 " + Number(workspaceRoot.selectedExperience.quality || 0), "Q " + Number(workspaceRoot.selectedExperience.quality || 0)),
                        "color": textSecondary,
                        "fill": isDark ? "#18FFFFFF" : "#12000000"
                    },
                    {
                        "text": workspaceRoot.tr("成功率 " + Number(workspaceRoot.selectedExperience.success_rate || 0) + "%", "Rate " + Number(workspaceRoot.selectedExperience.success_rate || 0) + "%"),
                        "color": textSecondary,
                        "fill": isDark ? "#18FFFFFF" : "#12000000"
                    }
                ]

                delegate: Rectangle {
                    required property var modelData
                    radius: 10
                    color: modelData.fill
                    implicitWidth: metaText.implicitWidth + 12
                    implicitHeight: metaText.implicitHeight + 6

                    Text {
                        id: metaText
                        anchors.centerIn: parent
                        text: modelData.text
                        color: modelData.color
                        font.pixelSize: typeCaption
                        font.weight: weightDemiBold
                    }
                }
            }
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            contentWidth: availableWidth

            Column {
                width: parent.width
                spacing: 16

                Text {
                    width: parent.width
                    text: workspaceRoot.tr("经验内容", "Lesson")
                    color: textSecondary
                    font.pixelSize: typeMeta
                    font.weight: weightBold
                }

                Text {
                    width: parent.width
                    text: workspaceRoot.selectedExperience.lessons || workspaceRoot.tr("暂无详细内容", "No lesson text")
                    color: textPrimary
                    wrapMode: Text.WordWrap
                    font.pixelSize: typeBody
                }

                Rectangle { width: parent.width; height: 1; color: borderSubtle; opacity: 0.9 }

                Text {
                    width: parent.width
                    text: workspaceRoot.tr("判断信息", "Signals")
                    color: textSecondary
                    font.pixelSize: typeMeta
                    font.weight: weightBold
                }

                Column {
                    width: parent.width
                    spacing: 8

                    Text { text: workspaceRoot.tr("分类：", "Category: ") + String(workspaceRoot.selectedExperience.category || workspaceRoot.tr("无", "none")); color: textPrimary; font.pixelSize: typeLabel }
                    Text { text: workspaceRoot.tr("复用次数：", "Reuse: ") + Number(workspaceRoot.selectedExperience.uses || 0); color: textPrimary; font.pixelSize: typeLabel }
                    Text { text: workspaceRoot.tr("成功次数：", "Successes: ") + Number(workspaceRoot.selectedExperience.successes || 0); color: textPrimary; font.pixelSize: typeLabel }
                    Text { text: workspaceRoot.tr("命中次数：", "Hits: ") + Number(workspaceRoot.selectedExperience.hit_count || 0); color: textPrimary; font.pixelSize: typeLabel }
                    Text { text: workspaceRoot.tr("最近更新：", "Updated: ") + String(workspaceRoot.selectedExperience.updated_label || workspaceRoot.tr("无", "none")); color: textPrimary; font.pixelSize: typeLabel }
                    Text { visible: !!workspaceRoot.selectedExperience.last_hit_label; text: workspaceRoot.tr("最近命中：", "Last hit: ") + String(workspaceRoot.selectedExperience.last_hit_label || workspaceRoot.tr("无", "none")); color: textPrimary; font.pixelSize: typeLabel }
                    Text { visible: !!workspaceRoot.selectedExperience.keywords; text: workspaceRoot.tr("关键词：", "Keywords: ") + String(workspaceRoot.selectedExperience.keywords || ""); color: textPrimary; font.pixelSize: typeLabel; wrapMode: Text.WordWrap; width: parent.width }
                    Text { visible: !!workspaceRoot.selectedExperience.trace; text: workspaceRoot.tr("轨迹：", "Trace: ") + String(workspaceRoot.selectedExperience.trace || ""); color: textSecondary; font.pixelSize: typeMeta; wrapMode: Text.WordWrap; width: parent.width }
                }

                Rectangle { width: parent.width; height: 1; color: borderSubtle; opacity: 0.9 }

                Text {
                    width: parent.width
                    text: workspaceRoot.tr("提升为长期记忆", "Promote to memory")
                    color: textSecondary
                    font.pixelSize: typeMeta
                    font.weight: weightBold
                }

                Flow {
                    width: parent.width
                    spacing: 8

                    Repeater {
                        model: ["preference", "personal", "project", "general"]

                        delegate: PillActionButton {
                            required property var modelData
                            text: modelData === "preference" ? workspaceRoot.tr("偏好", "Preference")
                                  : modelData === "personal" ? workspaceRoot.tr("个人", "Personal")
                                  : modelData === "project" ? workspaceRoot.tr("项目", "Project")
                                  : workspaceRoot.tr("通用", "General")
                            fillColor: workspaceRoot.promoteCategory === modelData ? accentMuted : "transparent"
                            hoverFillColor: workspaceRoot.promoteCategory === modelData ? accentMuted : bgCardHover
                            outlineColor: workspaceRoot.promoteCategory === modelData ? accent : borderSubtle
                            textColor: textPrimary
                            outlined: true
                            onClicked: workspaceRoot.promoteCategory = modelData
                        }
                    }
                }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 8

            AsyncActionButton {
                Layout.fillWidth: true
                text: workspaceRoot.tr("提升为长期记忆", "Promote to memory")
                busy: workspaceRoot.hasMemoryService && workspaceRoot.memoryService.blockingBusy
                iconSource: workspaceRoot.saveIconSource
                fillColor: isDark ? "#2A1B11" : "#E7D5C7"
                hoverFillColor: isDark ? "#342116" : "#DDC7B6"
                textColor: textPrimary
                spinnerColor: textPrimary
                spinnerSecondaryColor: isDark ? "#A0F7EFE7" : "#886B5649"
                spinnerHaloColor: isDark ? "#24FFFFFF" : "#186B5649"
                buttonEnabled: workspaceRoot.canMutate && !!workspaceRoot.selectedExperience.key
                minHeight: 36
                onClicked: workspaceRoot.memoryService.promoteExperienceToMemory(
                    workspaceRoot.selectedExperience.key,
                    workspaceRoot.promoteCategory
                )
            }

            Flow {
                Layout.fillWidth: true
                spacing: 8

                PillActionButton {
                    text: workspaceRoot.selectedExperience.deprecated
                        ? workspaceRoot.tr("恢复启用", "Restore")
                        : workspaceRoot.tr("停用这条经验", "Deprecate")
                    iconSource: workspaceRoot.deprecateIconSource
                    buttonEnabled: workspaceRoot.canMutate && !!workspaceRoot.selectedExperience.key
                    outlined: true
                    fillColor: "transparent"
                    hoverFillColor: bgCardHover
                    outlineColor: workspaceRoot.selectedExperience.deprecated ? accent : statusError
                    textColor: workspaceRoot.selectedExperience.deprecated ? accent : statusError
                    onClicked: workspaceRoot.memoryService.setExperienceDeprecated(
                        workspaceRoot.selectedExperience.key,
                        !workspaceRoot.selectedExperience.deprecated
                    )
                }

                PillActionButton {
                    text: workspaceRoot.tr("删除这条经验", "Delete")
                    iconSource: workspaceRoot.removeIconSource
                    outlined: true
                    fillColor: "transparent"
                    hoverFillColor: isDark ? "#2A1614" : "#FFF1EE"
                    outlineColor: statusError
                    textColor: statusError
                    buttonEnabled: workspaceRoot.canMutate && !!workspaceRoot.selectedExperience.key
                    onClicked: workspaceRoot.openDestructiveModal(
                        "deleteExperience",
                        workspaceRoot.selectedExperience.key,
                        ""
                    )
                }
            }
        }
    }

    Item {
        anchors.fill: parent
        visible: !workspaceRoot.hasSelectedExperience

        Column {
            anchors.centerIn: parent
            width: Math.min(parent.width - 48, 320)
            spacing: 12

            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                implicitWidth: 60
                implicitHeight: 60
                radius: 30
                color: isDark ? "#1B1512" : "#FFF5EB"
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
                text: workspaceRoot.tr("选择一条经验查看细节", "Choose an experience to inspect")
                color: textPrimary
                font.pixelSize: typeButton + 1
                font.weight: weightBold
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
            }

            Text {
                width: parent.width
                text: workspaceRoot.tr(
                    "你可以在这里停用噪音经验、删除失效经验，或把高价值经验提升为长期记忆。",
                    "From here you can deprecate noisy experiences, delete stale ones, or promote high-value ones into long-term memory."
                )
                color: textSecondary
                font.pixelSize: typeLabel
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
            }
        }
    }
}
