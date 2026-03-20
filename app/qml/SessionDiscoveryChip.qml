import QtQuick 2.15

Rectangle {
    id: root

    property string chipObjectName: ""
    property string text: ""
    property string categoryLabel: ""
    property bool buttonEnabled: true
    property color fillColor: accent
    property color hoverFillColor: accentHover
    property color disabledFillColor: isDark ? "#24FFFFFF" : "#14000000"
    property color outlineColor: accent
    property color hoverOutlineColor: accent
    property color textColor: "#FFFFFFFF"
    property color categoryTextColor: root.textColor
    property color disabledTextColor: textSecondary
    property real horizontalPadding: 14
    property real minHeight: 28
    property real maxWidth: 240
    property real hoverScale: motionHoverScaleSubtle
    property real pressedScale: 0.988
    property int titleFontSize: typeLabel
    property int titleFontWeight: weightDemiBold
    property int categoryFontSize: typeMeta
    property int categoryFontWeight: weightBold
    readonly property bool hasCategoryLabel: root.categoryLabel !== ""
    readonly property color resolvedTextColor: root.buttonEnabled ? root.textColor : root.disabledTextColor
    readonly property color resolvedCategoryTextColor: root.buttonEnabled
        ? root.categoryTextColor
        : root.disabledTextColor
    readonly property real measuredWidth: measurementRow.implicitWidth + root.horizontalPadding * 2

    objectName: root.chipObjectName
    width: implicitWidth
    implicitWidth: root.maxWidth > 0 ? Math.min(root.maxWidth, root.measuredWidth) : root.measuredWidth
    implicitHeight: root.minHeight
    radius: implicitHeight / 2
    color: !root.buttonEnabled ? root.disabledFillColor : (buttonArea.containsMouse ? root.hoverFillColor : root.fillColor)
    border.width: 1
    border.color: !root.buttonEnabled ? root.outlineColor : (buttonArea.containsMouse ? root.hoverOutlineColor : root.outlineColor)
    opacity: root.buttonEnabled ? 1.0 : 0.6
    scale: !root.buttonEnabled ? 1.0 : (buttonArea.pressed ? root.pressedScale : (buttonArea.containsMouse ? root.hoverScale : 1.0))

    Behavior on color { ColorAnimation { duration: motionFast; easing.type: easeStandard } }
    Behavior on border.color { ColorAnimation { duration: motionFast; easing.type: easeStandard } }
    Behavior on border.width { NumberAnimation { duration: motionFast; easing.type: easeStandard } }
    Behavior on opacity { NumberAnimation { duration: motionFast; easing.type: easeStandard } }
    Behavior on scale { NumberAnimation { duration: motionFast; easing.type: easeStandard } }

    Item {
        anchors.fill: parent
        anchors.leftMargin: root.horizontalPadding
        anchors.rightMargin: root.horizontalPadding

        Text {
            id: categoryText
            objectName: root.chipObjectName !== "" ? root.chipObjectName + "_label" : ""
            visible: root.hasCategoryLabel
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            text: root.categoryLabel
            color: root.resolvedCategoryTextColor
            font.pixelSize: root.categoryFontSize
            font.weight: root.categoryFontWeight
            elide: Text.ElideRight
            renderType: Text.NativeRendering
        }

        Text {
            id: titleText
            objectName: root.chipObjectName !== "" ? root.chipObjectName + "_title" : ""
            anchors.left: root.hasCategoryLabel ? categoryText.right : parent.left
            anchors.leftMargin: root.hasCategoryLabel ? 6 : 0
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            text: root.text
            color: root.resolvedTextColor
            font.pixelSize: root.titleFontSize
            font.weight: root.titleFontWeight
            elide: Text.ElideRight
            renderType: Text.NativeRendering
        }
    }

    Item {
        visible: false

        Row {
            id: measurementRow
            spacing: root.hasCategoryLabel ? 6 : 0

            Text {
                visible: root.hasCategoryLabel
                text: root.categoryLabel
                font.pixelSize: root.categoryFontSize
                font.weight: root.categoryFontWeight
            }

            Text {
                text: root.text
                font.pixelSize: root.titleFontSize
                font.weight: root.titleFontWeight
            }
        }
    }

    MouseArea {
        id: buttonArea
        anchors.fill: parent
        enabled: root.buttonEnabled
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton
        scrollGestureEnabled: false
        cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
        onClicked: root.clicked()
    }

    signal clicked()
}
