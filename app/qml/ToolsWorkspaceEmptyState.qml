import QtQuick 2.15

Column {
    id: root

    property var workspace
    property string title: ""
    property string description: ""
    property string titleObjectName: ""
    property string descriptionObjectName: ""

    readonly property color textPrimary: workspace ? workspace.textPrimary : "transparent"
    readonly property color textSecondary: workspace ? workspace.textSecondary : "transparent"
    readonly property int typeBody: workspace ? workspace.typeBody : 14
    readonly property int typeMeta: workspace ? workspace.typeMeta : 12
    readonly property int weightBold: workspace ? workspace.weightBold : Font.Normal

    width: Math.min(parent.width - 40, 280)
    spacing: 10

    Text {
        objectName: root.titleObjectName
        width: parent.width
        text: root.title
        color: root.textPrimary
        font.pixelSize: root.typeBody
        font.weight: root.weightBold
        horizontalAlignment: Text.AlignHCenter
    }

    Text {
        objectName: root.descriptionObjectName
        width: parent.width
        text: root.description
        color: root.textSecondary
        font.pixelSize: root.typeMeta
        wrapMode: Text.WordWrap
        horizontalAlignment: Text.AlignHCenter
    }
}
