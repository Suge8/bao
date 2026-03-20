import QtQuick 2.15
import QtQuick.Controls 2.15

AppModal {
    id: root

    required property var rootView

    z: 22
    darkMode: isDark
    title: rootView._helpTitle
    closeText: rootView.tr("我知道了", "Got it")

    Repeater {
        model: rootView._helpSections

        delegate: Rectangle {
            required property var modelData

            width: parent.width
            radius: radiusMd
            color: isDark ? "#0DFFFFFF" : "#08000000"
            border.color: borderSubtle
            border.width: 1
            implicitHeight: helpBlock.implicitHeight + 24

            Column {
                id: helpBlock
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 12
                spacing: 8

                Text { width: parent.width; text: modelData.title || ""; color: textPrimary; font.pixelSize: typeBody; font.weight: Font.DemiBold; wrapMode: Text.WordWrap }
                Text { width: parent.width; text: modelData.body || ""; color: textSecondary; font.pixelSize: typeLabel; wrapMode: Text.WordWrap; lineHeight: 1.25 }
            }
        }
    }
}
