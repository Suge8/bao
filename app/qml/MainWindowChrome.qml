import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: chrome

    required property var appRoot
    readonly property bool compactSidebar: width <= 720
    readonly property int sidebarPreferredWidth: compactSidebar ? 224 : 240

    anchors.fill: parent
    radius: appRoot.chromeRadius
    color: appRoot.design.bgSidebar
    antialiasing: true
    opacity: 1.0

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        Item {
            id: titleBar
            Layout.fillWidth: true
            visible: !appRoot.useNativeTitleBar
            Layout.preferredHeight: visible ? 48 : 0

            MouseArea {
                anchors.fill: parent
                visible: !appRoot.useNativeTitleBar
                enabled: visible
                acceptedButtons: Qt.LeftButton
                hoverEnabled: true
                cursorShape: Qt.ArrowCursor
                onPressed: function(mouse) {
                    if (mouse.x < 92 || mouse.x > parent.width - 120) {
                        mouse.accepted = false
                        return
                    }
                    appRoot.startSystemMove()
                }
            }

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 12
                spacing: 0

                Row {
                    visible: !appRoot.useNativeTitleBar
                    spacing: 8

                    Repeater {
                        model: [
                            { color: "#FF5F57", hoverColor: "#FF3B30", action: "close" },
                            { color: "#FEBC2E", hoverColor: "#F5A623", action: "minimize" },
                            { color: "#28C840", hoverColor: "#1DB954", action: "maximize" }
                        ]

                        delegate: Rectangle {
                            width: 14
                            height: 14
                            radius: 7
                            color: tlHover.containsMouse ? modelData.hoverColor : modelData.color
                            opacity: tlHover.containsMouse ? 1.0 : appRoot.design.opacityInactive

                            Behavior on color { ColorAnimation { duration: appRoot.design.motionMicro; easing.type: appRoot.design.easeStandard } }
                            Behavior on opacity { NumberAnimation { duration: appRoot.design.motionMicro; easing.type: appRoot.design.easeStandard } }

                            Text {
                                anchors.centerIn: parent
                                text: modelData.action === "close" ? "✕"
                                      : (modelData.action === "minimize" ? "−" : "+")
                                color: "#60000000"
                                font.pixelSize: 8
                                font.weight: Font.Bold
                                visible: tlHover.containsMouse
                            }

                            MouseArea {
                                id: tlHover
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (modelData.action === "close") {
                                        appRoot.close()
                                    } else if (modelData.action === "minimize") {
                                        appRoot.showMinimized()
                                    } else {
                                        appRoot.showMaximized()
                                    }
                                }
                            }
                        }
                    }
                }

                Item { Layout.fillWidth: true }

                Text {
                    text: "Bao"
                    color: appRoot.design.textPrimary
                    font.pixelSize: 14
                    font.weight: Font.DemiBold
                    font.letterSpacing: 0.5
                    opacity: 0.7
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: appRoot.design.bgBase
            radius: chrome.radius
            antialiasing: true

            Rectangle {
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                height: parent.radius
                color: parent.color
            }

            RowLayout {
                anchors.fill: parent
                spacing: 0

                Sidebar {
                    objectName: "appSidebar"
                    id: sidebar
                    Layout.preferredWidth: chrome.sidebarPreferredWidth
                    Layout.fillHeight: true
                    z: 20
                    visible: !appRoot.setupMode
                    selectionTarget: appRoot.sidebarSelectionTarget
                    chatService: appRoot.chatService
                    profileService: appRoot.profileService
                    sessionService: appRoot.sessionService
                    supervisorService: appRoot.profileSupervisorService
                    diagnosticsService: appRoot.diagnosticsService
                    onSettingsRequested: appRoot.startView = "settings"
                    onDiagnosticsRequested: appRoot.openDiagnostics()
                    onSectionRequested: function(section) {
                        appRoot.activeWorkspace = section
                        appRoot.startView = "chat"
                    }
                    onNewSessionRequested: if (appRoot.hasSessionService) appRoot.sessionService.newSession("")
                    onSessionSelected: function(key) {
                        if (appRoot.hasSessionService)
                            appRoot.sessionService.selectSession(key)
                        appRoot.activeWorkspace = "sessions"
                        appRoot.startView = "chat"
                    }
                    onSessionDeleteRequested: function(key) {
                        if (!appRoot.hasSessionService)
                            return
                        appRoot.sessionService.deleteSession(key)
                    }
                }

                StackLayout {
                    objectName: "mainStack"
                    id: stack
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.minimumWidth: 0
                    currentIndex: appRoot.currentPageIndex

                    MainChatPage {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.minimumWidth: 0
                        clip: true
                        appRoot: chrome.appRoot
                        cornerRadius: chrome.radius
                    }

                    MainSettingsPage {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.minimumWidth: 0
                        clip: true
                        appRoot: chrome.appRoot
                        cornerRadius: chrome.radius
                    }
                }
            }
        }
    }
}
