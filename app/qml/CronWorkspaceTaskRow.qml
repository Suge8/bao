import QtQuick 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root

    required property string taskId
    required property string name
    required property bool enabled
    required property string statusKey
    required property string scheduleSummary
    required property string nextRunText
    required property string lastResultText
    required property bool isDraft
    property var workspace
    property real listWidth: 0

    objectName: isDraft ? "cronDraftRow" : "cronTaskRow_" + taskId
    width: listWidth
    implicitHeight: rowColumn.implicitHeight + 16
    radius: 18
    color: workspace.hasCronService && workspace.cronService.activeListItemId === taskId ? workspace.selectedRowFill : (rowHit.containsMouse ? workspace.bgCardHover : "transparent")
    border.width: workspace.hasCronService && workspace.cronService.activeListItemId === taskId ? 1.2 : 1
    border.color: workspace.hasCronService && workspace.cronService.activeListItemId === taskId ? workspace.selectedRowBorder : workspace.fieldBorder

    Behavior on color { ColorAnimation { duration: workspace.motionFast; easing.type: workspace.easeStandard } }
    Behavior on border.color { ColorAnimation { duration: workspace.motionFast; easing.type: workspace.easeStandard } }

    MouseArea {
        id: rowHit
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: workspace.chooseTask(taskId)
    }

    ColumnLayout {
        id: rowColumn
        anchors.fill: parent
        anchors.margins: 10
        spacing: 6

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Item {
                Layout.preferredWidth: 16
                Layout.preferredHeight: 16

                AppIcon {
                    anchors.fill: parent
                    source: statusKey === "error" ? workspace.icon("message-alert") : workspace.icon("calendar-rotate")
                    sourceSize: Qt.size(width, height)
                    opacity: 0.9
                }
            }

            Rectangle {
                radius: 10
                color: workspace.statusSurface(statusKey)
                implicitHeight: stateLabel.implicitHeight + 10
                implicitWidth: stateLabel.implicitWidth + 16

                Text {
                    id: stateLabel
                    anchors.centerIn: parent
                    text: workspace.statusLabel(statusKey)
                    color: workspace.statusColor(statusKey)
                    font.pixelSize: workspace.typeMeta
                    font.weight: workspace.weightBold
                }
            }

            Item { Layout.fillWidth: true }

            PillActionButton {
                visible: !root.isDraft
                iconSource: root.enabled ? workspace.icon("bubble-xmark") : workspace.icon("circle-spark")
                text: root.enabled ? workspace.tr("停用", "Pause") : workspace.tr("启用", "Enable")
                fillColor: "transparent"
                hoverFillColor: root.enabled ? (workspace.isDark ? "#311816" : "#FFF0EC") : workspace.bgCardHover
                outlineColor: root.enabled ? workspace.statusError : workspace.borderSubtle
                hoverOutlineColor: root.enabled ? workspace.statusError : workspace.borderDefault
                textColor: root.enabled ? workspace.statusError : workspace.textSecondary
                outlined: true
                horizontalPadding: 10
                minHeight: 26
                onClicked: {
                    workspace.chooseTask(taskId)
                    if (workspace.hasCronService)
                        workspace.cronService.setSelectedEnabled(!root.enabled)
                }
            }
        }

        Text {
            Layout.fillWidth: true
            text: root.name
            color: workspace.textPrimary
            font.pixelSize: workspace.typeBody
            font.weight: workspace.weightBold
            elide: Text.ElideRight
        }

        Text {
            Layout.fillWidth: true
            text: root.scheduleSummary
            color: workspace.textSecondary
            font.pixelSize: workspace.typeBody
            elide: Text.ElideRight
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 2

                Text {
                    text: workspace.tr("下次执行", "Next run")
                    color: workspace.textTertiary
                    font.pixelSize: workspace.typeMeta
                    font.weight: workspace.weightBold
                }

                Text {
                    Layout.fillWidth: true
                    text: workspace.summaryText(root.nextRunText, "未安排", "Not scheduled")
                    color: workspace.textPrimary
                    font.pixelSize: workspace.typeBody
                    elide: Text.ElideRight
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 2

                Text {
                    text: workspace.tr("最近结果", "Last result")
                    color: workspace.textTertiary
                    font.pixelSize: workspace.typeMeta
                    font.weight: workspace.weightBold
                }

                Text {
                    Layout.fillWidth: true
                    text: root.lastResultText
                    color: root.statusKey === "error" ? workspace.statusError : workspace.textPrimary
                    font.pixelSize: workspace.typeBody
                    elide: Text.ElideRight
                }
            }
        }
    }
}
