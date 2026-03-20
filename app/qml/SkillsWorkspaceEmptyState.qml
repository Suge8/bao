pragma ComponentBehavior: Bound

import QtQuick 2.15

Item {
    id: root

    property string title: ""
    property string description: ""

    Column {
        anchors.centerIn: parent
        width: Math.min(parent.width - 40, 280)
        spacing: 10
        visible: parent.height > 0

        Text {
            width: parent.width
            text: root.title
            color: textPrimary
            font.pixelSize: typeBody
            font.weight: weightBold
            horizontalAlignment: Text.AlignHCenter
        }

        Text {
            width: parent.width
            text: root.description
            color: textSecondary
            font.pixelSize: typeMeta
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
        }
    }
}
