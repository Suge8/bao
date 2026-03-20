import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

SettingsSection {
    id: root

    required property var rootView

    visible: rootView.onboardingMode || rootView._activeTab === 0
    spotlight: rootView.onboardingMode && rootView.onboardingStepIndex === 0
    title: rootView.onboardingMode
           ? rootView.tr("第 1 步 · 选择界面语言", "Step 1 · Choose your language")
           : strings.section_app
    description: rootView.onboardingMode
                 ? rootView.tr(
                     "这一步只决定界面显示中文还是英文，不影响后面的模型配置。",
                     "This only changes how the app reads visually; it does not affect model setup."
                 )
                 : rootView.tr(
                     "先处理界面语言这类最直接的项目。",
                     "Start with the most direct app-level preferences such as UI language."
                 )

    ColumnLayout {
        id: appSectionBody
        anchors.left: parent.left
        anchors.right: parent.right
        spacing: 10

        Text {
            visible: rootView.onboardingMode
            Layout.fillWidth: true
            text: rootView.tr("选完会立刻生效，你后面随时还能改。", "The change applies immediately and you can switch again any time.")
            color: textTertiary
            font.pixelSize: typeMeta
            wrapMode: Text.WordWrap
        }

        Flow {
            visible: rootView.onboardingMode
            Layout.fillWidth: true
            spacing: spacingSm

            Repeater {
                model: [
                    {
                        "value": "auto",
                        "title": strings.ui_language_auto,
                        "body": rootView.tr("跟着你的系统语言走，最省事。", "Follow your system language for the easiest start."),
                        "accent": rootView.tr("推荐", "Recommended")
                    },
                    {
                        "value": "zh",
                        "title": strings.ui_language_zh,
                        "body": rootView.tr("界面固定显示中文。", "Keep the interface in Chinese."),
                        "accent": "ZH"
                    },
                    {
                        "value": "en",
                        "title": strings.ui_language_en,
                        "body": rootView.tr("界面固定显示英文。", "Keep the interface in English."),
                        "accent": "EN"
                    }
                ]

                delegate: ChoiceCard {
                    required property var modelData

                    readonly property bool selectedCard: rootView.onboardingUiLanguage === modelData.value
                    width: rootView._flowItemWidth(appSectionBody.width, 190, 3, spacingSm)
                    badgeText: modelData.accent || ""
                    title: modelData.title || ""
                    description: modelData.body || ""
                    trailingText: selectedCard ? rootView.tr("当前选中", "Selected") : ""
                    selected: selectedCard
                    onClicked: rootView._applyUiLanguageChoice(modelData.value)
                }
            }
        }

        SettingsCollapsible {
            visible: rootView.onboardingMode
            Layout.fillWidth: true
            title: rootView.tr("手动切换语言", "Choose language manually")

            ColumnLayout {
                anchors.left: parent.left
                anchors.right: parent.right
                spacing: spacingMd

                SettingsSelect {
                    configService: rootView.configService
                    label: strings.ui_language
                    dotpath: ""
                    initialValue: rootView.onboardingUiLanguage
                    options: [
                        { "label": strings.ui_language_auto, "value": "auto" },
                        { "label": strings.ui_language_zh, "value": "zh" },
                        { "label": strings.ui_language_en, "value": "en" }
                    ]
                    onValueChanged: function(v) {
                        if (!rootView._applyUiLanguageChoice(v))
                            presetValue(rootView.onboardingUiLanguage)
                    }
                }

                SettingsSelect {
                    configService: rootView.configService
                    label: strings.ui_theme
                    dotpath: ""
                    initialValue: rootView.currentThemeMode
                    options: [
                        { "label": strings.ui_theme_system, "value": "system" },
                        { "label": strings.ui_theme_light, "value": "light" },
                        { "label": strings.ui_theme_dark, "value": "dark" }
                    ]
                    onValueChanged: function(v) {
                        if (!rootView._applyThemeModeChoice(v))
                            presetValue(rootView.currentThemeMode)
                    }
                }
            }
        }

        RowLayout {
            visible: !rootView.onboardingMode
            Layout.fillWidth: true
            spacing: spacingMd

            SettingsSelect {
                configService: rootView.configService
                Layout.fillWidth: true
                label: strings.ui_language
                dotpath: ""
                initialValue: rootView.onboardingUiLanguage
                options: [
                    { "label": strings.ui_language_auto, "value": "auto" },
                    { "label": strings.ui_language_zh, "value": "zh" },
                    { "label": strings.ui_language_en, "value": "en" }
                ]
                onValueChanged: function(v) {
                    if (!rootView._applyUiLanguageChoice(v))
                        presetValue(rootView.onboardingUiLanguage)
                }
            }

            SettingsSelect {
                configService: rootView.configService
                Layout.fillWidth: true
                label: strings.ui_theme
                dotpath: ""
                initialValue: rootView.currentThemeMode
                options: [
                    { "label": strings.ui_theme_system, "value": "system" },
                    { "label": strings.ui_theme_light, "value": "light" },
                    { "label": strings.ui_theme_dark, "value": "dark" }
                ]
                onValueChanged: function(v) {
                    if (!rootView._applyThemeModeChoice(v))
                        presetValue(rootView.currentThemeMode)
                }
            }
        }
    }
}
