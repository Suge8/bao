function cloneValue(value) {
    return JSON.parse(JSON.stringify(value))
}

function isSupportedChoice(value, supportedValues) {
    return typeof value === "string" && supportedValues.indexOf(value) >= 0
}

function getProviderMap(configService) {
    var providers = configService ? configService.getValue("providers") : null
    if (providers && typeof providers === "object" && !Array.isArray(providers))
        return providers
    return {}
}

function mergeUiChanges(configService, changes) {
    var hasUpdatePatch = false
    for (var key in changes) {
        if (key.indexOf("ui.update.") === 0) {
            hasUpdatePatch = true
            break
        }
    }
    if (!hasUpdatePatch)
        return
    var updateValue = configService ? configService.getValue("ui.update") : null
    var updateNode = (updateValue && typeof updateValue === "object" && !Array.isArray(updateValue))
        ? cloneValue(updateValue)
        : {}
    for (var updateKey in changes) {
        if (updateKey.indexOf("ui.update.") !== 0)
            continue
        updateNode[updateKey.substring("ui.update.".length)] = changes[updateKey]
        delete changes[updateKey]
    }
    changes.ui = { "update": updateNode }
}

function translateError(root, msg) {
    if (msg.indexOf("token_required:") !== 0)
        return msg
    var channel = msg.split(":")[1]
    var names = { "telegram": "Telegram", "discord": "Discord", "slack": "Slack" }
    var name = names[channel] || channel
    return root.tr(name + " 启用时需要填写 Token", name + " requires a token when enabled")
}

function loadProviders(root) {
    if (!root.configService)
        return
    root._providerList = root.configService.getProviders() || []
}

function loadUpdateDraft(root) {
    var current = root.configService ? root.configService.getValue("ui.update.autoCheck") : undefined
    root._updateAutoCheckDraft = current === true
}

function reloadLocalState(root) {
    loadProviders(root)
    loadUpdateDraft(root)
}

function hasConfiguredProvider(configService) {
    var providers = getProviderMap(configService)
    for (var name in providers) {
        var provider = providers[name]
        if (!provider || typeof provider !== "object" || Array.isArray(provider))
            continue
        var apiKey = provider.apiKey
        if (typeof apiKey === "string" && apiKey.trim() !== "")
            return true
    }
    return false
}

function hasConfiguredModel(configService) {
    if (!configService)
        return false
    var value = configService.getValue("agents.defaults.model")
    return typeof value === "string" && value.trim() !== ""
}

function collectFields(item, changes) {
    if (!item)
        return
    for (var i = 0; i < item.children.length; i++) {
        var child = item.children[i]
        if (child.dotpath && child.currentValue !== undefined)
            changes[child.dotpath] = child.currentValue
        collectFields(child, changes)
    }
}

function commitChanges(root, changes) {
    root._rememberScrollPosition()
    var ok = root.configService.save(changes)
    if (!ok) {
        root._savedScrollY = -1
        return false
    }
    Qt.callLater(function() { root._restoreScrollPosition() })
    return true
}

function saveChanges(root, changes, onSuccess) {
    if (!root.configService)
        return false
    mergeUiChanges(root.configService, changes)
    if (!commitChanges(root, changes))
        return false
    if (root.updateBridge)
        root.updateBridge.reloadRequested()
    root.toast.show(root.appRoot.strings.settings_saved_hint, true)
    if (onSuccess)
        onSuccess()
    return true
}

function saveImmediate(root, changes, onSuccess) {
    if (!root.configService)
        return false
    if (!commitChanges(root, changes))
        return false
    if (onSuccess)
        onSuccess()
    return true
}

function saveSection(root, sectionBody, overrides, onSuccess) {
    var changes = {}
    collectFields(sectionBody, changes)
    if (overrides && typeof overrides === "object" && !Array.isArray(overrides)) {
        for (var overrideKey in overrides)
            changes[overrideKey] = overrides[overrideKey]
    }
    return saveChanges(root, changes, onSuccess)
}
