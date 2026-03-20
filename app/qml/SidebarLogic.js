function sectionIconSource(root, section) {
    switch (section) {
    case "control_tower":
        return "../resources/icons/sidebar-control-tower-solid.svg"
    case "memory":
        return "../resources/icons/sidebar-memory.svg"
    case "skills":
        return "../resources/icons/sidebar-skills.svg"
    case "tools":
        return "../resources/icons/sidebar-tools.svg"
    case "cron":
        return "../resources/icons/sidebar-cron.svg"
    default:
        return root.themedIconSource("sidebar-sessions-title")
    }
}

function channelVisualSource(root, channel, filled) {
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
        if (filled)
            return root.isDark
                ? "../resources/icons/sidebar-monitor-solid-dark.svg"
                : "../resources/icons/sidebar-monitor-solid.svg"
        return root.isDark ? "../resources/icons/sidebar-monitor-dark.svg" : "../resources/icons/sidebar-monitor.svg"
    case "subagent":
        return filled ? "../resources/icons/sidebar-subagent-solid.svg" : "../resources/icons/sidebar-subagent.svg"
    case "system":
        return filled ? "../resources/icons/sidebar-system-solid.svg" : "../resources/icons/sidebar-system.svg"
    case "heartbeat":
        return filled ? "../resources/icons/sidebar-heartbeat-solid.svg" : "../resources/icons/sidebar-heartbeat.svg"
    case "cron":
        return filled ? "../resources/icons/sidebar-cron-solid.svg" : "../resources/icons/sidebar-cron.svg"
    case "email":
        return filled ? "../resources/icons/sidebar-mail-solid.svg" : "../resources/icons/sidebar-mail.svg"
    default:
        return filled ? "../resources/icons/sidebar-chat-solid.svg" : "../resources/icons/sidebar-chat.svg"
    }
}

function channelAccent(root, channel) {
    switch (channel) {
    case "telegram":
        return root.isDark ? Qt.rgba(0.33, 0.73, 1.0, 1.0) : Qt.rgba(0.00, 0.60, 0.96, 1.0)
    case "discord":
        return root.isDark ? Qt.rgba(0.56, 0.60, 1.0, 1.0) : Qt.rgba(0.39, 0.44, 1.0, 1.0)
    case "whatsapp":
        return root.isDark ? Qt.rgba(0.31, 0.90, 0.53, 1.0) : Qt.rgba(0.00, 0.78, 0.34, 1.0)
    case "feishu":
        return root.isDark ? Qt.rgba(0.54, 0.71, 1.0, 1.0) : Qt.rgba(0.17, 0.52, 0.98, 1.0)
    case "slack":
        return root.isDark ? Qt.rgba(0.99, 0.58, 0.76, 1.0) : Qt.rgba(0.83, 0.12, 0.44, 1.0)
    case "qq":
        return root.isDark ? Qt.rgba(0.61, 0.67, 1.0, 1.0) : Qt.rgba(0.24, 0.40, 0.98, 1.0)
    case "dingtalk":
        return root.isDark ? Qt.rgba(0.38, 0.74, 1.0, 1.0) : Qt.rgba(0.00, 0.62, 0.97, 1.0)
    case "imessage":
        return root.isDark ? Qt.rgba(0.54, 0.70, 1.0, 1.0) : Qt.rgba(0.12, 0.62, 1.0, 1.0)
    case "desktop":
        return root.isDark ? Qt.rgba(1.0, 0.78, 0.29, 1.0) : Qt.rgba(0.97, 0.63, 0.05, 1.0)
    case "subagent":
        return root.isDark ? Qt.rgba(1.0, 0.72, 0.24, 1.0) : Qt.rgba(0.96, 0.57, 0.00, 1.0)
    case "system":
        return root.isDark ? Qt.rgba(0.53, 0.82, 1.0, 1.0) : Qt.rgba(0.18, 0.67, 0.98, 1.0)
    case "heartbeat":
        return root.isDark ? Qt.rgba(0.20, 0.90, 0.56, 1.0) : Qt.rgba(0.00, 0.82, 0.40, 1.0)
    case "cron":
        return root.isDark ? Qt.rgba(1.0, 0.66, 0.18, 1.0) : Qt.rgba(0.99, 0.58, 0.00, 1.0)
    case "email":
        return root.isDark ? Qt.rgba(0.46, 0.69, 1.0, 1.0) : Qt.rgba(0.16, 0.56, 0.95, 1.0)
    default:
        return root.isDark ? Qt.rgba(0.79, 0.55, 1.0, 1.0) : Qt.rgba(0.52, 0.27, 0.84, 1.0)
    }
}

function resolvedHubState(root) {
    if (!root.hasChatService)
        return "idle"
    if (typeof root.chatService.hubState === "string" && root.chatService.hubState !== "")
        return root.chatService.hubState
    if (typeof root.chatService.state === "string" && root.chatService.state !== "")
        return root.chatService.state
    return "idle"
}

function updateNavHighlight(root, navContent, navItems) {
    var target = navItems.sessions
    switch (root.selectionTarget) {
    case "memory":
        target = navItems.memory
        break
    case "skills":
        target = navItems.skills
        break
    case "tools":
        target = navItems.tools
        break
    case "cron":
        target = navItems.cron
        break
    case "control_tower":
    case "settings":
        target = null
        break
    }
    if (!target) {
        root.navHighlightOpacity = 0.0
        return
    }
    root.navHighlightY = navContent.y + target.y
    root.navHighlightHeight = target.height
    root.navHighlightOpacity = 1.0
}

function containsItemPoint(root, item, x, y) {
    if (!item || !item.visible)
        return false
    var point = item.mapFromItem(root, x, y)
    return item.contains(point)
}
