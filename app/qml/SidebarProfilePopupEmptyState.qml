import QtQuick 2.15

Rectangle {
    id: root

    required property var sidebarRoot

    radius: 18
    color: sidebarRoot.isDark ? "#181210" : "#FFF8F1"
    border.width: 1
    border.color: sidebarRoot.isDark ? "#31241E" : "#E9D8C5"
    implicitHeight: emptyStateColumn.implicitHeight + 20
    height: visible ? implicitHeight : 0

    Column {
        id: emptyStateColumn
        anchors.fill: parent
        anchors.margins: 10
        spacing: 4

        Text {
            text: sidebarRoot.strings.profile_empty_title
            color: sidebarRoot.textPrimary
            font.pixelSize: sidebarRoot.typeBody
            font.weight: sidebarRoot.weightDemiBold
        }

        Text {
            width: parent.width
            text: sidebarRoot.strings.profile_empty_hint
            color: sidebarRoot.textSecondary
            font.pixelSize: sidebarRoot.typeCaption + 1
            font.weight: sidebarRoot.weightMedium
            wrapMode: Text.WordWrap
        }
    }
}
