import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: pane

    required property var workspaceRoot

    ColumnLayout {
        anchors.fill: parent
        spacing: 12
        visible: workspaceRoot.hasSelectedMemory

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
                    source: workspaceRoot.detailIconSource
                    fillMode: Image.PreserveAspectFit
                    smooth: true
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 2

                Text {
                    Layout.fillWidth: true
                    text: workspaceRoot.memoryCategoryTitle(workspaceRoot.selectedMemoryCategory.category)
                    color: textPrimary
                    font.pixelSize: typeTitle - 3
                    font.weight: weightBold
                    elide: Text.ElideRight
                }

                Text {
                    Layout.fillWidth: true
                    text: workspaceRoot.memoryCategoryMeta(workspaceRoot.selectedMemoryCategory)
                    color: textSecondary
                    font.pixelSize: typeMeta
                    wrapMode: Text.WordWrap
                }
            }
        }

        Text {
            Layout.fillWidth: true
            text: workspaceRoot.tr("事实清单", "Fact list")
            color: textSecondary
            font.pixelSize: typeMeta
            font.weight: weightBold
        }

        MemoryWorkspaceFactList {
            Layout.fillWidth: true
            workspaceRoot: pane.workspaceRoot
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: radiusLg
            color: bgInput
            border.width: 1
            border.color: editor.activeFocus ? borderFocus : borderSubtle

            Behavior on border.color { ColorAnimation { duration: motionUi; easing.type: easeStandard } }

            ScrollView {
                anchors.fill: parent
                clip: true

                TextArea {
                    id: editor
                    objectName: "memoryCategoryEditor"
                    color: textPrimary
                    text: workspaceRoot.editorText
                    placeholderText: workspaceRoot.tr(
                        "把值得长期保留的内容写在这里。每一行都会被视为一个稳定记忆片段。",
                        "Write durable information here. Each line is treated as a stable memory fragment."
                    )
                    placeholderTextColor: textPlaceholder
                    wrapMode: TextArea.Wrap
                    selectByMouse: true
                    selectionColor: textSelectionBg
                    selectedTextColor: textSelectionFg
                    background: null
                    padding: 14
                    Component.onCompleted: {
                        workspaceRoot.memoryEditorRef = editor
                        workspaceRoot.syncEditorFromSelection(true)
                    }
                    onTextChanged: {
                        if (workspaceRoot.syncingEditors)
                            return
                        workspaceRoot.editorText = text
                        workspaceRoot.editorDirty = text !== String(workspaceRoot.selectedMemoryCategory.content || "")
                    }
                }
            }
        }

        MemoryWorkspaceFactComposer {
            Layout.fillWidth: true
            workspaceRoot: pane.workspaceRoot
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 8

            AsyncActionButton {
                Layout.fillWidth: true
                text: workspaceRoot.tr("保存当前分类", "Save current category")
                busy: workspaceRoot.hasMemoryService && workspaceRoot.memoryService.blockingBusy
                iconSource: workspaceRoot.saveIconSource
                fillColor: isDark ? "#2A1B11" : "#E7D5C7"
                hoverFillColor: isDark ? "#342116" : "#DDC7B6"
                textColor: textPrimary
                spinnerColor: textPrimary
                spinnerSecondaryColor: isDark ? "#A0F7EFE7" : "#886B5649"
                spinnerHaloColor: isDark ? "#24FFFFFF" : "#186B5649"
                buttonEnabled: workspaceRoot.canMutate && !!workspaceRoot.selectedMemoryCategory.category
                minHeight: 36
                onClicked: workspaceRoot.memoryService.saveMemoryCategory(
                    workspaceRoot.selectedMemoryCategory.category,
                    workspaceRoot.memoryEditorRef ? workspaceRoot.memoryEditorRef.text : workspaceRoot.editorText
                )
            }

            PillActionButton {
                text: workspaceRoot.tr("清空当前分类", "Clear")
                iconSource: workspaceRoot.removeIconSource
                outlined: true
                fillColor: "transparent"
                hoverFillColor: isDark ? "#2A1614" : "#FFF1EE"
                outlineColor: statusError
                textColor: statusError
                buttonEnabled: workspaceRoot.canMutate
                    && !!workspaceRoot.selectedMemoryCategory.category
                    && String(workspaceRoot.selectedMemoryCategory.content || "").trim().length > 0
                onClicked: workspaceRoot.openDestructiveModal(
                    "clearMemory",
                    "",
                    workspaceRoot.selectedMemoryCategory.category
                )
            }
        }
    }

    Item {
        anchors.fill: parent
        visible: !workspaceRoot.hasSelectedMemory

        Column {
            anchors.centerIn: parent
            width: Math.min(parent.width - 48, 300)
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
                    text: "▣"
                    color: accent
                    font.pixelSize: 22
                    font.weight: weightBold
                }
            }

            Text {
                width: parent.width
                text: workspaceRoot.tr("选择一个分类开始管理", "Choose a category to manage")
                color: textPrimary
                font.pixelSize: typeButton + 1
                font.weight: weightBold
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
            }

            Text {
                width: parent.width
                text: workspaceRoot.tr(
                    "长期记忆适合存放稳定偏好、项目上下文和值得长期保留的做法。",
                    "Long-term memory is ideal for stable preferences, project context, and durable practices."
                )
                color: textSecondary
                font.pixelSize: typeLabel
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
            }
        }
    }
}
