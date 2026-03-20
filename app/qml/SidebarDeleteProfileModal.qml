import QtQuick 2.15

AppModal {
    id: root

    required property var sidebarRoot

    title: sidebarRoot.strings.profile_delete_title
    closeText: sidebarRoot.strings.profile_delete_cancel
    darkMode: sidebarRoot.isDark
    maxModalWidth: 468
    maxModalHeight: 396
    bodyScrollable: false
    showDefaultCloseAction: true

    property real heroRevealScale: 0.92
    property real heroRevealY: 12
    property real bodyRevealOpacity: 0.0
    property real bodyRevealY: 16
    property real actionRevealOpacity: 0.0
    property real actionRevealScale: 0.92
    property real warningPulse: 0.0
    property real auraOpacity: 0.0

    Behavior on heroRevealScale { NumberAnimation { duration: sidebarRoot.motionPanel; easing.type: sidebarRoot.easeEmphasis } }
    Behavior on heroRevealY { NumberAnimation { duration: sidebarRoot.motionPanel; easing.type: sidebarRoot.easeEmphasis } }
    Behavior on bodyRevealOpacity { NumberAnimation { duration: sidebarRoot.motionUi; easing.type: sidebarRoot.easeStandard } }
    Behavior on bodyRevealY { NumberAnimation { duration: sidebarRoot.motionPanel; easing.type: sidebarRoot.easeEmphasis } }
    Behavior on actionRevealOpacity { NumberAnimation { duration: sidebarRoot.motionUi; easing.type: sidebarRoot.easeStandard } }
    Behavior on actionRevealScale { NumberAnimation { duration: sidebarRoot.motionPanel; easing.type: sidebarRoot.easeEmphasis } }
    Behavior on auraOpacity { NumberAnimation { duration: sidebarRoot.motionUi; easing.type: sidebarRoot.easeSoft } }

    onOpened: {
        heroRevealScale = 0.92
        heroRevealY = 12
        bodyRevealOpacity = 0.0
        bodyRevealY = 16
        actionRevealOpacity = 0.0
        actionRevealScale = 0.92
        warningPulse = 0.0
        auraOpacity = 0.0
        Qt.callLater(function() {
            root.heroRevealScale = 1.0
            root.heroRevealY = 0
            root.bodyRevealOpacity = 1.0
            root.bodyRevealY = 0
            root.actionRevealOpacity = 1.0
            root.actionRevealScale = 1.0
            root.auraOpacity = sidebarRoot.isDark ? 0.08 : 0.06
        })
        warningPulseLoop.restart()
    }
    onClosed: {
        warningPulseLoop.stop()
        sidebarRoot.clearPendingDeleteProfile()
    }

    Rectangle {
        id: dangerCard
        width: parent ? parent.width : 360
        radius: 20
        color: sidebarRoot.isDark ? "#18110F" : "#FFF8F3"
        border.width: 1
        border.color: sidebarRoot.isDark ? "#4A2621" : "#EDC1B6"
        implicitHeight: bodyColumn.implicitHeight + 28
        opacity: 0.94 + root.bodyRevealOpacity * 0.06
        y: root.bodyRevealY
        Behavior on opacity { NumberAnimation { duration: sidebarRoot.motionUi; easing.type: sidebarRoot.easeStandard } }
        Behavior on y { NumberAnimation { duration: sidebarRoot.motionPanel; easing.type: sidebarRoot.easeEmphasis } }

        Rectangle { anchors.fill: parent; anchors.margins: 1; radius: parent.radius - 1; color: sidebarRoot.isDark ? "#0AFFFFFF" : "#12FFFFFF" }
        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            height: 72
            radius: parent.radius
            color: sidebarRoot.statusError
            opacity: root.auraOpacity
            Behavior on opacity { NumberAnimation { duration: sidebarRoot.motionUi; easing.type: sidebarRoot.easeStandard } }
            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: parent.radius; color: dangerCard.color }
        }

        Column {
            id: bodyColumn
            anchors.fill: parent
            anchors.margins: 14
            spacing: 14

            Row {
                width: parent.width
                spacing: 12
                opacity: 0.78 + root.bodyRevealOpacity * 0.22
                y: root.heroRevealY
                Behavior on opacity { NumberAnimation { duration: sidebarRoot.motionUi; easing.type: sidebarRoot.easeStandard } }
                Behavior on y { NumberAnimation { duration: sidebarRoot.motionPanel; easing.type: sidebarRoot.easeEmphasis } }

                Item {
                    width: 58
                    height: 58
                    scale: root.heroRevealScale + root.warningPulse * 0.02
                    Behavior on scale { NumberAnimation { duration: sidebarRoot.motionPanel; easing.type: sidebarRoot.easeEmphasis } }

                    Rectangle { anchors.centerIn: parent; width: 54; height: 54; radius: 18; color: sidebarRoot.isDark ? "#261714" : "#FDECE6"; border.width: 1; border.color: sidebarRoot.isDark ? "#5F312B" : "#E7ACA0" }
                    ProfileAvatar { anchors.centerIn: parent; size: 46; source: sidebarRoot.profileAvatarSource((sidebarRoot.pendingDeleteProfile || {}).avatarKey); active: true; hovered: false; accent: sidebarRoot.accent; isDark: sidebarRoot.isDark; motionFast: sidebarRoot.motionFast; easeStandard: sidebarRoot.easeStandard }

                    Rectangle {
                        width: 22
                        height: 22
                        radius: 11
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        color: sidebarRoot.statusError
                        border.width: 2
                        border.color: sidebarRoot.isDark ? "#18110F" : "#FFF8F3"
                        scale: 1.0 + root.warningPulse * 0.08
                        Behavior on scale { NumberAnimation { duration: sidebarRoot.motionUi; easing.type: sidebarRoot.easeSoft } }
                        AppIcon { anchors.centerIn: parent; width: 12; height: 12; source: "../resources/icons/vendor/iconoir/message-alert.svg"; sourceSize: Qt.size(12, 12) }
                    }
                }

                Column {
                    width: parent.width - 70
                    spacing: 6
                    Text { width: parent.width; text: String((sidebarRoot.pendingDeleteProfile || {}).displayName || ""); color: sidebarRoot.textPrimary; font.pixelSize: sidebarRoot.typeBody + 2; font.weight: sidebarRoot.weightBold; elide: Text.ElideRight }
                    Rectangle {
                        width: irreversibleLabel.implicitWidth + 16
                        height: 22
                        radius: 11
                        color: sidebarRoot.isDark ? "#331714" : "#FFECE7"
                        border.width: 1
                        border.color: sidebarRoot.isDark ? "#72332B" : "#E4AEA2"
                        Text { id: irreversibleLabel; anchors.centerIn: parent; text: sidebarRoot.strings.profile_delete_irreversible; color: sidebarRoot.statusError; font.pixelSize: sidebarRoot.typeCaption; font.weight: sidebarRoot.weightBold }
                    }
                }
            }

            Rectangle {
                width: parent.width
                radius: 16
                color: sidebarRoot.isDark ? "#221613" : "#FFF2ED"
                border.width: 1
                border.color: sidebarRoot.isDark ? "#3C221D" : "#E9D2C8"
                implicitHeight: hintColumn.implicitHeight + 24

                Column {
                    id: hintColumn
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 8
                    Text { text: sidebarRoot.strings.profile_delete_irreversible; color: sidebarRoot.statusError; font.pixelSize: sidebarRoot.typeCaption; font.weight: sidebarRoot.weightBold; font.letterSpacing: sidebarRoot.letterWide }
                    Text {
                        width: parent.width
                        text: String(sidebarRoot.strings.profile_delete_hint || "").replace("%1", String((sidebarRoot.pendingDeleteProfile || {}).displayName || ""))
                        color: sidebarRoot.textSecondary
                        font.pixelSize: sidebarRoot.typeBody
                        font.weight: sidebarRoot.weightMedium
                        wrapMode: Text.WordWrap
                    }
                }
            }
        }
    }

    footer: PillActionButton {
        text: sidebarRoot.strings.profile_delete_confirm
        iconSource: "../resources/icons/vendor/iconoir/message-alert.svg"
        iconSize: 13
        fillColor: sidebarRoot.statusError
        hoverFillColor: Qt.darker(sidebarRoot.statusError, 1.08)
        outlineColor: "transparent"
        hoverOutlineColor: "transparent"
        textColor: "#FFFFFF"
        opacity: root.actionRevealOpacity
        scale: root.actionRevealScale
        Behavior on opacity { NumberAnimation { duration: sidebarRoot.motionUi; easing.type: sidebarRoot.easeStandard } }
        Behavior on scale { NumberAnimation { duration: sidebarRoot.motionPanel; easing.type: sidebarRoot.easeEmphasis } }
        onClicked: sidebarRoot.confirmDeleteProfile()
    }

    SequentialAnimation {
        id: warningPulseLoop
        loops: Animation.Infinite
        running: false
        NumberAnimation { target: root; property: "warningPulse"; to: 1.0; duration: sidebarRoot.motionBreath; easing.type: sidebarRoot.easeSoft }
        NumberAnimation { target: root; property: "warningPulse"; to: 0.0; duration: sidebarRoot.motionBreath; easing.type: sidebarRoot.easeSoft }
    }
}
