import QtQuick 2.15

Rectangle {
    id: root
    objectName: "sidebarDiagnosticsPill"

    required property var dockRoot
    required property var appIconButton
    readonly property bool hovered: diagnosticsArea.containsMouse
    signal clicked()

    width: 104
    height: 42
    radius: 21
    anchors.left: appIconButton.right
    anchors.leftMargin: 16
    anchors.verticalCenter: appIconButton.verticalCenter
    antialiasing: true
    border.width: 1
    border.color: dockRoot.diagnosticsBorderColor
    scale: diagnosticsArea.pressed ? dockRoot.motionPressScaleStrong : dockRoot.diagnosticsHoverScale
    color: dockRoot.diagnosticsFillColor

    Behavior on border.color { ColorAnimation { duration: dockRoot.motionUi; easing.type: dockRoot.easeStandard } }
    Behavior on color { ColorAnimation { duration: dockRoot.motionUi; easing.type: dockRoot.easeStandard } }
    Behavior on scale { NumberAnimation { duration: dockRoot.motionUi; easing.type: dockRoot.easeEmphasis } }

    Rectangle {
        anchors.fill: parent
        anchors.margins: 1
        radius: parent.radius - 1
        color: dockRoot.diagnosticsOverlayColor
    }

    Row {
        id: diagnosticsContentRow
        objectName: "sidebarDiagnosticsContentRow"
        anchors.fill: parent
        anchors.leftMargin: 11
        anchors.rightMargin: 10
        anchors.verticalCenter: parent.verticalCenter
        spacing: 14

        Item {
            id: diagnosticsIconChip
            objectName: "sidebarDiagnosticsIconChip"
            width: 20
            height: 20
            anchors.verticalCenter: parent.verticalCenter
            scale: dockRoot.diagnosticsIconScale
            Behavior on scale { NumberAnimation { duration: dockRoot.motionFast; easing.type: dockRoot.easeStandard } }

            AppIcon {
                width: 20
                height: 20
                anchors.centerIn: parent
                source: dockRoot.isDark ? "../resources/icons/sidebar-diagnostics-dark.svg" : "../resources/icons/sidebar-diagnostics-light.svg"
                sourceSize: Qt.size(20, 20)
                opacity: dockRoot.diagnosticsIconOpacity
            }
        }

        Column {
            id: diagnosticsLabelStack
            objectName: "sidebarDiagnosticsLabelStack"
            anchors.verticalCenter: parent.verticalCenter
            spacing: 0
            width: parent.width - diagnosticsIconChip.width - parent.spacing

            Text {
                width: parent.width
                text: dockRoot.diagnosticsLabel
                color: dockRoot.primaryInk
                font.pixelSize: dockRoot.typeMeta + 1
                font.weight: dockRoot.weightBold
                maximumLineCount: 1
                elide: Text.ElideRight
                wrapMode: Text.NoWrap
                renderType: Text.NativeRendering
                opacity: dockRoot.diagnosticsLabelOpacity
            }

            Text {
                width: parent.width
                text: dockRoot.diagnosticsHint
                color: dockRoot.diagnosticsHintColor
                font.pixelSize: dockRoot.typeMeta - 1
                font.weight: dockRoot.diagnosticsHintWeight
                maximumLineCount: 1
                elide: Text.ElideRight
                wrapMode: Text.NoWrap
                renderType: Text.NativeRendering
            }
        }
    }

    Rectangle {
        visible: dockRoot.hasDiagnostics && dockRoot.visibleDiagnosticsCount > 0
        width: 18
        height: 18
        radius: 9
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.rightMargin: -3
        anchors.topMargin: -3
        color: dockRoot.accent
        scale: dockRoot.diagnosticsBadgeScale
        Behavior on scale { NumberAnimation { duration: dockRoot.motionFast; easing.type: dockRoot.easeStandard } }

        Text {
            anchors.centerIn: parent
            text: dockRoot.diagnosticsCountLabel
            color: dockRoot.isDark ? "#241106" : "#FFFFFF"
            font.pixelSize: 8
            font.weight: dockRoot.weightBold
            renderType: Text.NativeRendering
        }
    }

    MouseArea {
        id: diagnosticsArea
        anchors.fill: parent
        anchors.margins: -4
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.clicked()
    }
}
