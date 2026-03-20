import QtQuick 2.15

Item {
    id: root

    implicitWidth: 10
    implicitHeight: 10
    property color markerColor: typeof isDark !== "undefined" && isDark ? "#18FFFFFF" : "#16000000"
    property int markerWidth: 2
    property int markerHeight: 4
    property int markerSpacing: 6
    readonly property int markerStep: markerHeight + markerSpacing
    readonly property real availableHeight: Math.max(markerHeight, height)
    readonly property int markerCount: Math.max(1, Math.floor((availableHeight + markerSpacing) / markerStep))

    Column {
        id: markerColumn
        objectName: "workspaceSplitHandleMarkerColumn"
        anchors.centerIn: parent
        spacing: root.markerSpacing

        Repeater {
            model: root.markerCount

            delegate: Rectangle {
                width: root.markerWidth
                height: root.markerHeight
                radius: 1
                color: root.markerColor
            }
        }
    }
}
