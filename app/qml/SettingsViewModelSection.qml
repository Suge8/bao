import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "SettingsViewOnboarding.js" as Onboarding

SettingsSection {
    id: root

    required property var rootView
    property alias onboardingPrimaryModelField: onboardingPrimaryModelField
    property alias onboardingModelManualField: onboardingModelManualField

    visible: rootView.onboardingMode
    spotlight: rootView.onboardingMode && rootView.onboardingStepIndex === 2
    title: rootView.tr("第 3 步 · 选默认聊天模型", "Step 3 · Pick your default chat AI")
    description: rootView.providerConfigured
                 ? rootView.tr("最后一步只要选一个你想先用来聊天的模型；保存后如果上面的服务和 API 密钥都有效，会自动进入聊天。", "The last step is choosing the AI you want to start chatting with. Once saved, the app automatically enters chat if the service and API key above are valid.")
                 : rootView.tr("你也可以先把默认聊天模型选好，但真正生效前，先把上面的服务连接保存一下。", "You can choose the default chat AI now, but it only becomes usable after the service connection above is saved.")
    actionText: rootView.providerConfigured
                ? rootView.tr("保存并开始聊天", "Save and start chatting")
                : rootView.tr("先保存上面的服务连接", "Save the connection above first")
    actionEnabled: rootView.providerConfigured && rootView.onboardingModelReady
    actionHandler: function() { rootView._saveSection(onboardingModelSectionBody) }

    ColumnLayout {
        id: onboardingModelSectionBody
        anchors.left: parent.left
        anchors.right: parent.right
        spacing: spacingMd

        Flow {
            Layout.fillWidth: true
            spacing: spacingSm

            Repeater {
                model: rootView.onboardingModelPresets

                delegate: ChoiceCard {
                    required property var modelData

                    width: rootView._flowItemWidth(onboardingModelSectionBody.width, 210, 3, spacingSm)
                    title: modelData.label || ""
                    description: modelData.hint || ""
                    selected: Onboarding.modelPresetSelected(rootView, modelData)
                    onClicked: Onboarding.applyModelPreset(rootView, modelData)
                }
            }
        }

        CalloutPanel {
            Layout.fillWidth: true
            panelColor: rootView.modelConfigured ? (isDark ? "#1022C55E" : "#0F22C55E") : (isDark ? "#0CFFFFFF" : "#07000000")
            panelBorderColor: rootView.modelConfigured ? (isDark ? "#3622C55E" : "#3022C55E") : borderSubtle

            ColumnLayout {
                anchors.left: parent.left
                anchors.right: parent.right
                spacing: 6

                Text {
                    Layout.fillWidth: true
                    text: rootView.onboardingDraftModel !== ""
                          ? rootView.tr("你当前选的是：", "Your current choice is:")
                          : rootView.tr("先从推荐卡片里选一个最省心的", "Start with one of the recommended cards")
                    color: textPrimary
                    font.pixelSize: typeLabel
                    font.weight: Font.DemiBold
                    wrapMode: Text.WordWrap
                }

                Text {
                    Layout.fillWidth: true
                    text: rootView.onboardingDraftModel !== ""
                          ? Onboarding.displayModelLabel(rootView, rootView.onboardingDraftModel) + " (" + rootView.onboardingDraftModel + ")"
                          : rootView.tr("推荐卡已经按你上一步选的模型服务做了简化。只有你知道准确模型名时，才需要手动填写。", "The recommended cards are already simplified based on the AI service you picked above. Only enter a model manually when you already know the exact model name.")
                    color: textSecondary
                    font.pixelSize: typeMeta
                    wrapMode: Text.WordWrap
                }
            }
        }

        SettingsCollapsible {
            id: onboardingModelManualField
            Layout.fillWidth: true
            title: rootView.tr("我知道准确模型名，手动填写", "I know the exact model name")

            ColumnLayout {
                anchors.left: parent.left
                anchors.right: parent.right
                spacing: spacingMd

                SettingsField {
                    configService: rootView.configService
                    id: onboardingPrimaryModelField
                    objectName: "onboardingPrimaryModelField"
                    label: rootView.tr("默认聊天模型", "Default chat AI")
                    dotpath: "agents.defaults.model"
                    placeholder: "openai/gpt-4o"
                    description: rootView.tr("只有你知道准确模型名时才需要手填。否则直接点上面的推荐卡片就够了。", "Only fill this when you already know the exact model name. Otherwise, using one of the recommended cards above is enough.")
                }
            }
        }

        SettingsCollapsible {
            Layout.fillWidth: true
            title: rootView.tr("可选：再省一点成本", "Optional: save a bit more on background tasks")

            ColumnLayout {
                anchors.left: parent.left
                anchors.right: parent.right
                spacing: spacingMd

                Text {
                    Layout.fillWidth: true
                    text: rootView.tr("这一项不是开始聊天所必需的。只有你想把标题生成、总结这类后台动作换成更便宜的模型时，再填这里。", "This is not required to start chatting. Only fill it when you want background actions like titles or summaries to use a cheaper model.")
                    color: textTertiary
                    font.pixelSize: typeMeta
                    wrapMode: Text.WordWrap
                }

                SettingsField {
                    configService: rootView.configService
                    label: rootView.tr("更省钱的后台模型（可选）", "Cheaper background AI (optional)")
                    dotpath: "agents.defaults.utilityModel"
                    placeholder: "openrouter/google/gemini-flash-1.5"
                    description: rootView.tr("留空也完全没问题。", "Leaving this empty is perfectly fine.")
                }
            }
        }
    }
}
