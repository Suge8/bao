import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root
    color: "transparent"

    property var chatService: null
    property var sessionService: null
    property var configService: null
    readonly property int composerMinHeight: 44
    readonly property int composerMaxHeight: 140
    readonly property int composerScrollInset: 12
    readonly property int composerBottomSafeGap: 4
    readonly property real composerFieldRadius: composerMinHeight / 2
    readonly property int chatTopSafeInset: windowContentInsetTop
    readonly property int chatTopContentGap: spacingMd
    readonly property int chatSideInset: windowContentInsetSide + spacingSm
    readonly property int chatIdleBottomGap: windowContentInsetBottom
    readonly property int composerBottomMargin: Math.max(spacingXs, windowContentInsetBottom - spacingSm)
    readonly property int composerDockGap: windowContentInsetBottom
    readonly property int composerEdgeInset: spacingSm
    readonly property bool hasDraftAttachments: chatService ? chatService.draftAttachmentCount > 0 : false
    readonly property bool hasSessionService: sessionService !== null
    readonly property bool activeSessionReadOnly: hasSessionService ? sessionService.activeSessionReadOnly : false
    readonly property string hubStateValue: {
        if (!chatService)
            return "idle"
        if (typeof chatService.hubState === "string" && chatService.hubState !== "")
            return chatService.hubState
        if (typeof chatService.state === "string" && chatService.state !== "")
            return chatService.state
        return "idle"
    }
    signal messageCopied()

    function themedIcon(name) {
        return themedIconSource(name)
    }

    function sendMessage(text) {
        var trimmed = String(text || "").trim()
        if ((!trimmed && !root.hasDraftAttachments) || !chatService)
            return
        chatService.sendMessage(trimmed)
    }

    ChatMessagePane {
        id: messagePane
        anchors.fill: parent
        chatRoot: root
        chatService: root.chatService
        sessionService: root.sessionService
        configService: root.configService
        hubStateValue: root.hubStateValue
        presentedListBottomInset: composerBar.presentedListBottomInset
        composerInputActiveFocus: composerBar.inputActiveFocus
        onMessageCopied: root.messageCopied()
    }

    ChatComposerBar {
        id: composerBar
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        chatRoot: root
        chatService: root.chatService
        hubStateValue: root.hubStateValue
        activeSessionReadOnly: root.activeSessionReadOnly
        hasDraftAttachments: root.hasDraftAttachments
        onSendRequested: function(text) { root.sendMessage(text) }
    }
}
