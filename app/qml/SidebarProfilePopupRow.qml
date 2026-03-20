import QtQuick 2.15

Item {
    id: root

    required property var sidebarRoot
    required property var profileData
    property var createFieldTarget: null

    readonly property string profileId: String(profileData.id || "")
    readonly property string displayName: String(profileData.displayName || "")
    readonly property string avatarKey: String(profileData.avatarKey || "mochi")
    readonly property bool canDelete: Boolean(profileData.canDelete)
    readonly property bool isActive: Boolean(profileData.isActive)
    readonly property bool isEditing: sidebarRoot.editingProfileId === root.profileId
    readonly property bool isKeyboardCurrent: Boolean(ListView.isCurrentItem && ListView.view && ListView.view.activeFocus)
    readonly property bool cardHovered: hovered || isKeyboardCurrent
    readonly property bool hovered: rowMouse.containsMouse || renameAction.hovered || deleteAction.hovered

    width: ListView.view ? ListView.view.width : 0
    implicitHeight: profileCard.height + (renameBubble.active ? renameBubble.height + 8 : 0)
    height: implicitHeight

    Behavior on height { NumberAnimation { duration: sidebarRoot.motionUi; easing.type: sidebarRoot.easeEmphasis } }

    onIsEditingChanged: {
        if (!isEditing)
            return
        Qt.callLater(function() {
            renameBubble.focusEditor()
        })
    }

    Rectangle {
        id: profileCard
        width: parent.width
        height: 58
        radius: 19
        color: root.isActive ? (sidebarRoot.isDark ? "#241712" : "#F7E9D7") : (root.cardHovered ? (sidebarRoot.isDark ? "#1E1511" : "#FBF0E4") : "transparent")
        border.width: root.isActive || root.isEditing || root.cardHovered ? 1 : 0
        border.color: root.isEditing || root.isKeyboardCurrent ? sidebarRoot.accent : (root.isActive ? (sidebarRoot.isDark ? "#6A4322" : "#E3AA54") : (sidebarRoot.isDark ? "#2C211B" : "#E9D8C5"))
        scale: rowMouse.pressed ? 0.992 : 1.0

        Behavior on color { ColorAnimation { duration: sidebarRoot.motionFast; easing.type: sidebarRoot.easeStandard } }
        Behavior on border.color { ColorAnimation { duration: sidebarRoot.motionFast; easing.type: sidebarRoot.easeStandard } }
        Behavior on scale { NumberAnimation { duration: sidebarRoot.motionFast; easing.type: sidebarRoot.easeStandard } }

        Rectangle {
            anchors.fill: parent
            anchors.margins: 1
            radius: parent.radius - 1
            color: sidebarRoot.isDark ? "#04FFFFFF" : "#0AFFFFFF"
            opacity: root.isActive ? 1.0 : 0.0
            Behavior on opacity { NumberAnimation { duration: sidebarRoot.motionFast; easing.type: sidebarRoot.easeStandard } }
        }

        ProfileAvatar {
            anchors.left: parent.left
            anchors.leftMargin: 14
            anchors.verticalCenter: parent.verticalCenter
            size: 40
            source: sidebarRoot.profileAvatarSource(root.avatarKey)
            active: root.isActive
            hovered: root.cardHovered
            accent: sidebarRoot.accent
            isDark: sidebarRoot.isDark
            motionFast: sidebarRoot.motionFast
            easeStandard: sidebarRoot.easeStandard
        }

        Text {
            anchors.left: parent.left
            anchors.leftMargin: 66
            anchors.right: profileActions.left
            anchors.rightMargin: 12
            anchors.verticalCenter: parent.verticalCenter
            elide: Text.ElideRight
            text: root.displayName
            color: sidebarRoot.textPrimary
            font.pixelSize: sidebarRoot.typeBody + 1
            font.weight: root.isActive ? sidebarRoot.weightBold : sidebarRoot.weightDemiBold
        }

        Row {
            id: profileActions
            anchors.right: parent.right
            anchors.rightMargin: 12
            anchors.verticalCenter: parent.verticalCenter
            spacing: 7

            IconCircleButton {
                id: renameAction
                buttonSize: 30
                iconSource: sidebarRoot.themedIconSource("profile-edit")
                glyphSize: 18
                fillColor: root.isEditing ? (sidebarRoot.isDark ? "#24150C" : "#F6E1C9") : (sidebarRoot.isDark ? "#16100D" : "#FFF7EF")
                hoverFillColor: root.isEditing ? (sidebarRoot.isDark ? "#2E1B10" : "#F0D3AC") : sidebarRoot.bgCardHover
                outlineColor: root.isEditing ? sidebarRoot.accent : (sidebarRoot.isDark ? "#352821" : "#E1CCB9")
                glyphColor: root.isEditing ? sidebarRoot.accent : sidebarRoot.textSecondary
                hoverScale: 1.06
                onClicked: sidebarRoot.beginRenameProfile(root.profileId, root.displayName)
            }

            IconCircleButton {
                id: deleteAction
                visible: root.canDelete
                buttonSize: 30
                iconSource: sidebarRoot.themedIconSource("profile-trash")
                glyphSize: 18
                fillColor: sidebarRoot.isDark ? "#16100D" : "#FFF7EF"
                hoverFillColor: sidebarRoot.isDark ? "#301715" : "#FBE8E2"
                outlineColor: deleteAction.hovered ? (sidebarRoot.isDark ? "#8D3C33" : "#D79082") : (sidebarRoot.isDark ? "#3F241F" : "#E7C9C1")
                glyphColor: deleteAction.hovered ? sidebarRoot.statusError : sidebarRoot.textSecondary
                hoverScale: 1.06
                onClicked: sidebarRoot.requestDeleteProfile(root.profileId, root.displayName, root.avatarKey)
            }
        }

        MouseArea {
            id: rowMouse
            objectName: "profileRowMouse_" + root.profileId
            anchors.fill: parent
            anchors.rightMargin: profileActions.width + 18
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            enabled: !root.isEditing
            onClicked: {
                sidebarRoot.activateProfile(root.profileId)
            }
        }
    }

    SidebarProfileRenameBubble {
        id: renameBubble
        anchors.top: profileCard.bottom
        anchors.topMargin: 8
        anchors.left: profileCard.left
        anchors.leftMargin: 62
        anchors.right: profileCard.right
        anchors.rightMargin: 10
        sidebarRoot: root.sidebarRoot
        active: root.isEditing
        nextTabTarget: root.createFieldTarget
        previousTabTarget: ListView.view ? ListView.view : root.createFieldTarget
        textValue: sidebarRoot.editingProfileName
        onTextEdited: function(text) {
            sidebarRoot.editingProfileName = text
        }
        onSubmitted: sidebarRoot.submitRenameProfile()
        onCancelled: sidebarRoot.cancelRenameProfile()
    }
}
