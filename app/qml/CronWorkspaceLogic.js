.pragma library

function resolveLang(root) {
    if (typeof effectiveLang === "string" && effectiveLang !== "")
        return effectiveLang
    if (typeof uiLanguage === "string" && uiLanguage !== "auto")
        return uiLanguage
    if (typeof autoLanguage === "string" && autoLanguage !== "")
        return autoLanguage
    return "en"
}

function workspaceString(root, key, fallbackZh, fallbackEn) {
    if (typeof strings === "object" && strings !== null) {
        var value = strings[key]
        if (value !== undefined && value !== null && String(value))
            return String(value)
    }
    return root.tr(fallbackZh, fallbackEn)
}

function automationHeaderCaption(root) {
    return workspaceString(
        root,
        "workspace_cron_caption",
        "统一管理任务与自动检查。",
        "Manage tasks and automated checks."
    )
}

function currentPaneDirection(root) {
    return root.currentPane === "checks" ? 1 : -1
}

function statusItems(root) {
    return [
        { key: "all", label: root.tr("全部", "All") },
        { key: "enabled", label: root.tr("启用中", "Enabled") },
        { key: "issues", label: root.tr("异常", "Errors") }
    ]
}

function statusLabel(root, statusKey) {
    switch (statusKey) {
    case "scheduled":
        return root.tr("已调度", "Scheduled")
    case "error":
        return root.tr("异常", "Error")
    case "idle_ok":
        return root.tr("已就绪", "Ready")
    case "disabled":
        return root.tr("已停用", "Disabled")
    default:
        return root.tr("未安排", "Not scheduled")
    }
}

function statusColor(root, statusKey) {
    switch (statusKey) {
    case "scheduled":
        return root.cronAccent
    case "error":
        return root.statusError
    case "idle_ok":
        return root.statusSuccess
    case "disabled":
        return root.textTertiary
    default:
        return root.textSecondary
    }
}

function statusSurface(root, statusKey) {
    switch (statusKey) {
    case "scheduled":
        return root.isDark ? "#23180F" : "#FFF2E2"
    case "error":
        return root.isDark ? "#2A1513" : "#FFF1EE"
    case "idle_ok":
        return root.isDark ? "#132116" : "#EFF9F1"
    case "disabled":
        return root.isDark ? "#161616" : "#F3F1EE"
    default:
        return root.isDark ? "#17120F" : "#F7F2EC"
    }
}

function summaryText(root, value, fallbackZh, fallbackEn) {
    var text = String(value || "")
    return text !== "" ? text : root.tr(fallbackZh, fallbackEn)
}

function icon(path) {
    return "../resources/icons/vendor/iconoir/" + path + ".svg"
}

function labIcon(path) {
    return "../resources/icons/vendor/lucide-lab/" + path + ".svg"
}

function scheduleModeHint(root) {
    var kind = root.draftString("schedule_kind", "every")
    if (kind === "at") {
        return root.tr(
            "适合一次性提醒，例如明天上午提醒我。",
            "Best for one-time reminders like reminding you tomorrow morning."
        )
    }
    if (kind === "cron") {
        return root.tr(
            "高级模式，只有在你清楚 Cron 语法时再使用。",
            "Advanced mode. Use it only if you are comfortable with cron syntax."
        )
    }
    return ""
}

function deliveryHint(root) {
    return root.draftBool("deliver", false)
        ? root.tr(
            "Bao 执行后会把结果发到你指定的渠道。",
            "Bao will send the result to the channel you choose."
        )
        : ""
}

function taskStatusKey(root) {
    if (root.showingExistingTask)
        return String(root.visibleTask.status_key || "draft")
    return root.draftBool("enabled", true) ? "scheduled" : "disabled"
}

function taskSelectionPrompt(root) {
    return root.tr("先从任务列表选中一个任务", "Select a task from the list first")
}

function emptyTaskStatusHint(root) {
    return root.tr(
        "选中后，这里会显示状态和快捷操作。",
        "After you select one, this area shows status and quick actions."
    )
}
