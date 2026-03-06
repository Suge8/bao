import QtQuick 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    property bool expanded: false
    property real reveal: expanded ? 1 : 0
    property real bottomPadding: 0
    property int slideAxis: Qt.Vertical
    property int slideSign: 1
    property real slideDistance: 16
    default property alias content: inner.data

    Layout.fillWidth: true
    clip: true
    implicitHeight: body.height

    Behavior on reveal { NumberAnimation { duration: motionPanel; easing.type: easeEmphasis } }

    Item {
        id: body
        width: parent.width
        height: (inner.implicitHeight + root.bottomPadding) * root.reveal
        opacity: root.reveal
        scale: 0.985 + (0.015 * root.reveal)
        x: root.slideAxis === Qt.Horizontal ? (1 - root.reveal) * root.slideDistance * root.slideSign : 0
        y: root.slideAxis === Qt.Vertical ? (1 - root.reveal) * root.slideDistance * root.slideSign : 0
        transformOrigin: Item.Top
        visible: height > 0.5
        Column {
            id: inner
            width: parent.width
        }
    }
}
