import QtQuick 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    required property string metricId
    required property string iconSource
    required property string valueText
    required property string labelText
    required property bool isDark
    required property color textPrimary
    required property color textSecondary
    required property int typeTitle
    required property int typeCaption
    required property int weightBold
    required property int weightMedium

    objectName: "controlTowerHeroMetric_" + metricId
    Layout.fillWidth: true
    implicitHeight: metricRow.implicitHeight + 8

    RowLayout {
        id: metricRow
        anchors.fill: parent
        spacing: 10

        AppIcon {
            Layout.alignment: Qt.AlignTop
            Layout.preferredWidth: 20
            Layout.preferredHeight: 20
            source: root.iconSource
            sourceSize: Qt.size(20, 20)
            opacity: root.isDark ? 0.88 : 0.9
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 1

            Text {
                text: root.valueText
                color: root.textPrimary
                font.pixelSize: root.typeTitle
                font.weight: root.weightBold
                textFormat: Text.PlainText
            }

            Text {
                Layout.fillWidth: true
                text: root.labelText
                color: root.textSecondary
                font.pixelSize: root.typeCaption
                font.weight: root.weightMedium
                textFormat: Text.PlainText
                elide: Text.ElideRight
                maximumLineCount: 1
            }
        }
    }
}
