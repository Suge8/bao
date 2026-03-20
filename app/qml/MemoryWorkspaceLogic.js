function langCode(root) {
    if (typeof effectiveLang === "string" && (effectiveLang === "zh" || effectiveLang === "en"))
        return effectiveLang
    if (typeof uiLanguage === "string" && uiLanguage === "zh")
        return "zh"
    return "en"
}

function tr(root, zh, en) {
    return langCode(root) === "zh" ? zh : en
}

function currentHeaderTitle(root) {
    return root.currentScope === "memory"
        ? tr(root, "长期记忆", "Long-term Memory")
        : tr(root, "经验", "Experiences")
}

function currentHeaderCaption(root) {
    return root.currentScope === "memory"
        ? tr(root, "管理 Bao 的长期记忆。", "Manage Bao's long-term memory.")
        : tr(root, "管理 Bao 总结出的经验。", "Manage Bao's extracted experiences.")
}

function memoryCategoryTitle(root, category) {
    switch (String(category || "")) {
    case "preference":
        return tr(root, "偏好记忆", "Preference Memory")
    case "personal":
        return tr(root, "个人记忆", "Personal Memory")
    case "project":
        return tr(root, "项目记忆", "Project Memory")
    case "general":
        return tr(root, "通用记忆", "General Memory")
    default:
        return tr(root, "选择一个分类", "Choose a category")
    }
}

function memoryCategoryMeta(root, detail) {
    var updatedLabel = String(detail.updated_label || "")
    var factCount = Number(detail.fact_count || 0)
    if (!updatedLabel)
        return tr(root, "这里适合保存长期有效的信息。", "Use this area for durable information.")
    return tr(
        root,
        "最近更新 " + updatedLabel + " · " + factCount + " 条事实",
        "Updated " + updatedLabel + " · " + factCount + " facts"
    )
}

function memoryFactMeta(root, fact) {
    var updatedLabel = String(fact.updated_label || "")
    var hitCount = Number(fact.hit_count || 0)
    if (!updatedLabel && hitCount <= 0)
        return tr(root, "稳定事实", "Durable fact")
    if (!updatedLabel)
        return tr(root, "命中 " + hitCount + " 次", "Used " + hitCount + " times")
    if (hitCount <= 0)
        return tr(root, "更新于 " + updatedLabel, "Updated " + updatedLabel)
    return tr(
        root,
        "更新于 " + updatedLabel + " · 命中 " + hitCount + " 次",
        "Updated " + updatedLabel + " · Used " + hitCount + " times"
    )
}

function experienceCategoryLabel(root, category) {
    switch (String(category || "")) {
    case "coding":
        return tr(root, "编码", "Coding")
    case "project":
        return tr(root, "项目", "Project")
    case "general":
        return tr(root, "通用", "General")
    default:
        return category ? String(category) : tr(root, "全部分类", "All categories")
    }
}

function experienceOutcomeLabel(root, outcome) {
    switch (String(outcome || "")) {
    case "success":
        return tr(root, "成功", "Success")
    case "failed":
        return tr(root, "失败", "Failed")
    default:
        return outcome ? String(outcome) : tr(root, "全部结果", "All outcomes")
    }
}

function applyExperienceFilters(root) {
    if (!root.hasMemoryService)
        return
    root.memoryService.reloadExperiences(
        root.experienceSearchQuery,
        root.experienceCategory,
        root.experienceOutcome,
        root.experienceDeprecatedMode,
        root.experienceMinQuality,
        root.experienceSortBy
    )
}

function selectMemory(root, category) {
    if (!root.hasMemoryService)
        return
    root.factEditorActive = false
    root.memoryService.selectMemoryCategory(category)
    root.promoteCategory = category
}

function syncEditorFromSelection(root, force) {
    if (root.currentScope !== "memory")
        return
    var detail = root.selectedMemoryCategory
    var category = String(detail.category || "")
    if (!category)
        return
    if (!force && root.editorDirty && root.editorCategory === category)
        return
    root.syncingEditors = true
    root.editorCategory = category
    root.editorText = String(detail.content || "")
    root.editorDirty = false
    root.syncingEditors = false
}

