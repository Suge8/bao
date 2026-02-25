import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root

    property string currentView: "chat"
    signal viewRequested(string view)
    signal newSessionRequested()
    signal sessionSelected(string key)
    signal sessionDeleteRequested(string key)

    color: "transparent"

    Rectangle {
        anchors.fill: parent
        radius: 20
        color: bgSidebar
        antialiasing: true

        Rectangle {
            anchors { top: parent.top; left: parent.left; right: parent.right }
            height: parent.radius
            color: parent.color
        }
        Rectangle {
            anchors { top: parent.top; bottom: parent.bottom; right: parent.right }
            width: parent.radius
            color: parent.color
        }
    }

    ListModel { id: groupModel }

    property var expandedGroups: ({})

    function rebuildGroupModel() {
        if (!sessionService) return
        var sm = sessionService.sessionsModel
        if (!sm) return

        var groups = {}
        var order = []
        for (var i = 0; i < sm.rowCount(); i++) {
            var idx = sm.index(i, 0)
            var key     = sm.data(idx, Qt.UserRole + 1) || ""
            var title   = sm.data(idx, Qt.UserRole + 2) || key
            var active  = sm.data(idx, Qt.UserRole + 3) || false
            var channel = sm.data(idx, Qt.UserRole + 5) || "other"
            if (!groups[channel]) { groups[channel] = []; order.push(channel) }
            groups[channel].push({ key: key, title: title, isActive: active, channel: channel })
        }

        order.sort(function(a, b) {
            if (a === "desktop") return -1
            if (b === "desktop") return 1
            return a < b ? -1 : 1
        })

        for (var ci = 0; ci < order.length; ci++) {
            var ch = order[ci]
            if (!(ch in root.expandedGroups))
                root.expandedGroups[ch] = (ch === "desktop")
        }

        groupModel.clear()
        for (var gi = 0; gi < order.length; gi++) {
            var grp = order[gi]
            var exp = root.expandedGroups[grp] === true
            groupModel.append({ isHeader: true,  channel: grp, expanded: exp,
                                 itemKey: "", itemTitle: "", isActive: false, itemVisible: true })
            var items = groups[grp]
            for (var si = 0; si < items.length; si++) {
                var s = items[si]
                groupModel.append({ isHeader: false, channel: grp, expanded: false,
                                     itemKey: s.key, itemTitle: s.title, isActive: s.isActive,
                                     itemVisible: exp })
            }
        }
    }

    function toggleGroup(channel) {
        var newExp = !(root.expandedGroups[channel] === true)
        root.expandedGroups[channel] = newExp
        for (var i = 0; i < groupModel.count; i++) {
            var item = groupModel.get(i)
            if (item.channel === channel) {
                if (item.isHeader)
                    groupModel.setProperty(i, "expanded", newExp)
                else
                    groupModel.setProperty(i, "itemVisible", newExp)
            }
        }
    }

    Connections {
        target: sessionService
        function onSessionsChanged() { root.rebuildGroupModel() }
    }

    Component.onCompleted: rebuildGroupModel()

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // ── Nav buttons ──────────────────────────────────────────────────
        Item {
            Layout.fillWidth: true
            height: 108

            ColumnLayout {
                anchors { top: parent.top; left: parent.left; right: parent.right; topMargin: 16 }
                spacing: 4

                Repeater {
                    model: [
                        { iconSource: "../resources/icons/chat.svg", view: "chat"     },
                        { iconSource: "../resources/icons/settings.svg",  view: "settings" }
                    ]
                    delegate: NavButton {
                        Layout.fillWidth: true
                        Layout.leftMargin: 10
                        Layout.rightMargin: 10
                        iconSource: modelData.iconSource
                        label: modelData.view === "chat" ? strings.nav_chat : strings.nav_settings
                        active: root.currentView === modelData.view
                        onClicked: {
                            root.currentView = modelData.view
                            root.viewRequested(modelData.view)
                        }
                    }
                }
            }
        }

        // ── Sessions header ───────────────────────────────────────────────
        RowLayout {
            Layout.fillWidth: true
            Layout.leftMargin: 16
            Layout.rightMargin: 12
            Layout.topMargin: 14
            Layout.bottomMargin: 10
            spacing: 0

            Text {
                text: strings.sidebar_sessions
                color: textSecondary
                font.pixelSize: 15
                font.weight: Font.DemiBold
                font.letterSpacing: 0.5
                textFormat: Text.PlainText
                Layout.fillWidth: true
            }

            Rectangle {
                width: 36
                height: 36
                radius: 18
                color: newSessionHover.containsMouse ? accent : accentMuted
                border.width: 1
                border.color: newSessionHover.containsMouse ? accent : borderSubtle
                scale: newSessionHover.containsMouse ? 1.04 : 1.0
                Behavior on color { ColorAnimation { duration: 140 } }
                Behavior on scale { NumberAnimation { duration: 140 } }

                Text {
                    anchors.centerIn: parent
                    text: "+"
                    color: "#FFFFFF"
                    font.pixelSize: 22
                    font.weight: Font.DemiBold
                }

                MouseArea {
                    id: newSessionHover
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.newSessionRequested()
                }
            }
        }

        // ── Session list ──────────────────────────────────────────────────
        ListView {
            id: sessionList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: groupModel
            spacing: 0
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

            delegate: Item {
                width: sessionList.width
                // height driven by content type
                height: model.isHeader ? 38 : sessionRow.height

                // ── Group header row ──────────────────────────────────────
                Rectangle {
                    visible: model.isHeader
                    anchors { left: parent.left; right: parent.right; top: parent.top }
                    height: 38
                    color: "transparent"

                    RowLayout {
                        anchors { fill: parent; leftMargin: 14; rightMargin: 10 }
                        spacing: 6

                        Text {
                            text: model.expanded ? "▾" : "▸"
                            color: textPrimary
                            font.pixelSize: 15
                            font.weight: Font.DemiBold
                        }
                        Text {
                            text: model.channel || "other"
                            color: textPrimary
                            font.pixelSize: 15
                            font.weight: Font.DemiBold
                            font.letterSpacing: 0.4
                            textFormat: Text.PlainText
                            Layout.fillWidth: true
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.toggleGroup(model.channel)
                    }
                }

                // ── Session item row ──────────────────────────────────────
                Item {
                    id: sessionRow
                    visible: !model.isHeader
                    anchors { left: parent.left; right: parent.right; top: parent.top }
                    height: model.itemVisible ? (inner.height + 4) : 0
                    clip: true
                    Behavior on height { NumberAnimation { duration: 120; easing.type: Easing.OutCubic } }

                    SessionItem {
                        id: inner
                        width: parent.width - 20
                        x: 10
                        sessionKey:   model.itemKey   ?? ""
                        sessionTitle: model.itemTitle ?? model.itemKey ?? ""
                        isActive:     model.isActive  ?? false
                        onSelected:       root.sessionSelected(sessionKey)
                        onDeleteRequested: root.sessionDeleteRequested(sessionKey)
                    }
                }
            }

            // Empty state
            Text {
                anchors.centerIn: parent
                visible: groupModel.count === 0
                text: strings.sidebar_no_sessions
                color: textTertiary
                font.pixelSize: 13
            }
        }
    }
}
