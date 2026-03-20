import QtQuick 2.15

Rectangle {
    id: root

    required property var sidebarRoot
    required property bool active
    required property string textValue
    property var nextTabTarget: null
    property var previousTabTarget: null

    signal textEdited(string text)
    signal submitted()
    signal cancelled()

    height: 52
    radius: 17
    visible: opacity > 0.01
    opacity: active ? 1.0 : 0.0
    scale: active ? 1.0 : 0.985
    color: sidebarRoot.isDark ? "#181210" : "#FFF8F1"
    border.width: 1
    border.color: active ? sidebarRoot.accent : (sidebarRoot.isDark ? "#31241E" : "#E4D2C0")

    Behavior on opacity { NumberAnimation { duration: sidebarRoot.motionFast; easing.type: sidebarRoot.easeStandard } }
    Behavior on scale { NumberAnimation { duration: sidebarRoot.motionUi; easing.type: sidebarRoot.easeEmphasis } }
    Behavior on border.color { ColorAnimation { duration: sidebarRoot.motionFast; easing.type: sidebarRoot.easeStandard } }

    Rectangle {
        anchors.fill: parent
        anchors.margins: 1
        radius: parent.radius - 1
        color: sidebarRoot.isDark ? "#08FFFFFF" : "#12FFFFFF"
    }

    Loader {
        id: renameFieldLoader
        anchors.left: parent.left
        anchors.leftMargin: 8
        anchors.right: renameBubbleActions.left
        anchors.rightMargin: 8
        anchors.verticalCenter: parent.verticalCenter
        active: root.active
        sourceComponent: renameFieldComponent
    }

    Row {
        id: renameBubbleActions
        anchors.right: parent.right
        anchors.rightMargin: 8
        anchors.verticalCenter: parent.verticalCenter
        spacing: 6

        IconCircleButton {
            buttonSize: 28
            glyphText: "\u2713"
            glyphSize: 13
            fillColor: sidebarRoot.accent
            hoverFillColor: sidebarRoot.accentHover
            outlineColor: sidebarRoot.accent
            glyphColor: sidebarRoot.isDark ? sidebarRoot.bgSidebar : "#FFFFFF"
            hoverScale: 1.06
            onClicked: root.submitted()
        }

        IconCircleButton {
            buttonSize: 28
            glyphText: "\u00D7"
            glyphSize: 13
            fillColor: sidebarRoot.isDark ? "#16100D" : "#FFF7EF"
            hoverFillColor: sidebarRoot.bgCardHover
            outlineColor: sidebarRoot.isDark ? "#352821" : "#E1CCB9"
            glyphColor: sidebarRoot.textSecondary
            hoverScale: 1.06
            onClicked: root.cancelled()
        }
    }

    Component {
        id: renameFieldComponent

        SettingsField {
            objectName: "profileRenameField"
            label: ""
            showLabel: false
            showDescription: false
            placeholder: String(sidebarRoot.strings.profile_display_name_placeholder || "")
            fieldHeight: 38
            fieldFontPixelSize: sidebarRoot.typeBody
            nextTabTarget: root.nextTabTarget ? root.nextTabTarget : inputItem
            previousTabTarget: root.previousTabTarget ? root.previousTabTarget : inputItem
            text: root.textValue
            onTextEdited: function(text) {
                root.textEdited(text)
            }
            onAccepted: root.submitted()
        }
    }

    function focusEditor() {
        if (!renameFieldLoader.item)
            return
        sidebarRoot.focusProfileRenameEditor(renameFieldLoader.item)
    }
}
