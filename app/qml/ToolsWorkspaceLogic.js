.pragma library

function localizedText(root, value, fallback) {
    if (value && typeof value === "object") {
        var primary = root.isZhLang ? value.zh : value.en
        var secondary = root.isZhLang ? value.en : value.zh
        if (primary !== undefined && primary !== null && String(primary))
            return String(primary)
        if (secondary !== undefined && secondary !== null && String(secondary))
            return String(secondary)
    }
    if (value !== undefined && value !== null && typeof value !== "object" && String(value))
        return String(value)
    return String(fallback || "")
}

function domainLabel(root, domain) {
    if (domain && typeof domain === "object")
        return localizedText(root, domain, "")
    switch (String(domain || "")) {
    case "core":
        return root.tr("核心本地", "Core local")
    case "messaging":
        return root.tr("消息发送", "Messaging")
    case "handoff":
        return root.tr("会话接力", "Handoff")
    case "web_research":
        return root.tr("网页检索", "Web research")
    case "desktop_automation":
        return root.tr("桌面自动化", "Desktop automation")
    case "coding_backend":
        return root.tr("代码任务", "Coding backend")
    default:
        return String(domain || "")
    }
}

function itemIconBackdrop(root, item) {
    switch (String(item.status || "")) {
    case "healthy":
    case "ready":
        return root.isDark ? "#1B1A12" : "#FFF2E2"
    case "configured":
        return root.isDark ? "#111B22" : "#EEF7FF"
    case "blocked":
    case "error":
        return root.isDark ? "#241111" : "#FFF0EE"
    default:
        return root.isDark ? "#171512" : "#F8F4EF"
    }
}

function capabilityLabel(root, capability) {
    if (capability && typeof capability === "object")
        return localizedText(root, capability, "")
    switch (String(capability || "")) {
    case "Filesystem":
        return root.tr("文件系统", "Filesystem")
    case "Workspace":
        return root.tr("工作区", "Workspace")
    case "Authoring":
        return root.tr("编辑", "Authoring")
    case "Shell":
        return root.tr("命令行", "Shell")
    case "Local host":
        return root.tr("本机", "Local host")
    case "Diagnostics":
        return root.tr("诊断", "Diagnostics")
    case "Codegen":
        return root.tr("代码生成", "Codegen")
    case "Refactor":
        return root.tr("重构", "Refactor")
    case "Debug":
        return root.tr("调试", "Debug")
    case "Search":
        return root.tr("搜索", "Search")
    case "Fetch":
        return root.tr("抓取", "Fetch")
    case "Browser":
        return root.tr("浏览器", "Browser")
    case "Embeddings":
        return root.tr("向量", "Embeddings")
    case "Retrieval":
        return root.tr("检索", "Retrieval")
    case "Memory":
        return root.tr("记忆", "Memory")
    case "Image":
        return root.tr("图像", "Image")
    case "Creative":
        return root.tr("创作", "Creative")
    case "Generation":
        return root.tr("生成", "Generation")
    case "Persistence":
        return root.tr("持久化", "Persistence")
    case "Curation":
        return root.tr("整理", "Curation")
    case "Plan":
        return root.tr("计划", "Plan")
    case "Delegate":
        return root.tr("委派", "Delegate")
    case "Track":
        return root.tr("追踪", "Track")
    case "Messaging":
        return root.tr("消息", "Messaging")
    case "Support":
        return root.tr("支持", "Support")
    case "Schedule":
        return root.tr("调度", "Schedule")
    case "Reminder":
        return root.tr("提醒", "Reminder")
    case "Automation":
        return root.tr("自动化", "Automation")
    case "Desktop":
        return root.tr("桌面", "Desktop")
    case "Input":
        return root.tr("输入", "Input")
    case "Visual":
        return root.tr("视觉", "Visual")
    case "External":
        return root.tr("外部", "External")
    case "MCP":
    case "STDIO":
    case "HTTP":
        return String(capability || "")
    case "Setup":
        return root.tr("待配置", "Setup")
    default:
        return String(capability || "")
    }
}

function statusTone(root, item) {
    switch (String(item.status || "")) {
    case "healthy":
    case "ready":
        return root.accent
    case "configured":
        return "#60A5FA"
    case "limited":
        return "#F59E0B"
    case "disabled":
    case "needs_setup":
    case "unavailable":
        return "#F97316"
    case "blocked":
    case "error":
        return root.statusError
    default:
        return root.textSecondary
    }
}

function statusLabel(root, item) {
    if (item && item.displayStatusLabel)
        return localizedText(root, item.displayStatusLabel, item.statusLabel || "")
    switch (String(item.status || "")) {
    case "healthy":
        return root.tr("已连接", "Connected")
    case "ready":
        return root.tr("已就绪", "Ready")
    case "configured":
        return root.tr("已设置", "Configured")
    case "limited":
        return root.tr("受限", "Limited")
    case "disabled":
        return root.tr("已关闭", "Disabled")
    case "needs_setup":
        return root.tr("待配置", "Needs setup")
    case "unavailable":
        return root.tr("不可用", "Unavailable")
    case "blocked":
        return root.tr("受阻", "Blocked")
    case "error":
        return root.tr("异常", "Error")
    default:
        return String(item.statusLabel || "")
    }
}

