import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs
import QtQuick.Layouts 1.15

Item {
    id: root
    objectName: "composerBar"

    required property var chatRoot
    property var chatService: null
    property string hubStateValue: "idle"
    property bool activeSessionReadOnly: false
    property bool hasDraftAttachments: false

    readonly property bool active: hubStateValue === "running" && !activeSessionReadOnly
    readonly property real visibleHeight: composerContent.implicitHeight + 20
    readonly property int revealDuration: motionPanel + 40
    readonly property real targetListBottomInset: active
                                               ? visibleHeight + chatRoot.composerBottomMargin + chatRoot.composerDockGap
                                               : chatRoot.chatIdleBottomGap
    readonly property bool inputActiveFocus: messageInput.activeFocus
    property real presentedListBottomInset: targetListBottomInset

    signal sendRequested(string text)

    anchors.leftMargin: chatRoot.chatSideInset + chatRoot.composerEdgeInset
    anchors.rightMargin: chatRoot.chatSideInset + chatRoot.composerEdgeInset
    anchors.bottomMargin: chatRoot.composerBottomMargin
    height: visibleHeight
    enabled: active
    opacity: active ? 1.0 : 0.0
    scale: active ? 1.0 : 0.992
    transform: Translate {
        y: root.active ? 0 : 22
        Behavior on y { NumberAnimation { duration: root.revealDuration; easing.type: easeEmphasis } }
    }

    Behavior on presentedListBottomInset { NumberAnimation { duration: root.revealDuration; easing.type: easeEmphasis } }
    Behavior on opacity { NumberAnimation { duration: motionUi + 40; easing.type: easeStandard } }
    Behavior on scale { NumberAnimation { duration: root.revealDuration; easing.type: easeEmphasis } }

    function submitMessage() {
        var text = messageInput.text.trim()
        if ((!text && !hasDraftAttachments) || !chatService)
            return
        sendRequested(text)
        messageInput.text = ""
    }

    Column {
        id: composerContent
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        anchors.leftMargin: 18
        anchors.rightMargin: 18
        spacing: root.hasDraftAttachments ? 10 : 0

        ChatDraftAttachmentStrip {
            chatService: root.chatService
            hasDraftAttachments: root.hasDraftAttachments
        }

        RowLayout {
            width: parent.width
            spacing: 0

            Rectangle {
                id: composerField
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignVCenter
                readonly property bool focused: messageInput.activeFocus
                readonly property bool hovered: messageInput.hovered || attachHover.containsMouse
                readonly property color fillColor: focused ? bgInputFocus : (hovered ? bgInputHover : bgInput)
                readonly property color strokeColor: focused ? borderFocus : (hovered ? borderDefault : borderSubtle)
                readonly property real strokeWidth: focused ? 1.35 : 1.0
                readonly property real fieldScale: focused ? 1.006 : (hovered ? 1.003 : 1.0)
                Layout.preferredHeight: Math.min(
                                          Math.max(
                                              messageInput.contentHeight
                                              + messageInput.topPadding
                                              + messageInput.bottomPadding
                                              + chatRoot.composerScrollInset,
                                              chatRoot.composerMinHeight
                                          ),
                                          chatRoot.composerMaxHeight
                                      )
                radius: chatRoot.composerFieldRadius
                color: fillColor
                border.color: strokeColor
                border.width: strokeWidth
                clip: true
                scale: fieldScale
                Behavior on border.color { ColorAnimation { duration: motionFast; easing.type: easeStandard } }
                Behavior on border.width { NumberAnimation { duration: motionFast; easing.type: easeStandard } }
                Behavior on color { ColorAnimation { duration: motionUi; easing.type: easeStandard } }
                Behavior on scale { NumberAnimation { duration: motionUi; easing.type: easeEmphasis } }

                Rectangle {
                    id: attachButton
                    width: 32
                    height: 32
                    radius: 16
                    anchors.left: parent.left
                    anchors.leftMargin: 8
                    anchors.verticalCenter: parent.verticalCenter
                    color: attachHover.containsMouse ? (isDark ? "#38F38F1A" : "#1AE68A18") : "transparent"
                    scale: attachHover.containsMouse ? motionHoverScaleSubtle : 1.0
                    Behavior on color { ColorAnimation { duration: motionFast; easing.type: easeStandard } }
                    Behavior on scale { NumberAnimation { duration: motionFast; easing.type: easeStandard } }

                    Rectangle {
                        anchors.fill: parent
                        radius: parent.radius
                        color: "transparent"
                        border.width: 1
                        border.color: root.hasDraftAttachments ? accent : "transparent"
                        opacity: root.hasDraftAttachments ? 0.42 : 0.0
                        scale: root.hasDraftAttachments ? 1.0 : 0.92
                        Behavior on border.color { ColorAnimation { duration: motionFast; easing.type: easeStandard } }
                        Behavior on opacity { NumberAnimation { duration: motionFast; easing.type: easeStandard } }
                        Behavior on scale { NumberAnimation { duration: motionUi; easing.type: easeEmphasis } }
                    }

                    Rectangle {
                        width: 6
                        height: 6
                        radius: 3
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.rightMargin: 3
                        anchors.topMargin: 3
                        color: accent
                        opacity: root.hasDraftAttachments ? 0.95 : 0.0
                        scale: root.hasDraftAttachments ? 1.0 : 0.6
                        Behavior on opacity { NumberAnimation { duration: motionFast; easing.type: easeStandard } }
                        Behavior on scale { NumberAnimation { duration: motionUi; easing.type: easeEmphasis } }
                    }

                    Image {
                        anchors.centerIn: parent
                        source: "../resources/icons/paperclip.svg"
                        width: 19
                        height: 19
                        sourceSize: Qt.size(19, 19)
                        opacity: attachHover.containsMouse ? 1.0 : 0.78
                        Behavior on opacity { NumberAnimation { duration: motionFast; easing.type: easeStandard } }
                    }

                    MouseArea {
                        id: attachHover
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: attachmentDialog.open()
                    }
                }

                Rectangle {
                    id: innerSendButton
                    width: sizeButton
                    height: sizeButton
                    radius: width / 2
                    anchors.right: parent.right
                    anchors.rightMargin: 8
                    anchors.verticalCenter: parent.verticalCenter
                    property bool canSend: (messageInput.text.trim().length > 0 || root.hasDraftAttachments)
                                          && root.chatService
                                          && root.hubStateValue === "running"
                    color: sendHover.containsMouse && canSend
                           ? accentHover
                           : (canSend ? accent : chatComposerSendDisabled)
                    border.width: canSend ? 0 : 1
                    border.color: canSend ? "transparent" : borderSubtle
                    scale: sendHover.pressed && canSend
                           ? motionPressScaleStrong
                           : (sendHover.containsMouse && canSend ? motionHoverScaleSubtle : 1.0)
                    antialiasing: true
                    Behavior on color { ColorAnimation { duration: motionFast; easing.type: easeStandard } }
                    Behavior on border.color { ColorAnimation { duration: motionFast; easing.type: easeStandard } }
                    Behavior on scale { NumberAnimation { duration: motionFast; easing.type: easeStandard } }

                    Rectangle {
                        anchors.fill: parent
                        radius: parent.radius
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: chatComposerSendHighlight }
                            GradientStop { position: 1.0; color: "#00FFFFFF" }
                        }
                        opacity: parent.canSend ? (sendHover.containsMouse ? 0.82 : 0.66) : 0.0
                        Behavior on opacity { NumberAnimation { duration: motionFast; easing.type: easeStandard } }
                    }

                    Image {
                        anchors.centerIn: parent
                        source: "../resources/icons/send.svg"
                        width: 20
                        height: 20
                        sourceSize: Qt.size(20, 20)
                        opacity: parent.canSend ? 1.0 : 0.3
                        Behavior on opacity { NumberAnimation { duration: motionFast; easing.type: easeStandard } }
                    }

                    MouseArea {
                        id: sendHover
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: parent.canSend ? Qt.PointingHandCursor : Qt.ArrowCursor
                        onClicked: if (parent.canSend) root.submitMessage()
                    }
                }

                ScrollView {
                    id: inputScroll
                    anchors.left: attachButton.right
                    anchors.right: innerSendButton.left
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.leftMargin: 4
                    anchors.rightMargin: 8
                    clip: true
                    ScrollBar.vertical.policy: ScrollBar.AsNeeded

                    TextArea {
                        id: messageInput
                        objectName: "chatMessageInput"
                        property bool baoClickAwayEditor: true
                        hoverEnabled: true
                        placeholderText: strings.chat_placeholder
                        placeholderTextColor: textPlaceholder
                        color: textPrimary
                        background: null
                        wrapMode: TextArea.Wrap
                        leftPadding: sizeFieldPaddingX - 2
                        rightPadding: sizeFieldPaddingX
                        topPadding: 15
                        bottomPadding: 5
                        font.pixelSize: typeBody
                        selectionColor: textSelectionBg
                        selectedTextColor: textSelectionFg

                        onCursorPositionChanged: {
                            if (!activeFocus || cursorPosition !== length) return
                            var flick = inputScroll.contentItem
                            if (!flick) return
                            var contentHeight = messageInput.contentHeight + topPadding + bottomPadding
                            var viewportHeight = Number(flick.height || 0)
                            if (contentHeight > viewportHeight)
                                flick.contentY = contentHeight - viewportHeight + chatRoot.composerBottomSafeGap
                        }

                        Keys.onReturnPressed: function(event) {
                            if (event.modifiers & Qt.ShiftModifier) {
                                event.accepted = false
                                return
                            }
                            event.accepted = true
                            root.submitMessage()
                        }

                        Keys.onPressed: function(event) {
                            if (!event.matches(StandardKey.Paste) || !root.chatService)
                                return
                            if (root.chatService.pasteClipboardAttachment())
                                event.accepted = true
                        }
                    }
                }
            }
        }
    }

    FileDialog {
        id: attachmentDialog
        title: strings.chat_attach_title
        fileMode: FileDialog.OpenFiles
        onAccepted: if (root.chatService) root.chatService.addDraftAttachments(selectedFiles)
    }
}
