function finishProjectionMotion(root, listView) {
    root.projectionMotionEnabled = false
    updateActiveHighlight(root, listView)
}

function syncViewportHighlight(root, listView, clampContentY) {
    if (clampContentY && listView)
        listView.contentY = clampListContentY(root, listView, listView.contentY)
    if (!root.projectionMotionEnabled)
        updateActiveHighlight(root, listView)
}

function findActiveSessionDelegate(root, listView) {
    if (!listView || !listView.contentItem)
        return null
    var children = listView.contentItem.children
    for (var i = 0; i < children.length; i++) {
        var child = children[i]
        if (!child || child.anchorReady !== true)
            continue
        if (child.anchorIsHeader)
            continue
        if ((child.anchorKey || "") !== root.activeSessionKey)
            continue
        return child
    }
    return null
}

function updateActiveHighlight(root, listView) {
    var target = findActiveSessionDelegate(root, listView)
    if (!target) {
        root.activeHighlightOpacity = 0.0
        return
    }
    root.activeHighlightX = target.highlightContentX
    root.activeHighlightY = target.highlightContentY - listView.contentY
    root.activeHighlightWidth = target.highlightContentWidth
    root.activeHighlightHeight = target.highlightContentHeight
    root.activeHighlightOpacity = root.showSelection ? 1.0 : 0.0
}

function channelVisualSource(darkMode, channel, filled) {
    switch (channel) {
    case "telegram":
        return "../resources/icons/channel-telegram.svg"
    case "discord":
        return "../resources/icons/channel-discord.svg"
    case "whatsapp":
        return "../resources/icons/channel-whatsapp.svg"
    case "feishu":
        return "../resources/icons/channel-feishu.svg"
    case "slack":
        return "../resources/icons/channel-slack.svg"
    case "qq":
        return "../resources/icons/channel-qq.svg"
    case "dingtalk":
        return "../resources/icons/channel-dingtalk.svg"
    case "imessage":
        return "../resources/icons/channel-imessage.svg"
    case "desktop":
        if (filled) {
            return darkMode
                ? "../resources/icons/sidebar-monitor-solid-dark.svg"
                : "../resources/icons/sidebar-monitor-solid.svg"
        }
        return darkMode
            ? "../resources/icons/sidebar-monitor-dark.svg"
            : "../resources/icons/sidebar-monitor.svg"
    case "subagent":
        return filled
            ? "../resources/icons/sidebar-subagent-solid.svg"
            : "../resources/icons/sidebar-subagent.svg"
    case "system":
        return filled
            ? "../resources/icons/sidebar-system-solid.svg"
            : "../resources/icons/sidebar-system.svg"
    case "heartbeat":
        return filled
            ? "../resources/icons/sidebar-heartbeat-solid.svg"
            : "../resources/icons/sidebar-heartbeat.svg"
    case "cron":
        return filled
            ? "../resources/icons/sidebar-cron-solid.svg"
            : "../resources/icons/sidebar-cron.svg"
    case "email":
        return filled
            ? "../resources/icons/sidebar-mail-solid.svg"
            : "../resources/icons/sidebar-mail.svg"
    default:
        return filled
            ? "../resources/icons/sidebar-chat-solid.svg"
            : "../resources/icons/sidebar-chat.svg"
    }
}

function channelUsesTint(channel) {
    switch (channel) {
    case "telegram":
    case "discord":
    case "whatsapp":
    case "feishu":
    case "slack":
    case "qq":
    case "dingtalk":
    case "imessage":
        return true
    default:
        return false
    }
}

