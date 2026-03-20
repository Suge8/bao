import QtQuick 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root

    property var workspace
    property string iconSource: ""
    property string modeKey: ""
    property string title: ""
    property string summary: ""
    property string detail: ""
    property bool selected: false
    property bool hovered: hoverArea.containsMouse

    signal pressed()

    objectName: modeKey.length > 0 ? "execModeCard-" + modeKey : ""

    readonly property color idleFill: workspace && workspace.isDark ? "#15110D" : "#FFF9F2"
    readonly property color hoverFill: workspace && workspace.isDark ? "#19130F" : "#FFF5EA"
    readonly property color activeFill: workspace && workspace.isDark ? "#2A180F" : "#FFF1E4"
    readonly property color idleBorder: workspace && workspace.isDark ? "#18FFFFFF" : "#12000000"
    readonly property color hoverBorder: workspace && workspace.isDark ? "#30FFFFFF" : "#22000000"
    readonly property color activeBorder: workspace ? workspace.accent : "#F97316"
    readonly property color currentFill: selected ? activeFill : (hovered ? hoverFill : idleFill)
    readonly property color currentBorder: selected ? activeBorder : (hovered ? hoverBorder : idleBorder)
    readonly property real currentScale: selected ? 1.0 : (hovered ? 0.992 : 0.985)

    Layout.fillWidth: true
    implicitHeight: 104
    radius: 18
    color: currentFill
    border.width: selected ? 1.5 : 1
    border.color: currentBorder
    scale: currentScale
    transformOrigin: Item.Center

    Behavior on color { ColorAnimation { duration: 150 } }
    Behavior on border.color { ColorAnimation { duration: 150 } }
    Behavior on scale { NumberAnimation { duration: 140; easing.type: Easing.OutCubic } }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 14
        spacing: 6

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Rectangle {
                visible: root.iconSource.length > 0
                width: visible ? 24 : 0
                height: 24
                radius: 12
                color: selected
                    ? (workspace && workspace.isDark ? "#24FFFFFF" : "#FFF4E8")
                    : (workspace && workspace.isDark ? "#18FFFFFF" : "#FFFDFC")
                border.width: 1
                border.color: selected ? root.currentBorder : (workspace && workspace.isDark ? "#20FFFFFF" : "#14000000")

                Image {
                    anchors.centerIn: parent
                    width: 14
                    height: 14
                    source: root.iconSource
                    fillMode: Image.PreserveAspectFit
                    smooth: true
                    mipmap: false
                    opacity: 0.92
                }
            }

            Text {
                Layout.fillWidth: true
                text: root.title
                color: workspace ? workspace.textPrimary : "transparent"
                font.pixelSize: workspace ? workspace.typeBody : 14
                font.weight: workspace ? workspace.weightBold : Font.Normal
                elide: Text.ElideRight
            }

            Rectangle {
                width: 9
                height: 9
                radius: 4.5
                color: selected ? (workspace ? workspace.accent : "#F97316") : "transparent"
                border.width: selected ? 0 : 1
                border.color: workspace && workspace.isDark ? "#26FFFFFF" : "#22000000"
            }
        }

        Text {
            Layout.fillWidth: true
            text: root.summary
            color: workspace ? workspace.textPrimary : "transparent"
            font.pixelSize: workspace ? workspace.typeBody : 14
            maximumLineCount: 2
            wrapMode: Text.WordWrap
        }

        Text {
            Layout.fillWidth: true
            text: root.detail
            color: workspace ? workspace.textSecondary : "transparent"
            font.pixelSize: workspace ? workspace.typeMeta : 12
            maximumLineCount: 2
            wrapMode: Text.WordWrap
        }
    }

    MouseArea {
        id: hoverArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.pressed()
    }
}
