import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ColumnLayout {
    id: pane

    required property var workspaceRoot

    spacing: 12

    ColumnLayout {
        Layout.fillWidth: true
        spacing: 2

        Text {
            text: workspaceRoot.tr("选择经验", "Choose an experience")
            color: textPrimary
            font.pixelSize: typeLabel
            font.weight: weightBold
        }

        Text {
            text: workspaceRoot.tr(
                "筛选你关心的经验，再在右侧决定是否保留。",
                "Filter the experiences you care about, then decide what to keep on the right."
            )
            color: textSecondary
            font.pixelSize: typeMeta
        }
    }

    Rectangle {
        Layout.fillWidth: true
        implicitHeight: 40
        radius: 16
        color: experienceSearchField.activeFocus ? bgInputFocus : (experienceSearchField.hovered ? bgInputHover : bgInput)
        border.width: experienceSearchField.activeFocus ? 1.5 : 1
        border.color: experienceSearchField.activeFocus ? borderFocus : borderSubtle

        Image {
            anchors.left: parent.left
            anchors.leftMargin: 12
            anchors.verticalCenter: parent.verticalCenter
            width: 16
            height: 16
            source: workspaceRoot.searchIconSource
            fillMode: Image.PreserveAspectFit
            smooth: true
            opacity: 0.75
        }

        TextField {
            id: experienceSearchField
            property bool baoClickAwayEditor: true
            anchors.fill: parent
            leftPadding: 36
            rightPadding: 12
            background: null
            color: textPrimary
            text: workspaceRoot.experienceSearchQuery
            placeholderText: workspaceRoot.tr("搜索任务、经验、关键词…", "Search tasks, lessons, keywords…")
            placeholderTextColor: textPlaceholder
            selectionColor: textSelectionBg
            selectedTextColor: textSelectionFg
            font.pixelSize: typeLabel
            onTextChanged: {
                if (workspaceRoot.experienceSearchQuery !== text)
                    workspaceRoot.experienceSearchQuery = text
                workspaceRoot.applyExperienceFilters()
            }
        }
    }

    Flow {
        Layout.fillWidth: true
        spacing: 8

        Repeater {
            model: ["", "coding", "project", "general"]

            delegate: PillActionButton {
                required property var modelData
                text: workspaceRoot.experienceCategoryLabel(modelData)
                minHeight: 30
                horizontalPadding: 14
                outlined: true
                fillColor: workspaceRoot.experienceCategory === String(modelData) ? accentMuted : "transparent"
                hoverFillColor: workspaceRoot.experienceCategory === String(modelData) ? accentMuted : bgCardHover
                outlineColor: workspaceRoot.experienceCategory === String(modelData) ? accent : borderSubtle
                textColor: textPrimary
                onClicked: {
                    workspaceRoot.experienceCategory = String(modelData)
                    workspaceRoot.applyExperienceFilters()
                }
            }
        }
    }

    Flow {
        Layout.fillWidth: true
        spacing: 8

        Repeater {
            model: ["", "success", "failed"]

            delegate: PillActionButton {
                required property var modelData
                text: workspaceRoot.experienceOutcomeLabel(modelData)
                minHeight: 30
                horizontalPadding: 14
                outlined: true
                fillColor: workspaceRoot.experienceOutcome === String(modelData) ? accentMuted : "transparent"
                hoverFillColor: workspaceRoot.experienceOutcome === String(modelData) ? accentMuted : bgCardHover
                outlineColor: workspaceRoot.experienceOutcome === String(modelData) ? accent : borderSubtle
                textColor: textPrimary
                onClicked: {
                    workspaceRoot.experienceOutcome = String(modelData)
                    workspaceRoot.applyExperienceFilters()
                }
            }
        }
    }

    Flow {
        Layout.fillWidth: true
        spacing: 8

        Repeater {
            model: ["active", "high_quality", "deprecated", "all"]

            delegate: PillActionButton {
                required property var modelData
                text: modelData === "active" ? workspaceRoot.tr("活跃", "Active")
                      : modelData === "high_quality" ? workspaceRoot.tr("高质量", "High quality")
                      : modelData === "deprecated" ? workspaceRoot.tr("已停用", "Deprecated")
                      : workspaceRoot.tr("全部", "All")
                outlined: true
                fillColor: {
                    if (modelData === "active")
                        return workspaceRoot.experienceDeprecatedMode === "active" && workspaceRoot.experienceMinQuality === 0 ? accentMuted : "transparent"
                    if (modelData === "high_quality")
                        return workspaceRoot.experienceDeprecatedMode === "active" && workspaceRoot.experienceMinQuality === 4 ? accentMuted : "transparent"
                    if (modelData === "deprecated")
                        return workspaceRoot.experienceDeprecatedMode === "deprecated" ? accentMuted : "transparent"
                    return workspaceRoot.experienceDeprecatedMode === "all" ? accentMuted : "transparent"
                }
                hoverFillColor: bgCardHover
                outlineColor: fillColor === "transparent" ? borderSubtle : accent
                textColor: textPrimary
                onClicked: {
                    if (modelData === "active") {
                        workspaceRoot.experienceDeprecatedMode = "active"
                        workspaceRoot.experienceMinQuality = 0
                    } else if (modelData === "high_quality") {
                        workspaceRoot.experienceDeprecatedMode = "active"
                        workspaceRoot.experienceMinQuality = 4
                    } else if (modelData === "deprecated") {
                        workspaceRoot.experienceDeprecatedMode = "deprecated"
                        workspaceRoot.experienceMinQuality = 0
                    } else {
                        workspaceRoot.experienceDeprecatedMode = "all"
                        workspaceRoot.experienceMinQuality = 0
                    }
                    workspaceRoot.applyExperienceFilters()
                }
            }
        }
    }

    Flow {
        Layout.fillWidth: true
        spacing: 8

        Repeater {
            model: ["updated_desc", "quality_desc", "uses_desc"]

            delegate: PillActionButton {
                required property var modelData
                text: modelData === "quality_desc" ? workspaceRoot.tr("按质量", "By quality")
                      : modelData === "uses_desc" ? workspaceRoot.tr("按复用", "By reuse")
                      : workspaceRoot.tr("最近更新", "Recent")
                minHeight: 30
                horizontalPadding: 14
                outlined: true
                fillColor: workspaceRoot.experienceSortBy === modelData ? accentMuted : "transparent"
                hoverFillColor: workspaceRoot.experienceSortBy === modelData ? accentMuted : bgCardHover
                outlineColor: workspaceRoot.experienceSortBy === modelData ? accent : borderSubtle
                textColor: textPrimary
                onClicked: {
                    workspaceRoot.experienceSortBy = modelData
                    workspaceRoot.applyExperienceFilters()
                }
            }
        }
    }

    Text {
        Layout.fillWidth: true
        text: workspaceRoot.tr("结果数 ", "Results ") + workspaceRoot.experienceCount
        color: textSecondary
        font.pixelSize: typeMeta
    }

    Rectangle {
        Layout.fillWidth: true
        Layout.fillHeight: true
        color: "transparent"
        border.width: 0

        MemoryWorkspaceExperienceList {
            anchors.fill: parent
            workspaceRoot: pane.workspaceRoot
        }
    }
}
