import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

AppModal {
    id: root

    required property var rootView

    z: 23
    darkMode: isDark
    title: strings.update_modal_title
    showDefaultCloseAction: false
    maxModalWidth: 460
    maxModalHeight: 520

    Text {
        width: parent.width
        text: strings.update_latest_version + " " + (rootView.updateService ? rootView.updateService.latestVersion : "")
        color: textSecondary
        font.pixelSize: typeBody
        wrapMode: Text.WordWrap
        visible: rootView.updateService !== null && !!rootView.updateService.latestVersion
    }

    Text {
        width: parent.width
        text: rootView.updateService ? rootView.updateService.notesMarkdown : ""
        color: textSecondary
        font.pixelSize: typeMeta
        wrapMode: Text.WordWrap
        visible: rootView.updateService !== null && !!rootView.updateService.notesMarkdown
    }

    footer: [
        Item { Layout.fillWidth: true },
        Rectangle {
            implicitWidth: laterLabel.implicitWidth + 28
            implicitHeight: 38
            radius: 19
            color: dialogLater.containsMouse ? bgCardHover : "transparent"
            border.width: 1
            border.color: borderSubtle

            Text { id: laterLabel; anchors.centerIn: parent; text: strings.update_modal_later; color: textSecondary; font.pixelSize: typeLabel; font.weight: Font.Medium }

            MouseArea { id: dialogLater; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.close() }
        },
        Rectangle {
            implicitWidth: installLabel.implicitWidth + 28
            implicitHeight: 38
            radius: 19
            color: dialogInstall.containsMouse ? accentHover : accent

            Text { id: installLabel; anchors.centerIn: parent; text: strings.update_modal_install; color: "#FFFFFFFF"; font.pixelSize: typeLabel; font.weight: Font.DemiBold }

            MouseArea {
                id: dialogInstall
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                    root.close()
                    if (rootView.updateBridge)
                        rootView.updateBridge.installRequested()
                }
            }
        }
    ]
}
