import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

AppModal {
    id: root

    required property var appRoot
    required property var toastTarget

    objectName: "diagnosticsModal"
    title: appRoot.strings.diagnostics_title
    closeText: appRoot.strings.diagnostics_close
    maxModalWidth: 920
    maxModalHeight: 760
    darkMode: appRoot.isDark
    bodyScrollable: false
    showDefaultCloseAction: false

    onOpened: {
        if (appRoot.diagnosticsService)
            appRoot.diagnosticsService.refresh()
    }

    Item {
        width: parent.width
        height: root.height - 92

        ColumnLayout {
            anchors.fill: parent
            spacing: 16

            RowLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: 134
                spacing: 16

                MainDiagnosticsHubCard {
                    appRoot: root.appRoot
                }

                MainDiagnosticsLogFileCard {
                    appRoot: root.appRoot
                }
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 16

                MainDiagnosticsEventsCard {
                    appRoot: root.appRoot
                    toastTarget: root.toastTarget
                    modalTarget: root
                }

                MainDiagnosticsLogTailCard {
                    appRoot: root.appRoot
                    toastTarget: root.toastTarget
                }
            }
        }
    }
}