function channelAccent(darkMode, channel) {
    switch (channel) {
    case "telegram":
        return darkMode ? Qt.rgba(0.33, 0.73, 1.0, 1.0) : Qt.rgba(0.00, 0.60, 0.96, 1.0)
    case "discord":
        return darkMode ? Qt.rgba(0.56, 0.60, 1.0, 1.0) : Qt.rgba(0.39, 0.44, 1.0, 1.0)
    case "whatsapp":
        return darkMode ? Qt.rgba(0.31, 0.90, 0.53, 1.0) : Qt.rgba(0.00, 0.78, 0.34, 1.0)
    case "feishu":
        return darkMode ? Qt.rgba(0.54, 0.71, 1.0, 1.0) : Qt.rgba(0.17, 0.52, 0.98, 1.0)
    case "slack":
        return darkMode ? Qt.rgba(0.99, 0.58, 0.76, 1.0) : Qt.rgba(0.83, 0.12, 0.44, 1.0)
    case "qq":
        return darkMode ? Qt.rgba(0.61, 0.67, 1.0, 1.0) : Qt.rgba(0.24, 0.40, 0.98, 1.0)
    case "dingtalk":
        return darkMode ? Qt.rgba(0.38, 0.74, 1.0, 1.0) : Qt.rgba(0.00, 0.62, 0.97, 1.0)
    case "imessage":
        return darkMode ? Qt.rgba(0.54, 0.70, 1.0, 1.0) : Qt.rgba(0.12, 0.62, 1.0, 1.0)
    case "desktop":
        return darkMode ? Qt.rgba(1.0, 0.78, 0.29, 1.0) : Qt.rgba(0.97, 0.63, 0.05, 1.0)
    case "subagent":
        return darkMode ? Qt.rgba(1.0, 0.72, 0.24, 1.0) : Qt.rgba(0.96, 0.57, 0.00, 1.0)
    case "system":
        return darkMode ? Qt.rgba(0.53, 0.82, 1.0, 1.0) : Qt.rgba(0.18, 0.67, 0.98, 1.0)
    case "heartbeat":
        return darkMode ? Qt.rgba(0.20, 0.90, 0.56, 1.0) : Qt.rgba(0.00, 0.82, 0.40, 1.0)
    case "cron":
        return darkMode ? Qt.rgba(1.0, 0.66, 0.18, 1.0) : Qt.rgba(0.99, 0.58, 0.00, 1.0)
    case "email":
        return darkMode ? Qt.rgba(0.46, 0.69, 1.0, 1.0) : Qt.rgba(0.16, 0.56, 0.95, 1.0)
    default:
        return darkMode ? Qt.rgba(0.79, 0.55, 1.0, 1.0) : Qt.rgba(0.52, 0.27, 0.84, 1.0)
    }
}

function listContentYBounds(listView) {
    var minY = listView ? listView.originY : 0
    var maxY = minY
    if (listView)
        maxY = minY + Math.max(0, listView.contentHeight - listView.height)
    return { minY: minY, maxY: maxY }
}

function clampListContentY(_root, listView, y) {
    var bounds = listContentYBounds(listView)
    return Math.max(bounds.minY, Math.min(y, bounds.maxY))
}

function visibleDelegates(root, listView) {
    if (!listView || !listView.contentItem)
        return []
    var delegates = []
    var children = listView.contentItem.children
    var minY = listView.contentY - root.viewportPadding
    var maxY = listView.contentY + listView.height + root.viewportPadding
    for (var i = 0; i < children.length; i++) {
        var child = children[i]
        if (!child || child.anchorReady !== true)
            continue
        var childTop = child.y
        var childBottom = child.y + child.height
        if (childBottom < minY || childTop > maxY)
            continue
        delegates.push(child)
    }
    delegates.sort(function(a, b) { return a.y - b.y })
    return delegates
}

function findVisibleAnchorDelegate(root, listView, targetY) {
    var delegates = visibleDelegates(root, listView)
    for (var i = 0; i < delegates.length; i++) {
        var delegate = delegates[i]
        if (delegate.height <= 0)
            continue
        if (delegate.y + delegate.height > targetY)
            return delegate
    }
    return null
}

function findVisibleDelegateByAnchor(root, listView, anchor) {
    if (!anchor)
        return null
    var delegates = visibleDelegates(root, listView)
    for (var i = 0; i < delegates.length; i++) {
        var delegate = delegates[i]
        if (anchor.isHeader) {
            if (delegate.anchorIsHeader && delegate.anchorChannel === anchor.channel)
                return delegate
            continue
        }
        if (!delegate.anchorIsHeader && delegate.anchorKey === anchor.key)
            return delegate
    }
    return null
}

function captureScrollAnchor(root, listView, activeSessionKey) {
    if (!listView || listView.count === 0) {
        return {
            contentY: listView ? listView.contentY : 0,
            key: "",
            channel: "",
            isHeader: false,
            offset: 0,
        }
    }
    var targetY = listView.contentY
    var anchorDelegate = findVisibleAnchorDelegate(root, listView, targetY)
    if (anchorDelegate) {
        if (!anchorDelegate.anchorIsHeader && anchorDelegate.anchorKey === (activeSessionKey || ""))
            return { contentY: targetY, key: "", channel: "", isHeader: false, offset: 0 }
        return {
            contentY: targetY,
            key: anchorDelegate.anchorIsHeader ? "" : (anchorDelegate.anchorKey || ""),
            channel: anchorDelegate.anchorChannel || "",
            isHeader: anchorDelegate.anchorIsHeader === true,
            offset: targetY - anchorDelegate.y,
        }
    }
    return { contentY: targetY, key: "", channel: "", isHeader: false, offset: 0 }
}

function restoreScrollAnchor(root, listView, anchor) {
    if (!listView)
        return
    var targetY = anchor && anchor.contentY !== undefined ? anchor.contentY : listView.contentY
    var anchorDelegate = findVisibleDelegateByAnchor(root, listView, anchor)
    if (anchorDelegate)
        targetY = anchorDelegate.y + (anchor.offset || 0)
    listView.contentY = clampListContentY(root, listView, targetY)
}
