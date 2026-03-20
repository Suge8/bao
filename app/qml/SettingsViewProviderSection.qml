import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "SettingsViewHelp.js" as Help
import "SettingsViewOnboarding.js" as Onboarding

SettingsSection {
    id: root

    required property var rootView
    property alias providerSectionBody: providerSectionBody
    property alias onboardingProviderApiKeyField: onboardingProviderApiKeyField
    property alias onboardingProviderTypeField: onboardingProviderTypeField
    property alias onboardingProviderApiBaseField: onboardingProviderApiBaseField

    visible: rootView.onboardingMode || rootView._activeTab === 0
    spotlight: rootView.onboardingMode && rootView.onboardingStepIndex === 1
    title: rootView.onboardingMode ? rootView.tr("第 2 步 · 选一个模型服务", "Step 2 · Pick one AI service") : strings.section_provider
    description: rootView.onboardingMode
                 ? rootView.tr("这里先只做一件事：连上一个能聊天的模型服务。大多数第三方平台都选 openai；只有直连 Claude 或 Gemini 官方时才改成对应类型。", "Keep this simple: connect one AI service that can chat. Most proxy and aggregator services stay on openai; switch only when you connect to the official Claude or Gemini endpoints.")
                 : rootView.tr("先配一个能用的服务就够了；其他服务可以后面再加。", "One working provider is enough to get started; you can add others later.")
    actionText: rootView.onboardingMode ? rootView.tr("保存服务连接", "Save connection") : strings.settings_save
    actionHandler: function() { rootView.saveOnboardingProviderStep() }
    helpVisible: true
    helpHandler: function() {
        rootView._openHelp(rootView.tr("模型服务连接说明", "AI Service Connection Guide"), Help.providerSections(rootView))
    }

    ColumnLayout {
        id: providerSectionBody
        anchors.left: parent.left
        anchors.right: parent.right
        spacing: spacingMd

        Flow {
            visible: rootView.onboardingMode
            Layout.fillWidth: true
            spacing: spacingSm

            Repeater {
                model: rootView.onboardingProviderPresets

                delegate: ChoiceCard {
                    required property var modelData
                    objectName: "onboardingProviderPreset_" + (modelData.id || "unknown")

                    width: rootView._flowItemWidth(providerSectionBody.width, 210, 3, spacingSm)
                    badgeText: modelData.accent || ""
                    title: modelData.title || ""
                    description: modelData.subtitle || ""
                    trailingText: modelData.type || "openai"
                    selected: Onboarding.providerPresetSelected(rootView, modelData)
                    onClicked: Onboarding.applyProviderPreset(rootView, modelData)
                }
            }
        }

        CalloutPanel {
            visible: rootView.onboardingMode
            Layout.fillWidth: true
            panelColor: rootView.providerConfigured ? (isDark ? "#1022C55E" : "#0F22C55E") : (isDark ? "#0CFFFFFF" : "#07000000")
            panelBorderColor: rootView.providerConfigured ? (isDark ? "#3622C55E" : "#3022C55E") : borderSubtle

            ColumnLayout {
                anchors.left: parent.left
                anchors.right: parent.right
                spacing: 6

                Text {
                    Layout.fillWidth: true
                    text: rootView.providerConfigured ? rootView.tr("模型服务已准备好", "AI service ready") : rootView.tr("只需要先连一个就够", "One service is enough")
                    color: textPrimary
                    font.pixelSize: typeLabel
                    font.weight: Font.DemiBold
                    wrapMode: Text.WordWrap
                }

                Text {
                    Layout.fillWidth: true
                    text: rootView.providerConfigured
                          ? rootView.tr("你已经有可用的 API 密钥了。接下来只剩确认默认模型。", "You already have a working API key. The last step is confirming the default model.")
                          : rootView.tr("如果不确定，先点上面的 OpenAI 官方 或 OpenRouter 预设，再把 API 密钥填进去。只有你用代理或公司网关时，才需要展开“自定义接口（可选）”。", "If you are unsure, start with the OpenAI / Official or OpenRouter preset above, then paste in the API key. Only expand Custom Endpoint when you use a proxy or company gateway.")
                    color: textSecondary
                    font.pixelSize: typeMeta
                    wrapMode: Text.WordWrap
                }
            }
        }

        Repeater {
            id: providerRepeater
            model: rootView.onboardingMode ? [] : rootView._providerList

            delegate: ProviderCardShell {
                id: providerCard
                property var provData: modelData || ({})

                Component.onCompleted: {
                    if (rootView._pendingExpandProviderName === (provData.name || "")) {
                        expanded = true
                        Qt.callLater(function() {
                            rootView._scrollToItem(providerCard, 12)
                            rootView._pendingExpandProviderName = ""
                        })
                    }
                }

                title: rootView.onboardingMode ? Onboarding.providerDisplayName(rootView, provData) : (provData.name || "")
                typeText: provData.type || ""
                removable: !(rootView.onboardingMode && rootView._providerList.length <= 1)
                onRemoveClicked: if (provData.name) Onboarding.removeProviderDraft(rootView, provData.name)

                SettingsField { configService: rootView.configService; visible: !rootView.onboardingMode; label: rootView.tr("名称", "Name"); placeholder: "openaiCompatible"; dotpath: "_prov_" + index + "_name"; Component.onCompleted: presetText(provData.name || "") }
                SettingsSelect { configService: rootView.configService; visible: !rootView.onboardingMode; label: rootView.tr("类型", "Type"); dotpath: "_prov_" + index + "_type"; description: rootView.tr("大多数平台选 openai；只有 Claude 官方选 anthropic，Gemini 官方选 gemini。", "Choose openai for most services. Use anthropic only for official Claude, and gemini only for official Gemini."); options: [{ "label": rootView.tr("openai - OpenAI / OpenRouter / DeepSeek / Groq", "openai - OpenAI / OpenRouter / DeepSeek / Groq"), "value": "openai" }, { "label": rootView.tr("anthropic - Claude 官方", "anthropic - Official Claude"), "value": "anthropic" }, { "label": rootView.tr("gemini - Gemini 官方", "gemini - Official Gemini"), "value": "gemini" }]; Component.onCompleted: presetValue(provData.type || "openai") }
                SettingsCollapsible {
                    visible: rootView.onboardingMode
                    Layout.fillWidth: true
                    title: rootView.tr("更改连接方式（可选）", "Change connection mode (optional)")

                    ColumnLayout {
                        anchors.left: parent.left
                        anchors.right: parent.right
                        spacing: spacingMd

                        SettingsSelect { configService: rootView.configService; label: rootView.tr("连接方式", "Connection mode"); dotpath: "_prov_" + index + "_type"; description: rootView.tr("默认不用动。只有你明确知道自己连的是 Claude 官方或 Gemini 官方时才改。", "You usually do not need to change this. Only switch when you know you are connecting to the official Claude or Gemini endpoints."); options: [{ "label": rootView.tr("openai - 大多数服务", "openai - Most services"), "value": "openai" }, { "label": rootView.tr("anthropic - Claude 官方", "anthropic - Official Claude"), "value": "anthropic" }, { "label": rootView.tr("gemini - Gemini 官方", "gemini - Official Gemini"), "value": "gemini" }]; Component.onCompleted: presetValue(provData.type || "openai") }
                    }
                }
                SettingsField { configService: rootView.configService; label: rootView.tr("API 密钥", "API Key"); placeholder: "sk-..."; dotpath: "_prov_" + index + "_apiKey"; isSecret: true; Component.onCompleted: presetText(provData.apiKey || "") }
                SettingsCollapsible {
                    visible: rootView.onboardingMode
                    Layout.fillWidth: true
                    title: rootView.tr("自定义接口（可选）", "Custom endpoint (optional)")

                    ColumnLayout {
                        anchors.left: parent.left
                        anchors.right: parent.right
                        spacing: spacingMd

                        SettingsField { configService: rootView.configService; label: rootView.tr("API 地址", "API Base URL"); placeholder: rootView.tr("可留空；例如 https://api.openai.com/v1", "Optional; for example https://api.openai.com/v1"); dotpath: "_prov_" + index + "_apiBase"; description: rootView.tr("只在你用代理或自建服务时填写；官方默认通常可以留空。", "Only fill this when you use a proxy or self-hosted service. Official defaults can usually stay empty."); Component.onCompleted: presetText(provData.apiBase || "") }
                    }
                }
                SettingsField { configService: rootView.configService; visible: !rootView.onboardingMode; label: rootView.tr("API 地址", "API Base URL"); placeholder: rootView.tr("可留空；例如 https://api.openai.com/v1", "Optional; for example https://api.openai.com/v1"); dotpath: "_prov_" + index + "_apiBase"; description: rootView.tr("只在你用代理或自建服务时填写；官方默认通常可以留空。", "Only fill this when you use a proxy or self-hosted service. Official defaults can usually stay empty."); Component.onCompleted: presetText(provData.apiBase || "") }
            }
        }

        SelectedProviderSummaryCard {
            visible: rootView.onboardingMode && rootView._providerList.length > 0
            title: Onboarding.providerDisplayName(rootView, rootView.onboardingPrimaryProvider)
            description: rootView.providerConfigured
                         ? rootView.tr("这个服务连接已经可用了。你可以直接继续下一步，或者在下面替换 API 密钥。", "This service connection is ready. You can continue to the next step or replace the API key below.")
                         : rootView.tr("主路径只需要一件事：把这个服务的 API 密钥粘进来。", "The main path only needs one thing: paste the API key for this service here.")
            typeText: rootView.onboardingPrimaryProvider.type || "openai"
            highlighted: rootView.providerConfigured

            SettingsField {
                configService: rootView.configService
                id: onboardingProviderApiKeyField
                objectName: "onboardingProviderApiKeyField"
                label: rootView.tr("这个服务的 API 密钥", "API key for this service")
                placeholder: "sk-..."
                dotpath: "_prov_0_apiKey"
                isSecret: true
                description: rootView.tr("只填这一项就可以先继续。", "This is the only field you need to continue.")
                Component.onCompleted: presetText(rootView.onboardingPrimaryProvider.apiKey || "")
            }

            SettingsCollapsible {
                Layout.fillWidth: true
                title: rootView.tr("需要的话，再改连接细节", "Change connection details only if needed")

                ColumnLayout {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    spacing: spacingMd

                    SettingsSelect { configService: rootView.configService; id: onboardingProviderTypeField; objectName: "onboardingProviderTypeField"; label: rootView.tr("连接方式", "Connection mode"); dotpath: "_prov_0_type"; description: rootView.tr("默认不用动。只有你确定自己连的是 Claude 官方或 Gemini 官方时才改。", "You usually do not need to change this. Only switch when you know you are connecting to the official Claude or Gemini endpoints."); options: [{ "label": rootView.tr("openai - 大多数服务", "openai - Most services"), "value": "openai" }, { "label": rootView.tr("anthropic - Claude 官方", "anthropic - Official Claude"), "value": "anthropic" }, { "label": rootView.tr("gemini - Gemini 官方", "gemini - Official Gemini"), "value": "gemini" }]; Component.onCompleted: presetValue(rootView.onboardingPrimaryProvider.type || "openai") }
                    SettingsField { configService: rootView.configService; id: onboardingProviderApiBaseField; objectName: "onboardingProviderApiBaseField"; label: rootView.tr("自定义接口地址", "Custom endpoint URL"); dotpath: "_prov_0_apiBase"; placeholder: rootView.tr("可留空；例如 https://api.openai.com/v1", "Optional; for example https://api.openai.com/v1"); description: rootView.tr("只有你用代理、自建服务或公司网关时才需要填写。", "Only needed for proxies, self-hosted services, or company gateways."); Component.onCompleted: presetText(rootView.onboardingPrimaryProvider.apiBase || "") }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            implicitHeight: rootView.onboardingMode && rootView._providerList.length === 0 ? 48 : 42
            Layout.preferredHeight: implicitHeight
            radius: radiusMd
            color: rootView.onboardingMode && rootView._providerList.length === 0
                   ? (addHover.containsMouse ? accentHover : accent)
                   : (addHover.containsMouse ? (isDark ? "#0AFFFFFF" : "#08000000") : "transparent")
            border.color: accent
            border.width: 1
            opacity: addHover.containsMouse ? 1.0 : 0.7

            Behavior on color { ColorAnimation { duration: motionFast; easing.type: easeStandard } }
            Behavior on opacity { NumberAnimation { duration: motionFast; easing.type: easeStandard } }

            Text {
                anchors.centerIn: parent
                text: rootView.onboardingMode && rootView._providerList.length === 0 ? rootView.tr("+ 先添加第一个服务", "+ Add your first provider") : ("+ " + strings.section_provider_add)
                color: rootView.onboardingMode && rootView._providerList.length === 0 ? "#FFFFFFFF" : accent
                font.pixelSize: 13
                font.weight: Font.Medium
            }

            MouseArea {
                id: addHover
                objectName: "addProviderHitArea"
                anchors.fill: parent
                hoverEnabled: true
                acceptedButtons: Qt.LeftButton
                scrollGestureEnabled: false
                cursorShape: Qt.PointingHandCursor
                onClicked: rootView._addNewProvider()
            }
        }
    }
}
