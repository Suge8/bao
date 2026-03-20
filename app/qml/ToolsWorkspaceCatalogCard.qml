import QtQuick 2.15
import QtQuick.Layouts 1.15
import "ToolsWorkspaceLogic.js" as ToolsWorkspaceLogic

Item {
    id: root

    property var workspace
    property var itemData
    property bool selected: false
    property bool serverMode: false
    signal clicked()

    readonly property bool isDark: workspace ? workspace.isDark : false
    readonly property color accent: workspace ? workspace.accent : "transparent"
    readonly property color bgCardHover: workspace ? workspace.bgCardHover : "transparent"
    readonly property color borderSubtle: workspace ? workspace.borderSubtle : "transparent"
    readonly property color textPrimary: workspace ? workspace.textPrimary : "transparent"
    readonly property color textSecondary: workspace ? workspace.textSecondary : "transparent"
    readonly property int typeBody: workspace ? workspace.typeBody : 14
    readonly property int typeMeta: workspace ? workspace.typeMeta : 12
    readonly property int typeLabel: workspace ? workspace.typeLabel : 14
    readonly property int typeCaption: workspace ? workspace.typeCaption : 12
    readonly property int weightBold: workspace ? workspace.weightBold : Font.Normal
    readonly property int motionFast: workspace ? workspace.motionFast : 120
    readonly property int easeStandard: workspace ? workspace.easeStandard : Easing.OutCubic

    width: ListView.view ? ListView.view.width : 0
    implicitHeight: 120

    function titleText() {
        return serverMode ? String(itemData.name || "") : workspace.itemDisplayName(itemData)
    }

    function summaryText() {
        return serverMode ? workspace.statusDetail(itemData) : workspace.itemDisplaySummary(itemData)
    }

    Rectangle {
        anchors.fill: parent
        radius: 22
        color: cardArea.containsMouse
            ? (root.selected ? (root.isDark ? "#241914" : "#FFF1E2") : root.bgCardHover)
            : (root.selected ? (root.isDark ? "#201612" : "#FFF7F0") : (root.isDark ? "#17120F" : "#FFFFFF"))
        border.width: root.selected ? 1.5 : 1
        border.color: root.selected ? root.accent : (root.isDark ? "#14FFFFFF" : "#10000000")

        Behavior on color { ColorAnimation { duration: root.motionFast; easing.type: root.easeStandard } }
        Behavior on border.color { ColorAnimation { duration: root.motionFast; easing.type: root.easeStandard } }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 12
            anchors.bottomMargin: 16
            spacing: 8

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Rectangle {
                    Layout.alignment: Qt.AlignTop
                    implicitWidth: 36
                    implicitHeight: 36
                    Layout.preferredWidth: implicitWidth
                    Layout.preferredHeight: implicitHeight
                    radius: 12
                    color: ToolsWorkspaceLogic.itemIconBackdrop(root, root.itemData)
                    border.width: root.selected ? 1 : 0
                    border.color: root.selected ? root.accent : "transparent"

                    AppIcon {
                        anchors.centerIn: parent
                        width: 18
                        height: 18
                        source: root.serverMode ? root.workspace.icon("database-settings") : root.workspace.itemIconSource(root.itemData)
                        sourceSize: Qt.size(width, height)
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2

                    Text {
                        Layout.fillWidth: true
                        text: root.titleText()
                        color: root.textPrimary
                        font.pixelSize: root.typeBody
                        font.weight: root.weightBold
                        elide: Text.ElideRight
                    }

                    Text {
                        Layout.fillWidth: true
                        text: root.summaryText()
                        color: root.isDark ? root.textSecondary : "#5A4537"
                        font.pixelSize: root.typeMeta
                        wrapMode: Text.WordWrap
                        maximumLineCount: 2
                        elide: Text.ElideRight
                    }
                }

                IconCircleButton {
                    buttonSize: 30
                    glyphText: "→"
                    glyphSize: root.typeLabel
                    fillColor: "transparent"
                    hoverFillColor: root.bgCardHover
                    outlineColor: root.selected ? root.accent : root.borderSubtle
                    glyphColor: root.selected ? root.accent : root.textSecondary
                    onClicked: root.clicked()
                }
            }

            Row {
                Layout.fillWidth: true
                spacing: 8
                clip: true

                Repeater {
                    model: ToolsWorkspaceLogic.listBadges(root.workspace, root.itemData)

                    delegate: ToolsWorkspaceBadge {
                        required property var modelData
                        workspace: root.workspace
                        text: modelData.text
                        tone: modelData.tone
                        prominent: true
                    }
                }
            }
        }

        MouseArea {
            id: cardArea
            anchors.fill: parent
            hoverEnabled: true
            acceptedButtons: Qt.LeftButton
            cursorShape: Qt.PointingHandCursor
            onClicked: root.clicked()
        }
    }
}
