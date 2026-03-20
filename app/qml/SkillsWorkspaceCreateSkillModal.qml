pragma ComponentBehavior: Bound

import QtQuick 2.15
import QtQuick.Controls 2.15

AppModal {
    id: root

    required property var workspace

    title: workspace.tr("新建用户技能", "Create user skill")
    closeText: workspace.tr("关闭", "Close")
    maxModalWidth: 560
    maxModalHeight: 420
    darkMode: isDark

    onOpened: {
        skillNameInput.text = ""
        skillDescriptionInput.text = ""
        skillNameInput.forceActiveFocus()
    }

    Column {
        width: parent.width
        spacing: 14

        Text {
            width: parent.width
            text: workspace.tr(
                "技能名只允许小写字母、数字和连字符，创建后直接写入用户技能目录。",
                "Skill names accept lowercase letters, digits, and hyphens, then get written directly into user skills."
            )
            color: textSecondary
            font.pixelSize: typeMeta
            wrapMode: Text.WordWrap
        }

        Rectangle {
            width: parent.width
            height: 44
            radius: 16
            color: skillNameInput.activeFocus ? bgInputFocus : (skillNameInput.hovered ? bgInputHover : bgInput)
            border.width: skillNameInput.activeFocus ? 1.5 : 1
            border.color: skillNameInput.activeFocus ? borderFocus : borderSubtle

            TextField {
                id: skillNameInput
                property bool baoClickAwayEditor: true

                anchors.fill: parent
                hoverEnabled: true
                leftPadding: sizeFieldPaddingX
                rightPadding: sizeFieldPaddingX
                background: null
                color: textPrimary
                placeholderText: workspace.tr("例如：design-ops", "For example: design-ops")
                placeholderTextColor: textPlaceholder
                selectionColor: textSelectionBg
                selectedTextColor: textSelectionFg
                font.pixelSize: typeBody
            }
        }

        Rectangle {
            width: parent.width
            height: 120
            radius: 18
            color: skillDescriptionInput.activeFocus
                ? bgInputFocus
                : (skillDescriptionInput.hovered ? bgInputHover : bgInput)
            border.width: skillDescriptionInput.activeFocus ? 1.5 : 1
            border.color: skillDescriptionInput.activeFocus ? borderFocus : borderSubtle

            TextArea {
                id: skillDescriptionInput
                property bool baoClickAwayEditor: true

                anchors.fill: parent
                hoverEnabled: true
                background: null
                wrapMode: TextArea.Wrap
                leftPadding: sizeFieldPaddingX
                rightPadding: sizeFieldPaddingX
                topPadding: 12
                bottomPadding: 12
                color: textPrimary
                placeholderText: workspace.tr(
                    "一句话描述这个技能何时使用。",
                    "Describe when this skill should be used."
                )
                placeholderTextColor: textPlaceholder
                selectionColor: textSelectionBg
                selectedTextColor: textSelectionFg
                font.pixelSize: typeBody
            }
        }
    }

    footer: [
        PillActionButton {
            text: workspace.tr("创建技能", "Create skill")
            minHeight: 34
            horizontalPadding: 24
            fillColor: accent
            hoverFillColor: accentHover
            buttonEnabled: skillNameInput.text.trim().length > 0
            onClicked: {
                if (!workspace.hasSkillsService)
                    return
                if (workspace.skillsService.createSkill(skillNameInput.text, skillDescriptionInput.text))
                    root.close()
            }
        }
    ]
}
