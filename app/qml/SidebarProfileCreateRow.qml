import QtQuick 2.15

Item {
    id: root
    objectName: "profileCreateRow"

    required property var sidebarRoot
    property var nextTabTarget: null
    property var previousTabTarget: null
    readonly property var inputItem: newProfileField.inputItem

    signal submit(string name)

    width: parent ? parent.width - 24 : 0
    height: 38

    SettingsField {
        id: newProfileField
        anchors.left: parent.left
        anchors.right: createButton.left
        anchors.rightMargin: 10
        anchors.verticalCenter: parent.verticalCenter
        label: ""
        showLabel: false
        showDescription: false
        fieldHeight: 38
        fieldFontPixelSize: sidebarRoot.typeLabel
        inputObjectName: "profileCreateField"
        nextTabTarget: root.nextTabTarget ? root.nextTabTarget : root.inputItem
        previousTabTarget: root.previousTabTarget ? root.previousTabTarget : root.inputItem
        placeholder: sidebarRoot.strings.profile_create_placeholder
        onAccepted: root.submit(text)
    }

    IconCircleButton {
        id: createButton
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        buttonSize: 38
        glyphText: "+"
        glyphSize: 20
        fillColor: sidebarRoot.accent
        hoverFillColor: sidebarRoot.accentHover
        outlineColor: sidebarRoot.accent
        glyphColor: sidebarRoot.isDark ? sidebarRoot.bgSidebar : "#FFFFFF"
        hoverScale: 1.05
        pressedScale: 0.92
        onClicked: root.submit(newProfileField.text)
    }

    function clear() {
        newProfileField.text = ""
    }

    function focusField() {
        newProfileField.forceActiveFocus()
    }
}
