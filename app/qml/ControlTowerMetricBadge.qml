import QtQuick 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    property string valueText: ""
    property string labelText: ""
    property bool isDark: false
    property color textPrimary: "transparent"
    property color textSecondary: "transparent"
    property int fontPixelSize: 12
    property int weightBold: Font.Bold
    property int weightMedium: Font.Medium
    property real maximumWidth: -1
    readonly property real horizontalPadding: 4
    readonly property real verticalPadding: 2
    readonly property real contentWidth: metricRow.implicitWidth + horizontalPadding * 2
    readonly property real resolvedMaximumWidth: maximumWidth > 0 ? maximumWidth : contentWidth

    clip: true
    implicitWidth: Math.min(contentWidth, resolvedMaximumWidth)
    implicitHeight: metricRow.implicitHeight + verticalPadding * 2

    RowLayout {
        id: metricRow
        anchors.fill: parent
        anchors.leftMargin: horizontalPadding
        anchors.rightMargin: horizontalPadding
        anchors.topMargin: verticalPadding
        anchors.bottomMargin: verticalPadding
        spacing: 4

        Text {
            text: root.valueText
            color: root.textPrimary
            font.pixelSize: root.fontPixelSize
            font.weight: root.weightBold
            textFormat: Text.PlainText
        }

        Text {
            Layout.fillWidth: true
            text: root.labelText
            color: root.textSecondary
            font.pixelSize: root.fontPixelSize
            font.weight: root.weightMedium
            textFormat: Text.PlainText
            elide: Text.ElideRight
            maximumLineCount: 1
        }
    }
}
