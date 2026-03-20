import QtQuick 2.15
import QtQuick.Controls 2.15

Popup {
    id: root
    objectName: "profilePopup"

    required property var sidebarRoot
    required property var profileBar
    readonly property int profileListMaxHeight: 212
    readonly property int profileListCacheBuffer: profileListMaxHeight * 3
    readonly property var profilesModel: sidebarRoot.hasProfileService ? (sidebarRoot.profileService.profiles || []) : []
    readonly property int profileCount: profilesModel.length
    readonly property bool hasProfiles: profileCount > 0
    readonly property string activeProfileId: sidebarRoot.hasProfileService ? String(sidebarRoot.profileService.activeProfileId || "") : ""
    readonly property string lastErrorText: sidebarRoot.hasProfileService ? String(sidebarRoot.profileService.lastError || "") : ""
    readonly property string profileCountLabel: String(sidebarRoot.strings.profile_count_badge || "%1").replace("%1", String(profileCount))
    readonly property var createFieldFocusTarget: createRow.inputItem ? createRow.inputItem : profileListView

    parent: sidebarRoot
    x: profileBar.x
    y: profileBar.y + profileBar.height + 8
    width: Math.max(profileBar.width + 8, 256)
    padding: 0
    modal: false
    focus: true
    transformOrigin: Item.Top
    closePolicy: Popup.CloseOnEscape
    onClosed: sidebarRoot.cancelRenameProfile()
    onOpened: Qt.callLater(function() {
        root.syncCurrentIndexToActiveProfile()
        if (root.hasProfiles)
            profileListView.forceActiveFocus()
        else
            createRow.focusField()
    })
    onProfileCountChanged: {
        if (opened)
            Qt.callLater(root.syncCurrentIndexToActiveProfile)
    }
    onProfilesModelChanged: {
        if (opened)
            Qt.callLater(root.syncCurrentIndexToActiveProfile)
    }
    onActiveProfileIdChanged: {
        if (opened && !sidebarRoot.editingProfileId.length)
            Qt.callLater(root.syncCurrentIndexToActiveProfile)
    }

    function profileAt(index) {
        if (index < 0 || index >= root.profileCount)
            return null
        return root.profilesModel[index] || null
    }

    function findProfileIndex(profileId) {
        var targetId = String(profileId || "").trim()
        if (!targetId.length)
            return -1
        for (var index = 0; index < root.profilesModel.length; index += 1) {
            var profile = root.profilesModel[index]
            if (String((profile || {}).id || "") === targetId)
                return index
        }
        return -1
    }

    function syncCurrentIndexToActiveProfile() {
        if (!root.hasProfiles) {
            profileListView.currentIndex = -1
            return
        }
        var nextIndex = root.findProfileIndex(root.activeProfileId)
        if (nextIndex < 0) {
            if (profileListView.currentIndex < 0)
                nextIndex = 0
            else
                nextIndex = Math.min(profileListView.currentIndex, root.profileCount - 1)
        }
        profileListView.currentIndex = nextIndex
        profileListView.positionViewAtIndex(nextIndex, ListView.Contain)
    }

    function activateCurrentProfile() {
        var profile = root.profileAt(profileListView.currentIndex)
        if (!profile)
            return false
        return sidebarRoot.activateProfile(String(profile.id || ""))
    }

    function beginRenameCurrentProfile() {
        var profile = root.profileAt(profileListView.currentIndex)
        if (!profile)
            return false
        sidebarRoot.beginRenameProfile(String(profile.id || ""), String(profile.displayName || ""))
        return true
    }

    enter: Transition {
        ParallelAnimation {
            NumberAnimation { property: "opacity"; from: 0; to: 1; duration: sidebarRoot.motionFast; easing.type: sidebarRoot.easeStandard }
            NumberAnimation { property: "scale"; from: 0.985; to: 1.0; duration: sidebarRoot.motionFast; easing.type: sidebarRoot.easeEmphasis }
        }
    }
    exit: Transition {
        ParallelAnimation {
            NumberAnimation { property: "opacity"; from: 1; to: 0; duration: sidebarRoot.motionMicro; easing.type: sidebarRoot.easeStandard }
            NumberAnimation { property: "scale"; from: 1.0; to: 0.988; duration: sidebarRoot.motionMicro; easing.type: sidebarRoot.easeStandard }
        }
    }

    background: Item {
        Rectangle {
            anchors.fill: parent
            anchors.topMargin: 6
            radius: 22
            color: sidebarRoot.isDark ? "#24000000" : "#18000000"
            opacity: 0.9
        }

        Rectangle {
            anchors.fill: parent
            radius: 22
            color: sidebarRoot.isDark ? "#171210" : "#FFFBF6"
            border.width: 1
            border.color: sidebarRoot.isDark ? "#2D221C" : "#E8D7C5"
        }
    }

    contentItem: Column {
        width: root.width
        spacing: 10
        topPadding: 10
        bottomPadding: 12

        Row {
            id: popupHeader
            width: parent.width - 20
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 10

            Text {
                width: Math.max(0, popupHeader.width - popupCountBadge.width - popupHeader.spacing)
                elide: Text.ElideRight
                text: sidebarRoot.strings.profile_switch
                color: sidebarRoot.textPrimary
                font.pixelSize: sidebarRoot.typeLabel
                font.weight: sidebarRoot.weightBold
            }

            ProfileCountBadge {
                id: popupCountBadge
                objectName: "profilePopupCountBadge"
                count: root.profileCount
                labelText: root.profileCountLabel
                isDark: sidebarRoot.isDark
                borderColor: sidebarRoot.isDark ? "#2D221C" : "#E8D7C5"
                textColor: sidebarRoot.textSecondary
                fontPixelSize: sidebarRoot.typeCaption
                fontWeight: sidebarRoot.weightMedium
            }
        }

        SidebarProfilePopupEmptyState {
            objectName: "profilePopupEmptyState"
            width: parent.width - 20
            anchors.horizontalCenter: parent.horizontalCenter
            sidebarRoot: root.sidebarRoot
            visible: !root.hasProfiles
        }

        ListView {
            id: profileListView
            objectName: "profilePopupList"
            width: parent.width - 20
            anchors.horizontalCenter: parent.horizontalCenter
            visible: root.hasProfiles
            implicitHeight: root.hasProfiles ? Math.min(contentHeight, root.profileListMaxHeight) : 0
            height: implicitHeight
            clip: true
            interactive: root.hasProfiles && contentHeight > height
            spacing: 8
            focus: true
            keyNavigationEnabled: true
            keyNavigationWraps: true
            currentIndex: -1
            reuseItems: true
            cacheBuffer: root.profileListCacheBuffer
            boundsBehavior: Flickable.StopAtBounds
            KeyNavigation.tab: root.createFieldFocusTarget
            KeyNavigation.backtab: root.createFieldFocusTarget
            model: root.profilesModel
            onCurrentIndexChanged: {
                if (currentIndex >= 0)
                    positionViewAtIndex(currentIndex, ListView.Contain)
            }
            Keys.onReturnPressed: function(event) {
                if (root.activateCurrentProfile())
                    event.accepted = true
            }
            Keys.onEnterPressed: function(event) {
                if (root.activateCurrentProfile())
                    event.accepted = true
            }
            Keys.onPressed: function(event) {
                if (event.key !== Qt.Key_F2)
                    return
                if (root.beginRenameCurrentProfile())
                    event.accepted = true
            }
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

            delegate: SidebarProfilePopupRow {
                required property var modelData
                sidebarRoot: root.sidebarRoot
                profileData: modelData
                createFieldTarget: root.createFieldFocusTarget
            }
        }

        Item {
            width: parent.width - 24
            anchors.horizontalCenter: parent.horizontalCenter
            visible: root.hasProfiles
            height: visible ? 10 : 0

            Row {
                anchors.fill: parent
                spacing: 6

                Repeater {
                    model: Math.max(1, Math.floor(parent.width / 12))
                    delegate: Rectangle {
                        width: 7
                        height: 1
                        radius: 0.5
                        anchors.verticalCenter: parent.verticalCenter
                        color: sidebarRoot.isDark ? "#3A2A20" : "#DCC8B4"
                        opacity: 0.8
                    }
                }
            }
        }

        SidebarProfileCreateRow {
            id: createRow
            anchors.horizontalCenter: parent.horizontalCenter
            sidebarRoot: root.sidebarRoot
            nextTabTarget: root.hasProfiles ? profileListView : createRow.inputItem
            previousTabTarget: root.hasProfiles ? profileListView : createRow.inputItem
            onSubmit: function(name) {
                if (sidebarRoot.createProfile(name))
                    clear()
            }
        }

        Rectangle {
            width: parent.width - 24
            anchors.horizontalCenter: parent.horizontalCenter
            radius: 14
            color: sidebarRoot.isDark ? "#2A1715" : "#FCE7E2"
            border.width: 1
            border.color: sidebarRoot.isDark ? "#5E2B26" : "#E2A69A"
            visible: root.lastErrorText.length > 0
            implicitHeight: errorText.implicitHeight + 18

            Text {
                id: errorText
                anchors.fill: parent
                anchors.margins: 9
                text: root.lastErrorText
                color: sidebarRoot.isDark ? "#FFD6CF" : "#A23A2B"
                font.pixelSize: sidebarRoot.typeCaption
                font.weight: sidebarRoot.weightMedium
                wrapMode: Text.WordWrap
            }
        }
    }
}
