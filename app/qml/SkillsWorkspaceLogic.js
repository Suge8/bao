.pragma library

function icon(path) {
    return "../resources/icons/vendor/iconoir/" + path + ".svg"
}

function labIcon(path) {
    return "../resources/icons/vendor/lucide-lab/" + path + ".svg"
}

function workspaceString(root, key, fallbackZh, fallbackEn) {
    if (typeof root.strings === "object" && root.strings !== null) {
        var value = root.strings[key]
        if (value !== undefined && value !== null && String(value))
            return String(value)
    }
    return root.tr(fallbackZh, fallbackEn)
}

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

function localizedSkillName(root, skill) {
    return localizedText(root, skill ? skill.displayName : null, skill && skill.name ? skill.name : "")
}

function localizedSkillDescription(root, skill) {
    return localizedText(root, skill ? skill.displaySummary : null, skill && skill.summary ? skill.summary : "")
}

function skillIconSource(root, skill) {
    if (!skill)
        return labIcon("toolbox")
    return String(skill.iconSource || labIcon("toolbox"))
}

function sourceLabel(root, skill) {
    return String(skill && skill.source || "") === "user"
        ? root.tr("用户", "User")
        : root.tr("内建", "Built-in")
}

function primaryStatusLabel(root, skill) {
    if (!skill)
        return ""
    if (skill.shadowed)
        return root.tr("已覆盖", "Overridden")
    var statusLabel = localizedText(root, skill.statusLabel, "")
    if (statusLabel)
        return statusLabel
    if (skill.always)
        return root.tr("常驻", "Always on")
    return ""
}

function primaryStatusColor(root, skill) {
    if (!skill)
        return root.textSecondary
    if (skill.shadowed)
        return "#F59E0B"
    if (String(skill.status || "") === "needs_setup")
        return root.statusError
    if (String(skill.status || "") === "instruction_only")
        return "#8B5CF6"
    if (skill.always)
        return root.accent
    return "#22C55E"
}

function selectedValue(item, key, fallbackValue) {
    var source = item || {}
    var value = source[key]
    return (typeof value === "undefined" || value === null) ? fallbackValue : value
}

function selectedFlag(item, key) {
    return !!selectedValue(item, key, false)
}

function discoverTaskTone(root, state) {
    switch (String(state || "")) {
    case "working":
        return root.accent
    case "completed":
        return "#22C55E"
    case "failed":
        return root.statusError
    case "cancelled":
        return "#F59E0B"
    default:
        return root.textSecondary
    }
}

function discoverTaskLabel(root, state) {
    switch (String(state || "")) {
    case "working":
        return root.tr("进行中", "Working")
    case "completed":
        return root.tr("已完成", "Completed")
    case "failed":
        return root.tr("失败", "Failed")
    case "cancelled":
        return root.tr("已取消", "Cancelled")
    default:
        return root.tr("空闲", "Idle")
    }
}

function toastMessage(root, code, ok) {
    if (!ok)
        return code
    if (code === "created")
        return root.tr("技能已创建", "Skill created")
    if (code === "saved")
        return root.tr("技能已保存", "Skill saved")
    if (code === "deleted")
        return root.tr("技能已删除", "Skill deleted")
    if (code === "installed")
        return root.tr("技能已导入到用户技能目录", "Skill imported into user skills")
    if (code === "search_ok")
        return root.tr("搜索完成", "Search complete")
    return code
}

function syncDraft(root, force) {
    if (!root.hasSkillsService || !root.editorRef)
        return
    var selectedId = root.selectedSkillId
    if (
        !force
        && root.draftDirty
        && root.draftSkillId === selectedId
        && root.editorRef.text !== root.selectedContent
    )
        return
    root.syncingDraft = true
    root.draftSkillId = selectedId
    root.editorRef.text = root.selectedContent
    root.draftDirty = false
    root.syncingDraft = false
}

function installedCountSummary(root) {
    return root.tr("共显示 ", "Showing ")
        + String(root.installedSkillCount)
        + root.tr(" · 就绪 ", " · Ready ")
        + String(root.overview.readyCount || 0)
        + root.tr(" · 待配置 ", " · Setup ")
        + String(root.overview.needsSetupCount || 0)
}

function discoverPublisherVersion(item) {
    var publisher = String(item && item.publisher || "")
    var version = String(item && item.version || "")
    if (publisher && version)
        return publisher + " · " + version
    return publisher || version
}

function installedSummaryFallback(root) {
    return root.tr(
        "选中一个技能后，这里会显示说明、状态和可编辑内容。",
        "Choose a skill from the list to inspect its summary, status, and editable content."
    )
}

function discoverSummaryFallback(root) {
    return root.tr(
        "选中一个候选技能后，这里会显示引用、信任信息与导入动作。",
        "Choose a candidate from the list to inspect its reference, trust notes, and import action."
    )
}