function setFactEditorState(root, key, text, active) {
    root.syncingEditors = true
    root.factDraftKey = String(key || "")
    root.factEditorText = String(text || "")
    root.factEditorActive = active
    root.syncingEditors = false
}

function beginFactEdit(root) {
    var fact = root.selectedMemoryFact
    if (!String(fact.key || ""))
        return
    setFactEditorState(root, fact.key, fact.content, true)
    if (root.factEditorRef)
        root.factEditorRef.forceActiveFocus()
}

function beginNewFact(root) {
    setFactEditorState(root, "", "", true)
    if (root.factEditorRef)
        root.factEditorRef.forceActiveFocus()
}

function submitFactEditor(root) {
    var category = String(root.selectedMemoryCategory.category || "")
    var draftText = root.factEditorRef ? root.factEditorRef.text : root.factEditorText
    var content = String(draftText || "").trim()
    if (!category || !content)
        return
    root.factEditorText = content
    root.factEditorActive = false
    root.memoryService.saveMemoryFact(category, root.factDraftKey, content)
}

function triggerPrimaryFactAction(root) {
    if (root.factEditorActive) {
        submitFactEditor(root)
        return
    }
    beginFactEdit(root)
}

function syncFactEditorFromSelection(root) {
    if (root.currentScope !== "memory" || root.factEditorActive)
        return
    setFactEditorState(root, root.selectedMemoryFact.key, root.selectedMemoryFact.content, false)
}

function factComposerTitle(root) {
    if (root.factEditorActive)
        return root.factDraftKey ? tr(root, "编辑该条事实", "Edit fact") : tr(root, "新增一条事实", "Add fact")
    return tr(root, "当前事实", "Current fact")
}

function factComposerPlaceholder(root) {
    if (root.factEditorActive) {
        return root.factDraftKey
            ? tr(root, "编辑这条稳定事实，然后点右上角保存。", "Edit this durable fact, then save from the top right.")
            : tr(root, "写一条短而稳定的事实，然后点右上角保存。", "Write one short durable fact, then save from the top right.")
    }
    return tr(root, "点右上角编辑当前事实，或新增一条。", "Edit the current fact or add a new one from the top right.")
}

function factComposerMeta(root) {
    if (root.factEditorActive) {
        return root.factDraftKey
            ? tr(root, "保存后会覆盖当前这条事实。", "Saving replaces the current fact.")
            : tr(root, "保存后会追加到当前分类。", "Saving appends a new fact to this category.")
    }
    if (!root.hasSelectedMemoryFact)
        return tr(root, "这个分类还没有稳定事实。可以先新增一条。", "This category has no durable facts yet. Add one to get started.")
    return memoryFactMeta(root, root.selectedMemoryFact)
}

function selectFact(root, fact) {
    if (!root.hasMemoryService)
        return
    var key = String((fact && fact.key) || "")
    if (!key)
        return
    root.factEditorActive = false
    root.memoryService.selectMemoryFact(key)
}

function isSelectedFact(root, fact) {
    return String((fact && fact.key) || "") === String(root.selectedMemoryFactKey || "")
}

function openDestructiveModal(root, action, key, category) {
    root.destructiveAction = action
    root.destructiveKey = key
    root.destructiveCategory = category
    if (root.destructiveModalRef)
        root.destructiveModalRef.open()
}

function confirmDestructiveAction(root) {
    if (!root.hasMemoryService)
        return
    if (root.destructiveAction === "clearMemory")
        root.memoryService.clearMemoryCategory(root.destructiveCategory)
    else if (root.destructiveAction === "deleteExperience")
        root.memoryService.deleteExperience(root.destructiveKey)
    if (root.destructiveModalRef)
        root.destructiveModalRef.close()
}

function onReadyIfNeeded(root) {
    if (!root.hasMemoryService)
        return
    if (!root.memoryService.ready) {
        if (root.active && root.memoryService.ensureHydrated)
            root.memoryService.ensureHydrated()
        return
    }
    root.memoryService.selectMemoryCategory(root.promoteCategory)
}
