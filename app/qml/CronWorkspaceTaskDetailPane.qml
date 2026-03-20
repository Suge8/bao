import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    property var workspace
    property var deleteModal
    property bool compactLayout: false

    objectName: "cronDetailPanel"
    SplitView.preferredWidth: compactLayout ? 0 : 620
    SplitView.minimumWidth: compactLayout ? 0 : 420
    SplitView.preferredHeight: compactLayout ? workspace.compactDetailPaneMinHeight : 0
    SplitView.minimumHeight: compactLayout ? workspace.compactDetailPaneMinHeight : 0
    SplitView.fillWidth: true
    SplitView.fillHeight: true

    Loader {
        anchors.fill: parent
        active: !workspace.hasDraft
        sourceComponent: CronWorkspaceDetailEmptyState { workspace: root.workspace }
    }

    ScrollView {
        id: detailScroll
        anchors.fill: parent
        anchors.margins: 2
        visible: workspace.hasDraft
        clip: true
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

        ColumnLayout {
            width: Math.max(0, detailScroll.availableWidth)
            spacing: 12

            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 4

                    Text {
                        text: workspace.editingNewTask ? workspace.tr("正在新建任务", "Creating a task") : workspace.tr("任务详情", "Task details")
                        color: workspace.textSecondary
                        font.pixelSize: workspace.typeMeta
                        font.weight: workspace.weightBold
                        font.letterSpacing: workspace.letterWide
                    }

                    Text {
                        Layout.fillWidth: true
                        text: workspace.draftString("name", "") !== "" ? workspace.draftString("name", "") : workspace.tr("未命名任务", "Untitled task")
                        color: workspace.textPrimary
                        font.pixelSize: workspace.typeLabel
                        font.weight: workspace.weightBold
                        elide: Text.ElideRight
                    }
                }

                Flow {
                    Layout.alignment: Qt.AlignRight | Qt.AlignTop
                    spacing: 8

                    Rectangle {
                        radius: 12
                        color: workspace.statusSurface(workspace.taskStatusKey())
                        implicitHeight: 30
                        implicitWidth: detailStateLabel.implicitWidth + 18

                        Text {
                            id: detailStateLabel
                            anchors.centerIn: parent
                            text: workspace.showingExistingTask ? workspace.statusLabel(workspace.taskStatusKey()) : (workspace.draftBool("enabled", true) ? workspace.tr("已启用", "Enabled") : workspace.tr("已停用", "Disabled"))
                            color: workspace.showingExistingTask ? workspace.statusColor(workspace.taskStatusKey()) : (workspace.draftBool("enabled", true) ? workspace.statusSuccess : workspace.textSecondary)
                            font.pixelSize: workspace.typeLabel
                            font.weight: workspace.weightBold
                        }
                    }

                    PillActionButton {
                        text: workspace.draftBool("delete_after_run", false) ? workspace.tr("执行后删除", "Delete after run") : workspace.tr("保留任务", "Keep task")
                        fillColor: workspace.draftBool("delete_after_run", false) ? workspace.statusWarning : "transparent"
                        hoverFillColor: workspace.draftBool("delete_after_run", false) ? Qt.darker(workspace.statusWarning, 1.05) : workspace.bgCardHover
                        outlineColor: workspace.draftBool("delete_after_run", false) ? workspace.statusWarning : workspace.borderSubtle
                        textColor: workspace.draftBool("delete_after_run", false) ? "#FFFFFFFF" : workspace.textSecondary
                        outlined: !workspace.draftBool("delete_after_run", false)
                        onClicked: workspace.setDraft("delete_after_run", !workspace.draftBool("delete_after_run", false))
                    }
                }
            }

            CronWorkspaceStatusCard { workspace: root.workspace }
            CronWorkspaceBasicsSection { workspace: root.workspace }
            CronWorkspaceScheduleSection { workspace: root.workspace }
            CronWorkspaceDeliverySection { workspace: root.workspace }

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                AsyncActionButton {
                    Layout.preferredWidth: 150
                    text: workspace.editingNewTask ? workspace.tr("创建任务", "Create task") : workspace.tr("保存任务", "Save task")
                    busy: workspace.hasCronService && workspace.cronService.busy
                    buttonEnabled: workspace.hasCronService && !workspace.cronService.busy
                    fillColor: workspace.cronAccent
                    hoverFillColor: workspace.cronAccentHover
                    iconSource: workspace.icon("circle-spark")
                    onClicked: if (workspace.hasCronService) workspace.cronService.saveDraft()
                }

                PillActionButton {
                    Layout.preferredWidth: 132
                    text: workspace.tr("另存副本", "Save as copy")
                    iconSource: workspace.labIcon("copy-file-path")
                    fillColor: "transparent"
                    hoverFillColor: workspace.bgCardHover
                    outlineColor: workspace.borderSubtle
                    textColor: workspace.textSecondary
                    outlined: true
                    buttonEnabled: workspace.showingExistingTask
                    onClicked: if (workspace.hasCronService) workspace.cronService.duplicateSelected()
                }

                PillActionButton {
                    Layout.preferredWidth: 132
                    text: workspace.tr("删除任务", "Delete task")
                    iconSource: workspace.labIcon("tab-x")
                    fillColor: "transparent"
                    hoverFillColor: workspace.isDark ? "#311816" : "#FFF0EC"
                    outlineColor: workspace.statusError
                    hoverOutlineColor: workspace.statusError
                    textColor: workspace.statusError
                    outlined: true
                    buttonEnabled: workspace.showingExistingTask
                    onClicked: if (root.deleteModal) root.deleteModal.open()
                }

                Item { Layout.fillWidth: true }
            }
        }
    }
}
