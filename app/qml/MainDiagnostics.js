.pragma library

function hubState(chatService) {
    if (!chatService)
        return "idle"
    if (typeof chatService.hubState === "string" && chatService.hubState)
        return chatService.hubState
    if (typeof chatService.state === "string" && chatService.state)
        return chatService.state
    return "idle"
}

function hubLabel(strings, chatService) {
    var state = hubState(chatService)
    if (state === "running")
        return strings.diagnostics_hub_running
    if (state === "starting")
        return strings.diagnostics_hub_starting
    if (state === "error")
        return strings.diagnostics_hub_error
    return strings.diagnostics_hub_idle
}

function hubIcon(chatService) {
    var state = hubState(chatService)
    if (state === "running")
        return "../resources/icons/hub-running.svg"
    if (state === "starting")
        return "../resources/icons/hub-starting.svg"
    if (state === "error")
        return "../resources/icons/hub-error.svg"
    return "../resources/icons/hub-idle.svg"
}

function hubBadgeColor(chatService, isDark) {
    var state = hubState(chatService)
    if (state === "running")
        return isDark ? "#1F8A5B" : "#16A34A"
    if (state === "starting")
        return isDark ? "#A45E15" : "#EA8A12"
    if (state === "error")
        return isDark ? "#B14C43" : "#DC5B4F"
    return isDark ? "#725542" : "#C68642"
}

function observabilityItems(service) {
    if (!service || !service.observabilityItems)
        return []
    return service.observabilityItems
}

function events(service) {
    if (!service || !service.events)
        return []
    return service.events
}

function eventCount(service) {
    if (!service || typeof service.eventCount !== "number")
        return 0
    return service.eventCount
}

function logFilePath(service) {
    if (!service || typeof service.logFilePath !== "string")
        return ""
    return service.logFilePath
}

function recentLogText(service) {
    if (!service || typeof service.recentLogText !== "string")
        return ""
    return service.recentLogText
}

function sectionIcon(section, isDark) {
    var suffix = isDark ? "dark" : "light"
    if (section === "hub")
        return "../resources/icons/diag-section-hub-" + suffix + ".svg"
    if (section === "file")
        return "../resources/icons/diag-section-file-" + suffix + ".svg"
    if (section === "events")
        return "../resources/icons/diag-section-events-" + suffix + ".svg"
    return "../resources/icons/diag-section-logtail-" + suffix + ".svg"
}

function observabilitySummary(service) {
    var items = observabilityItems(service)
    if (!items.length)
        return ""
    return items.map(function(item) {
        return String(item.label || "") + " " + String(item.value || "")
    }).join("  ·  ")
}
