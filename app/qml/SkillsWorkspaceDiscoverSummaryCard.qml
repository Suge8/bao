pragma ComponentBehavior: Bound

import QtQuick 2.15
import "SkillsWorkspaceLogic.js" as SkillsWorkspaceLogic

Rectangle {
    required property var workspace

    implicitHeight: discoverSummaryColumn.implicitHeight + 16
    radius: 16
    color: isDark ? "#181310" : "#FFF9F3"
    border.width: 1
    border.color: isDark ? "#12FFFFFF" : "#10000000"

    Column {
        id: discoverSummaryColumn
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 10
        spacing: 8

        Text {
            width: parent.width
            text: String(workspace.selectedDiscoverValue(
                "title",
                workspace.selectedDiscoverValue("name", workspace.tr("选择一个候选技能", "Choose a candidate skill"))
            ))
            color: textPrimary
            font.pixelSize: typeLabel
            font.weight: weightBold
            elide: Text.ElideRight
        }

        Text {
            width: parent.width
            text: String(workspace.selectedDiscoverValue(
                "summary",
                SkillsWorkspaceLogic.discoverSummaryFallback(workspace)
            ))
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
                labelText: String(workspace.selectedDiscoverValue("publisher", ""))
                tinted: false
                badgeHeight: 22
                horizontalPadding: 14
                badgeFontSize: 11
            }

            SkillsWorkspaceBadge {
                labelText: workspace.localizedText(
                    workspace.selectedDiscoverValue("installStateLabel", ""),
                    ""
                )
                tinted: false
                badgeHeight: 22
                horizontalPadding: 14
                badgeFontSize: 11
            }
        }

        Text {
            width: parent.width
            text: String(workspace.selectedDiscoverValue("reference", workspace.discoverReferenceValue))
            color: accent
            font.pixelSize: typeCaption
            wrapMode: Text.WrapAnywhere
        }

        Text {
            width: parent.width
            text: workspace.localizedText(
                workspace.selectedDiscoverValue("trustNote", ""),
                workspace.tr(
                    "选择结果后，直接导入到用户技能目录。",
                    "Select a result and import it into user skills."
                )
            )
            color: textSecondary
            font.pixelSize: typeCaption
            wrapMode: Text.WordWrap
        }

        Text {
            width: parent.width
            visible: (workspace.selectedDiscoverValue("requires", []) || []).length > 0
            text: workspace.tr("导入前提：", "Import prerequisites: ")
                + String((workspace.selectedDiscoverValue("requires", []) || []).join(", "))
            color: textSecondary
            font.pixelSize: typeCaption
            wrapMode: Text.WordWrap
        }

        Text {
            width: parent.width
            text: workspace.localizedText(workspace.selectedDiscoverValue("installStateDetail", ""), "")
            color: textSecondary
            font.pixelSize: typeCaption
            wrapMode: Text.WordWrap
        }
    }
}
