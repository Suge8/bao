import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: panel

    required property var workspaceRoot

    Layout.fillWidth: true
    implicitHeight: factComposerColumn.implicitHeight + 24
    radius: radiusLg
    color: workspaceRoot.factEditorActive ? bgInput : bgCard
    border.width: 1
    border.color: appendEditor.activeFocus ? borderFocus : (workspaceRoot.factEditorActive ? accent : borderSubtle)

    Behavior on color { ColorAnimation { duration: motionUi; easing.type: easeStandard } }
    Behavior on border.color { ColorAnimation { duration: motionUi; easing.type: easeStandard } }

    ColumnLayout {
        id: factComposerColumn
        anchors.fill: parent
        anchors.margins: 12
        spacing: 10

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Text {
                Layout.fillWidth: true
                text: workspaceRoot.factComposerTitle()
                color: textSecondary
                font.pixelSize: typeMeta
                font.weight: weightBold
            }

            IconCircleButton {
                id: factPrimaryAction
                objectName: "memoryFactPrimaryAction"
                buttonSize: 32
                glyphSize: typeMeta + 2
                glyphText: workspaceRoot.factEditorActive ? "✓" : "✎"
                emphasized: workspaceRoot.factEditorActive
                fillColor: workspaceRoot.factEditorActive ? accent : "transparent"
                hoverFillColor: workspaceRoot.factEditorActive ? accentHover : bgCardHover
                outlineColor: workspaceRoot.factEditorActive ? accent : borderSubtle
                glyphColor: workspaceRoot.factEditorActive ? "#FFFFFFFF" : accent
                buttonEnabled: workspaceRoot.factEditorActive
                    ? workspaceRoot.canMutate
                      && !!workspaceRoot.selectedMemoryCategory.category
                      && workspaceRoot.factEditorText.trim().length > 0
                    : workspaceRoot.canMutate && workspaceRoot.hasSelectedMemoryFact
                onClicked: workspaceRoot.triggerPrimaryFactAction()
            }

            IconCircleButton {
                objectName: "memoryFactAddAction"
                buttonSize: 32
                glyphSize: typeMeta + 4
                glyphText: "+"
                fillColor: "transparent"
                hoverFillColor: bgCardHover
                outlineColor: borderSubtle
                glyphColor: accent
                buttonEnabled: workspaceRoot.canMutate && !!workspaceRoot.selectedMemoryCategory.category
                onClicked: workspaceRoot.beginNewFact()
            }
        }

        Text {
            Layout.fillWidth: true
            text: workspaceRoot.factComposerMeta()
            color: textSecondary
            font.pixelSize: typeMeta
            wrapMode: Text.WordWrap
        }

        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 124
            radius: radiusMd
            color: bgBase
            border.width: 1
            border.color: borderSubtle

            ScrollView {
                anchors.fill: parent
                clip: true

                TextArea {
                    id: appendEditor
                    objectName: "memoryFactEditor"
                    color: textPrimary
                    text: workspaceRoot.factEditorText
                    readOnly: !workspaceRoot.factEditorActive
                    placeholderText: workspaceRoot.factComposerPlaceholder()
                    placeholderTextColor: textPlaceholder
                    wrapMode: TextArea.Wrap
                    selectByMouse: true
                    selectionColor: textSelectionBg
                    selectedTextColor: textSelectionFg
                    background: null
                    padding: 12
                    Component.onCompleted: {
                        workspaceRoot.factEditorRef = appendEditor
                    }
                    onTextChanged: {
                        if (workspaceRoot.syncingEditors)
                            return
                        workspaceRoot.factEditorText = text
                    }
                }
            }
        }
    }
}
