import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "SettingsViewHelp.js" as Help

SettingsSection {
    id: root

    required property var rootView

    visible: !rootView.onboardingMode && rootView._activeTab === 0
    title: strings.section_agent_defaults
    description: rootView.tr("先填一个主模型，Bao 就能开始聊天；下面这些只是默认回复习惯。", "Set one primary model first; the rest only shapes Bao's default reply behavior.")
    actionText: strings.settings_save
    actionHandler: function() { rootView._saveSection(agentSectionBody) }
    helpVisible: true
    helpHandler: function() {
        rootView._openHelp(rootView.tr("回复方式与模型说明", "Response Setup Guide"), Help.agentSections(rootView))
    }

    ColumnLayout {
        id: agentSectionBody
        anchors.left: parent.left
        anchors.right: parent.right
        spacing: spacingMd

        SettingsField { configService: rootView.configService; label: rootView.tr("工作目录", "Workspace Folder"); dotpath: "agents.defaults.workspace"; placeholder: "~/.bao/workspace" }
        SettingsField { configService: rootView.configService; label: rootView.tr("默认聊天模型", "Primary Model"); dotpath: "agents.defaults.model"; placeholder: "openai/gpt-4o"; description: rootView.tr("Bao 平时聊天最常用的模型", "The model Bao uses for normal chats") }
        SettingsField { configService: rootView.configService; label: rootView.tr("后台小任务模型", "Background Model"); dotpath: "agents.defaults.utilityModel"; placeholder: "openrouter/google/gemini-flash-1.5"; description: rootView.tr("做标题生成、经验整理这类后台任务时更省钱的模型", "A cheaper model for background tasks such as titles and summaries") }
        SettingsField { configService: rootView.configService; label: rootView.tr("自动学习经验", "Learning Mode"); dotpath: "agents.defaults.memory.learningMode"; placeholder: "utility / main / none"; description: rootView.tr("utility = 用后台模型 / main = 用主模型 / none = 关闭自动学习", "utility = use the background model / main = use the primary model / none = turn off automatic learning") }
        SettingsListField { configService: rootView.configService; label: rootView.tr("聊天里可切换的模型", "Switchable Models"); dotpath: "agents.defaults.models"; placeholder: "model1, model2"; description: rootView.tr("聊天中通过 /model 可以切到这些模型，不填也可以", "Models you can switch to with /model in chat; optional") }

        SettingsCollapsible {
            Layout.fillWidth: true
            title: rootView.tr("高级选项", "Advanced")

            ColumnLayout {
                anchors.left: parent.left
                anchors.right: parent.right
                spacing: spacingMd

                SettingsField { configService: rootView.configService; label: rootView.tr("单次回复上限", "Reply Length Limit"); dotpath: "agents.defaults.maxTokens"; placeholder: "8192"; inputType: "number"; description: rootView.tr("一条回复最多能输出多少内容", "How much one reply can generate at most") }
                SettingsField { configService: rootView.configService; label: rootView.tr("稳定 / 发散程度", "Stability vs Variety"); dotpath: "agents.defaults.temperature"; placeholder: "0.1"; inputType: "number"; description: rootView.tr("越低越稳，越高越发散（0-2）", "Lower is steadier; higher is more varied (0-2)") }
                SettingsField { configService: rootView.configService; label: rootView.tr("单轮最多调用工具次数", "Tool Call Limit Per Turn"); dotpath: "agents.defaults.maxToolIterations"; placeholder: "20"; inputType: "number"; description: rootView.tr("一轮对话里最多让 Bao 调多少次工具", "The maximum number of tool calls Bao can make in one turn") }
                SettingsField { configService: rootView.configService; label: rootView.tr("最近对话上下文", "Recent Context Window"); dotpath: "agents.defaults.memory.recentWindow"; placeholder: "50"; inputType: "number"; description: rootView.tr("保留最近多少条消息作为上下文，不会写入长期记忆", "How many recent messages Bao keeps in prompt context; this does not control long-term memory") }
                SettingsSelect { configService: rootView.configService; label: rootView.tr("长对话管理", "Long Chat Handling"); dotpath: "agents.defaults.contextManagement"; description: rootView.tr("对话很长时，Bao 怎么压缩和整理上下文", "How Bao trims and manages context in long conversations"); options: [{ "label": rootView.tr("关闭", "off"), "value": "off" }, { "label": rootView.tr("观察", "observe"), "value": "observe" }, { "label": rootView.tr("自动", "auto"), "value": "auto" }, { "label": rootView.tr("激进", "aggressive"), "value": "aggressive" }] }
                SettingsSelect { configService: rootView.configService; label: rootView.tr("深度思考强度", "Reasoning Depth"); dotpath: "agents.defaults.reasoningEffort"; description: rootView.tr("控制模型要不要多想一点；自动 = 交给模型自己判断", "Controls how much extra reasoning the model should use; Auto lets the model decide"); options: [{ "label": rootView.tr("自动", "Auto"), "value": null }, { "label": "off", "value": "off" }, { "label": "low", "value": "low" }, { "label": "medium", "value": "medium" }, { "label": "high", "value": "high" }] }
                SettingsSelect { configService: rootView.configService; label: rootView.tr("回复加速模式", "Reply Speed Mode"); dotpath: "agents.defaults.serviceTier"; description: rootView.tr("仅对支持的 OpenAI / Codex 服务生效。极速优先会尽量更快回复；省钱优先更便宜，但排队时间可能更长。", "Only applies to supported OpenAI / Codex services. Speed Priority aims for faster replies; Cost Saver is cheaper, but queue time may be longer."); options: [{ "label": rootView.tr("默认", "Default"), "value": null }, { "label": rootView.tr("极速优先", "Speed Priority"), "value": "priority" }, { "label": rootView.tr("省钱优先", "Cost Saver"), "value": "flex" }] }
                SettingsField { configService: rootView.configService; label: rootView.tr("工具结果预览长度", "Tool Preview Length"); dotpath: "agents.defaults.toolOutputPreviewChars"; placeholder: "3000"; inputType: "number"; description: rootView.tr("工具结果太长时，消息里先显示多少预览", "How much preview to keep in the message when tool output is long") }
                SettingsField { configService: rootView.configService; label: rootView.tr("工具结果外置阈值", "Tool Offload Threshold"); dotpath: "agents.defaults.toolOutputOffloadChars"; placeholder: "8000"; inputType: "number"; description: rootView.tr("超过这个长度就自动存成文件，不全塞进对话", "Tool output longer than this is moved to a file instead of staying fully in chat") }
                SettingsField { configService: rootView.configService; label: rootView.tr("开始压缩上下文的阈值", "Context Trim Threshold"); dotpath: "agents.defaults.contextCompactBytesEst"; placeholder: "240000"; inputType: "number"; description: rootView.tr("对话太长时，达到这个体量就开始压缩", "When the conversation grows past this size, Bao starts compacting it") }
                SettingsField { configService: rootView.configService; label: rootView.tr("压缩时保留最近工具块", "Recent Tool Blocks to Keep"); dotpath: "agents.defaults.contextCompactKeepRecentToolBlocks"; placeholder: "4"; inputType: "number"; description: rootView.tr("压缩长对话时，保留最近几组工具调用", "How many recent tool call groups to keep when compacting") }
                SettingsField { configService: rootView.configService; label: rootView.tr("临时产物保留天数", "Artifact Cleanup Days"); dotpath: "agents.defaults.artifactRetentionDays"; placeholder: "7"; inputType: "number"; description: rootView.tr("自动清理临时文件前保留多少天", "How many days temporary output files are kept before cleanup") }
                SettingsToggle { configService: rootView.configService; label: rootView.tr("回复里显示进度提示", "Show Progress Updates"); dotpath: "agents.defaults.sendProgress" }
                SettingsToggle { configService: rootView.configService; label: rootView.tr("回复里显示工具提示", "Show Tool Hints"); dotpath: "agents.defaults.sendToolHints" }
            }
        }
    }
}
