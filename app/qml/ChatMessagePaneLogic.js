function positionAfterLayout(list) {
    if (list.count <= 0)
        return
    list.forceLayout()
    list.positionViewAtEnd()
}

function maxContentY(list) {
    return Math.max(list.originY, list.originY + list.contentHeight - list.height)
}

function minContentY(list) {
    return list.originY
}

function clampContentY(list, value) {
    return Math.max(minContentY(list), Math.min(maxContentY(list), value))
}

function isNearEnd(list) {
    return maxContentY(list) - list.contentY <= list.nearEndThresholdPx
}

function withSuppressedViewportTracking(list, callback) {
    list.suppressViewportTracking += 1
    try {
        callback()
    } finally {
        list.suppressViewportTracking = Math.max(0, list.suppressViewportTracking - 1)
    }
}

function refreshPinnedFromViewport(list) {
    if (list.suppressViewportTracking > 0)
        return
    if (list.count <= 0) {
        list.bottomPinned = true
        return
    }
    list.bottomPinned = isNearEnd(list)
}

function finishProgrammaticFollow(list, follower) {
    if (!list.programmaticFollowActive)
        return
    list.programmaticFollowActive = false
    list.suppressViewportTracking = Math.max(0, list.suppressViewportTracking - 1)
    if (list.bottomPinned && !list.historyLoading && list.count > 0 && !isNearEnd(list))
        queuePinnedReconcile(list, shouldAnimatePinnedReconcile(list))
}

function cancelProgrammaticFollow(list, follower) {
    if (!list.programmaticFollowActive && !follower.running)
        return
    follower.stop()
    if (!list.programmaticFollowActive)
        return
    list.programmaticFollowActive = false
    list.suppressViewportTracking = Math.max(0, list.suppressViewportTracking - 1)
}

function applyPinnedReconcileOnce(list, animated, follower) {
    if (!list.bottomPinned || list.historyLoading || list.count <= 0)
        return
    list.forceLayout()
    setProgrammaticContentY(list, maxContentY(list), animated, follower)
}

function setProgrammaticContentY(list, targetY, animated, follower) {
    if (list.count <= 0)
        return
    var nextY = clampContentY(list, targetY)
    if (Math.abs(nextY - list.contentY) <= 1) {
        cancelProgrammaticFollow(list, follower)
        withSuppressedViewportTracking(list, function() { list.contentY = nextY })
        return
    }
    if (!animated) {
        cancelProgrammaticFollow(list, follower)
        withSuppressedViewportTracking(list, function() { list.contentY = nextY })
        return
    }
    if (!list.programmaticFollowActive) {
        list.suppressViewportTracking += 1
        list.programmaticFollowActive = true
    } else if (follower.running) {
        follower.stop()
    }
    follower.from = list.contentY
    follower.to = nextY
    follower.start()
}

function reconcilePinnedBottom(list, animated, follower) {
    applyPinnedReconcileOnce(list, animated !== false, follower)
}

function queuePinnedReconcile(list, animated) {
    if (list.pendingPinnedReconcile !== null) {
        list.pendingPinnedReconcile = {
            animated: Boolean(list.pendingPinnedReconcile.animated) && animated !== false
        }
        return
    }
    list.pendingPinnedReconcile = { animated: animated !== false }
    scheduleQueuedReconcile(list)
}

function scheduleQueuedReconcile(list) {
    Qt.callLater(function() {
        var request = list.pendingPinnedReconcile
        if (request === null)
            return
        var useAnimation = request.animated !== false
        list.pendingPinnedReconcile = null
        reconcilePinnedBottom(list, useAnimation, list.bottomPinnedFollower)
    })
}

function shouldAnimatePinnedReconcile(list) {
    return Math.abs(maxContentY(list) - list.contentY) <= list.animateReconcileThresholdPx
}

function forceFollowToEnd(list, animated, follower) {
    list.bottomPinned = true
    if (animated === false) {
        list.pendingPinnedReconcile = null
        reconcilePinnedBottom(list, false, follower)
        return
    }
    queuePinnedReconcile(list, animated)
}

