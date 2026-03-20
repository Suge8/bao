import QtQuick 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    objectName: "sidebarControlTowerCard"

    required property var sidebarRoot
    signal clicked()
    readonly property bool compactCard: width <= 196
    readonly property int cardInset: compactCard ? 12 : 14
    readonly property int titleFontSize: compactCard ? sidebarRoot.typeBody : sidebarRoot.typeBody + 1
    readonly property int towerIconSize: compactCard ? 42 : 48
    readonly property int titleLineCount: compactCard ? 3 : 2
    readonly property int titleIconGap: 12
    readonly property int metricChipSpacing: 8
    readonly property int metricChipHorizontalPadding: compactCard ? 22 : 24
    readonly property int metricChipMinHeight: compactCard ? 24 : 26
    readonly property var metricItems: [
        {
            "chipId": "sidebarWorking",
            "label": sidebarRoot.isChinese
                ? Number(sidebarRoot.supervisorOverview.workingCount || 0) + " 工作中"
                : Number(sidebarRoot.supervisorOverview.workingCount || 0) + " Working",
            "fillColor": sidebarRoot.isDark ? "#192118" : "#EAF7EE",
            "borderColor": sidebarRoot.isDark ? "#294034" : "#BCDCC4",
            "textColor": sidebarRoot.isDark ? "#D8F3DE" : "#2E6541"
        },
        {
            "chipId": "sidebarAutomation",
            "label": sidebarRoot.isChinese
                ? Number(sidebarRoot.supervisorOverview.automationCount || 0) + " 自动化"
                : Number(sidebarRoot.supervisorOverview.automationCount || 0) + " Automation",
            "fillColor": sidebarRoot.isDark ? "#1D1814" : "#FFF2E2",
            "borderColor": sidebarRoot.isDark ? "#43311F" : "#E0BC83",
            "textColor": sidebarRoot.isDark ? "#F5D5A8" : "#8E5D19"
        },
        {
            "chipId": "sidebarPending",
            "label": sidebarRoot.isChinese
                ? Number(sidebarRoot.supervisorOverview.attentionCount || 0) + " 待处理"
                : Number(sidebarRoot.supervisorOverview.attentionCount || 0) + " Pending",
            "fillColor": sidebarRoot.isDark ? "#221615" : "#FFF0EC",
            "borderColor": sidebarRoot.isDark ? "#4A2723" : "#E6B8B0",
            "textColor": sidebarRoot.isDark ? "#F5C7C0" : "#8F4B41"
        }
    ]

    Layout.fillWidth: true
    Layout.leftMargin: 16
    Layout.rightMargin: 16
    Layout.topMargin: 12
    implicitHeight: contentColumn.implicitHeight + root.cardInset * 2
    radius: 24
    color: sidebarRoot.selectionTarget === "control_tower"
           ? (sidebarRoot.isDark ? "#24160F" : "#FFF0DE")
           : (mouseArea.containsMouse ? (sidebarRoot.isDark ? "#1C130F" : "#FFF7EF") : (sidebarRoot.isDark ? "#15100D" : "#FFFBF7"))
    border.width: 1
    border.color: sidebarRoot.selectionTarget === "control_tower"
                  ? (sidebarRoot.isDark ? "#6A4322" : "#E2AA55")
                  : (sidebarRoot.isDark ? "#2A1F18" : "#E7D7C6")
    scale: mouseArea.pressed ? 0.992 : (mouseArea.containsMouse ? sidebarRoot.motionHoverScaleSubtle : 1.0)

    Behavior on color { ColorAnimation { duration: sidebarRoot.motionFast; easing.type: sidebarRoot.easeStandard } }
    Behavior on border.color { ColorAnimation { duration: sidebarRoot.motionFast; easing.type: sidebarRoot.easeStandard } }
    Behavior on scale { NumberAnimation { duration: sidebarRoot.motionFast; easing.type: sidebarRoot.easeEmphasis } }

    Rectangle {
        anchors.fill: parent
        anchors.margins: 1
        radius: parent.radius - 1
        color: sidebarRoot.isDark ? "#0AFFFFFF" : "#10FFFFFF"
    }

    Column {
        id: contentColumn
        anchors.fill: parent
        anchors.margins: root.cardInset
        spacing: compactCard ? 12 : 10

        Item {
            width: parent.width
            height: Math.max(controlTowerIcon.height, titleText.implicitHeight)

            AppIcon {
                id: controlTowerIcon
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                width: root.towerIconSize
                height: root.towerIconSize
                source: sidebarRoot.sectionIconSource("control_tower")
                sourceSize: Qt.size(width, height)
            }

            Text {
                id: titleText
                objectName: "sidebarControlTowerTitle"
                anchors.left: controlTowerIcon.right
                anchors.leftMargin: root.titleIconGap
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                text: sidebarRoot.strings.sidebar_control_tower
                color: sidebarRoot.textPrimary
                font.pixelSize: root.titleFontSize
                font.weight: sidebarRoot.weightBold
                wrapMode: Text.WordWrap
                maximumLineCount: root.titleLineCount
                elide: Text.ElideRight
                lineHeight: 1.05
                lineHeightMode: Text.ProportionalHeight
            }
        }

        Flow {
            id: metricsFlow
            objectName: "sidebarControlTowerMetricsFlow"
            width: parent.width
            spacing: root.metricChipSpacing

            Repeater {
                model: root.metricItems

                delegate: ControlTowerInfoChip {
                    required property var modelData
                    objectName: "sidebarControlTowerMetric_" + String(modelData.chipId || "")
                    chipId: String(modelData.chipId || "")
                    labelText: String(modelData.label || "")
                    isDark: sidebarRoot.isDark
                    fillColor: modelData.fillColor
                    borderColor: modelData.borderColor
                    textColor: modelData.textColor
                    fontPixelSize: compactCard ? sidebarRoot.typeCaption : sidebarRoot.typeMeta
                    fontWeight: sidebarRoot.weightDemiBold
                    horizontalPadding: root.metricChipHorizontalPadding
                    minHeight: root.metricChipMinHeight
                }
            }
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.clicked()
    }
}
