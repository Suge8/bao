import QtQuick 2.15

Item {
    id: root
    z: 3

    property var browserRoot: null
    property var listView: null
    property var sessionService: null
    property bool hasSessionService: false
    readonly property real availableListWidth: root.listView ? root.listView.width : 0
    readonly property real loadingStateWidth: Math.max(156, Math.min(root.availableListWidth - 24, 208))
    readonly property real emptyStateWidth: Math.max(160, Math.min(root.availableListWidth - 32, 184))
    readonly property color stateTitleColor: isDark ? "#FFF1E1" : "#4B2D12"
    readonly property color stateHintColor: isDark ? "#DCC5A8" : "#74512F"
    readonly property color emptyIconFillColor: emptyStateMouse.containsMouse
        ? (isDark ? "#18FFFFFF" : "#10000000")
        : chatEmptyIconBg
    readonly property color emptyIconBorderColor: emptyStateMouse.containsMouse
        ? sessionRowActiveBorder
        : (isDark ? "#38FFFFFF" : chatEmptyIconBorder)
    readonly property color emptyButtonFillColor: emptyStateMouse.containsMouse ? accent : accentGlow

    Item {
        id: loadingStateWrap
        objectName: "sidebarLoadingState"
        anchors.top: parent.top
        anchors.topMargin: 18
        anchors.horizontalCenter: parent.horizontalCenter
        width: root.loadingStateWidth
        height: loadingStateContent.implicitHeight
        visible: root.listView
            && root.listView.count === 0
            && root.hasSessionService
            && root.sessionService.sessionsLoading

        Column {
            id: loadingStateContent
            width: parent.width
            spacing: 10

            Item {
                width: parent.width
                height: 46

                Rectangle {
                    width: 46
                    height: 46
                    radius: 23
                    anchors.horizontalCenter: parent.horizontalCenter
                    color: isDark ? "#16FFFFFF" : "#10FFB33D"
                    border.width: 1
                    border.color: isDark ? "#22FFFFFF" : borderSubtle

                    LoadingOrbit {
                        anchors.centerIn: parent
                        width: 28
                        height: 28
                        running: loadingStateWrap.visible
                        haloOpacity: 0.16
                    }
                }
            }

            Text {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                text: strings.sidebar_loading_title
                color: root.stateTitleColor
                font.pixelSize: typeBody + 1
                font.weight: weightBold
                wrapMode: Text.WordWrap
                lineHeight: 1.12
                textFormat: Text.PlainText
            }

            Text {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                text: strings.sidebar_loading_hint
                color: root.stateHintColor
                font.pixelSize: typeMeta
                wrapMode: Text.WordWrap
                lineHeight: 1.18
                textFormat: Text.PlainText
            }
        }
    }

    Item {
        id: emptyStateWrap
        objectName: "sidebarEmptyState"
        anchors.top: parent.top
        anchors.topMargin: 18
        anchors.horizontalCenter: parent.horizontalCenter
        width: root.emptyStateWidth
        height: emptyStateContent.implicitHeight
        visible: root.listView
            && root.listView.count === 0
            && !(root.hasSessionService && root.sessionService.sessionsLoading)

        Column {
            id: emptyStateContent
            width: parent.width
            spacing: 11

            Item {
                width: parent.width
                height: 50

                Item {
                    width: 50
                    height: 50
                    anchors.horizontalCenter: parent.horizontalCenter

                    Rectangle {
                        width: 46
                        height: 46
                        radius: 23
                        anchors.centerIn: parent
                        color: root.emptyIconFillColor
                        border.width: 1
                        border.color: root.emptyIconBorderColor

                        Behavior on color { ColorAnimation { duration: motionFast; easing.type: easeStandard } }
                        Behavior on border.color { ColorAnimation { duration: motionFast; easing.type: easeStandard } }

                        AppIcon {
                            objectName: "sidebarEmptyChatIcon"
                            width: 18
                            height: 18
                            anchors.centerIn: parent
                            source: themedIconSource("chat")
                            sourceSize: Qt.size(18, 18)
                            opacity: 0.96
                        }
                    }

                    Rectangle {
                        width: 16
                        height: 16
                        radius: 8
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.rightMargin: 4
                        anchors.topMargin: 4
                        color: root.emptyButtonFillColor

                        Behavior on color { ColorAnimation { duration: motionFast; easing.type: easeStandard } }

                        PlusGlyph {
                            glyphSize: 7
                            barThickness: 1.8
                            glyphColor: bgSidebar
                            anchors.centerIn: parent
                        }
                    }
                }
            }

            Text {
                objectName: "sidebarEmptyTitle"
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                text: strings.sidebar_empty_title
                color: root.stateTitleColor
                font.pixelSize: typeBody + 1
                font.weight: weightBold
                wrapMode: Text.WordWrap
                textFormat: Text.PlainText
            }

            Text {
                objectName: "sidebarEmptyHint"
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                text: strings.sidebar_empty_hint
                color: root.stateHintColor
                font.pixelSize: typeMeta
                wrapMode: Text.WordWrap
                textFormat: Text.PlainText
            }

            Item {
                width: parent.width
                height: emptyStateButton.implicitHeight

                PillActionButton {
                    id: emptyStateButton
                    objectName: "sidebarEmptyCta"
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: strings.sidebar_empty_cta
                    leadingText: "+"
                    minHeight: 28
                    horizontalPadding: 18
                    fillColor: root.emptyButtonFillColor
                    hoverFillColor: accent
                    outlineColor: emptyStateMouse.containsMouse ? accent : sessionRowActiveBorder
                    hoverOutlineColor: accent
                    textColor: bgSidebar
                    onClicked: root.browserRoot.requestNewSession()
                }
            }

        }

        MouseArea {
            id: emptyStateMouse
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: root.browserRoot.requestNewSession()
        }
    }
}
