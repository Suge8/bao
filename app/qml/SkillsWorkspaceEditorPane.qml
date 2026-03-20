pragma ComponentBehavior: Bound

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    required property var workspace

    radius: 20
    color: isDark ? "#100C0A" : "#F6EFE6"
    border.width: 1
    border.color: isDark ? "#12FFFFFF" : "#10000000"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 14
        spacing: 12

        RowLayout {
            Layout.fillWidth: true

            Text {
                Layout.fillWidth: true
                text: workspace.selectedSkillValue("source", "") === "user"
                    ? workspace.tr("编辑技能文件", "Edit skill file")
                    : workspace.tr("查看技能文件", "View skill file")
                color: textPrimary
                font.pixelSize: typeLabel
                font.weight: weightBold
            }

            PillActionButton {
                visible: workspace.selectedSkillFlag("path")
                text: workspace.tr("目录地址", "Folder path")
                iconSource: workspace.labIcon("copy-file-path")
                minHeight: 34
                horizontalPadding: 18
                outlined: true
                fillColor: isDark ? "#1D1612" : "#FFF8F1"
                hoverFillColor: bgCardHover
                outlineColor: borderSubtle
                hoverOutlineColor: borderDefault
                textColor: textPrimary
                onClicked: if (workspace.hasSkillsService) workspace.skillsService.openSelectedFolder()
            }

            Text {
                visible: workspace.draftDirty
                text: workspace.tr("未保存", "Unsaved")
                color: statusWarning
                font.pixelSize: typeMeta
                font.weight: weightBold
            }
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

            TextArea {
                id: editor
                objectName: "skillsEditor"
                property bool baoClickAwayEditor: true

                readOnly: !workspace.selectedSkillFlag("canEdit")
                color: textPrimary
                placeholderText: workspace.tr(
                    "这里显示技能的 SKILL.md 内容。",
                    "This shows the selected skill's SKILL.md content."
                )
                placeholderTextColor: textPlaceholder
                background: null
                wrapMode: TextArea.Wrap
                leftPadding: sizeFieldPaddingX - 2
                rightPadding: sizeFieldPaddingX
                topPadding: 15
                bottomPadding: 12
                font.pixelSize: typeBody
                selectionColor: textSelectionBg
                selectedTextColor: textSelectionFg

                Component.onCompleted: {
                    workspace.editorRef = editor
                    workspace.syncDraft(true)
                }

                onTextChanged: {
                    if (workspace.syncingDraft)
                        return
                    workspace.draftDirty = workspace.draftSkillId !== ""
                        && text !== workspace.selectedContent
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true

            PillActionButton {
                visible: workspace.selectedSkillFlag("canEdit")
                text: workspace.tr("还原", "Revert")
                minHeight: 34
                horizontalPadding: 18
                outlined: true
                fillColor: "transparent"
                hoverFillColor: bgCardHover
                outlineColor: borderSubtle
                hoverOutlineColor: borderDefault
                textColor: textPrimary
                onClicked: workspace.syncDraft(true)
            }

            Item { Layout.fillWidth: true }

            PillActionButton {
                visible: workspace.selectedSkillFlag("canDelete")
                text: workspace.tr("删除", "Delete")
                minHeight: 34
                horizontalPadding: 18
                outlined: true
                fillColor: "transparent"
                hoverFillColor: isDark ? "#20F05A5A" : "#14F05A5A"
                outlineColor: statusError
                hoverOutlineColor: statusError
                textColor: statusError
                onClicked: if (workspace.hasSkillsService) workspace.skillsService.deleteSelectedSkill()
            }

            PillActionButton {
                visible: workspace.selectedSkillFlag("canEdit")
                text: workspace.tr("保存", "Save")
                minHeight: 34
                horizontalPadding: 20
                fillColor: accent
                hoverFillColor: accentHover
                buttonEnabled: workspace.draftDirty
                onClicked: if (workspace.hasSkillsService) workspace.skillsService.saveSelectedContent(editor.text)
            }
        }
    }
}
