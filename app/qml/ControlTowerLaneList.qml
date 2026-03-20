import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ListView {
    id: laneList

    property var workspaceRoot: null
    property string sectionKind: ""
    property var sectionModel: null
    property bool isDark: false
    property color textPrimary: "transparent"
    property color textSecondary: "transparent"
    property color textTertiary: "transparent"
    property color tileActive: "transparent"
    property color tileHover: "transparent"
    property real motionFast: 0
    property int easeStandard: 0
    property int typeMeta: 12
    property int typeLabel: 14
    property int typeCaption: 11
    property int weightBold: Font.Bold
    property int weightMedium: Font.Medium
    readonly property int laneItemHeight: 76
    readonly property int laneListSpacing: 10
    readonly property int laneListCacheItems: 5
    readonly property int laneListCacheBuffer: (laneItemHeight + laneListSpacing) * laneListCacheItems

    objectName: "controlTowerLaneList_" + sectionKind
    implicitHeight: Math.max(laneItemHeight, Math.min(contentHeight, 360))
    height: implicitHeight
    clip: true
    spacing: laneListSpacing
    reuseItems: true
    cacheBuffer: laneListCacheBuffer
    model: sectionModel
    ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

    delegate: Rectangle {
        required property var modelData
        readonly property bool itemCanOpen: Boolean(modelData.canOpen)
        readonly property string itemAccentKey: String(modelData.accentKey || modelData.visualChannel || "system")
        readonly property color itemAccentColor: workspaceRoot.accentColor(itemAccentKey)
        objectName: "laneItemCard_" + String(modelData.id || "")
        width: ListView.view ? ListView.view.width : 0
        implicitHeight: laneList.laneItemHeight
        height: implicitHeight
        radius: 16
        color: laneItemMouse.containsMouse && itemCanOpen ? tileActive : tileHover
        border.width: 1
        border.color: itemCanOpen
                      ? Qt.rgba(itemAccentColor.r,
                                itemAccentColor.g,
                                itemAccentColor.b,
                                isDark ? 0.28 : 0.18)
                      : (isDark ? "#14FFFFFF" : "#12000000")

        Behavior on color { ColorAnimation { duration: motionFast; easing.type: easeStandard } }
        Behavior on border.color { ColorAnimation { duration: motionFast; easing.type: easeStandard } }

        GridLayout {
            anchors.fill: parent
            anchors.margins: 12
            columns: 3
            rows: 2
            columnSpacing: 8
            rowSpacing: 0

            WorkerToken {
                Layout.row: 0
                Layout.column: 0
                Layout.rowSpan: 2
                Layout.alignment: Qt.AlignTop
                avatarSource: String(modelData.avatarSource || "")
                variant: "mini"
                ringColor: itemAccentColor
                glyphSources: workspaceRoot.itemGlyphSources(modelData)
                glyphSource: String(modelData.glyphSource || "")
                statusKey: String(modelData.statusKey || "idle")
                active: laneItemMouse.containsMouse && itemCanOpen
            }

            Text {
                Layout.row: 0
                Layout.column: 1
                Layout.fillWidth: true
                text: String(modelData.title || "")
                color: textPrimary
                font.pixelSize: typeMeta
                font.weight: weightBold
                elide: Text.ElideRight
                verticalAlignment: Text.AlignBottom
            }

            ControlTowerInfoChip {
                Layout.row: 0
                Layout.column: 2
                Layout.alignment: Qt.AlignTop | Qt.AlignRight
                chipId: String(modelData.id || "") + "_status"
                labelText: String(modelData.statusLabel || "")
                isDark: laneList.isDark
                fillColor: laneList.isDark ? "#18120E" : "#FFF5EA"
                borderColor: itemAccentColor
                textColor: laneList.textSecondary
                fontPixelSize: laneList.typeCaption
                fontWeight: laneList.weightMedium
                horizontalPadding: 12
                minHeight: 20
            }

            Text {
                Layout.row: 1
                Layout.column: 1
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop
                text: String(modelData.summary || "")
                color: textSecondary
                font.pixelSize: typeMeta
                font.weight: weightMedium
                elide: Text.ElideRight
            }

            Text {
                Layout.row: 1
                Layout.column: 2
                Layout.alignment: Qt.AlignTop | Qt.AlignRight
                text: workspaceRoot.itemTimeLabel(modelData)
                visible: text !== ""
                color: textTertiary
                font.pixelSize: typeMeta
                font.weight: weightMedium
                elide: Text.ElideRight
                horizontalAlignment: Text.AlignRight
            }
        }

        MouseArea {
            id: laneItemMouse
            anchors.fill: parent
            hoverEnabled: true
            enabled: itemCanOpen
            cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
            onClicked: workspaceRoot.openItem(modelData)
        }
    }
}
