import QtQuick 2.15

Rectangle {
    id: root

    property bool checked: false
    property bool buttonEnabled: true
    property real switchWidth: 44
    property real switchHeight: 24
    signal toggled(bool checked)

    implicitWidth: root.switchWidth
    implicitHeight: root.switchHeight
    radius: height / 2
    color: root.checked ? accent : (isDark ? "#252538" : "#D1D5DB")
    scale: root.checked ? motionHoverScaleSubtle : 1.0

    Behavior on color { ColorAnimation { duration: motionUi; easing.type: easeStandard } }
    Behavior on scale { NumberAnimation { duration: motionUi; easing.type: easeEmphasis } }

    Rectangle {
        width: 18
        height: 18
        radius: 9
        color: "#FFFFFF"
        anchors.verticalCenter: parent.verticalCenter
        x: root.checked ? parent.width - width - 3 : 3
        Behavior on x { SmoothedAnimation { velocity: motionTrackVelocity; duration: motionUi } }
    }

    MouseArea {
        anchors.fill: parent
        enabled: root.buttonEnabled
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton
        scrollGestureEnabled: false
        cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
        onClicked: {
            root.toggled(!root.checked)
        }
    }
}
