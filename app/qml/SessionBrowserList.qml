import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root

    property var browserRoot: null
    property var sessionService: null
    property bool hasSessionService: false
    property string activeSessionKey: ""
    property real topMargin: 0
    readonly property int listCacheBuffer: 720

    readonly property alias listView: sessionList

    ListView {
        id: sessionList
        objectName: "sidebarSessionList"
        z: 2
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.leftMargin: 10
        anchors.rightMargin: 10
        anchors.topMargin: root.topMargin
        clip: true
        boundsBehavior: Flickable.StopAtBounds
        boundsMovement: Flickable.StopAtBounds
        reuseItems: true
        cacheBuffer: root.listCacheBuffer
        model: root.hasSessionService ? root.sessionService.sidebarModel : null
        spacing: 0

        onContentHeightChanged: root.browserRoot.syncViewportHighlight(true)
        onHeightChanged: root.browserRoot.syncViewportHighlight(true)
        onContentYChanged: root.browserRoot.syncViewportHighlight(false)

        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AsNeeded
            width: 4
            background: Item {}
            contentItem: Rectangle {
                implicitWidth: 4
                radius: 2
                color: sidebarScrollbarThumb
                opacity: 0.72
            }
        }

        footer: Item {
            width: sessionList.width
            height: 0
        }

        add: Transition {
            enabled: root.browserRoot.projectionMotionEnabled
            NumberAnimation {
                property: "opacity"
                from: 0.0
                to: 1.0
                duration: motionFast
                easing.type: easeStandard
            }
        }

        remove: Transition {
            enabled: root.browserRoot.projectionMotionEnabled
            NumberAnimation {
                property: "opacity"
                to: 0.0
                duration: motionFast
                easing.type: easeStandard
            }
        }

        addDisplaced: Transition {
            enabled: root.browserRoot.projectionMotionEnabled
            NumberAnimation {
                properties: "y"
                duration: motionUi
                easing.type: easeStandard
            }
        }

        removeDisplaced: Transition {
            enabled: root.browserRoot.projectionMotionEnabled
            NumberAnimation {
                properties: "y"
                duration: motionUi
                easing.type: easeStandard
            }
        }

        delegate: Item {
            z: 2
            property bool anchorReady: true
            property bool anchorIsHeader: model.isHeader === true
            property string anchorKey: model.itemKey || ""
            property string anchorChannel: model.channel || ""
            readonly property real sessionTopGap: model.isFirstInGroup ? sizeSidebarHeaderToRowGap : 0
            readonly property real sessionBottomGap: model.isLastInGroup ? sizeSidebarGroupGap : sizeSidebarGroupInnerGap
            readonly property real highlightContentX: sessionRow.x + inner.x
            readonly property real highlightContentY: y + sessionRow.y
            readonly property real highlightContentWidth: inner.width
            readonly property real highlightContentHeight: inner.height
            width: sessionList.width
            height: model.isHeader
                ? (sizeSidebarHeader + (!model.expanded ? sizeSidebarGroupGap : 0))
                : (sizeSessionRow + sessionTopGap + sessionBottomGap)
            opacity: model.isHeader ? 1.0 : (sessionRow.visible ? 1.0 : 0.0)
            ListView.onPooled: inner.pooledByListView = true
            ListView.onReused: inner.pooledByListView = false

            SidebarGroupHeader {
                visible: model.isHeader
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                height: sizeSidebarHeader
                channel: model.channel || "other"
                expanded: model.expanded ?? false
                itemCount: model.itemCount || 0
                unreadCount: model.groupUnreadCount || 0
                groupHasRunning: model.groupHasRunning ?? false
                iconSource: root.browserRoot.channelIconSource(model.channel)
                chevronObjectName: "sidebarGroupChevronIcon_" + (model.channel || "other")
                unreadBadgeObjectName: "sidebarGroupUnreadBadge_" + (model.channel || "other")
                unreadTextObjectName: "sidebarGroupUnreadText_" + (model.channel || "other")
                onClicked: root.browserRoot.toggleGroup(model.channel)
            }

            Item {
                id: sessionRow
                visible: !model.isHeader
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                y: sessionTopGap
                height: sizeSessionRow + sessionBottomGap
                clip: true

                SessionItem {
                    id: inner
                    width: parent.width - 16 - ((model.isChildSession ?? false) ? 12 : 0)
                    x: 8 + ((model.isChildSession ?? false) ? 12 : 0)
                    pooledByListView: false
                    sessionKey: model.itemKey ?? ""
                    sessionTitle: model.itemTitle ?? model.itemKey ?? ""
                    sessionRelativeTime: model.itemUpdatedText ?? ""
                    filledIconSource: (model.isChildSession ?? false)
                        ? "../resources/icons/sidebar-subagent.svg"
                        : root.browserRoot.channelFilledIconSource(model.visualChannel ?? model.channel)
                    iconTintColor: root.browserRoot.channelAccent(model.visualChannel ?? model.channel)
                    useIconTint: (model.isChildSession ?? false)
                        ? false
                        : root.browserRoot.channelUsesTint(model.visualChannel ?? model.channel)
                    isRunning: model.isRunning ?? false
                    childIndent: (model.isChildSession ?? false) ? 2 : 0
                    isActive: root.browserRoot.showSelection && sessionKey === root.activeSessionKey
                    useExternalActiveHighlight: true
                    dimmed: root.browserRoot.hubIdle
                    hasUnread: model.itemHasUnread ?? false
                    readOnlySession: model.isReadOnly ?? false
                    onSelected: root.browserRoot.sessionSelected(sessionKey)
                    onDeleteRequested: root.browserRoot.sessionDeleteRequested(sessionKey)
                }
            }
        }
    }

    Connections {
        target: root.hasSessionService ? root.sessionService : null
        property var pendingAnchor: null

        function onSidebarProjectionWillChange() {
            if (root.browserRoot.projectionMotionEnabled) {
                pendingAnchor = null
                return
            }
            pendingAnchor = root.browserRoot.captureScrollAnchor()
        }

        function onSidebarProjectionChanged() {
            if (root.browserRoot.projectionMotionEnabled)
                return
            if (!pendingAnchor) {
                root.browserRoot.finishProjectionMotion()
                return
            }
            var anchor = pendingAnchor
            pendingAnchor = null
            sessionList.forceLayout()
            root.browserRoot.restoreScrollAnchor(anchor)
            root.browserRoot.finishProjectionMotion()
        }
    }
}
