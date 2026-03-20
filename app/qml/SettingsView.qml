import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "SettingsViewCatalog.js" as Catalog
import "SettingsViewHelp.js" as Help
import "SettingsViewOnboarding.js" as Onboarding
import "SettingsViewSave.js" as Save

Rectangle {
    id: root
    color: "transparent"

    property var appRoot: null
    property var configService: null
    property var updateService: null
    property var updateBridge: null
    property var desktopPreferences: null
    property bool onboardingMode: false
    property bool _pendingManualUpdateCheck: false
    property string updateStateUi: updateService ? updateService.state : "idle"
    property string updateErrorUi: updateService ? updateService.errorMessage : ""
    property var _providerList: []
    property bool _updateAutoCheckDraft: false
    property int _activeTab: 0
    property string _helpTitle: ""
    property var _helpSections: []
    property var _tabLabels: Catalog.tabLabels(root)
    property int _pendingTab: -1
    property int _tabDirection: 1
    property real _savedScrollY: -1
    property string _pendingExpandProviderName: ""
    property var _supportedUiLanguages: ["auto", "zh", "en"]
    property var _supportedThemeModes: ["system", "light", "dark"]
    property var _onboardingProviderApiKeyFieldRef: null
    property var _onboardingProviderTypeFieldRef: null
    property var _onboardingProviderApiBaseFieldRef: null

    readonly property bool isZh: appRoot ? appRoot.effectiveLang === "zh" : false
    readonly property bool updateBusy: updateStateUi === "checking" || updateStateUi === "downloading" || updateStateUi === "installing"
    readonly property string updateActionText: updateBusy ? strings.update_action_checking : strings.update_action_check
    readonly property int setupTopInset: appRoot ? appRoot.design.windowContentInsetTop : spacingLg
    readonly property int setupSideInset: appRoot ? appRoot.design.windowContentInsetSide : spacingLg
    readonly property int setupBottomInset: appRoot ? appRoot.design.windowContentInsetBottom : spacingLg
    readonly property int setupMaxContentWidth: onboardingMode ? 900 : 820
    readonly property var _scrollFlickable: settingsScroll ? settingsScroll.contentItem : null
    readonly property string configFilePath: configService ? configService.getConfigFilePath() : ""
    readonly property bool languageConfigured: Save.isSupportedChoice(desktopPreferences ? desktopPreferences.uiLanguage : null, _supportedUiLanguages)
    readonly property bool providerConfigured: Save.hasConfiguredProvider(configService)
    readonly property bool modelConfigured: Save.hasConfiguredModel(configService)
    readonly property var onboardingPrimaryProvider: Onboarding.primaryProviderDraft(_providerList)
    readonly property var onboardingStepSpecs: Catalog.onboardingStepSpecs(root)
    readonly property var onboardingPrimaryModelField: onboardingModelSection ? onboardingModelSection.onboardingPrimaryModelField : null
    readonly property var onboardingModelManualField: onboardingModelSection ? onboardingModelSection.onboardingModelManualField : null
    readonly property string onboardingDraftModel: {
        var field = onboardingPrimaryModelField
        if (field && field.currentValue !== undefined && field.currentValue !== null)
            return String(field.currentValue)
        if (!configService)
            return ""
        var value = configService.getValue("agents.defaults.model")
        return typeof value === "string" && value !== "" ? value : ""
    }
    readonly property bool onboardingModelReady: onboardingDraftModel.trim() !== ""
    readonly property int onboardingCompletedCount: (languageConfigured ? 1 : 0) + (providerConfigured ? 1 : 0) + (modelConfigured ? 1 : 0)
    readonly property real onboardingProgress: onboardingCompletedCount / 3
    readonly property int onboardingStepIndex: !languageConfigured ? 0 : (!providerConfigured ? 1 : 2)
    readonly property string onboardingCurrentTitle: Onboarding.stepSpec(root, onboardingStepIndex).heroTitle || ""
    readonly property string onboardingCurrentBody: Onboarding.stepSpec(root, onboardingStepIndex).heroBody || ""
    readonly property string onboardingUiLanguage: Save.isSupportedChoice(desktopPreferences ? desktopPreferences.uiLanguage : null, _supportedUiLanguages) ? desktopPreferences.uiLanguage : "auto"
    readonly property string currentThemeMode: Save.isSupportedChoice(desktopPreferences ? desktopPreferences.themeMode : null, _supportedThemeModes) ? desktopPreferences.themeMode : "system"
    readonly property var onboardingProviderPresets: Catalog.providerPresets(root)
    readonly property var onboardingModelPresets: Onboarding.suggestedModelPresets(root)

    function tr(zh, en) { return isZh ? zh : en }
    function _rememberScrollPosition() { var flick = root._scrollFlickable; if (flick && flick.contentY !== undefined) _savedScrollY = flick.contentY }
    function _restoreScrollPosition() { var flick = root._scrollFlickable; if (!flick || _savedScrollY < 0 || flick.contentY === undefined || flick.contentHeight === undefined) return; var maxY = Math.max(0, flick.contentHeight - flick.height); flick.contentY = Math.max(0, Math.min(maxY, _savedScrollY)); _savedScrollY = -1 }
    function _scrollToItem(item, topOffset) { if (!item || !root._scrollFlickable) return; var flick = root._scrollFlickable; var top = item.mapToItem(scrollContent, 0, 0).y; var maxY = Math.max(0, flick.contentHeight - flick.height); var offset = (topOffset !== undefined && topOffset !== null) ? topOffset : 20; flick.contentY = Math.max(0, Math.min(maxY, top - offset)) }
    function _flowColumnCount(availableWidth, minWidth, maxColumns, gap) { var width = Math.max(0, Number(availableWidth || 0)); var columns = Math.max(1, Number(maxColumns || 1)); var spacing = Number(gap || 0); while (columns > 1) { if ((width - spacing * (columns - 1)) / columns >= minWidth) break; columns -= 1 } return columns }
    function _flowItemWidth(availableWidth, minWidth, maxColumns, gap) { var width = Math.max(0, Number(availableWidth || 0)); var spacing = Number(gap || 0); if (width <= 0) return minWidth; var columns = _flowColumnCount(width, minWidth, maxColumns, spacing); if (columns <= 1) return width; return Math.floor((width - spacing * (columns - 1)) / columns) }
    function _applyUiLanguageChoice(value) { return desktopPreferences ? desktopPreferences.setUiLanguage(value) : false }
    function _applyThemeModeChoice(value) { return desktopPreferences ? desktopPreferences.setThemeMode(value) : false }
    function _openOnboardingStep(step) { if (step === 0) { _scrollToItem(appSection); return } if (step === 1) { _scrollToItem(providerSection); return } _scrollToItem(onboardingModelSection) }
    function _switchTab(index) { if (index === _activeTab) return; _tabDirection = index > _activeTab ? 1 : -1; _pendingTab = index; tabSwitchAnim.restart() }
    function _reloadLocalState() { Save.reloadLocalState(root) }
    function _openHelp(title, sections) { _helpTitle = title; _helpSections = sections; helpModal.open() }
    function _saveChanges(changes, onSuccess) { return Save.saveChanges(root, changes, onSuccess) }
    function _saveImmediate(changes, onSuccess) { return Save.saveImmediate(root, changes, onSuccess) }
    function _saveSection(sectionBody, overrides, onSuccess) { return Save.saveSection(root, sectionBody, overrides, onSuccess) }
    function _addNewProvider() { Onboarding.addNewProvider(root) }
    function saveOnboardingProviderStep() { return Onboarding.saveProvidersSection(root, providerSection.providerSectionBody, function() { if (root.onboardingMode) root._scrollToItem(onboardingModelSection) }) }
    function activateCustomModelInput() { if (!onboardingPrimaryModelField) return; onboardingModelManualField.expanded = true; onboardingPrimaryModelField.setCurrentText(""); _scrollToItem(onboardingModelSection) }

    Component.onCompleted: {
        _reloadLocalState()
        _onboardingProviderApiKeyFieldRef = providerSection.onboardingProviderApiKeyField
        _onboardingProviderTypeFieldRef = providerSection.onboardingProviderTypeField
        _onboardingProviderApiBaseFieldRef = providerSection.onboardingProviderApiBaseField
    }

    onUpdateStateUiChanged: {
        if (!_pendingManualUpdateCheck)
            return
        if (updateStateUi === "available") { _pendingManualUpdateCheck = false; updateConfirmModal.open(); return }
        if (updateStateUi === "up_to_date") { toast.show(strings.update_status_up_to_date, true); _pendingManualUpdateCheck = false; return }
        if (updateStateUi === "error") { toast.show(updateErrorUi || strings.update_status_error, false); _pendingManualUpdateCheck = false }
    }
    onOnboardingPrimaryProviderChanged: Onboarding.syncOnboardingProviderFields(root, onboardingPrimaryProvider)

    WheelHandler {
        target: null
        acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
        onWheel: function(event) {
            var flick = root._scrollFlickable
            if (!flick)
                return
            var maxY = Math.max(0, flick.contentHeight - flick.height)
            if (maxY <= 0)
                return
            var deltaY = event.pixelDelta.y !== 0 ? -event.pixelDelta.y : (-event.angleDelta.y / 3)
            flick.contentY = Math.max(0, Math.min(maxY, flick.contentY + deltaY))
            event.accepted = true
        }
    }

    SequentialAnimation {
        id: tabSwitchAnim
        ParallelAnimation {
            NumberAnimation { target: pagesWrap; property: "opacity"; to: 0.12; duration: 110; easing.type: easeStandard }
            NumberAnimation { target: pagesWrap; property: "x"; to: -root._tabDirection * 30; duration: 110; easing.type: easeStandard }
        }
        ScriptAction { script: { if (root._pendingTab >= 0) { root._activeTab = root._pendingTab; pagesWrap.x = root._tabDirection * 30 } } }
        ParallelAnimation {
            NumberAnimation { target: pagesWrap; property: "opacity"; to: 1; duration: 200; easing.type: easeEmphasis }
            NumberAnimation { target: pagesWrap; property: "x"; to: 0; duration: 200; easing.type: easeEmphasis }
        }
        ScriptAction { script: { root._pendingTab = -1; pagesWrap.x = 0 } }
    }

    ScrollView {
        id: settingsScroll
        objectName: "settingsScroll"
        anchors.fill: parent
        contentWidth: scrollContent.width
        contentHeight: scrollContent.height
        ScrollBar.vertical.policy: ScrollBar.AlwaysOn
        clip: true

        Item {
            id: scrollContent
            width: settingsScroll.width
            height: innerCol.implicitHeight + setupBottomInset + 48
            implicitHeight: height

            ColumnLayout {
                id: innerCol
                width: Math.min(Math.max(settingsScroll.availableWidth - Math.max(32, setupSideInset * 2 + 16), 320), setupMaxContentWidth)
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: setupTopInset + (root.onboardingMode ? spacingSm : spacingLg)
                spacing: root.onboardingMode ? spacingLg : spacingXl

                SettingsViewTabs { rootView: root }

                ColumnLayout {
                    id: pagesWrap
                    Layout.fillWidth: true
                    spacing: spacingXl

                    SettingsViewOnboardingHero { id: onboardingHeroSection; rootView: root }
                    SettingsViewAppSection { id: appSection; rootView: root }
                    SettingsViewUpdatesSection { id: updatesSection; rootView: root }
                    SettingsViewAgentSection { id: agentSection; rootView: root }
                    SettingsViewProviderSection { id: providerSection; rootView: root }
                    SettingsViewModelSection { id: onboardingModelSection; rootView: root }
                    SettingsViewChannelsSection { id: channelsSection; rootView: root }
                    SettingsViewConfigFileSection { id: configFileSection; rootView: root }
                    SettingsViewHubToolsSection { rootView: root }
                    Item { Layout.fillWidth: true; Layout.preferredHeight: 40 }
                }
            }
        }
    }

    AppToast {
        id: toast
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.topMargin: 24
        anchors.rightMargin: 24
        z: 21
        successBg: isDark ? "#1F7A4D" : "#16A34A"
        errorBg: isDark ? "#B84040" : "#DC2626"
        textColor: "#FFFFFF"
        duration: toastDurationLong
    }

    SettingsHelpModal { id: helpModal; rootView: root }
    SettingsUpdateModal { id: updateConfirmModal; rootView: root }

    Connections {
        target: configService
        function onConfigLoaded() {
            root._reloadLocalState()
            Qt.callLater(function() { root._restoreScrollPosition() })
        }
        function onSaveError(msg) {
            toast.show(Save.translateError(root, msg), false)
        }
    }
}
