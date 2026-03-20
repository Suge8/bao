import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root

    required property var messageList
    required property var chatRoot
    property var chatService: null
    property var configService: null
    property string hubStateValue: "idle"

    readonly property bool needsSetup: configService && configService.needsSetup
    readonly property bool showLoadingState: messageList.count === 0 && messageList.viewPhase === "loading"
    readonly property bool showEmptyState: messageList.count === 0 && messageList.viewPhase !== "loading"

    function emptyStateWidth() {
        var availableWidth = Math.max(0, Number(messageList.width || 0))
        if (availableWidth >= 440)
            return Math.min(360, availableWidth - 80)
        if (availableWidth >= 280)
            return Math.min(320, availableWidth - 56)
        return Math.max(0, availableWidth - 32)
    }

    Item {
        id: historyLoadingState
        anchors.centerIn: parent
        width: Math.min(320, messageList.width - 80)
        height: loadingCol.implicitHeight
        visible: root.showLoadingState

        Column {
            id: loadingCol
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 12

            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                width: 68
                height: 68
                radius: 34
                color: isDark ? "#16FFFFFF" : "#10FFB33D"
                border.color: isDark ? "#22FFFFFF" : borderSubtle

                LoadingOrbit {
                    anchors.centerIn: parent
                    width: 38
                    height: 38
                    running: historyLoadingState.visible
                    haloOpacity: 0.16
                }
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: root.hubStateValue === "starting"
                      ? strings.empty_starting_hint
                      : strings.chat_loading_history
                color: textTertiary
                font.pixelSize: typeMeta
                font.weight: weightDemiBold
                font.letterSpacing: letterWide
            }
        }
    }

    Item {
        anchors.centerIn: parent
        width: root.emptyStateWidth()
        height: emptyCol.implicitHeight
        visible: root.showEmptyState

        Column {
            id: emptyCol
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width
            spacing: 16

            Column {
                anchors.horizontalCenter: parent.horizontalCenter
                visible: root.needsSetup
                spacing: 14
                width: parent.width

                Rectangle {
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: 72
                    height: 72
                    radius: 36
                    color: chatEmptyIconBg
                    border.width: isDark ? 0 : 1
                    border.color: chatEmptyIconBorder

                    Image {
                        objectName: "chatEmptySetupIcon"
                        anchors.centerIn: parent
                        source: chatRoot.themedIcon("settings")
                        sourceSize: Qt.size(34, 34)
                        width: 34
                        height: 34
                        opacity: isDark ? 0.72 : 0.96
                    }
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: strings.empty_setup_title
                    color: textPrimary
                    font.pixelSize: typeTitle
                    font.weight: weightDemiBold
                    font.letterSpacing: 0.3
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: strings.empty_setup_hint
                    color: textTertiary
                    font.pixelSize: typeButton
                    horizontalAlignment: Text.AlignHCenter
                    width: parent.width
                    wrapMode: Text.WordWrap
                }
            }

            Column {
                anchors.horizontalCenter: parent.horizontalCenter
                visible: messageList.viewPhase === "error" && !root.needsSetup
                spacing: 14
                width: parent.width

                Rectangle {
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: 72
                    height: 72
                    radius: 36
                    color: chatErrorBadgeBg

                    Text {
                        anchors.centerIn: parent
                        text: "!"
                        color: statusError
                        font.pixelSize: 28
                        font.weight: Font.Bold
                    }
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: strings.empty_error_hint
                    color: textPrimary
                    font.pixelSize: typeTitle
                    font.weight: weightDemiBold
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: chatService ? (chatService.lastError || "") : ""
                    color: textTertiary
                    font.pixelSize: typeLabel
                    horizontalAlignment: Text.AlignHCenter
                    width: parent.width
                    wrapMode: Text.WordWrap
                    visible: text !== ""
                }

                PillActionButton {
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: 120
                    minHeight: 38
                    text: strings.empty_error_btn
                    onClicked: if (chatService) chatService.start()
                }
            }

            Column {
                id: readyEmptyState
                objectName: "chatEmptyReadyState"
                anchors.horizontalCenter: parent.horizontalCenter
                visible: messageList.viewPhase === "ready" && !messageList.sessionHasMessages
                spacing: 14

                Rectangle {
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: 72
                    height: 72
                    radius: 36
                    color: chatEmptyIconBg
                    border.width: isDark ? 0 : 1
                    border.color: chatEmptyIconBorder

                    Image {
                        objectName: "chatEmptyReadyIcon"
                        anchors.centerIn: parent
                        source: chatRoot.themedIcon("chat")
                        sourceSize: Qt.size(34, 34)
                        width: 34
                        height: 34
                        opacity: isDark ? 0.68 : 0.94
                    }
                }

                Text {
                    objectName: "chatEmptyReadyTitle"
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: parent.width
                    text: strings.empty_chat_title
                    color: textPrimary
                    font.pixelSize: typeTitle
                    font.weight: weightDemiBold
                    font.letterSpacing: 0.3
                    horizontalAlignment: Text.AlignHCenter
                    wrapMode: Text.WordWrap
                }

                Text {
                    objectName: "chatEmptyReadyHint"
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: parent.width
                    text: root.hubStateValue === "running"
                          ? strings.empty_chat_hint
                          : strings.empty_chat_idle_hint
                    color: textTertiary
                    font.pixelSize: typeButton
                    horizontalAlignment: Text.AlignHCenter
                    wrapMode: Text.WordWrap
                }
            }

            Column {
                id: idleEmptyState
                objectName: "chatEmptyIdleState"
                anchors.horizontalCenter: parent.horizontalCenter
                visible: messageList.viewPhase === "idle" && !root.needsSetup
                spacing: 14
                width: parent.width

                Rectangle {
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: 72
                    height: 72
                    radius: 36
                    color: chatEmptyIconBg
                    border.width: isDark ? 0 : 1
                    border.color: chatEmptyIconBorder

                    Image {
                        objectName: "chatEmptyIdleIcon"
                        anchors.centerIn: parent
                        source: chatRoot.themedIcon("zap")
                        sourceSize: Qt.size(34, 34)
                        width: 34
                        height: 34
                        opacity: isDark ? 0.7 : 0.96
                    }
                }

                Text {
                    objectName: "chatEmptyIdleTitle"
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: parent.width
                    text: strings.empty_idle_title
                    color: textPrimary
                    font.pixelSize: typeTitle
                    font.weight: weightDemiBold
                    font.letterSpacing: 0.3
                    horizontalAlignment: Text.AlignHCenter
                    wrapMode: Text.WordWrap
                }

                Text {
                    objectName: "chatEmptyIdleHint"
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: parent.width
                    text: strings.empty_idle_hint
                    color: textTertiary
                    font.pixelSize: typeButton
                    horizontalAlignment: Text.AlignHCenter
                    wrapMode: Text.WordWrap
                }
            }
        }
    }
}
