import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    property string title: ""
    property bool expanded: false
    default property alias content: contentArea.content

    Layout.fillWidth: true
    clip: true
    implicitHeight: header.height + contentArea.implicitHeight

    Column {
        id: col
        width: parent.width
        spacing: 0

        // Header row — clickable to toggle
        ExpandHeader {
            id: header
            width: parent.width
            headerHeight: 36
            title: root.title
            expanded: root.expanded
            titleColor: textSecondary
            titlePixelSize: typeLabel
            titleWeight: weightMedium
            onClicked: root.expanded = !root.expanded
        }

        // Content area — only visible when expanded
        ExpandReveal {
            id: contentArea
            width: parent.width
            expanded: root.expanded
            bottomPadding: spacingSm
            slideAxis: Qt.Vertical
            slideSign: 1
            slideDistance: 12
        }
    }
}
