import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    property var sessionService: null
    property bool hasSessionService: false
    readonly property bool compactHeader: width <= 220
    readonly property int headerSpacing: compactHeader ? 6 : 8
    readonly property int titleRowHeight: compactHeader ? 32 : 34
    readonly property int searchBoxHeight: compactHeader ? 34 : 36
    readonly property int searchIconSize: compactHeader ? 14 : 16
    readonly property int searchIconLeftMargin: compactHeader ? 10 : 12
    readonly property int searchFieldLeftMargin: compactHeader ? 30 : 36
    readonly property int searchFieldRightMargin: compactHeader ? 6 : 8
    readonly property int clearButtonSize: compactHeader ? 22 : 24
    readonly property int clearButtonRightMargin: compactHeader ? 4 : 6
    readonly property int discoveryChipSpacing: compactHeader ? 6 : 8
    readonly property int discoveryChipHeight: compactHeader ? 26 : 28
    readonly property int discoveryChipPadding: compactHeader ? 12 : 14
    readonly property real discoveryChipMaxWidth: Math.max(136, Math.min(width - 10, compactHeader ? 184 : 220))
    readonly property string lookupPlaceholderText: compactHeader
        ? strings.sidebar_session_lookup_placeholder_compact
        : strings.sidebar_session_lookup_placeholder
    readonly property var defaultSession: root.hasSessionService ? (root.sessionService.defaultSession || ({})) : ({})
    readonly property var resolvedSession: root.hasSessionService ? (root.sessionService.resolvedSession || ({})) : ({})
    readonly property var recentSessions: root.hasSessionService ? (root.sessionService.recentSessions || []) : []
    readonly property var lookupResults: root.hasSessionService ? (root.sessionService.lookupResults || []) : []
    readonly property string lookupQuery: root.hasSessionService ? String(root.sessionService.sessionLookupQuery || "") : ""
    readonly property bool showingLookup: root.lookupQuery !== ""
    readonly property bool hasDiscoveryItems: root.showingLookup
        ? (root.lookupResults.length > 0 || String(root.resolvedSession.session_ref || "") !== "")
        : (root.recentSessions.length > 0 || String(root.defaultSession.session_ref || "") !== "")
    readonly property var discoveryChips: {
        var chips = []
        if (!root.showingLookup && String(root.defaultSession.session_ref || "") !== "") {
            chips.push(
                root.buildDiscoveryChip(
                    "default",
                    "sessionDefaultChip",
                    root.defaultSession,
                    strings.sidebar_session_default_label,
                )
            )
        }
        if (root.showingLookup && String(root.resolvedSession.session_ref || "") !== "") {
            chips.push(
                root.buildDiscoveryChip(
                    "resolved",
                    "sessionResolvedChip",
                    root.resolvedSession,
                    strings.sidebar_session_resolved_label,
                )
            )
        }

        var dynamicItems = root.showingLookup ? root.lookupResults : root.recentSessions
        for (var i = 0; i < dynamicItems.length; ++i) {
            var item = dynamicItems[i] || {}
            chips.push(
                root.buildDiscoveryChip(
                    "recent",
                    root.discoveryChipObjectName("sessionRecentChip", item),
                    item,
                    !root.showingLookup && i === 0 ? strings.sidebar_session_recent_label : "",
                )
            )
        }
        return chips
    }

    signal newSessionRequested()
    signal discoverySessionRequested(string key)

    objectName: "sessionsHeaderBar"
    implicitHeight: headerColumn.implicitHeight

    function refreshDiscoveryQuery(text) {
        if (!root.hasSessionService)
            return
        var nextValue = String(text || "")
        root.sessionService.setSessionLookupQuery(nextValue)
        root.clearResolvedSessionReference()
    }

    function clearDiscoveryQuery() {
        if (!root.hasSessionService)
            return
        if (typeof root.sessionService.clearSessionLookup === "function")
            root.sessionService.clearSessionLookup()
        else
            root.sessionService.setSessionLookupQuery("")
        root.clearResolvedSessionReference()
    }

    function clearResolvedSessionReference() {
        if (!root.hasSessionService)
            return
        root.sessionService.resolveSessionReference("")
    }

    function openDiscoveryItem(item) {
        var nextItem = item || {}
        var sessionKey = String(nextItem.session_key || "")
        if (sessionKey !== "") {
            root.discoverySessionRequested(sessionKey)
            return
        }
        var sessionRef = String(nextItem.session_ref || "")
        if (sessionRef !== "" && root.hasSessionService)
            root.sessionService.resolveSessionReference(sessionRef)
    }

    function discoveryChipObjectName(prefix, item) {
        var nextItem = item || {}
        var rawKey = String(nextItem.session_key || nextItem.session_ref || nextItem.title || "")
        var sanitized = rawKey.replace(/[^A-Za-z0-9]+/g, "_").replace(/^_+|_+$/g, "")
        return sanitized !== "" ? prefix + "_" + sanitized : prefix
    }

    function discoveryChipPalette(kind) {
        if (kind === "default") {
            return {
                "fillColor": isDark ? "#1C2C24" : "#E6F5EB",
                "hoverFillColor": isDark ? "#254032" : "#D9F0E1",
                "outlineColor": isDark ? "#315342" : "#B6D8C0",
                "textColor": isDark ? "#DDF4E5" : "#28573B",
                "categoryTextColor": isDark ? "#DDF4E5" : "#28573B"
            }
        }
        if (kind === "resolved") {
            return {
                "fillColor": isDark ? "#20263A" : "#E8EEFF",
                "hoverFillColor": isDark ? "#2A3350" : "#DCE5FF",
                "outlineColor": isDark ? "#39476B" : "#BFCDFE",
                "textColor": isDark ? "#E3EAFE" : "#31457A",
                "categoryTextColor": isDark ? "#E3EAFE" : "#31457A"
            }
        }
        return {
            "fillColor": isDark ? "#14FFFFFF" : "#14FFF7EF",
            "hoverFillColor": isDark ? "#1EFFFFFF" : "#1FFFF7EF",
            "outlineColor": isDark ? "#28FFFFFF" : "#206E4B2A",
            "textColor": textPrimary,
            "categoryTextColor": textSecondary
        }
    }

    function buildDiscoveryChip(kind, objectName, item, label) {
        var palette = root.discoveryChipPalette(kind)
        return {
            "kind": kind,
            "objectName": objectName,
            "item": item || {},
            "label": label || "",
            "fillColor": palette.fillColor,
            "hoverFillColor": palette.hoverFillColor,
            "outlineColor": palette.outlineColor,
            "textColor": palette.textColor,
            "categoryTextColor": palette.categoryTextColor
        }
    }

    function discoveryChipAt(index) {
        if (index < 0 || index >= root.discoveryChips.length)
            return {}
        return root.discoveryChips[index] || {}
    }

    Column {
        id: headerColumn
        anchors.fill: parent
        spacing: root.headerSpacing

        Item {
            width: parent.width
            height: root.titleRowHeight

            Item {
                anchors.left: parent.left
                anchors.right: newSessionButton.left
                anchors.rightMargin: 12
                anchors.verticalCenter: parent.verticalCenter
                height: parent.height

                Row {
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 8

                    AppIcon {
                        objectName: "sidebarSessionsTitleIcon"
                        width: 22
                        height: 22
                        anchors.verticalCenter: parent.verticalCenter
                        y: 1
                        source: themedIconSource("sidebar-sessions-title")
                        sourceSize: Qt.size(22, 22)
                        opacity: 0.98
                    }

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: strings.sidebar_sessions
                        color: textPrimary
                        font.pixelSize: typeBody + 2
                        font.weight: weightBold
                        font.letterSpacing: 0.35
                        textFormat: Text.PlainText
                        opacity: 0.96
                    }

                    UnreadBadge {
                        badgeObjectName: "sessionsHeaderUnreadBadge"
                        textObjectName: "sessionsHeaderUnreadText"
                        anchors.verticalCenter: parent.verticalCenter
                        active: root.hasSessionService && (root.sessionService.sidebarUnreadCount || 0) > 0
                        count: root.hasSessionService ? (root.sessionService.sidebarUnreadCount || 0) : 0
                        mode: "count"
                        fillColor: sidebarHeaderBadgeBg
                        textColor: sidebarHeaderBadgeText
                    }
                }
            }

            IconCircleButton {
                id: newSessionButton
                objectName: "newSessionButton"
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                buttonSize: sizeControlHeight - 6
                glyphText: "+"
                glyphSize: 18
                fillColor: isDark ? "#12FFFFFF" : "#16000000"
                hoverFillColor: accent
                outlineColor: newSessionButton.hovered ? accent : "transparent"
                glyphColor: newSessionButton.hovered ? "#FFFFFFFF" : textPrimary
                hoverScale: motionHoverScaleMedium
                onClicked: root.newSessionRequested()
            }
        }

        Rectangle {
            objectName: "sessionDiscoverySearchBox"
            width: parent.width
            height: root.searchBoxHeight
            radius: 18
            color: isDark ? "#12FFFFFF" : "#16000000"
            border.width: searchField.activeFocus ? 1.5 : 1
            border.color: searchField.activeFocus ? borderFocus : borderSubtle

            AppIcon {
                anchors.left: parent.left
                anchors.leftMargin: root.searchIconLeftMargin
                anchors.verticalCenter: parent.verticalCenter
                width: root.searchIconSize
                height: root.searchIconSize
                source: "../resources/icons/vendor/iconoir/page-search.svg"
                sourceSize: Qt.size(width, height)
                opacity: 0.72
            }

            TextField {
                id: searchField
                objectName: "sessionDiscoverySearchField"
                anchors.left: parent.left
                anchors.right: clearButton.visible ? clearButton.left : parent.right
                anchors.leftMargin: root.searchFieldLeftMargin
                anchors.rightMargin: root.searchFieldRightMargin
                anchors.verticalCenter: parent.verticalCenter
                height: parent.height - 8
                color: textPrimary
                text: root.lookupQuery
                placeholderText: root.lookupPlaceholderText
                placeholderTextColor: textPlaceholder
                background: null
                selectByMouse: true
                onTextEdited: root.refreshDiscoveryQuery(text)
            }

            IconCircleButton {
                id: clearButton
                objectName: "sessionDiscoveryClearButton"
                visible: searchField.text !== ""
                anchors.right: parent.right
                anchors.rightMargin: root.clearButtonRightMargin
                anchors.verticalCenter: parent.verticalCenter
                buttonSize: root.clearButtonSize
                glyphText: "×"
                glyphSize: 14
                fillColor: "transparent"
                hoverFillColor: isDark ? "#16FFFFFF" : "#14000000"
                outlineColor: "transparent"
                glyphColor: textSecondary
                onClicked: {
                    searchField.text = ""
                    root.clearDiscoveryQuery()
                }
            }
        }

        ListView {
            objectName: "sessionDiscoveryStrip"
            width: parent.width
            height: root.hasDiscoveryItems ? root.discoveryChipHeight : 0
            visible: height > 0
            orientation: ListView.Horizontal
            boundsBehavior: Flickable.StopAtBounds
            boundsMovement: Flickable.StopAtBounds
            clip: true
            spacing: root.discoveryChipSpacing
            model: root.discoveryChips.length

            delegate: SessionDiscoveryChip {
                required property int index
                readonly property var chipConfig: root.discoveryChipAt(index)
                readonly property var chipItem: chipConfig.item || ({})
                chipObjectName: String(chipConfig.objectName || "")
                text: String(chipItem.title || chipItem.session_key || chipItem.session_ref || "")
                categoryLabel: String(chipConfig.label || "")
                minHeight: root.discoveryChipHeight
                horizontalPadding: root.discoveryChipPadding
                maxWidth: root.discoveryChipMaxWidth
                fillColor: chipConfig.fillColor || "transparent"
                hoverFillColor: chipConfig.hoverFillColor || fillColor
                outlineColor: chipConfig.outlineColor || "transparent"
                hoverOutlineColor: outlineColor
                textColor: chipConfig.textColor || textPrimary
                categoryTextColor: chipConfig.categoryTextColor || textSecondary
                onClicked: root.openDiscoveryItem(chipItem)
            }
        }
    }
}
