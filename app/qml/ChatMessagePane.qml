import QtQuick 2.15
import QtQuick.Controls 2.15
import "ChatMessagePaneLogic.js" as ChatMessagePaneLogic

Item {
    id: root

    required property var chatRoot
    property var chatService: null
    property var sessionService: null
    property var configService: null
    property string hubStateValue: "idle"
    property real presentedListBottomInset: 0
    property bool composerInputActiveFocus: false

    signal messageCopied()

    ListView {
        id: messageList
        objectName: "chatMessageList"
        property alias bottomPinnedFollower: bottomPinnedFollower
        property bool historyLoading: root.chatService ? root.chatService.historyLoading : false
        property string renderedSessionKey: activeSessionKey
        property var pendingViewportRestore: null
        property bool bottomPinned: true
        property int suppressViewportTracking: 0
        property var pendingPinnedReconcile: null
        property bool pendingSessionViewportReady: false
        property bool deferredViewportFlushScheduled: false
        property bool programmaticFollowActive: false
        readonly property string activeSessionKey: root.sessionService ? root.sessionService.activeKey : ""
        readonly property string viewPhase: {
            if (!root.chatService) return "idle"
            var phase = root.chatService.viewPhase
            if (phase !== undefined && phase !== null && phase !== "") return phase
            if (root.hubStateValue === "error") return "error"
            if (root.chatService.historyLoading || root.hubStateValue === "starting") return "loading"
            if (root.chatService.activeSessionReady) return "ready"
            return "idle"
        }
        readonly property bool sessionHasMessages: root.chatService ? root.chatService.activeSessionHasMessages : false
        readonly property real keyboardLineStep: Math.max(48, Math.round(height * 0.08))
        readonly property real keyboardPageStep: Math.max(keyboardLineStep, Math.round(height * 0.9))
        readonly property real nearEndThresholdPx: Math.max(24, keyboardLineStep)
        readonly property real animateReconcileThresholdPx: Math.max(height * 0.75, 240)

        anchors.fill: parent
        anchors.leftMargin: chatRoot.chatSideInset
        anchors.rightMargin: chatRoot.chatSideInset
        anchors.bottomMargin: root.presentedListBottomInset
        topMargin: chatRoot.chatTopSafeInset + chatRoot.chatTopContentGap
        spacing: spacingLg
        clip: true
        focus: root.visible
        activeFocusOnTab: true
        boundsBehavior: Flickable.StopAtBounds
        cacheBuffer: 20000
        reuseItems: true
        highlightFollowsCurrentItem: false
        highlightRangeMode: ListView.NoHighlightRange
        verticalLayoutDirection: ListView.TopToBottom
        model: root.chatService ? root.chatService.messages : null
        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

        Component.onCompleted: ChatMessagePaneLogic.scheduleSessionViewportReady(messageList)
        onBottomPinnedChanged: if (!bottomPinned) ChatMessagePaneLogic.cancelProgrammaticFollow(messageList, bottomPinnedFollower)
        onMovementStarted: ChatMessagePaneLogic.cancelProgrammaticFollow(messageList, bottomPinnedFollower)
        onMovementEnded: ChatMessagePaneLogic.refreshPinnedFromViewport(messageList)
        onFlickEnded: ChatMessagePaneLogic.refreshPinnedFromViewport(messageList)
        onHeightChanged: ChatMessagePaneLogic.onViewportGeometryChanged(messageList)
        onContentHeightChanged: ChatMessagePaneLogic.onViewportGeometryChanged(messageList)

        Keys.onPressed: function(event) {
            if (ChatMessagePaneLogic.handleNavigationKey(messageList, event, root.composerInputActiveFocus, bottomPinnedFollower))
                event.accepted = true
        }

        delegate: MessageBubble {
            width: messageList.width
            role: model.role ?? "assistant"
            content: model.content ?? ""
            format: model.format ?? "plain"
            status: model.status ?? "done"
            attachments: model.attachments ?? []
            references: model.references ?? ({})
            messageId: model.id ?? -1
            messageRow: index
            entranceStyle: model.entranceStyle ?? "none"
            entrancePending: model.entrancePending ?? false
            showDateDivider: (model.dividerText ?? "") !== ""
            dateDividerText: model.dividerText ?? ""
            toastFunc: function() { root.messageCopied() }
        }

        Connections {
            target: root.chatService
            ignoreUnknownSignals: true

            function onHistoryLoadingChanged(loading) {
                if (!loading)
                    return
                messageList.cancelFlick()
                ChatMessagePaneLogic.cancelProgrammaticFollow(messageList, bottomPinnedFollower)
            }

            function onAppendAtBottom(row) {
                if (ChatMessagePaneLogic.pinOnAppend(messageList, row))
                    messageList.bottomPinned = true
                if (ChatMessagePaneLogic.shouldForceInstantAppend(messageList, row)) {
                    ChatMessagePaneLogic.forceFollowToEnd(messageList, false, bottomPinnedFollower)
                    return
                }
                ChatMessagePaneLogic.queuePinnedReconcile(
                    messageList,
                    ChatMessagePaneLogic.shouldAnimatePinnedReconcile(messageList)
                )
            }

            function onIncrementalContent(_row) {
                if (messageList.bottomPinned)
                    ChatMessagePaneLogic.forceFollowToEnd(messageList, false, bottomPinnedFollower)
            }

            function onStatusSettled(_row, _status) {
                if (ChatMessagePaneLogic.shouldReconcileOnStatusUpdate(messageList, _row, _status))
                    ChatMessagePaneLogic.queuePinnedReconcile(
                        messageList,
                        ChatMessagePaneLogic.shouldAnimatePinnedReconcile(messageList)
                    )
            }

            function onSessionSwitchedApplied(key) {
                messageList.renderedSessionKey = key || messageList.activeSessionKey
                ChatMessagePaneLogic.clearPendingViewportRestore(messageList)
                ChatMessagePaneLogic.cancelProgrammaticFollow(messageList, bottomPinnedFollower)
            }

            function onHistoryReady(key) {
                messageList.renderedSessionKey = key || messageList.activeSessionKey
                messageList.forceActiveFocus()
                ChatMessagePaneLogic.scheduleSessionViewportReady(messageList)
            }
        }

        Connections {
            target: messageList.model
            ignoreUnknownSignals: true

            function onModelAboutToBeReset() {
                if (messageList.activeSessionKey === messageList.renderedSessionKey) {
                    ChatMessagePaneLogic.captureViewportBeforeReset(messageList)
                    return
                }
                ChatMessagePaneLogic.clearPendingViewportRestore(messageList)
            }

            function onModelReset() {
                var switchedSession = messageList.activeSessionKey !== messageList.renderedSessionKey
                messageList.renderedSessionKey = messageList.activeSessionKey
                if (!switchedSession)
                    ChatMessagePaneLogic.restoreViewportAfterReset(messageList)
            }
        }

        SmoothedAnimation {
            id: bottomPinnedFollower
            target: messageList
            property: "contentY"
            velocity: Math.max(12000, messageList.height * 28)
            onRunningChanged: if (!running) ChatMessagePaneLogic.finishProgrammaticFollow(messageList, bottomPinnedFollower)
        }
    }

    ChatViewStatusStates {
        anchors.fill: parent
        messageList: messageList
        chatRoot: root.chatRoot
        chatService: root.chatService
        configService: root.configService
        hubStateValue: root.hubStateValue
    }
}
