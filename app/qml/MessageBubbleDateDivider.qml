import QtQuick 2.15

Item {
    id: divider

    required property var workspaceRoot

    objectName: "dateDivider"
    visible: workspaceRoot.showDateDivider && workspaceRoot.dateDividerText !== ""
    anchors.top: parent.top
    anchors.left: parent.left
    anchors.right: parent.right
    height: workspaceRoot.dividerBlockHeight
    opacity: visible ? 1.0 : 0.0

    Behavior on opacity { NumberAnimation { duration: motionFast; easing.type: easeStandard } }

    Rectangle {
        anchors.left: parent.left
        anchors.leftMargin: workspaceRoot.isSystem ? 24 : 34
        anchors.right: dividerLabel.left
        anchors.rightMargin: 12
        anchors.verticalCenter: parent.verticalCenter
        height: 1
        radius: 1
        color: workspaceRoot.dividerLineColor
        opacity: 0.9
    }

    Text {
        id: dividerLabel
        objectName: "dateDividerText"
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        text: workspaceRoot.dateDividerText
        color: textSecondary
        font.pixelSize: typeMeta
        font.weight: weightMedium
        font.letterSpacing: 0.3
        textFormat: Text.PlainText
        renderType: Text.NativeRendering
        opacity: 0.84
    }

    Rectangle {
        anchors.left: dividerLabel.right
        anchors.leftMargin: 12
        anchors.right: parent.right
        anchors.rightMargin: workspaceRoot.isSystem ? 24 : 34
        anchors.verticalCenter: parent.verticalCenter
        height: 1
        radius: 1
        color: workspaceRoot.dividerLineColor
        opacity: 0.9
    }
}
