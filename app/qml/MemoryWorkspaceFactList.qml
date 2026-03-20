import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: panel

    required property var workspaceRoot

    Layout.fillWidth: true
    implicitHeight: factColumn.implicitHeight + 24
    radius: radiusLg
    color: bgCard
    border.width: 1
    border.color: borderSubtle

    Column {
        id: factColumn
        anchors.fill: parent
        anchors.margins: 12
        spacing: 8

        Repeater {
            model: workspaceRoot.selectedMemoryCategory.facts || []

            delegate: Rectangle {
                required property var modelData
                width: factColumn.width
                radius: radiusMd
                color: workspaceRoot.isSelectedFact(modelData)
                    ? (isDark ? "#241A15" : "#FFF2E3")
                    : (isDark ? "#1B1512" : "#FFF9F3")
                border.width: 1
                border.color: workspaceRoot.isSelectedFact(modelData) ? accent : borderSubtle
                implicitHeight: factContent.implicitHeight + 20

                Behavior on color { ColorAnimation { duration: motionUi; easing.type: easeStandard } }
                Behavior on border.color { ColorAnimation { duration: motionUi; easing.type: easeStandard } }

                Column {
                    id: factContent
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 8

                    Text {
                        width: parent.width
                        text: String(modelData.content || "")
                        color: textPrimary
                        font.pixelSize: typeLabel
                        wrapMode: Text.WordWrap
                    }

                    RowLayout {
                        width: parent.width
                        spacing: 8

                        Text {
                            Layout.fillWidth: true
                            text: workspaceRoot.memoryFactMeta(modelData)
                            color: textSecondary
                            font.pixelSize: typeMeta
                            wrapMode: Text.WordWrap
                        }
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: workspaceRoot.selectFact(modelData)
                }
            }
        }

        Text {
            visible: (workspaceRoot.selectedMemoryCategory.facts || []).length === 0
            width: parent.width
            text: workspaceRoot.tr(
                "这个分类还没有稳定事实。先补充一条短而稳定的记忆。",
                "This category has no durable facts yet. Add one short, stable memory first."
            )
            color: textSecondary
            font.pixelSize: typeLabel
            wrapMode: Text.WordWrap
        }
    }
}
