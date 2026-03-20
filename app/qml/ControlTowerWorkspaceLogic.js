function accentColor(root, key) {
    switch (String(key || "")) {
    case "telegram": return root.isDark ? Qt.rgba(0.33, 0.73, 1.0, 1.0) : Qt.rgba(0.00, 0.60, 0.96, 1.0)
    case "discord": return root.isDark ? Qt.rgba(0.56, 0.60, 1.0, 1.0) : Qt.rgba(0.39, 0.44, 1.0, 1.0)
    case "whatsapp": return root.isDark ? Qt.rgba(0.31, 0.90, 0.53, 1.0) : Qt.rgba(0.00, 0.78, 0.34, 1.0)
    case "feishu": return root.isDark ? Qt.rgba(0.54, 0.71, 1.0, 1.0) : Qt.rgba(0.17, 0.52, 0.98, 1.0)
    case "slack": return root.isDark ? Qt.rgba(0.99, 0.58, 0.76, 1.0) : Qt.rgba(0.83, 0.12, 0.44, 1.0)
    case "qq": return root.isDark ? Qt.rgba(0.61, 0.67, 1.0, 1.0) : Qt.rgba(0.24, 0.40, 0.98, 1.0)
    case "dingtalk": return root.isDark ? Qt.rgba(0.38, 0.74, 1.0, 1.0) : Qt.rgba(0.00, 0.62, 0.97, 1.0)
    case "imessage": return root.isDark ? Qt.rgba(0.54, 0.70, 1.0, 1.0) : Qt.rgba(0.12, 0.62, 1.0, 1.0)
    case "subagent": return root.isDark ? Qt.rgba(1.0, 0.72, 0.24, 1.0) : Qt.rgba(0.96, 0.57, 0.00, 1.0)
    case "cron": return root.isDark ? Qt.rgba(1.0, 0.66, 0.18, 1.0) : Qt.rgba(0.99, 0.58, 0.00, 1.0)
    case "heartbeat": return root.isDark ? Qt.rgba(0.20, 0.90, 0.56, 1.0) : Qt.rgba(0.00, 0.82, 0.40, 1.0)
    case "system": return root.isDark ? Qt.rgba(0.53, 0.82, 1.0, 1.0) : Qt.rgba(0.18, 0.67, 0.98, 1.0)
    default:
        if (root.accent !== undefined && root.accent !== null)
            return root.accent
        return Qt.rgba(0.96, 0.57, 0.00, 1.0)
    }
}

function channelLabel(root, key) {
    switch (String(key || "")) {
    case "desktop": return root.isChinese ? "桌面" : "Desktop"
    case "telegram": return "Telegram"
    case "discord": return "Discord"
    case "whatsapp": return "WhatsApp"
    case "feishu": return root.isChinese ? "飞书" : "Feishu"
    case "slack": return "Slack"
    case "qq": return "QQ"
    case "dingtalk": return root.isChinese ? "钉钉" : "DingTalk"
    case "imessage": return "iMessage"
    case "subagent": return root.isChinese ? "子代理" : "Subagent"
    case "cron": return "Cron"
    case "heartbeat": return root.isChinese ? "检查" : "Heartbeat"
    default: return root.isChinese ? "系统" : "System"
    }
}

function channelIconSource(_root, key) {
    switch (String(key || "")) {
    case "telegram":
    case "discord":
    case "whatsapp":
    case "feishu":
    case "slack":
    case "qq":
    case "dingtalk":
    case "imessage":
        return "../resources/icons/channel-" + String(key || "") + ".svg"
    case "desktop": return "../resources/icons/sidebar-monitor.svg"
    case "subagent": return "../resources/icons/sidebar-subagent.svg"
    case "cron": return "../resources/icons/sidebar-cron.svg"
    case "heartbeat": return "../resources/icons/sidebar-heartbeat.svg"
    default: return "../resources/icons/sidebar-chat.svg"
    }
}

function icon(_root, path) { return "../resources/icons/vendor/iconoir/" + path + ".svg" }
function labIcon(_root, path) { return "../resources/icons/vendor/lucide-lab/" + path + ".svg" }
function solidIcon(_root, path) { return "../resources/icons/" + path + ".svg" }

