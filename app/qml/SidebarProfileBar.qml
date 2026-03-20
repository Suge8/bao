import QtQuick 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    objectName: "profileBar"

    required property var sidebarRoot
    required property bool popupOpened
    signal toggled()

    Layout.fillWidth: true
    Layout.leftMargin: 16
    Layout.rightMargin: 16
    Layout.topMargin: 12
    visible: sidebarRoot.hasProfileService
    implicitHeight: 72
    radius: 22
    color: sidebarRoot.isDark ? "#16100D" : "#FCF6EF"
    border.width: 1
    border.color: popupOpened ? (sidebarRoot.isDark ? "#5A3A20" : "#E7B05D") : (sidebarRoot.isDark ? "#2D221C" : "#E7D6C2")
    scale: mouseArea.containsPress ? 0.992 : 1.0

    Behavior on scale { NumberAnimation { duration: sidebarRoot.motionFast; easing.type: sidebarRoot.easeStandard } }
    Behavior on border.color { ColorAnimation { duration: sidebarRoot.motionFast; easing.type: sidebarRoot.easeStandard } }

    Item {
        anchors.fill: parent
        anchors.leftMargin: 14
        anchors.rightMargin: 16
        anchors.topMargin: 12
        anchors.bottomMargin: 12
        z: 1

        ProfileAvatar {
            id: activeProfileAvatar
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            size: 46
            source: sidebarRoot.profileAvatarSource(sidebarRoot.hasProfileService ? (sidebarRoot.profileService.activeProfile || {}).avatarKey : "mochi")
            active: true
            hovered: mouseArea.containsMouse
            accent: sidebarRoot.accent
            isDark: sidebarRoot.isDark
            motionFast: sidebarRoot.motionFast
            easeStandard: sidebarRoot.easeStandard
        }

        Column {
            anchors.left: activeProfileAvatar.right
            anchors.leftMargin: 14
            anchors.right: chevronFrame.left
            anchors.rightMargin: 12
            anchors.verticalCenter: parent.verticalCenter
            spacing: 2

            Text {
                width: parent.width
                elide: Text.ElideRight
                text: sidebarRoot.strings.profile_switch
                color: sidebarRoot.textSecondary
                font.pixelSize: sidebarRoot.typeMeta
                font.weight: sidebarRoot.weightBold
                font.letterSpacing: sidebarRoot.letterWide
            }

            Text {
                width: parent.width
                elide: Text.ElideRight
                text: sidebarRoot.hasProfileService ? String((sidebarRoot.profileService.activeProfile || {}).displayName || sidebarRoot.strings.profile_switch) : sidebarRoot.strings.profile_switch
                color: sidebarRoot.textPrimary
                font.pixelSize: sidebarRoot.typeBody
                font.weight: sidebarRoot.weightDemiBold
            }
        }

        Rectangle {
            id: chevronFrame
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            width: 34
            height: 34
            radius: 12
            color: mouseArea.containsMouse ? (sidebarRoot.isDark ? "#251B16" : "#F4E6D6") : (sidebarRoot.isDark ? "#1B1411" : "#F7EDE3")
            border.width: 1
            border.color: sidebarRoot.isDark ? "#30241D" : "#E5D2BD"
            Behavior on color { ColorAnimation { duration: sidebarRoot.motionFast; easing.type: sidebarRoot.easeStandard } }

            AppIcon {
                anchors.centerIn: parent
                width: 16
                height: 16
                source: sidebarRoot.themedIconSource("sidebar-chevron")
                sourceSize: Qt.size(16, 16)
                rotation: popupOpened ? -90 : 90
                opacity: 0.72
                Behavior on rotation { NumberAnimation { duration: sidebarRoot.motionFast; easing.type: sidebarRoot.easeStandard } }
            }
        }
    }

    Rectangle {
        anchors.fill: parent
        anchors.margins: 1
        radius: parent.radius - 1
        color: sidebarRoot.isDark ? "#08FFFFFF" : "#12FFFFFF"
        opacity: mouseArea.containsMouse ? 1.0 : 0.72
        Behavior on opacity { NumberAnimation { duration: sidebarRoot.motionFast; easing.type: sidebarRoot.easeStandard } }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.toggled()
    }
}
