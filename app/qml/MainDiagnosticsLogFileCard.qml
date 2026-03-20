import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root

    required property var appRoot

    objectName: "diagnosticsLogFileCard"
    Layout.preferredWidth: 340
    Layout.preferredHeight: 134
    radius: 16
    color: appRoot.isDark ? "#15110F" : "#FBF7F2"
    border.width: 1
    border.color: appRoot.design.borderSubtle

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Rectangle {
                Layout.preferredWidth: 30
                Layout.preferredHeight: 30
                radius: 10
                color: appRoot.isDark ? "#1F1814" : "#F1E8DF"

                AppIcon {
                    width: 24
                    height: 24
                    anchors.centerIn: parent
                    source: appRoot.diagnosticsSectionIcon("file")
                    sourceSize: Qt.size(24, 24)
                }
            }

            Text {
                text: appRoot.strings.diagnostics_log_file
                color: appRoot.design.textSecondary
                font.pixelSize: appRoot.design.typeMeta
                font.weight: appRoot.design.weightBold
            }

            Item { Layout.fillWidth: true }

            PillActionButton {
                text: appRoot.strings.diagnostics_refresh
                minHeight: 26
                horizontalPadding: 14
                fillColor: appRoot.design.accentGlow
                hoverFillColor: appRoot.design.accent
                outlineColor: appRoot.design.accent
                hoverOutlineColor: appRoot.design.accent
                textColor: appRoot.isDark ? appRoot.design.bgSidebar : "#FFFFFF"
                onClicked: if (appRoot.diagnosticsService) appRoot.diagnosticsService.refresh()
            }

            PillActionButton {
                text: appRoot.strings.diagnostics_open_folder
                minHeight: 26
                horizontalPadding: 14
                fillColor: appRoot.isDark ? "#1D1611" : "#FFF4E8"
                hoverFillColor: appRoot.isDark ? "#251B14" : "#FFECD8"
                outlineColor: appRoot.design.borderSubtle
                hoverOutlineColor: appRoot.design.accent
                textColor: appRoot.design.textPrimary
                outlined: true
                onClicked: if (appRoot.diagnosticsService) appRoot.diagnosticsService.openLogDirectory()
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            color: appRoot.design.borderSubtle
        }

        Text {
            Layout.fillWidth: true
            text: appRoot.diagnosticsLogFilePathSafe()
            color: appRoot.design.textPrimary
            wrapMode: Text.WrapAnywhere
            font.pixelSize: appRoot.design.typeMeta + 1
            font.family: Qt.platform.os === "osx" ? "Menlo" : "Monospace"
        }
    }
}
