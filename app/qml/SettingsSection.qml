import QtQuick 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    property string title: ""
    property string description: ""
    property string actionText: ""
    property bool actionEnabled: true
    property var actionHandler: null
    property bool helpVisible: false
    property var helpHandler: null
    property bool helpEmphasis: false
    property bool spotlight: false
    default property alias content: contentArea.data

    Layout.fillWidth: true
    implicitHeight: headerRow.implicitHeight + contentArea.implicitHeight + 68
    radius: radiusLg
    color: root.spotlight ? (isDark ? "#201E140F" : "#FFFDF9") : bgCard

    border.color: root.spotlight ? accent : borderSubtle
    border.width: root.spotlight ? 1.3 : 1

    Behavior on color { ColorAnimation { duration: motionUi; easing.type: easeStandard } }
    Behavior on border.color { ColorAnimation { duration: motionUi; easing.type: easeStandard } }
    Behavior on border.width { NumberAnimation { duration: motionUi; easing.type: easeStandard } }

    ColumnLayout {
        anchors { fill: parent; margins: 24 }
        spacing: 20

        RowLayout {
            id: headerRow
            Layout.fillWidth: true
            spacing: 16

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6

                Text {
                    id: titleText
                    text: root.title
                    color: root.spotlight ? accent : textPrimary
                    font.pixelSize: 15
                    font.weight: Font.DemiBold
                    font.letterSpacing: 0.3
                }

                Text {
                    visible: root.description !== ""
                    text: root.description
                    color: textTertiary
                    font.pixelSize: 12
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
            }

            RowLayout {
                spacing: 8

                IconCircleButton {
                    visible: root.helpVisible
                    buttonSize: 30
                    glyphText: "?"
                    glyphSize: typeButton
                    emphasized: root.helpEmphasis
                    fillColor: root.helpEmphasis ? accent : "transparent"
                    hoverFillColor: root.helpEmphasis ? accentHover : bgCardHover
                    outlineColor: root.helpEmphasis ? accent : borderSubtle
                    glyphColor: root.helpEmphasis ? "#FFFFFFFF" : textSecondary
                    onClicked: if (root.helpHandler) root.helpHandler()
                }

                PillActionButton {
                    visible: root.actionText !== ""
                    text: root.actionText
                    buttonEnabled: root.actionEnabled
                    minHeight: 30
                    horizontalPadding: 20
                    onClicked: if (root.actionHandler) root.actionHandler()
                }
            }
        }

        Item {
            id: contentArea
            Layout.fillWidth: true
            implicitHeight: childrenRect.height
        }
    }
}
