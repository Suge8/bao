pragma ComponentBehavior: Bound

import QtQuick 2.15
import QtQuick.Layouts 1.15
import "SkillsWorkspaceLogic.js" as SkillsWorkspaceLogic

Rectangle {
    required property var workspace

    implicitHeight: detailSummaryColumn.implicitHeight + 16
    radius: 16
    color: isDark ? "#181310" : "#FFF9F3"
    border.width: 1
    border.color: isDark ? "#12FFFFFF" : "#10000000"

    Column {
        id: detailSummaryColumn
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 10
        spacing: 8

        Text {
            width: parent.width
            text: workspace.localizedSkillName(workspace.selectedSkill)
                || workspace.tr("选择一个技能", "Choose a skill")
            color: textPrimary
            font.pixelSize: typeLabel
            font.weight: weightBold
            elide: Text.ElideRight
        }

        Text {
            width: parent.width
            text: workspace.selectedSkillId
                ? workspace.localizedText(
                    workspace.selectedSkill.displayDetail,
                    workspace.localizedSkillDescription(workspace.selectedSkill)
                )
                : SkillsWorkspaceLogic.installedSummaryFallback(workspace)
            color: textSecondary
            font.pixelSize: typeCaption
            maximumLineCount: 2
            elide: Text.ElideRight
            wrapMode: Text.WordWrap
        }

        Flow {
            width: parent.width
            spacing: 8

            SkillsWorkspaceBadge {
                labelText: workspace.selectedSkillFlag("name") ? workspace.sourceLabel(workspace.selectedSkill) : ""
                tone: workspace.selectedSkillValue("source", "") === "user" ? "#22C55E" : "#60A5FA"
                tinted: false
                badgeHeight: 20
                horizontalPadding: 14
                badgeFontSize: 11
            }

            SkillsWorkspaceBadge {
                labelText: workspace.primaryStatusLabel(workspace.selectedSkill)
                tone: workspace.primaryStatusColor(workspace.selectedSkill)
                tinted: false
                badgeHeight: 20
                horizontalPadding: 14
                badgeFontSize: 11
            }
        }

        Text {
            width: parent.width
            visible: workspace.selectedSkillFlag("statusDetailDisplay")
            text: workspace.localizedText(workspace.selectedSkillValue("statusDetailDisplay", ""), "")
            color: textSecondary
            font.pixelSize: typeCaption
            wrapMode: Text.WordWrap
        }

        Text {
            width: parent.width
            visible: workspace.selectedSkillFlag("missingRequirements")
            text: workspace.tr("缺失依赖：", "Missing requirements: ")
                + String(workspace.selectedSkillValue("missingRequirements", ""))
            color: statusError
            font.pixelSize: typeCaption
            font.weight: weightBold
            wrapMode: Text.WordWrap
        }

        Text {
            width: parent.width
            visible: workspace.selectedSkillFlag("path")
            text: String(workspace.selectedSkillValue("path", ""))
            color: textSecondary
            font.pixelSize: typeCaption
            wrapMode: Text.WrapAnywhere
        }

        Flow {
            width: parent.width
            spacing: 8
            visible: (workspace.selectedSkillValue("linkedCapabilities", []) || []).length > 0

            Repeater {
                model: workspace.selectedSkillValue("linkedCapabilities", [])

                delegate: SkillsWorkspaceBadge {
                    required property var modelData

                    labelText: workspace.localizedText(modelData.displayName, "")
                    tinted: false
                    badgeHeight: 24
                    horizontalPadding: 22
                }
            }
        }

        Column {
            width: parent.width
            spacing: 4
            visible: (workspace.selectedSkillValue("examplePrompts", []) || []).length > 0

            Text {
                width: parent.width
                text: workspace.tr("示例提示词", "Example prompts")
                color: textPrimary
                font.pixelSize: typeMeta
                font.weight: weightBold
            }

            Repeater {
                model: workspace.selectedSkillValue("examplePrompts", [])

                delegate: Text {
                    required property string modelData

                    width: detailSummaryColumn.width
                    text: "• " + modelData
                    color: textSecondary
                    font.pixelSize: typeCaption
                    wrapMode: Text.WordWrap
                }
            }
        }
    }
}
