import QtQuick 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root

    default property alias contentData: contentColumn.data
    property var workspace

    Layout.fillWidth: true
    radius: 18
    color: workspace.sectionFill
    border.width: 1
    border.color: workspace.panelBorder
    implicitHeight: contentColumn.implicitHeight + 28

    ColumnLayout {
        id: contentColumn
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 14
        spacing: 10
    }
}