function messageMetaAt(list, row) {
    if (row < 0 || !list.model)
        return null
    var idx = list.model.index(row, 0)
    return {
        role: list.model.data(idx, Qt.UserRole + 2) || "",
        status: list.model.data(idx, Qt.UserRole + 5) || "",
        entranceStyle: list.model.data(idx, Qt.UserRole + 7) || ""
    }
}

function pinOnAppend(list, row) {
    var message = messageMetaAt(list, row)
    return message !== null && (
        message.role === "user"
        || message.role === "assistant"
        || message.role === "system"
        || message.status === "typing"
    )
}

function shouldForceInstantAppend(list, row) {
    var message = messageMetaAt(list, row)
    return message !== null && (
        message.entranceStyle === "greeting"
        || message.role === "user"
        || message.status === "typing"
    )
}

function shouldReconcileOnStatusUpdate(list, row, status) {
    if (status !== "done" && status !== "error")
        return false
    var message = messageMetaAt(list, row)
    return message !== null && (message.role === "assistant" || message.role === "system")
}

function scrollBy(list, delta, follower) {
    if (list.count <= 0)
        return
    cancelProgrammaticFollow(list, follower)
    var nextY = list.contentY + delta
    if (nextY <= minContentY(list)) {
        list.positionViewAtBeginning()
        refreshPinnedFromViewport(list)
        return
    }
    if (nextY >= maxContentY(list)) {
        positionAfterLayout(list)
        refreshPinnedFromViewport(list)
        return
    }
    list.contentY = clampContentY(list, nextY)
    refreshPinnedFromViewport(list)
}

function handleNavigationKey(list, event, composerInputActiveFocus, follower) {
    if (!event || composerInputActiveFocus || list.count <= 0)
        return false
    cancelProgrammaticFollow(list, follower)
    switch (event.key) {
    case Qt.Key_Up:
        scrollBy(list, -list.keyboardLineStep, follower)
        return true
    case Qt.Key_Down:
        scrollBy(list, list.keyboardLineStep, follower)
        return true
    case Qt.Key_PageUp:
        scrollBy(list, -list.keyboardPageStep, follower)
        return true
    case Qt.Key_PageDown:
        scrollBy(list, list.keyboardPageStep, follower)
        return true
    case Qt.Key_Home:
        list.positionViewAtBeginning()
        refreshPinnedFromViewport(list)
        return true
    case Qt.Key_End:
        positionAfterLayout(list)
        refreshPinnedFromViewport(list)
        return true
    default:
        return false
    }
}

function captureViewportBeforeReset(list) {
    list.pendingViewportRestore = { pinned: list.bottomPinned, contentY: list.contentY }
}

function clearPendingViewportRestore(list) {
    list.pendingViewportRestore = null
}

function scheduleDeferredViewportActions(list) {
    if (list.deferredViewportFlushScheduled)
        return
    list.deferredViewportFlushScheduled = true
    Qt.callLater(function() { flushDeferredViewportActions(list, list.bottomPinnedFollower) })
}

function flushDeferredViewportActions(list, follower) {
    list.deferredViewportFlushScheduled = false
    if (list.pendingSessionViewportReady) {
        list.pendingSessionViewportReady = false
        if (!list.historyLoading && list.count > 0) {
            list.bottomPinned = true
            queuePinnedReconcile(list, false)
        }
    }
    var restore = list.pendingViewportRestore
    if (restore === null)
        return
    if (list.count <= 0) {
        clearPendingViewportRestore(list)
        list.bottomPinned = true
        return
    }
    if (Boolean(restore.pinned)) {
        list.bottomPinned = true
        reconcilePinnedBottom(list, false, follower)
    } else {
        setProgrammaticContentY(list, Number(restore.contentY || 0), false, follower)
        refreshPinnedFromViewport(list)
    }
    clearPendingViewportRestore(list)
}

function scheduleSessionViewportReady(list) {
    list.pendingSessionViewportReady = true
    scheduleDeferredViewportActions(list)
}

function restoreViewportAfterReset(list) {
    if (list.pendingViewportRestore !== null)
        scheduleDeferredViewportActions(list)
}

function onViewportGeometryChanged(list) {
    if (list.bottomPinned)
        queuePinnedReconcile(list, false)
}
