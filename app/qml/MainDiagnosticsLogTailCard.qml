import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root

    required property var appRoot
    required property var toastTarget

    objectName: "diagnosticsLogTailCard"
    Layout.fillWidth: true
    Layout.fillHeight: true
    radius: 16
    color: appRoot.isDark ? "#15110E" : "#FBF7F2"
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
                    source: appRoot.diagnosticsSectionIcon("logtail")
                    sourceSize: Qt.size(24, 24)
                }
            }

            Text {
                Layout.fillWidth: true
                text: appRoot.strings.diagnostics_log_tail
                color: appRoot.design.textPrimary
                font.pixelSize: appRoot.design.typeBody + 1
                font.weight: appRoot.design.weightBold
            }

            PillActionButton {
                text: appRoot.strings.diagnostics_copy_tail
                minHeight: 26
                horizontalPadding: 14
                fillColor: appRoot.isDark ? "#1D1611" : "#FFF4E8"
                hoverFillColor: appRoot.isDark ? "#251B14" : "#FFECD8"
                outlineColor: appRoot.design.borderSubtle
                hoverOutlineColor: appRoot.design.accent
                textColor: appRoot.design.textPrimary
                outlined: true
                onClicked: {
                    appRoot.copyPlainText(appRoot.diagnosticsRecentLogTextSafe())
                    toastTarget.show(appRoot.strings.copied_ok, true)
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            color: appRoot.design.borderSubtle
        }

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            Column {
                anchors.centerIn: parent
                spacing: 10
                visible: !appRoot.diagnosticsRecentLogTextSafe()

                Rectangle {
                    width: 40
                    height: 40
                    radius: 14
                    anchors.horizontalCenter: parent.horizontalCenter
                    color: appRoot.isDark ? "#1F1814" : "#F1E8DF"

                    AppIcon {
                        width: 24
                        height: 24
                        anchors.centerIn: parent
                        source: appRoot.diagnosticsSectionIcon("logtail")
                        sourceSize: Qt.size(24, 24)
                    }
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: appRoot.strings.diagnostics_empty_logs
                    color: appRoot.design.textSecondary
                    wrapMode: Text.WordWrap
                    horizontalAlignment: Text.AlignHCenter
                    font.pixelSize: appRoot.design.typeMeta + 1
                }
            }

            FollowTailLogView {
                id: diagnosticsLogTailView
                objectName: "diagnosticsLogTailScroll"
                anchors.fill: parent
                visible: !!appRoot.diagnosticsRecentLogTextSafe()
                text: appRoot.diagnosticsRecentLogTextSafe()
                textColor: appRoot.design.textPrimary
                fontPixelSize: appRoot.design.typeMeta
                fontFamily: Qt.platform.os === "osx" ? "Menlo" : "Monospace"
            }
        }
    }
}
