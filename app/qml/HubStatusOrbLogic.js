function hasState(root, state) {
    for (var i = 0; i < root.channelCount; i++) {
        var item = root.channels[i]
        if (item && item.state === state)
            return true
    }
    return false
}

function buildOrbChannels(root) {
    var items = []
    for (var i = 0; i < Math.min(2, root.channelCount); i++)
        items.push(root.channels[i])
    return items
}

function iconSource(root, channel) {
    return typeof root.channelFilledIconSource === "function" ? root.channelFilledIconSource(channel) : ""
}

function iconAccent(root, channel, state) {
    if (state === "error")
        return root.statusError
    if (state === "running")
        return root.statusSuccess
    if (state === "starting")
        return root.statusWarning
    return typeof root.channelAccent === "function" ? root.channelAccent(channel) : root.textSecondary
}

function channelLabel(root, channel) {
    var key = "channel_" + channel
    return typeof strings !== "undefined" && strings[key] ? strings[key] : channel
}

function channelStateText(root, state) {
    if (state === "running")
        return typeof strings !== "undefined" ? strings.hub_running : "Running"
    if (state === "starting")
        return typeof strings !== "undefined" ? strings.hub_starting : "Starting"
    if (state === "error")
        return typeof strings !== "undefined" ? strings.hub_error : "Error"
    return typeof strings !== "undefined" ? strings.button_start_hub : "Ready"
}

function defaultSummary(root) {
    if (root.hasErrorState)
        return typeof strings !== "undefined" ? strings.hub_channels_error : "Error"
    if (root.hasRunningState)
        return typeof strings !== "undefined" ? strings.hub_channels_running : "Running"
    if (root.hasStartingState)
        return typeof strings !== "undefined" ? strings.hub_starting : "Starting"
    return typeof strings !== "undefined" ? strings.hub_channels_idle : "Start"
}

function orbSurface(root) {
    if (root.hasErrorState)
        return root.isDark ? "#5B2A29" : "#FFF4F1"
    if (root.hasStartingState)
        return root.isDark ? "#614126" : "#FFF6EA"
    return root.isDark ? "#4B3126" : "#FFFDFC"
}

function bubbleSurface(root) {
    return root.hasErrorState ? (root.isDark ? "#FF472122" : "#FFFFF8F6") : (root.isDark ? "#FF2A241F" : "#FFFFFCF9")
}

function bubbleBorder(root) {
    return root.hasErrorState ? (root.isDark ? "#55F07A7A" : "#18DC2626") : (root.isDark ? "#22FFFFFF" : "#10000000")
}
