function tabLabels(root) {
    return [
        { "label": root.tr("快速开始", "Quick Start") },
        { "label": root.tr("渠道", "Channels") },
        { "label": root.tr("高级", "Advanced") }
    ]
}

function onboardingStepSpecs(root) {
    return [
        {
            "heroTitle": root.tr("先选界面语言", "Start with your interface language"),
            "heroBody": root.tr(
                "只影响界面显示语言，选完会立即生效。",
                "This only changes the interface language and applies immediately."
            ),
            "title": root.tr("界面语言", "UI language"),
            "body": root.tr(
                "先把界面切到你读起来最舒服的语言。",
                "Start by switching the interface to the language that feels natural to you."
            ),
            "cta": root.tr("去选择", "Choose")
        },
        {
            "heroTitle": root.tr("现在连接一个模型服务", "Now connect one AI service"),
            "heroBody": root.tr(
                "先让 Bao 连上一个能聊天的服务。大多数平台保持 openai 就够了。",
                "Get Bao connected to one working chat service first. For most services, keeping openai is enough."
            ),
            "title": root.tr("选择模型服务", "Choose an AI service"),
            "body": root.tr(
                "只要连好一个能用的服务和 API Key，就能继续下一步。",
                "You only need one working service and API key to move on."
            ),
            "cta": root.tr("去连接", "Connect it")
        },
        {
            "heroTitle": root.tr("最后确认默认聊天模型", "Finally confirm the default chat AI"),
            "heroBody": root.tr(
                "选一个默认模型，保存后就会直接进入聊天。",
                "Pick one default model and the app will take you straight into chat after saving."
            ),
            "title": root.tr("确认默认模型", "Confirm the default model"),
            "body": root.tr(
                "选一个默认模型，保存后会自动回到聊天界面。",
                "Choose the default model and the app will drop you into chat after saving."
            ),
            "cta": root.tr("去确认", "Confirm it")
        }
    ]
}

function providerPresets(root) {
    return [
        {
            "id": "openai",
            "title": root.tr("OpenAI 官方", "Official OpenAI"),
            "subtitle": root.tr("最稳妥的默认起点", "The safest default starting point"),
            "type": "openai",
            "name": "openai",
            "apiBase": "",
            "accent": root.isZh ? "官方" : "Official"
        },
        {
            "id": "openrouter",
            "title": "OpenRouter",
            "subtitle": root.tr("一处接多模型，最省事", "One endpoint for many models"),
            "type": "openai",
            "name": "openrouter",
            "apiBase": "https://openrouter.ai/api/v1",
            "accent": root.tr("聚合", "Multi-model")
        },
        {
            "id": "anthropic",
            "title": root.tr("Anthropic 官方", "Official Anthropic"),
            "subtitle": root.tr("只在直连 Anthropic 时选", "Choose only for direct Anthropic"),
            "type": "anthropic",
            "name": "anthropic",
            "apiBase": "",
            "accent": "Claude"
        },
        {
            "id": "gemini",
            "title": root.tr("Gemini 官方", "Official Gemini"),
            "subtitle": root.tr("只在直连 Gemini 时选", "Choose only for direct Gemini"),
            "type": "gemini",
            "name": "gemini",
            "apiBase": "",
            "accent": "Gemini"
        },
        {
            "id": "custom",
            "title": root.tr("自定义兼容接口", "Custom compatible API"),
            "subtitle": root.tr(
                "适合代理、自建或公司网关",
                "Best for proxies, self-hosting, or company gateways"
            ),
            "type": "openai",
            "name": "primary",
            "apiBase": "",
            "accent": root.tr("自定义", "Custom")
        }
    ]
}
