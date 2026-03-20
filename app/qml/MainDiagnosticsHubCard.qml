import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root

    required property var appRoot

    objectName: "diagnosticsHubCard"
    Layout.fillWidth: true
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
                    source: appRoot.diagnosticsSectionIcon("hub")
                    sourceSize: Qt.size(24, 24)
                }
            }

            Text {
                text: appRoot.strings.diagnostics_hub_title
                color: appRoot.design.textSecondary
                font.pixelSize: appRoot.design.typeMeta
                font.weight: appRoot.design.weightBold
            }

            Item { Layout.fillWidth: true }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            color: appRoot.design.borderSubtle
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            AppIcon {
                Layout.alignment: Qt.AlignTop
                source: appRoot.diagnosticsHubIcon()
                sourceSize: Qt.size(28, 28)
                Layout.preferredWidth: 28
                Layout.preferredHeight: 28
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 0

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Text {
                        text: appRoot.diagnosticsHubLabel()
                        color: appRoot.design.textPrimary
                        font.pixelSize: appRoot.design.typeBody + 2
                        font.weight: appRoot.design.weightBold
                    }

                    Rectangle {
                        Layout.alignment: Qt.AlignVCenter
                        Layout.preferredWidth: 8
                        Layout.preferredHeight: 8
                        radius: 4
                        color: appRoot.diagnosticsHubBadgeColor()
                    }

                    Item { Layout.fillWidth: true }

                    Text {
                        visible: appRoot.diagnosticsObservabilitySummary() !== ""
                        text: appRoot.diagnosticsObservabilitySummary()
                        color: appRoot.design.textSecondary
                        font.pixelSize: appRoot.design.typeMeta - 1
                        elide: Text.ElideRight
                        Layout.preferredWidth: 250
                    }
                }
            }
        }
    }
}
