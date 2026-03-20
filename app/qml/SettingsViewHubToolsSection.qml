import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ColumnLayout {
    id: root

    required property var rootView

    Layout.fillWidth: true
    spacing: spacingXl

    SettingsSection {
        Layout.fillWidth: true
        visible: !root.rootView.onboardingMode && root.rootView._activeTab === 2
        title: strings.section_hub
        description: root.rootView.tr("通常保持默认即可；只有你明确知道部署方式时再改。", "The defaults are usually fine; change these only when you know your deployment needs them.")
        actionText: strings.settings_save
        actionHandler: function() { root.rootView._saveSection(hubSectionBody) }

        ColumnLayout {
            id: hubSectionBody
            width: parent.width
            spacing: spacingMd

            SettingsField { configService: root.rootView.configService; label: root.rootView.tr("主机", "Host"); dotpath: "hub.host"; placeholder: "0.0.0.0" }
            SettingsField { configService: root.rootView.configService; label: root.rootView.tr("端口", "Port"); dotpath: "hub.port"; placeholder: "18790"; inputType: "number" }
            SettingsToggle { configService: root.rootView.configService; label: root.rootView.tr("启用心跳", "Enable heartbeat"); dotpath: "hub.heartbeat.enabled" }
            SettingsField { configService: root.rootView.configService; label: root.rootView.tr("心跳间隔秒", "Heartbeat interval seconds"); dotpath: "hub.heartbeat.intervalS"; placeholder: "1800"; inputType: "number" }
        }
    }

    SettingsSection {
        Layout.fillWidth: true
        visible: !root.rootView.onboardingMode && root.rootView._activeTab === 2
        title: strings.section_tools
        description: root.rootView.tr("这些是增强功能，不影响最基本的聊天启动。", "These are optional enhancements and are not required for basic chat setup.")
        actionText: strings.settings_save
        actionHandler: function() { root.rootView._saveSection(toolsSectionBody) }

        ColumnLayout {
            id: toolsSectionBody
            width: parent.width
            spacing: spacingMd

            Text { text: root.rootView.tr("网页搜索", "Web Search"); color: textSecondary; font.pixelSize: 13; font.weight: Font.DemiBold }
            SettingsField { configService: root.rootView.configService; label: root.rootView.tr("搜索服务来源", "Provider"); dotpath: "tools.web.search.provider"; placeholder: "tavily / brave" }
            SettingsField { configService: root.rootView.configService; label: root.rootView.tr("Tavily API 密钥", "Tavily API Key"); dotpath: "tools.web.search.tavilyApiKey"; placeholder: "tvly-..."; isSecret: true }
            SettingsField { configService: root.rootView.configService; label: root.rootView.tr("Brave API 密钥", "Brave API Key"); dotpath: "tools.web.search.braveApiKey"; placeholder: "BSA..."; isSecret: true }

            Text { text: root.rootView.tr("执行工具", "Exec"); color: textSecondary; font.pixelSize: 13; font.weight: Font.DemiBold; Layout.topMargin: 8 }
            SettingsField { configService: root.rootView.configService; label: root.rootView.tr("超时秒数", "Timeout"); dotpath: "tools.exec.timeout"; placeholder: "60"; inputType: "number" }

            Text { text: root.rootView.tr("向量嵌入", "Embeddings"); color: textSecondary; font.pixelSize: 13; font.weight: Font.DemiBold; Layout.topMargin: 8 }
            SettingsField { configService: root.rootView.configService; label: root.rootView.tr("模型", "Model"); dotpath: "tools.embedding.model"; placeholder: "text-embedding-3-small" }
            SettingsField { configService: root.rootView.configService; label: root.rootView.tr("API 密钥", "API Key"); dotpath: "tools.embedding.apiKey"; placeholder: "sk-..."; isSecret: true }
            SettingsField { configService: root.rootView.configService; label: root.rootView.tr("基础地址", "Base URL"); dotpath: "tools.embedding.baseUrl"; placeholder: "https://api.openai.com/v1" }
            SettingsField { configService: root.rootView.configService; label: root.rootView.tr("搜索最大结果数", "Web search max results"); dotpath: "tools.web.search.maxResults"; placeholder: "5"; inputType: "number" }
            SettingsField { configService: root.rootView.configService; label: root.rootView.tr("嵌入维度", "Embedding dimensions"); dotpath: "tools.embedding.dim"; placeholder: "0"; inputType: "number" }

            Text { text: root.rootView.tr("图像生成", "Image generation"); color: textSecondary; font.pixelSize: 13; font.weight: Font.DemiBold; Layout.topMargin: 8 }
            SettingsField { configService: root.rootView.configService; label: root.rootView.tr("API 密钥", "API Key"); dotpath: "tools.imageGeneration.apiKey"; placeholder: "AIza..."; isSecret: true }
            SettingsField { configService: root.rootView.configService; label: root.rootView.tr("模型", "Model"); dotpath: "tools.imageGeneration.model"; placeholder: "gemini-2.0-flash-exp-image-generation" }
            SettingsField { configService: root.rootView.configService; label: root.rootView.tr("基础地址", "Base URL"); dotpath: "tools.imageGeneration.baseUrl"; placeholder: "https://generativelanguage.googleapis.com/v1beta" }

            Text { text: root.rootView.tr("桌面自动化", "Desktop Automation"); color: textSecondary; font.pixelSize: 13; font.weight: Font.DemiBold; Layout.topMargin: 8 }
            SettingsToggle { configService: root.rootView.configService; label: root.rootView.tr("启用桌面控制", "Enable Desktop Control"); dotpath: "tools.desktop.enabled" }
            SettingsToggle { configService: root.rootView.configService; label: root.rootView.tr("限制到工作区", "Restrict To Workspace"); dotpath: "tools.restrictToWorkspace" }
        }
    }
}