function workspaceString(root, key, fallbackZh, fallbackEn) {
    if (typeof strings === "object" && strings !== null) {
        var value = strings[key]
        if (value !== undefined && value !== null && String(value))
            return String(value)
    }
    return root.isChinese ? fallbackZh : fallbackEn
}

function sectionTitle(root, kind) {
    if (kind === "working") return root.isChinese ? "正在工作" : "Working"
    if (kind === "completed") return root.isChinese ? "近 2 小时完成" : "Completed · 2h"
    if (kind === "attention") return root.isChinese ? "待处理" : "Needs Review"
    if (kind === "automation") return root.isChinese ? "自动化" : "Automation"
    return ""
}

function sectionAccentKey(_root, kind) {
    if (kind === "working") return "subagent"
    if (kind === "completed") return "desktop"
    if (kind === "attention") return "system"
    return "cron"
}

function sectionItems(root, kind) {
    if (kind === "working") return root.workingModel
    if (kind === "completed") return root.completedModel
    if (kind === "automation") return root.automationModel
    return root.attentionModel
}

function sectionCount(root, kind) {
    if (kind === "working") return root.workingCount
    if (kind === "completed") return root.completedCount
    if (kind === "automation") return root.automationCount
    return root.attentionCount
}

function profileIsCurrent(root, profile) { return String((profile || {}).id || "") === String(root.overview.liveProfileId || "") }
function profileIsSelected(root, profile) { return root.hasSelectedProfile && String((profile || {}).id || "") === String(root.selectedProfileId || "") }
function sharedHubLive(root) { return Boolean(root.overview.liveHubLive) }
function itemTimeLabel(_root, item) { return String((item || {}).updatedLabel || (item || {}).relativeLabel || "") }
function loaderItemHeight(_root, item) { return item ? Number(item.contentHeight || item.implicitHeight || item.height || 0) : 0 }

function profileAccentKey(root, profile) {
    var channels = (profile || {}).channelKeys || []
    if (profileIsCurrent(root, profile) && Boolean(profile.isHubLive))
        return channels.length > 0 ? String(channels[0]) : "subagent"
    if (Number(profile.attentionCount || 0) > 0)
        return "heartbeat"
    return channels.length > 0 ? String(channels[0]) : "system"
}

function profileTimeLabel(root, profile) {
    var label = String((profile || {}).updatedLabel || "")
    if (label !== "") return label
    label = String((profile || {}).snapshotLabel || "")
    if (label !== "") return label
    return root.isChinese ? "未观测" : "No snapshot"
}

function profileActionText(root, profile) {
    return profileIsCurrent(root, profile) ? (root.isChinese ? "当前" : "Current") : (root.isChinese ? "切换" : "Switch")
}

function scopeTitle(root) {
    return workspaceString(root, "workspace_control_tower_title", "指挥舱", "Control Tower")
}

function scopeCaption(root) {
    return workspaceString(root, "workspace_control_tower_caption", "统一查看分身回复、自动化与待处理事项。", "Monitor replies, automation, and review items across profiles.")
}

function totalSessionCount(root) {
    return root.hasSelectedProfile ? Number(root.selectedProfile.totalSessionCount || 0) : Number(root.overview.totalSessionCount || 0)
}

function itemGlyphSources(root, item) {
    var sources = []
    var keys = (item || {}).channelKeys || []
    for (var index = 0; index < keys.length; index += 1) {
        var source = channelIconSource(root, String(keys[index] || ""))
        if (source !== "" && sources.indexOf(source) === -1)
            sources.push(source)
    }
    if (sources.length === 0) {
        var fallback = String((item || {}).glyphSource || "")
        if (fallback !== "")
            sources.push(fallback)
    }
    return sources
}

function emptyTitle(root, kind) {
    if (kind === "working")
        return !sharedHubLive(root) ? (root.isChinese ? "中枢未启动" : "Hub is not running") : (root.isChinese ? "当前无人工作" : "No active workers")
    if (kind === "completed") return root.isChinese ? "近 2 小时没有完成" : "No completions in the last 2 hours"
    if (kind === "automation") return root.isChinese ? "还没有自动化任务" : "No automation tasks yet"
    return root.isChinese ? "当前没有要处理的问题" : "Nothing needs review right now"
}
