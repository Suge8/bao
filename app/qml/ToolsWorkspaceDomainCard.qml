import QtQuick 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root

    property var workspace
    property string title: ""
    property string summary: ""
    property string detail: ""
    property bool active: false
    property bool locked: false

    readonly property bool isDark: workspace ? workspace.isDark : false
    readonly property color fillBase: active
        ? (isDark ? "#1B1712" : "#FFF5EA")
        : (isDark ? "#130F0C" : "#FBF7F2")
    readonly property color outlineBase: active ? root.accent : root.borderSubtle
    readonly property color hoverFill: active
        ? (isDark ? "#231D16" : "#FFF0DF")
        : root.bgCardHover
    readonly property color hoverOutline: active ? root.accentHover : root.borderDefault
    readonly property color currentFill: domainMouse.containsMouse && !locked ? hoverFill : fillBase
    readonly property color currentOutline: domainMouse.containsMouse && !locked ? hoverOutline : outlineBase
    readonly property color accent: workspace ? workspace.accent : "transparent"
    readonly property color accentHover: workspace ? workspace.accentHover : "transparent"
    readonly property color accentMuted: workspace ? workspace.accentMuted : "transparent"
    readonly property color bgCardHover: workspace ? workspace.bgCardHover : "transparent"
    readonly property color borderSubtle: workspace ? workspace.borderSubtle : "transparent"
    readonly property color borderDefault: workspace ? workspace.borderDefault : "transparent"
    readonly property color textPrimary: workspace ? workspace.textPrimary : "transparent"
    readonly property color textSecondary: workspace ? workspace.textSecondary : "transparent"
    readonly property int typeBody: workspace ? workspace.typeBody : 14
    readonly property int typeMeta: workspace ? workspace.typeMeta : 12
    readonly property int typeCaption: workspace ? workspace.typeCaption : 11
    readonly property int weightBold: workspace ? workspace.weightBold : Font.Normal
    readonly property int weightMedium: workspace ? workspace.weightMedium : Font.Normal

    signal pressed()

    Layout.fillWidth: true
    radius: 18
    color: currentFill
    border.width: 1
    border.color: currentOutline
    implicitHeight: contentColumn.implicitHeight + 24

    MouseArea {
        id: domainMouse
        anchors.fill: parent
        hoverEnabled: true
        enabled: !root.locked
        cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
        onClicked: root.pressed()
    }

    ColumnLayout {
        id: contentColumn
        anchors.fill: parent
        anchors.margins: 12
        spacing: 8

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Text {
                Layout.fillWidth: true
                text: root.title
                color: root.textPrimary
                font.pixelSize: root.typeBody
                font.weight: root.weightBold
                wrapMode: Text.WordWrap
            }

            ToolsWorkspaceBadge {
                workspace: root.workspace
                text: root.locked
                    ? root.workspace.tr("始终开启", "Always on")
                    : (root.active ? root.workspace.tr("已纳入", "Included") : root.workspace.tr("未纳入", "Excluded"))
                tone: root.locked ? "#60A5FA" : (root.active ? root.accent : root.textSecondary)
                prominent: root.active || root.locked
            }
        }

        Text {
            Layout.fillWidth: true
            text: root.summary
            color: root.textSecondary
            font.pixelSize: root.typeMeta
            wrapMode: Text.WordWrap
        }

        Text {
            Layout.fillWidth: true
            text: root.detail
            color: root.active ? root.textPrimary : root.textSecondary
            font.pixelSize: root.typeCaption
            font.weight: root.weightMedium
            wrapMode: Text.WordWrap
            visible: text.length > 0
        }
    }
}
