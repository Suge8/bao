pragma ComponentBehavior: Bound

import QtQuick 2.15

Rectangle {
    id: root

    property string labelText: ""
    property color tone: textSecondary
    property bool tinted: true
    property int badgeHeight: 22
    property int horizontalPadding: 16
    property int badgeFontSize: typeCaption

    visible: labelText.length > 0
    radius: Math.round(badgeHeight / 2)
    implicitHeight: badgeHeight
    implicitWidth: label.implicitWidth + horizontalPadding
    color: tinted
        ? Qt.rgba(Qt.color(tone).r, Qt.color(tone).g, Qt.color(tone).b, isDark ? 0.18 : 0.10)
        : (isDark ? "#1D1713" : "#FFFFFF")
    border.width: 1
    border.color: tinted
        ? Qt.rgba(Qt.color(tone).r, Qt.color(tone).g, Qt.color(tone).b, isDark ? 0.34 : 0.24)
        : (isDark ? "#16FFFFFF" : "#10000000")

    Text {
        id: label
        anchors.centerIn: parent
        text: root.labelText
        color: textPrimary
        font.pixelSize: root.badgeFontSize
        font.weight: weightBold
    }
}
