import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: banner

    required property var workspaceRoot
    required property string noticeText
    required property bool noticeSuccess

    Layout.fillWidth: true
    visible: noticeText !== ""
    implicitHeight: noticeRow.implicitHeight + 18
    radius: 18
    color: noticeSuccess ? (isDark ? "#142317" : "#ECF8EF") : (isDark ? "#2A1513" : "#FFF1EE")
    border.width: 1
    border.color: noticeSuccess ? (isDark ? "#235D36" : "#AED9B6") : (isDark ? "#6B2A22" : "#F0B2A8")

    RowLayout {
        id: noticeRow
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        Rectangle {
            implicitWidth: 8
            implicitHeight: 8
            radius: 4
            color: noticeSuccess ? statusSuccess : statusError
        }

        Text {
            Layout.fillWidth: true
            text: noticeText
            color: textPrimary
            font.pixelSize: typeLabel
            wrapMode: Text.WordWrap
        }

        IconCircleButton {
            buttonSize: 28
            glyphText: "✕"
            glyphSize: typeCaption
            fillColor: "transparent"
            hoverFillColor: bgCardHover
            outlineColor: borderSubtle
            glyphColor: textSecondary
            onClicked: workspaceRoot.noticeText = ""
        }
    }
}
