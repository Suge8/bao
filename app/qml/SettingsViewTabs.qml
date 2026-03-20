import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root

    required property var rootView

    visible: !rootView.onboardingMode
    Layout.fillWidth: true
    implicitHeight: 46
    radius: 23
    color: isDark ? "#12FFFFFF" : "#08000000"
    border.color: borderSubtle
    border.width: 1

    readonly property real tabSpacing: 6
    readonly property real trackPadding: 6
    readonly property real segmentWidth: (
        width - (trackPadding * 2) - (tabSpacing * (rootView._tabLabels.length - 1))
    ) / rootView._tabLabels.length

    Rectangle {
        id: tabHighlight
        y: 6
        height: parent.height - 12
        width: parent.segmentWidth
        x: 6 + (parent.segmentWidth + parent.tabSpacing) * rootView._activeTab
        radius: height / 2
        color: accent

        Behavior on x { NumberAnimation { duration: 220; easing.type: easeEmphasis } }
        Behavior on width { NumberAnimation { duration: 220; easing.type: easeStandard } }
    }

    RowLayout {
        anchors.fill: parent
        anchors.margins: 6
        spacing: parent.tabSpacing

        Repeater {
            model: rootView._tabLabels

            delegate: Rectangle {
                required property int index
                required property var modelData

                Layout.fillWidth: true
                Layout.fillHeight: true
                color: tabHover.containsMouse && rootView._activeTab !== index
                       ? (isDark ? "#10FFFFFF" : "#08000000")
                       : "transparent"
                radius: 17

                Behavior on color { ColorAnimation { duration: motionFast; easing.type: easeStandard } }

                Text {
                    anchors.centerIn: parent
                    text: modelData.label
                    color: rootView._activeTab === index ? "#FFFFFFFF" : textSecondary
                    font.pixelSize: typeLabel
                    font.weight: Font.DemiBold
                }

                MouseArea {
                    id: tabHover
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: rootView._switchTab(index)
                }
            }
        }
    }
}
