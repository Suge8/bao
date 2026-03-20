import QtQuick 2.15
import QtQuick.Controls 2.15
import "SessionBrowserLogic.js" as SessionBrowserLogic

Item {
    id: root

    property var chatService: null
    property var sessionService: null
    property string activeSessionKey: ""
    property bool showSelection: true
    property bool hubIdle: {
        if (!hasChatService)
            return true
        if (typeof chatService.hubState === "string" && chatService.hubState !== "")
            return chatService.hubState === "idle"
        if (typeof chatService.state === "string" && chatService.state !== "")
            return chatService.state === "idle"
        return true
    }
    property bool projectionMotionEnabled: false
    property real activeHighlightX: 0.0
    property real activeHighlightY: 0.0
    property real activeHighlightWidth: 0.0
    property real activeHighlightHeight: 0.0
    property real activeHighlightOpacity: 0.0

    readonly property bool hasChatService: chatService !== null
    readonly property bool hasSessionService: sessionService !== null
    readonly property bool darkMode: isDark
    readonly property real viewportPadding: sizeSidebarHeader
    readonly property real listViewportX: sessionListArea.listView.x
    readonly property real listViewportY: sessionListArea.listView.y
    readonly property real listViewportWidth: sessionListArea.listView.width
    readonly property real listViewportHeight: sessionListArea.listView.height

    signal newSessionRequested()
    signal sessionSelected(string key)
    signal sessionDeleteRequested(string key)

    function requestNewSession() { root.newSessionRequested() }

    function finishProjectionMotion() {
        SessionBrowserLogic.finishProjectionMotion(root, sessionListArea.listView)
    }

    function syncViewportHighlight(clampContentY) {
        SessionBrowserLogic.syncViewportHighlight(root, sessionListArea.listView, clampContentY)
    }

    function updateActiveHighlight() {
        SessionBrowserLogic.updateActiveHighlight(root, sessionListArea.listView)
    }

    function channelIconSource(channel) {
        return SessionBrowserLogic.channelVisualSource(root.darkMode, channel, false)
    }

    function channelFilledIconSource(channel) {
        return SessionBrowserLogic.channelVisualSource(root.darkMode, channel, true)
    }

    function channelUsesTint(channel) {
        return SessionBrowserLogic.channelUsesTint(channel)
    }

    function channelAccent(channel) {
        return SessionBrowserLogic.channelAccent(root.darkMode, channel)
    }

    function captureScrollAnchor() {
        return SessionBrowserLogic.captureScrollAnchor(
            root,
            sessionListArea.listView,
            root.activeSessionKey,
        )
    }

    function restoreScrollAnchor(anchor) {
        SessionBrowserLogic.restoreScrollAnchor(root, sessionListArea.listView, anchor)
    }

    function toggleGroup(channel) {
        if (!hasSessionService)
            return
        root.projectionMotionEnabled = true
        projectionMotionSettler.restart()
        sessionService.toggleSidebarGroup(channel)
    }

    Component.onCompleted: Qt.callLater(function() { root.updateActiveHighlight() })

    onActiveSessionKeyChanged: Qt.callLater(function() { root.updateActiveHighlight() })
    onShowSelectionChanged: root.updateActiveHighlight()

    Rectangle {
        anchors.fill: parent
        radius: 28
        color: sidebarListPanelBg
        border.width: 1
        border.color: sidebarListPanelBorder

        Rectangle {
            anchors.fill: parent
            radius: parent.radius
            color: sidebarListPanelOverlay
            opacity: 0.9
        }
    }

    SessionBrowserHeader {
        id: sessionsHeaderBar
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.leftMargin: 16
        anchors.rightMargin: 14
        anchors.topMargin: 12
        height: implicitHeight
        sessionService: root.sessionService
        hasSessionService: root.hasSessionService
        onNewSessionRequested: root.requestNewSession()
        onDiscoverySessionRequested: function(key) { root.sessionSelected(key) }
    }

    SessionBrowserList {
        id: sessionListArea
        z: 2
        anchors.fill: parent
        browserRoot: root
        sessionService: root.sessionService
        hasSessionService: root.hasSessionService
        activeSessionKey: root.activeSessionKey
        topMargin: sessionsHeaderBar.y + sessionsHeaderBar.height + 8
    }

    SessionBrowserStates {
        x: root.listViewportX
        y: root.listViewportY
        width: root.listViewportWidth
        height: root.listViewportHeight
        browserRoot: root
        listView: sessionListArea.listView
        sessionService: root.sessionService
        hasSessionService: root.hasSessionService
    }

    Item {
        id: sessionHighlightViewport
        objectName: "sessionHighlightViewport"
        parent: sessionListArea.parent
        z: 1
        x: root.listViewportX
        y: root.listViewportY
        width: root.listViewportWidth
        height: root.listViewportHeight
        clip: true

        Rectangle {
            id: activeSessionHighlight
            objectName: "activeSessionHighlight"
            z: 1
            x: root.activeHighlightX
            y: root.activeHighlightY
            width: root.activeHighlightWidth
            height: root.activeHighlightHeight
            radius: 12
            color: isDark ? "#251B14" : "#F5EADF"
            border.width: 1
            border.color: isDark ? "#3A2A20" : "#E8D5C0"
            opacity: root.activeHighlightOpacity
            visible: opacity > 0.01

            Behavior on x { NumberAnimation { duration: motionUi; easing.type: easeStandard } }
            Behavior on y { NumberAnimation { duration: motionUi; easing.type: easeStandard } }
            Behavior on width { NumberAnimation { duration: motionUi; easing.type: easeStandard } }
            Behavior on height { NumberAnimation { duration: motionUi; easing.type: easeStandard } }
            Behavior on opacity { NumberAnimation { duration: motionFast; easing.type: easeStandard } }

            Rectangle {
                width: 3
                height: parent.height - 12
                radius: 1
                anchors.left: parent.left
                anchors.leftMargin: 6
                anchors.verticalCenter: parent.verticalCenter
                color: accent
                opacity: 0.9
            }

            Rectangle {
                anchors.fill: parent
                anchors.margins: 1
                radius: parent.radius - 1
                color: isDark ? "#08FFFFFF" : "#10FFFFFF"
                opacity: 0.72
            }
        }
    }

    SequentialAnimation {
        id: projectionMotionSettler
        PauseAnimation { duration: motionUi }
        ScriptAction { script: root.finishProjectionMotion() }
    }
}
