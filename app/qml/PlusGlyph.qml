import QtQuick 2.15

Item {
    id: root

    property color glyphColor: "white"
    property real glyphSize: 16
    property real barLength: glyphSize * 0.75
    property real barThickness: Math.max(1.8, glyphSize * 0.15)

    width: glyphSize
    height: glyphSize

    Rectangle {
        width: root.barLength
        height: root.barThickness
        radius: height / 2
        anchors.centerIn: parent
        color: root.glyphColor
    }

    Rectangle {
        width: root.barThickness
        height: root.barLength
        radius: width / 2
        anchors.centerIn: parent
        color: root.glyphColor
    }
}
