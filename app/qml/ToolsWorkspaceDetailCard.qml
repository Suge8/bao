import QtQuick 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root

    default property alias contentData: contentColumn.data
    property var workspace
    property color fillColor: workspace && workspace.isDark ? "#130F0C" : "#FBF7F2"

    Layout.fillWidth: true
    radius: 20
    color: fillColor
    border.width: 1
    border.color: workspace && workspace.isDark ? "#12FFFFFF" : "#10000000"
    implicitHeight: contentColumn.implicitHeight + 28

    ColumnLayout {
        id: contentColumn
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 14
        spacing: 12
    }
}
