function cloneValue(value) {
    return JSON.parse(JSON.stringify(value))
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

function getProviderMap(configService) {
    var providers = configService ? configService.getValue("providers") : null
    if (providers && typeof providers === "object" && !Array.isArray(providers))
        return providers
    return {}
}

function nextProviderName(providerList) {
    var used = {}
    for (var i = 0; i < providerList.length; i++) {
        if (providerList[i] && providerList[i].name)
            used[providerList[i].name] = true
    }
    if (!used.primary)
        return "primary"
    var idx = providerList.length + 1
    var name = "provider" + idx
    while (used[name]) {
        idx += 1
        name = "provider" + idx
    }
    return name
}

function stepSpec(root, step) {
    if (step < 0 || step >= root.onboardingStepSpecs.length)
        return {}
    return root.onboardingStepSpecs[step] || {}
}

function primaryProviderDraft(providerList) {
    if (providerList.length > 0 && providerList[0])
        return providerList[0]
    return { "type": "openai", "apiBase": "" }
}

function applyProviderPreset(root, preset) {
    if (!preset)
        return
    var nextProviders = []
    for (var i = 0; i < root._providerList.length; i++)
        nextProviders.push(cloneValue(root._providerList[i]))
    var baseName = preset.name || "primary"
    var chosenName = baseName
    var suffix = 2
    var currentName = nextProviders.length > 0 && nextProviders[0] ? nextProviders[0].name : ""
    var used = {}
    for (var j = 0; j < nextProviders.length; j++) {
        var item = nextProviders[j]
        if (item && item.name && item.name !== currentName)
            used[item.name] = true
    }
    while (used[chosenName]) {
        chosenName = baseName + suffix
        suffix += 1
    }
    var providerDraft = {
        "name": chosenName,
        "type": preset.type || "openai",
        "apiKey": currentOnboardingProviderApiKey(root),
        "apiBase": preset.apiBase !== undefined
            ? preset.apiBase
            : (nextProviders.length > 0 && nextProviders[0] ? nextProviders[0].apiBase || "" : "")
    }
    if (nextProviders.length === 0)
        nextProviders.push(providerDraft)
    else
        nextProviders[0] = providerDraft
    root._providerList = nextProviders
}

function currentOnboardingProviderApiKey(root) {
    if (root._onboardingProviderApiKeyFieldRef && root._onboardingProviderApiKeyFieldRef.currentValue !== undefined)
        return root._onboardingProviderApiKeyFieldRef.currentValue
    if (root._providerList.length > 0 && root._providerList[0] && root._providerList[0].apiKey)
        return root._providerList[0].apiKey
    return ""
}

function syncOnboardingProviderFields(root, provider) {
    if (!root.onboardingMode || !provider)
        return
    if (root._onboardingProviderApiKeyFieldRef)
        root._onboardingProviderApiKeyFieldRef.setCurrentText(provider.apiKey || "")
    if (root._onboardingProviderTypeFieldRef)
        root._onboardingProviderTypeFieldRef.presetValue(provider.type || "openai")
    if (root._onboardingProviderApiBaseFieldRef)
        root._onboardingProviderApiBaseFieldRef.setCurrentText(provider.apiBase || "")
}

function providerDisplayName(root, provider) {
    if (!provider || typeof provider !== "object")
        return root.tr("服务连接", "Service connection")
    var type = typeof provider.type === "string" ? provider.type : "openai"
    var apiBase = typeof provider.apiBase === "string" ? provider.apiBase.toLowerCase() : ""
    if (apiBase.indexOf("openrouter") >= 0)
        return "OpenRouter"
    if (type === "anthropic")
        return root.tr("Anthropic 官方", "Official Anthropic")
    if (type === "gemini")
        return root.tr("Gemini 官方", "Official Gemini")
    if (apiBase !== "")
        return root.tr("自定义兼容接口", "Custom compatible API")
    return root.tr("OpenAI 官方", "Official OpenAI")
}

function normalizeProviderApiBase(value) {
    if (typeof value !== "string")
        return ""
    var normalized = value.trim().toLowerCase()
    while (normalized.length > 0 && normalized.charAt(normalized.length - 1) === "/")
        normalized = normalized.slice(0, normalized.length - 1)
    if (normalized === "https://api.openai.com" || normalized === "https://api.openai.com/v1")
        return ""
    if (normalized === "https://openrouter.ai/api" || normalized === "https://openrouter.ai/api/v1")
        return "https://openrouter.ai/api/v1"
    return normalized
}

function liveOnboardingProviderDraft(root) {
    var provider = root.onboardingPrimaryProvider || {}
    var providerType = typeof provider.type === "string" ? provider.type : "openai"
    var providerApiBase = typeof provider.apiBase === "string" ? provider.apiBase : ""
    if (root._onboardingProviderTypeFieldRef && root._onboardingProviderTypeFieldRef.currentValue !== undefined && root._onboardingProviderTypeFieldRef.currentValue !== null)
        providerType = String(root._onboardingProviderTypeFieldRef.currentValue)
    if (root._onboardingProviderApiBaseFieldRef && root._onboardingProviderApiBaseFieldRef.currentValue !== undefined && root._onboardingProviderApiBaseFieldRef.currentValue !== null)
        providerApiBase = String(root._onboardingProviderApiBaseFieldRef.currentValue)
    return {
        "type": providerType,
        "apiBase": normalizeProviderApiBase(providerApiBase)
    }
}

function suggestedModelPresets(root) {
    var provider = liveOnboardingProviderDraft(root)
    var type = provider && typeof provider.type === "string" ? provider.type : "openai"
    var apiBase = provider && typeof provider.apiBase === "string" ? provider.apiBase : ""
    if (type === "anthropic") {
        return [
            { "label": root.tr("Claude Sonnet", "Claude Sonnet"), "value": "anthropic/claude-sonnet-4-20250514", "hint": root.tr("最稳妥的 Claude 起点", "The safest Claude default") },
            { "label": root.tr("Claude Haiku", "Claude Haiku"), "value": "anthropic/claude-3-5-haiku-latest", "hint": root.tr("更轻更快", "Lighter and faster") },
            { "label": root.tr("自己填写", "Custom"), "value": "", "hint": root.tr("如果你知道自己的模型名", "If you already know the exact model name") }
        ]
    }
    if (type === "gemini") {
        return [
            { "label": root.tr("Gemini Flash", "Gemini Flash"), "value": "gemini/gemini-2.0-flash", "hint": root.tr("推荐先从这个开始", "Recommended default") },
            { "label": root.tr("Gemini Pro", "Gemini Pro"), "value": "gemini/gemini-1.5-pro", "hint": root.tr("更适合复杂任务", "Better for heavier tasks") },
            { "label": root.tr("自己填写", "Custom"), "value": "", "hint": root.tr("如果你知道自己的模型名", "If you already know the exact model name") }
        ]
    }
    if (apiBase.indexOf("openrouter") >= 0) {
        return [
            { "label": "GPT-4o", "value": "openai/gpt-4o", "hint": root.tr("OpenRouter 上最省心的起点", "An easy OpenRouter default") },
            { "label": root.tr("Claude Sonnet", "Claude Sonnet"), "value": "anthropic/claude-sonnet-4-20250514", "hint": root.tr("如果你更喜欢 Claude 风格", "If you prefer Claude-style answers") },
            { "label": root.tr("Gemini Flash", "Gemini Flash"), "value": "gemini/gemini-2.0-flash", "hint": root.tr("更快更轻量", "Faster and lighter") }
        ]
    }
    return [
        { "label": "GPT-4o", "value": "openai/gpt-4o", "hint": root.tr("推荐先从这个开始", "Recommended default") },
        { "label": "GPT-4.1 mini", "value": "openai/gpt-4.1-mini", "hint": root.tr("更轻更快", "Lighter and faster") },
        { "label": root.tr("自己填写", "Custom"), "value": "", "hint": root.tr("如果你有自己的模型名", "If you already have a model name") }
    ]
}

function applyModelPreset(root, preset) {
    if (!preset || !root.onboardingPrimaryModelField)
        return
    if (preset.value === "") {
        root.activateCustomModelInput()
        return
    }
    root.onboardingPrimaryModelField.presetText(preset.value)
}

function displayModelLabel(root, modelId) {
    if (typeof modelId !== "string" || modelId.trim() === "")
        return root.tr("还没选默认聊天模型", "No default chat AI selected yet")
    var value = modelId.trim()
    if (value === "openai/gpt-4o")
        return "GPT-4o"
    if (value === "openai/gpt-4.1-mini")
        return "GPT-4.1 mini"
    if (value === "anthropic/claude-sonnet-4-20250514")
        return root.tr("Claude Sonnet", "Claude Sonnet")
    if (value === "anthropic/claude-3-5-haiku-latest")
        return root.tr("Claude Haiku", "Claude Haiku")
    if (value === "gemini/gemini-2.0-flash")
        return root.tr("Gemini Flash", "Gemini Flash")
    if (value === "gemini/gemini-1.5-pro")
        return root.tr("Gemini Pro", "Gemini Pro")
    var slash = value.lastIndexOf("/")
    return slash >= 0 ? value.slice(slash + 1) : value
}

function providerPresetSelected(root, preset) {
    if (!preset)
        return false
    var provider = liveOnboardingProviderDraft(root)
    var providerType = typeof provider.type === "string" ? provider.type : "openai"
    var providerApiBase = typeof provider.apiBase === "string" ? provider.apiBase : ""
    var presetApiBase = normalizeProviderApiBase(preset.apiBase)
    if (preset.id === "openrouter")
        return providerType === "openai" && providerApiBase === presetApiBase
    if (preset.id === "custom")
        return providerType === "openai" && providerApiBase !== "" && providerApiBase !== "https://openrouter.ai/api/v1"
    if (preset.type === "anthropic" || preset.type === "gemini")
        return providerType === preset.type
    return providerType === (preset.type || "openai") && providerApiBase === presetApiBase
}

function modelPresetSelected(root, preset) {
    if (!preset)
        return false
    if (preset.value === "")
        return root.onboardingPrimaryModelField && root.onboardingPrimaryModelField.currentValue === ""
    return root.onboardingDraftModel === preset.value
}

function addNewProvider(root) {
    var name = nextProviderName(root._providerList)
    var nextProviders = []
    for (var i = 0; i < root._providerList.length; i++)
        nextProviders.push(root._providerList[i])
    nextProviders.push({
        "name": name,
        "type": "openai",
        "apiKey": "",
        "apiBase": ""
    })
    root._pendingExpandProviderName = name
    root._providerList = nextProviders
}

function removeProviderDraft(root, name) {
    var nextProviders = []
    for (var i = 0; i < root._providerList.length; i++) {
        if (root._providerList[i] && root._providerList[i].name !== name)
            nextProviders.push(root._providerList[i])
    }
    root._providerList = nextProviders
}

function saveProvidersSection(root, providerSectionBody, onSuccess) {
    var changes = {}
    collectFields(providerSectionBody, changes)
    var allProviders = getProviderMap(root.configService)
    var seenProviderNames = {}
    var nextProviders = {}
    for (var i = 0; i < root._providerList.length; i++) {
        var prefix = "_prov_" + i + "_"
        var original = root._providerList[i] || {}
        var origName = original.name
        var requestedName = changes[prefix + "name"]
        var newName = origName
        if (requestedName !== undefined) {
            var trimmedName = String(requestedName).trim()
            if (trimmedName !== "")
                newName = trimmedName
        }
        if (seenProviderNames[newName]) {
            root.toast.show(
                root.tr(
                    "保存失败：提供商名称重复（" + newName + "）",
                    "Save failed: duplicate provider name (" + newName + ")"
                ),
                false
            )
            return false
        }
        seenProviderNames[newName] = true
        var sourceProvider = original
        if (allProviders && typeof allProviders === "object" && !Array.isArray(allProviders)
                && allProviders[origName] && typeof allProviders[origName] === "object") {
            sourceProvider = allProviders[origName]
        }
        var merged = cloneValue(sourceProvider)
        if (merged.type === undefined || merged.type === null || merged.type === "")
            merged.type = original.type || "openai"
        if (merged.apiKey === undefined || merged.apiKey === null)
            merged.apiKey = original.apiKey !== undefined && original.apiKey !== null ? original.apiKey : ""
        delete merged.order
        var fieldNames = ["type", "apiKey", "apiBase"]
        for (var j = 0; j < fieldNames.length; j++) {
            var fieldKey = prefix + fieldNames[j]
            if (changes[fieldKey] !== undefined)
                merged[fieldNames[j]] = changes[fieldKey]
            delete changes[fieldKey]
        }
        delete changes[prefix + "name"]
        nextProviders[newName] = merged
    }
    return root._saveChanges({ "providers": nextProviders }, function() {
        root._providerList = root.configService ? (root.configService.getProviders() || []) : []
        if (onSuccess)
            onSuccess()
    })
}
