import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

CalloutPanel {
    id: panel

    required property var workspaceRoot
    required property bool compactLayout
    required property bool isDark
    required property color textPrimary
    required property color textSecondary
    required property color borderSubtle
    required property int typeTitle
    required property int typeMeta
    required property int typeCaption
    required property int weightBold
    required property int weightMedium
    readonly property int metricValuePixelSize: typeTitle - 1
    readonly property int profilesMetricValue: workspaceRoot.hasSelectedProfile ? 1 : workspaceRoot.profileCount
    readonly property int sessionsMetricValue: workspaceRoot.totalSessionCount()
    readonly property int workingMetricValue: workspaceRoot.workingCount
    readonly property int automationMetricValue: workspaceRoot.automationCount
    readonly property string profilesMetricLabel: workspaceRoot.isChinese ? "分身" : "Profiles"
    readonly property string sessionsMetricLabel: workspaceRoot.isChinese ? "总会话" : "Sessions"
    readonly property string workingMetricLabel: workspaceRoot.isChinese ? "工作中" : "Working"
    readonly property string automationMetricLabel: workspaceRoot.isChinese ? "自动化" : "Automation"
    readonly property int metricColumns: compactLayout ? 2 : 4

    Layout.fillWidth: true
    panelColor: isDark ? "#15100D" : "#FFF7F0"
    panelBorderColor: isDark ? "#22FFFFFF" : "#14000000"
    overlayColor: isDark ? "#0BFFFFFF" : "#08FFFFFF"
    overlayVisible: true
    sideGlowVisible: false
    accentBlobVisible: false
    padding: 16

    ColumnLayout {
        width: parent.width
        spacing: 14

        Item {
            Layout.fillWidth: true
            implicitHeight: 52

            Row {
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                spacing: 10

                WorkspaceHeroIcon {
                    implicitWidth: 48
                    implicitHeight: 48
                    iconSize: 32
                    iconSource: workspaceRoot.solidIcon("sidebar-control-tower-solid")
                    fillColor: isDark ? "#241710" : "#F6E7D6"
                    outlineColor: isDark ? "#342116" : "#EBC9A0"
                }

                Column {
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 2

                    Text {
                        objectName: "controlTowerScopeTitle"
                        text: workspaceRoot.scopeTitle()
                        color: textPrimary
                        font.pixelSize: typeTitle - 1
                        font.weight: weightBold
                    }

                    Text {
                        text: workspaceRoot.scopeCaption()
                        color: textSecondary
                        font.pixelSize: typeMeta
                        maximumLineCount: 1
                        elide: Text.ElideRight
                    }
                }
            }

            PillActionButton {
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                text: workspaceRoot.isChinese ? "刷新" : "Refresh"
                iconSource: workspaceRoot.icon("clock-rotate-right")
                fillColor: "transparent"
                hoverFillColor: bgCardHover
                outlineColor: borderSubtle
                textColor: textSecondary
                outlined: true
                minHeight: 34
                horizontalPadding: 18
                onClicked: if (workspaceRoot.hasSupervisorService) workspaceRoot.supervisorService.refresh()
            }
        }

        GridLayout {
            Layout.fillWidth: true
            columns: panel.metricColumns
            rowSpacing: 8
            columnSpacing: 12

            ControlTowerHeroMetricStrip {
                metricId: "profiles"
                iconSource: workspaceRoot.solidIcon("sidebar-profiles-solid")
                valueText: String(panel.profilesMetricValue)
                labelText: panel.profilesMetricLabel
                isDark: panel.isDark
                textPrimary: panel.textPrimary
                textSecondary: panel.textSecondary
                typeTitle: panel.metricValuePixelSize
                typeCaption: panel.typeCaption
                weightBold: panel.weightBold
                weightMedium: panel.weightMedium
            }

            ControlTowerHeroMetricStrip {
                metricId: "sessions"
                iconSource: workspaceRoot.solidIcon("sidebar-chat-solid")
                valueText: String(panel.sessionsMetricValue)
                labelText: panel.sessionsMetricLabel
                isDark: panel.isDark
                textPrimary: panel.textPrimary
                textSecondary: panel.textSecondary
                typeTitle: panel.metricValuePixelSize
                typeCaption: panel.typeCaption
                weightBold: panel.weightBold
                weightMedium: panel.weightMedium
            }

            ControlTowerHeroMetricStrip {
                metricId: "working"
                iconSource: workspaceRoot.solidIcon("sidebar-monitor-solid")
                valueText: String(panel.workingMetricValue)
                labelText: panel.workingMetricLabel
                isDark: panel.isDark
                textPrimary: panel.textPrimary
                textSecondary: panel.textSecondary
                typeTitle: panel.metricValuePixelSize
                typeCaption: panel.typeCaption
                weightBold: panel.weightBold
                weightMedium: panel.weightMedium
            }

            ControlTowerHeroMetricStrip {
                metricId: "automation"
                iconSource: workspaceRoot.solidIcon("sidebar-cron-solid")
                valueText: String(panel.automationMetricValue)
                labelText: panel.automationMetricLabel
                isDark: panel.isDark
                textPrimary: panel.textPrimary
                textSecondary: panel.textSecondary
                typeTitle: panel.metricValuePixelSize
                typeCaption: panel.typeCaption
                weightBold: panel.weightBold
                weightMedium: panel.weightMedium
            }
        }
    }
}
