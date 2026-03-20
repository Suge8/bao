import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Flickable {
    id: root

    default property alias contentData: contentColumn.data
    property var workspace

    readonly property bool isDark: workspace ? workspace.isDark : false
    readonly property color textPrimary: workspace ? workspace.textPrimary : "transparent"
    readonly property color textSecondary: workspace ? workspace.textSecondary : "transparent"
    readonly property color accent: workspace ? workspace.accent : "transparent"
    readonly property color accentHover: workspace ? workspace.accentHover : "transparent"
    readonly property color accentMuted: workspace ? workspace.accentMuted : "transparent"
    readonly property color bgCardHover: workspace ? workspace.bgCardHover : "transparent"
    readonly property color borderSubtle: workspace ? workspace.borderSubtle : "transparent"
    readonly property color borderDefault: workspace ? workspace.borderDefault : "transparent"
    readonly property color statusError: workspace ? workspace.statusError : "transparent"
    readonly property real letterWide: workspace ? workspace.letterWide : 0
    readonly property int typeTitle: workspace ? workspace.typeTitle : 18
    readonly property int typeLabel: workspace ? workspace.typeLabel : 14
    readonly property int typeBody: workspace ? workspace.typeBody : 14
    readonly property int typeMeta: workspace ? workspace.typeMeta : 12
    readonly property int typeCaption: workspace ? workspace.typeCaption : 12
    readonly property int weightBold: workspace ? workspace.weightBold : Font.Normal

    contentWidth: width
    contentHeight: contentColumn.implicitHeight
    clip: true
    ScrollIndicator.vertical: ScrollIndicator {
        visible: false
        width: 4
        contentItem: Rectangle {
            implicitWidth: 2
            radius: 1
            color: root.isDark ? "#28FFFFFF" : "#22000000"
        }
    }

    ColumnLayout {
        id: contentColumn
        width: parent.width
        spacing: 14
    }
}