function statusDetail(root, item) {
    return localizedText(root, item ? item.statusDetailDisplay : null, item ? item.statusDetail || "" : "")
}

function exposureNote(root, item) {
    return localizedText(root, item ? item.exposureSummaryDisplay : null, "")
}

function attentionAction(root, item) {
    return localizedText(root, item ? item.attentionActionDisplay : null, "")
}

function runtimeStateText(root, item) {
    return localizedText(root, item ? item.runtimeStateDisplay : null, "")
}

function includesSummary(root, item) {
    if (item && item.includesSummaryDisplay)
        return localizedText(root, item.includesSummaryDisplay, "")
    var count = Number((item.includedTools || []).length)
    if (count <= 0)
        return root.tr("这个能力族没有单独的用户侧配置入口。", "This capability family does not expose separate end-user configuration.")
    if (item.kind === "mcp_server")
        return root.tr("本次探测共发现 ", "Latest probe found ") + count + root.tr(" 个运行时工具", " runtime tools")
    return root.tr("包含 ", "Includes ") + count + root.tr(" 个底层工具", " underlying tools")
}

function detailStatusNote(root, item) {
    if (!item || !item.kind)
        return ""
    var attentionReason = localizedText(root, item.attentionReasonDisplay, "")
    if (attentionReason)
        return attentionReason
    return statusDetail(root, item)
}

function listBadges(root, item) {
    if (item && item.badges && item.badges.length)
        return item.badges
    var badges = []
    var status = statusLabel(root, item)
    if (status)
        badges.push({ text: status, tone: statusTone(root, item) })
    if (item.kind === "builtin") {
        var labels = item.displayDomainLabels || []
        for (var i = 0; i < Math.min(labels.length, 2); ++i) {
            var domain = domainLabel(root, labels[i])
            if (domain)
                badges.push({ text: domain, tone: "#60A5FA" })
        }
    } else if (item.kind === "mcp_server") {
        var transport = capabilityLabel(
            root,
            item.configValues && item.configValues.transport ? String(item.configValues.transport).toUpperCase() : ""
        )
        if (transport)
            badges.push({ text: transport, tone: "#60A5FA" })
    }
    return badges
}

function summaryMetricLabel(root, key) {
    if (key && typeof key === "object")
        return localizedText(root, key, "")
    switch (key) {
    case "available":
        return root.tr("当前可用", "Available now")
    case "recent_exposure":
        return root.tr("最近暴露", "Exposed recently")
    case "mcp_connected":
        return root.tr("MCP 已连通", "MCP connected")
    case "builtin":
        return root.tr("工具族", "Families")
    case "mcp":
        return root.tr("MCP 源", "MCP sources")
    case "attention":
        return root.tr("待配/异常", "Setup / errors")
    default:
        return key
    }
}

function scopeIntroTitle(root) {
    return root.workspaceString("workspace_tools_title", "工具", "Tools")
}

function scopeIntroCaption(root) {
    return root.workspaceString("workspace_tools_caption", "管理 AI 可用工具", "Manage AI available tools")
}

function installedDetailFallback(root) {
    return root.tr(
        "从列表选择一个能力族后，这里会显示说明、状态和可配置项。",
        "Choose a capability family from the list to inspect its summary, status, and configurable settings."
    )
}

function serversEmptyDescription(root) {
    return root.tr(
        "点击右上角新增 MCP 服务，或导入你已有的 MCP JSON 配置。",
        "Use Add MCP server in the top right, or import an MCP definition you already use."
    )
}

function emptyServerDetailDescription(root) {
    return root.tr(
        "从列表选一个已配置的服务，或从右上角新增一个。",
        "Pick a configured server from the list, or add one from the top right."
    )
}

function serverDraftFromItem(item) {
    var values = item && item.configValues ? item.configValues : {}
    return {
        previousName: values.previousName || "",
        name: values.name || "",
        transport: values.transport || "stdio",
        command: values.command || "",
        argsText: values.argsText || "",
        envText: values.envText || "",
        url: values.url || "",
        headersText: values.headersText || "",
        toolTimeoutSeconds: values.toolTimeoutSeconds || 30,
        maxTools: values.maxTools || 0,
        slimSchema: values.slimSchema
    }
}

function slimSchemaModeFromValue(value) {
    if (value === true)
        return "enabled"
    if (value === false)
        return "disabled"
    return "inherit"
}

function slimSchemaValueFromMode(mode) {
    if (mode === "enabled")
        return true
    if (mode === "disabled")
        return false
    return null
}
