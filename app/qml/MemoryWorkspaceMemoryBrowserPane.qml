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
            text: workspaceRoot.tr("选择分类", "Choose a category")
            color: textPrimary
            font.pixelSize: typeLabel
            font.weight: weightBold
        }

        Text {
            text: workspaceRoot.tr(
                "先选分类，再在右侧查看和编辑。",
                "Pick a category first, then review and edit on the right."
            )
            color: textSecondary
            font.pixelSize: typeMeta
        }
    }

    Rectangle {
        Layout.fillWidth: true
        implicitHeight: 40
        radius: 16
        color: memorySearchField.activeFocus ? bgInputFocus : (memorySearchField.hovered ? bgInputHover : bgInput)
        border.width: memorySearchField.activeFocus ? 1.5 : 1
        border.color: memorySearchField.activeFocus ? borderFocus : borderSubtle

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
            id: memorySearchField
            property bool baoClickAwayEditor: true
            anchors.fill: parent
            leftPadding: 36
            rightPadding: 12
            background: null
            color: textPrimary
            text: workspaceRoot.memorySearchQuery
            placeholderText: workspaceRoot.tr("搜索分类或记忆内容…", "Search categories or memory text…")
            placeholderTextColor: textPlaceholder
            selectionColor: textSelectionBg
            selectedTextColor: textSelectionFg
            font.pixelSize: typeLabel
            onTextChanged: if (workspaceRoot.memorySearchQuery !== text) workspaceRoot.memorySearchQuery = text
        }
    }

    Flow {
        Layout.fillWidth: true
        spacing: 8

        Repeater {
            model: ["preference", "personal", "project", "general"]

            delegate: PillActionButton {
                required property var modelData
                text: modelData === "preference" ? workspaceRoot.tr("偏好", "Preference")
                      : modelData === "personal" ? workspaceRoot.tr("个人", "Personal")
                      : modelData === "project" ? workspaceRoot.tr("项目", "Project")
                      : workspaceRoot.tr("通用", "General")
                outlined: true
                fillColor: String(workspaceRoot.selectedMemoryCategory.category || "") === modelData
                    ? accentMuted
                    : "transparent"
                hoverFillColor: String(workspaceRoot.selectedMemoryCategory.category || "") === modelData
                    ? accentMuted
                    : bgCardHover
                outlineColor: String(workspaceRoot.selectedMemoryCategory.category || "") === modelData
                    ? accent
                    : borderSubtle
                textColor: textPrimary
                onClicked: workspaceRoot.selectMemory(modelData)
            }
        }
    }

    Text {
        Layout.fillWidth: true
        text: workspaceRoot.tr(
            "已使用分类 " + Number(workspaceRoot.memoryStats.used_categories || 0) + "/"
            + Number(workspaceRoot.memoryStats.total_categories || 0) + " · 事实 "
            + Number(workspaceRoot.memoryStats.total_facts || 0) + " 条",
            "Used categories " + Number(workspaceRoot.memoryStats.used_categories || 0) + "/"
            + Number(workspaceRoot.memoryStats.total_categories || 0) + " · "
            + Number(workspaceRoot.memoryStats.total_facts || 0) + " facts"
        )
        color: textSecondary
        font.pixelSize: typeMeta
    }

    Rectangle {
        Layout.fillWidth: true
        Layout.fillHeight: true
        color: "transparent"
        border.width: 0

        MemoryWorkspaceMemoryList {
            anchors.fill: parent
            workspaceRoot: pane.workspaceRoot
        }
    }
}
