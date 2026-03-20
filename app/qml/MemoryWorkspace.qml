pragma ComponentBehavior: Bound

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "MemoryWorkspaceLogic.js" as Logic

Item {
    id: root
    objectName: "memoryWorkspaceRoot"

    property bool active: false
    property var memoryService: null
    property string currentScope: "memory"
    property string experienceDeprecatedMode: "active"
    property string experienceCategory: ""
    property string experienceOutcome: ""
    property int experienceMinQuality: 0
    property string experienceSortBy: "updated_desc"
    property string noticeText: ""
    property bool noticeSuccess: true
    property string destructiveAction: ""
    property string destructiveKey: ""
    property string destructiveCategory: ""
    property string editorCategory: ""
    property string editorText: ""
    property bool editorDirty: false
    property string factDraftKey: ""
    property string factEditorText: ""
    property bool factEditorActive: false
    property string promoteCategory: "project"
    property string memorySearchQuery: ""
    property string experienceSearchQuery: ""
    property bool syncingEditors: false
    property var memoryEditorRef: null
    property var factEditorRef: null
    property var destructiveModalRef: null
    property real revealOpacity: 1.0
    property real revealScale: 1.0
    property real revealShift: 0.0
    readonly property int compactLayoutBreakpoint: 820
    readonly property bool compactLayout: width < compactLayoutBreakpoint
    readonly property int compactBrowserPaneHeight: 156
    readonly property int compactBrowserPaneMinHeight: 132
    readonly property int compactDetailPaneMinHeight: 188
    readonly property int listCacheBuffer: 720
    readonly property string memoryIconSource: "../resources/icons/vendor/iconoir/brain-electricity.svg"
    readonly property string experienceIconSource: "../resources/icons/zap.svg"
    readonly property string searchIconSource: "../resources/icons/vendor/iconoir/page-search.svg"
    readonly property string detailIconSource: "../resources/icons/vendor/iconoir/message-text.svg"
    readonly property string refreshIconSource: "../resources/icons/vendor/iconoir/calendar-rotate.svg"
    readonly property string saveIconSource: "../resources/icons/vendor/iconoir/book-stack.svg"
    readonly property string deprecateIconSource: "../resources/icons/vendor/iconoir/message-alert.svg"
    readonly property string removeIconSource: "../resources/icons/vendor/iconoir/bubble-xmark.svg"
    readonly property bool hasMemoryService: memoryService !== null
    readonly property var memoryStats: hasMemoryService ? memoryService.memoryStats : ({})
    readonly property var experienceStats: hasMemoryService ? memoryService.experienceStats : ({})
    readonly property var selectedMemoryCategory: hasMemoryService ? memoryService.selectedMemoryCategory : ({})
    readonly property var selectedMemoryFact: hasMemoryService ? memoryService.selectedMemoryFact : ({})
    readonly property string selectedMemoryFactKey: hasMemoryService ? String(memoryService.selectedMemoryFactKey || "") : ""
    readonly property var selectedExperience: hasMemoryService ? memoryService.selectedExperience : ({})
    readonly property var memoryCategoryModel: hasMemoryService && typeof memoryService.memoryCategoryModel !== "undefined"
        ? memoryService.memoryCategoryModel
        : null
    readonly property int memoryCategoryCount: hasMemoryService && typeof memoryService.memoryCategoryCount !== "undefined"
        ? Number(memoryService.memoryCategoryCount || 0)
        : 0
    readonly property var experienceModel: hasMemoryService && typeof memoryService.experienceModel !== "undefined"
        ? memoryService.experienceModel
        : null
    readonly property int experienceCount: hasMemoryService && typeof memoryService.experienceCount !== "undefined"
        ? Number(memoryService.experienceCount || 0)
        : 0
    readonly property bool canMutate: hasMemoryService && memoryService.ready && !memoryService.blockingBusy
    readonly property bool hasSelectedMemory: !!String(selectedMemoryCategory.category || "")
    readonly property bool hasSelectedExperience: !!String(selectedExperience.key || "")
    readonly property bool hasSelectedMemoryFact: !!String(selectedMemoryFact.key || "")

    function tr(zh, en) { return Logic.tr(root, zh, en) }
    function currentHeaderTitle() { return Logic.currentHeaderTitle(root) }
    function currentHeaderCaption() { return Logic.currentHeaderCaption(root) }
    function memoryCategoryTitle(category) { return Logic.memoryCategoryTitle(root, category) }
    function memoryCategoryMeta(detail) { return Logic.memoryCategoryMeta(root, detail) }
    function memoryFactMeta(fact) { return Logic.memoryFactMeta(root, fact) }
    function experienceCategoryLabel(category) { return Logic.experienceCategoryLabel(root, category) }
    function experienceOutcomeLabel(outcome) { return Logic.experienceOutcomeLabel(root, outcome) }
    function applyExperienceFilters() { Logic.applyExperienceFilters(root) }
    function selectMemory(category) { Logic.selectMemory(root, category) }
    function syncEditorFromSelection(force) { Logic.syncEditorFromSelection(root, force) }
    function beginFactEdit() { Logic.beginFactEdit(root) }
    function beginNewFact() { Logic.beginNewFact(root) }
    function triggerPrimaryFactAction() { Logic.triggerPrimaryFactAction(root) }
    function factComposerTitle() { return Logic.factComposerTitle(root) }
    function factComposerPlaceholder() { return Logic.factComposerPlaceholder(root) }
    function factComposerMeta() { return Logic.factComposerMeta(root) }
    function selectFact(fact) { Logic.selectFact(root, fact) }
    function isSelectedFact(fact) { return Logic.isSelectedFact(root, fact) }
    function openDestructiveModal(action, key, category) { Logic.openDestructiveModal(root, action, key, category) }
    function confirmDestructiveAction() { Logic.confirmDestructiveAction(root) }
    function onReadyIfNeeded() { Logic.onReadyIfNeeded(root) }

    function playReveal() {
        root.revealOpacity = motionPageRevealStartOpacity
        root.revealScale = motionPageRevealStartScale
        root.revealShift = motionPageShiftSubtle
        revealAnimation.restart()
    }

    onMemorySearchQueryChanged: {
        if (hasMemoryService && memoryService.setMemoryQuery)
            memoryService.setMemoryQuery(memorySearchQuery)
    }
    onActiveChanged: {
        if (!active)
            return
        playReveal()
        root.onReadyIfNeeded()
    }
    onSelectedMemoryCategoryChanged: {
        root.syncEditorFromSelection(false)
        Logic.syncFactEditorFromSelection(root)
    }
    onSelectedMemoryFactChanged: Logic.syncFactEditorFromSelection(root)
    onSelectedMemoryFactKeyChanged: Logic.syncFactEditorFromSelection(root)
    Component.onCompleted: root.onReadyIfNeeded()

    Connections {
        target: hasMemoryService ? memoryService : null

        function onReadyChanged() { root.onReadyIfNeeded() }
        function onOperationFinished(message, ok) {
            root.noticeText = message
            root.noticeSuccess = ok
            if (root.currentScope === "experience")
                root.applyExperienceFilters()
        }
        function onErrorChanged(error) {
            if (!error)
                return
            root.noticeText = error
            root.noticeSuccess = false
        }
    }

    Item {
        anchors.fill: parent
        opacity: root.revealOpacity
        scale: root.revealScale
        transform: Translate { x: root.revealShift }

        Rectangle {
            anchors.fill: parent
            anchors.margins: 16
            radius: 30
            color: bgCard
            border.width: 1
            border.color: isDark ? "#20FFFFFF" : "#146E4B2A"

            Rectangle {
                anchors.fill: parent
                radius: parent.radius
                color: isDark ? "#08FFFFFF" : "#0DFFF7EF"
            }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 22
                spacing: 18

                MemoryWorkspaceHeader { workspaceRoot: root }

                MemoryWorkspaceNoticeBanner {
                    workspaceRoot: root
                    noticeText: root.noticeText
                    noticeSuccess: root.noticeSuccess
                }

                SplitView {
                    id: mainSplit
                    objectName: "memoryWorkspaceMainSplit"
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    orientation: root.compactLayout ? Qt.Vertical : Qt.Horizontal
                    spacing: root.compactLayout ? 12 : 10
                    handle: WorkspaceSplitHandle {}

                    Rectangle {
                        objectName: "memoryWorkspaceBrowserPane"
                        SplitView.preferredWidth: root.compactLayout ? Math.max(0, mainSplit.width) : 420
                        SplitView.minimumWidth: root.compactLayout ? 0 : 320
                        SplitView.maximumWidth: root.compactLayout ? Math.max(0, mainSplit.width) : 520
                        SplitView.preferredHeight: root.compactLayout ? root.compactBrowserPaneHeight : Math.max(0, mainSplit.height)
                        SplitView.minimumHeight: root.compactLayout ? root.compactBrowserPaneMinHeight : 0
                        SplitView.fillWidth: root.compactLayout
                        SplitView.fillHeight: !root.compactLayout
                        radius: 24
                        color: "transparent"
                        border.width: 0

                        Loader {
                            anchors.fill: parent
                            anchors.margins: 14
                            active: true
                            sourceComponent: root.currentScope === "memory"
                                ? memoryBrowserPaneComponent
                                : experienceBrowserPaneComponent
                        }
                    }

                    Rectangle {
                        objectName: "memoryWorkspaceDetailPane"
                        SplitView.preferredWidth: root.compactLayout ? Math.max(0, mainSplit.width) : 520
                        SplitView.minimumWidth: root.compactLayout ? 0 : 420
                        SplitView.preferredHeight: root.compactLayout ? root.compactDetailPaneMinHeight : Math.max(0, mainSplit.height)
                        SplitView.minimumHeight: root.compactLayout ? root.compactDetailPaneMinHeight : 0
                        SplitView.fillWidth: true
                        SplitView.fillHeight: true
                        radius: 24
                        color: "transparent"
                        border.width: 0

                        Loader {
                            anchors.fill: parent
                            anchors.margins: 14
                            active: true
                            sourceComponent: root.currentScope === "memory"
                                ? memoryDetailPaneComponent
                                : experienceDetailPaneComponent
                        }
                    }
                }
            }
        }

        Rectangle {
            anchors.fill: parent
            color: isDark ? "#7A0E0B09" : "#60FCF8F4"
            visible: root.hasMemoryService && memoryService.blockingBusy

            LoadingOrbit {
                anchors.centerIn: parent
                width: 42
                height: 42
                running: parent.visible
                color: accent
                secondaryColor: accentHover
                haloColor: accentGlow
                haloOpacity: 0.18
                showCore: false
            }
        }
    }

    Component { id: memoryBrowserPaneComponent; MemoryWorkspaceMemoryBrowserPane { workspaceRoot: root } }
    Component { id: experienceBrowserPaneComponent; MemoryWorkspaceExperienceBrowserPane { workspaceRoot: root } }
    Component { id: memoryDetailPaneComponent; MemoryWorkspaceMemoryDetailPane { workspaceRoot: root } }
    Component { id: experienceDetailPaneComponent; MemoryWorkspaceExperienceDetailPane { workspaceRoot: root } }

    MemoryWorkspaceDestructiveModal { workspaceRoot: root }

    SequentialAnimation {
        id: revealAnimation

        ParallelAnimation {
            NumberAnimation { target: root; property: "revealOpacity"; to: 1.0; duration: motionUi; easing.type: easeStandard }
            NumberAnimation { target: root; property: "revealScale"; to: 1.0; duration: motionPanel; easing.type: easeEmphasis }
            NumberAnimation { target: root; property: "revealShift"; to: 0.0; duration: motionPanel; easing.type: easeEmphasis }
        }
    }
}
