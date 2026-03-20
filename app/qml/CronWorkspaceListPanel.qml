import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    property var workspace
    property bool compactLayout: false

    objectName: "cronListPanel"
    SplitView.preferredWidth: compactLayout ? 0 : 320
    SplitView.minimumWidth: compactLayout ? 0 : 288
    SplitView.maximumWidth: compactLayout ? 0 : 340
    SplitView.preferredHeight: compactLayout ? workspace.compactListPaneHeight : 0
    SplitView.minimumHeight: compactLayout ? 136 : 0
    SplitView.fillWidth: compactLayout
    SplitView.fillHeight: true

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 2
        spacing: 12

        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 44
            radius: 18
            color: searchArea.containsMouse ? workspace.fieldHoverFill : workspace.fieldFill
            border.width: searchField.activeFocus ? 1.5 : 1
            border.color: searchField.activeFocus ? workspace.borderFocus : workspace.fieldBorder

            Behavior on color { ColorAnimation { duration: workspace.motionFast; easing.type: workspace.easeStandard } }
            Behavior on border.color { ColorAnimation { duration: workspace.motionFast; easing.type: workspace.easeStandard } }

            MouseArea { id: searchArea; anchors.fill: parent; hoverEnabled: true; acceptedButtons: Qt.NoButton }

            TextField {
                id: searchField
                property bool baoClickAwayEditor: true
                anchors.fill: parent
                anchors.leftMargin: 14
                anchors.rightMargin: 14
                anchors.verticalCenter: parent.verticalCenter
                hoverEnabled: true
                color: workspace.textPrimary
                placeholderText: workspace.tr("搜索任务名称、消息或渠道", "Search tasks, messages, or channels")
                placeholderTextColor: workspace.textPlaceholder
                background: null
                leftPadding: 26
                topPadding: 0
                bottomPadding: 0
                verticalAlignment: TextInput.AlignVCenter
                selectionColor: workspace.textSelectionBg
                selectedTextColor: workspace.textSelectionFg
                onTextEdited: if (workspace.hasCronService) workspace.cronService.setFilterQuery(text)

                AppIcon {
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    width: 16
                    height: 16
                    source: workspace.icon("page-search")
                    sourceSize: Qt.size(width, height)
                    opacity: 0.52
                }
            }
        }

        Flow {
            Layout.fillWidth: true
            spacing: 8

            Repeater {
                model: workspace.statusItems()

                delegate: PillActionButton {
                    required property var modelData
                    text: modelData.label
                    fillColor: workspace.hasCronService && workspace.cronService.statusFilter === modelData.key ? workspace.cronAccent : "transparent"
                    hoverFillColor: workspace.hasCronService && workspace.cronService.statusFilter === modelData.key ? workspace.cronAccentHover : workspace.bgCardHover
                    outlineColor: workspace.hasCronService && workspace.cronService.statusFilter === modelData.key ? workspace.cronAccent : workspace.borderSubtle
                    textColor: workspace.hasCronService && workspace.cronService.statusFilter === modelData.key ? "#FFFFFFFF" : workspace.textSecondary
                    outlined: !workspace.hasCronService || workspace.cronService.statusFilter !== modelData.key
                    horizontalPadding: 14
                    minHeight: 30
                    onClicked: if (workspace.hasCronService) workspace.cronService.setStatusFilter(modelData.key)
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true

            Text {
                text: workspace.tr("任务列表", "Task list")
                color: workspace.textPrimary
                font.pixelSize: workspace.typeBody + 1
                font.weight: workspace.weightBold
            }

            Item { Layout.fillWidth: true }

            Text {
                text: workspace.hasCronService ? (workspace.cronService.visibleTaskCount + " / " + workspace.cronService.totalTaskCount) : "0 / 0"
                color: workspace.textSecondary
                font.pixelSize: workspace.typeMeta
                font.weight: workspace.weightBold
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            Loader {
                anchors.fill: parent
                active: workspace.hasCronService && workspace.cronService.visibleTaskCount === 0
                sourceComponent: Component {
                    Item {
                        Column {
                            anchors.centerIn: parent
                            width: Math.min(parent.width - 32, 220)
                            spacing: 10

                            Text {
                                width: parent.width
                                text: workspace.tr("当前没有符合条件的任务", "No tasks match the current view")
                                color: workspace.textPrimary
                                font.pixelSize: workspace.typeBody + 1
                                font.weight: workspace.weightBold
                                wrapMode: Text.WordWrap
                                horizontalAlignment: Text.AlignHCenter
                            }

                            Text {
                                width: parent.width
                                text: workspace.tr("你可以从右上角新建任务，或调整搜索和筛选。", "Create a task from the top right, or adjust search and filters.")
                                color: workspace.textSecondary
                                font.pixelSize: workspace.typeBody
                                wrapMode: Text.WordWrap
                                horizontalAlignment: Text.AlignHCenter
                            }
                        }
                    }
                }
            }

            ListView {
                id: taskList
                objectName: "cronTaskList"
                anchors.fill: parent
                anchors.topMargin: 4
                visible: !workspace.hasCronService || workspace.cronService.visibleTaskCount > 0
                clip: true
                spacing: 8
                model: workspace.hasCronService ? workspace.cronService.tasksModel : null
                reuseItems: true
                cacheBuffer: workspace.listCacheBuffer
                boundsBehavior: Flickable.StopAtBounds

                delegate: CronWorkspaceTaskRow {
                    workspace: root.workspace
                    listWidth: taskList.width
                }
            }
        }
    }
}
