import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root

    required property var appRoot
    required property var toastTarget
    required property var modalTarget

    objectName: "diagnosticsEventsCard"
    Layout.preferredWidth: 392
    Layout.fillHeight: true
    radius: 16
    color: appRoot.isDark ? "#15110F" : "#FBF7F2"
    border.width: 1
    border.color: appRoot.design.borderSubtle

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Rectangle {
                Layout.preferredWidth: 30
                Layout.preferredHeight: 30
                radius: 10
                color: appRoot.isDark ? "#1F1814" : "#F1E8DF"

                AppIcon {
                    width: 24
                    height: 24
                    anchors.centerIn: parent
                    source: appRoot.diagnosticsSectionIcon("events")
                    sourceSize: Qt.size(24, 24)
                }
            }

            Text {
                Layout.fillWidth: true
                text: appRoot.strings.diagnostics_recent_events
                color: appRoot.design.textPrimary
                font.pixelSize: appRoot.design.typeBody + 1
                font.weight: appRoot.design.weightBold
            }

            PillActionButton {
                text: appRoot.strings.diagnostics_ask_bao
                visible: appRoot.diagnosticsEventCountSafe() > 0
                minHeight: 26
                horizontalPadding: 14
                fillColor: appRoot.design.accentGlow
                hoverFillColor: appRoot.design.accent
                outlineColor: appRoot.design.accent
                hoverOutlineColor: appRoot.design.accent
                textColor: appRoot.isDark ? appRoot.design.bgSidebar : "#FFFFFF"
                onClicked: {
                    if (!appRoot.hasDiagnosticsService || !appRoot.hasChatService)
                        return
                    var prompt = appRoot.diagnosticsService.buildAssistantPrompt()
                    if (!prompt)
                        return
                    modalTarget.close()
                    appRoot.startView = "chat"
                    appRoot.chatService.sendMessage(prompt)
                    toastTarget.show(appRoot.strings.diagnostics_sent, true)
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            color: appRoot.design.borderSubtle
        }

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            Column {
                anchors.centerIn: parent
                spacing: 10
                visible: appRoot.diagnosticsEventCountSafe() === 0

                Rectangle {
                    width: 40
                    height: 40
                    radius: 14
                    anchors.horizontalCenter: parent.horizontalCenter
                    color: appRoot.isDark ? "#1F1814" : "#F1E8DF"

                    AppIcon {
                        width: 24
                        height: 24
                        anchors.centerIn: parent
                        source: appRoot.diagnosticsSectionIcon("events")
                        sourceSize: Qt.size(24, 24)
                    }
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: appRoot.strings.diagnostics_empty_events
                    color: appRoot.design.textSecondary
                    wrapMode: Text.WordWrap
                    horizontalAlignment: Text.AlignHCenter
                    font.pixelSize: appRoot.design.typeMeta + 1
                }
            }

            ScrollView {
                anchors.fill: parent
                visible: appRoot.diagnosticsEventCountSafe() > 0
                clip: true

                Column {
                    width: parent.width
                    spacing: 0

                    Repeater {
                        model: appRoot.diagnosticsEventsSafe()

                        delegate: Item {
                            required property var modelData

                            width: parent.width
                            height: eventBody.implicitHeight + 18

                            Rectangle {
                                anchors.left: parent.left
                                anchors.top: parent.top
                                anchors.bottom: parent.bottom
                                width: 3
                                radius: 1.5
                                color: {
                                    var level = String(modelData.level || "")
                                    if (level === "error")
                                        return appRoot.isDark ? "#D06A5B" : "#D65C45"
                                    if (level === "warning")
                                        return appRoot.isDark ? "#D5A44A" : "#D58B23"
                                    return appRoot.isDark ? "#7C6A58" : "#C8B5A2"
                                }
                            }

                            Column {
                                id: eventBody
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.leftMargin: 14
                                anchors.rightMargin: 4
                                anchors.verticalCenter: parent.verticalCenter
                                spacing: 4

                                RowLayout {
                                    width: parent.width
                                    spacing: 8

                                    Text {
                                        text: String(modelData.code || modelData.stage || "event")
                                        color: appRoot.design.textPrimary
                                        font.pixelSize: appRoot.design.typeMeta
                                        font.weight: appRoot.design.weightBold
                                    }

                                    Item { Layout.fillWidth: true }

                                    Text {
                                        text: String(modelData.timestamp || "")
                                        color: appRoot.design.textTertiary
                                        font.pixelSize: appRoot.design.typeMeta - 1
                                    }
                                }

                                Text {
                                    width: parent.width
                                    text: String(modelData.message || "")
                                    color: appRoot.design.textPrimary
                                    wrapMode: Text.WordWrap
                                    font.pixelSize: appRoot.design.typeMeta + 1
                                    font.weight: appRoot.design.weightDemiBold
                                }

                                Text {
                                    width: parent.width
                                    text: [String(modelData.source || ""), String(modelData.session_key || "")].filter(Boolean).join(" · ")
                                    color: appRoot.design.textSecondary
                                    wrapMode: Text.WordWrap
                                    font.pixelSize: appRoot.design.typeMeta - 1
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
