function rows(root) {
    return [
        {
            "rowObjectName": "channelRow_telegram",
            "headerObjectName": "channelHeader_telegram",
            "channelName": "Telegram",
            "enabledPath": "channels.telegram.enabled",
            "fields": [
                { "label": root.tr("机器人 Token", "Bot Token"), "dotpath": "channels.telegram.token", "placeholder": "123456:ABC-DEF...", "isSecret": true },
                { "label": root.tr("代理", "Proxy"), "dotpath": "channels.telegram.proxy", "placeholder": "socks5://127.0.0.1:1080" },
                { "label": root.tr("回复引用原消息", "Reply To Message"), "dotpath": "channels.telegram.replyToMessage", "placeholder": "true / false" },
                { "label": root.tr("允许列表", "Allow From"), "dotpath": "channels.telegram.allowFrom", "placeholder": "123456789, @name", "isList": true }
            ]
        },
        {
            "rowObjectName": "channelRow_discord",
            "headerObjectName": "channelHeader_discord",
            "channelName": "Discord",
            "enabledPath": "channels.discord.enabled",
            "fields": [
                { "label": root.tr("机器人 Token", "Bot Token"), "dotpath": "channels.discord.token", "placeholder": "MTIz...", "isSecret": true },
                { "label": root.tr("网关地址", "Gateway URL"), "dotpath": "channels.discord.gatewayUrl", "placeholder": "wss://gateway.discord.gg/?v=10&encoding=json" },
                { "label": root.tr("意图位掩码", "Intents"), "dotpath": "channels.discord.intents", "placeholder": "37377", "inputType": "number" },
                { "label": root.tr("允许列表", "Allow From"), "dotpath": "channels.discord.allowFrom", "placeholder": "user_id_1, user_id_2", "isList": true }
            ]
        },
        {
            "rowObjectName": "channelRow_whatsapp",
            "headerObjectName": "channelHeader_whatsapp",
            "channelName": "WhatsApp",
            "enabledPath": "channels.whatsapp.enabled",
            "fields": [
                { "label": root.tr("桥接地址", "Bridge URL"), "dotpath": "channels.whatsapp.bridgeUrl", "placeholder": "ws://localhost:3001" },
                { "label": root.tr("桥接令牌", "Bridge Token"), "dotpath": "channels.whatsapp.bridgeToken", "placeholder": root.tr("可选", "optional"), "isSecret": true },
                { "label": root.tr("允许列表", "Allow From"), "dotpath": "channels.whatsapp.allowFrom", "placeholder": "+8613800138000", "isList": true }
            ]
        },
        {
            "rowObjectName": "channelRow_feishu",
            "headerObjectName": "channelHeader_feishu",
            "channelName": root.tr("飞书", "Feishu"),
            "enabledPath": "channels.feishu.enabled",
            "fields": [
                { "label": root.tr("应用 ID", "App ID"), "dotpath": "channels.feishu.appId", "placeholder": "" },
                { "label": root.tr("应用密钥", "App Secret"), "dotpath": "channels.feishu.appSecret", "placeholder": "", "isSecret": true },
                { "label": root.tr("加密密钥", "Encrypt Key"), "dotpath": "channels.feishu.encryptKey", "placeholder": root.tr("可选", "optional"), "isSecret": true },
                { "label": root.tr("验证 Token", "Verification Token"), "dotpath": "channels.feishu.verificationToken", "placeholder": root.tr("可选", "optional"), "isSecret": true },
                { "label": root.tr("允许列表", "Allow From"), "dotpath": "channels.feishu.allowFrom", "placeholder": "open_id_1, open_id_2", "isList": true }
            ]
        },
        {
            "rowObjectName": "channelRow_slack",
            "headerObjectName": "channelHeader_slack",
            "channelName": "Slack",
            "enabledPath": "channels.slack.enabled",
            "fields": [
                { "label": root.tr("机器人 Token", "Bot Token"), "dotpath": "channels.slack.botToken", "placeholder": "xoxb-...", "isSecret": true },
                { "label": root.tr("应用 Token", "App Token"), "dotpath": "channels.slack.appToken", "placeholder": "xapp-...", "isSecret": true }
            ],
            "advancedFields": [
                { "label": root.tr("线程回复", "Reply In Thread"), "dotpath": "channels.slack.replyInThread", "placeholder": "true / false" },
                { "label": root.tr("反应表情", "React Emoji"), "dotpath": "channels.slack.reactEmoji", "placeholder": "eyes" },
                { "label": root.tr("群组策略", "Group Policy"), "dotpath": "channels.slack.groupPolicy", "placeholder": "mention / open / allowlist" },
                { "label": root.tr("模式", "Mode"), "dotpath": "channels.slack.mode", "placeholder": "socket" },
                { "label": root.tr("Webhook 路径", "Webhook Path"), "dotpath": "channels.slack.webhookPath", "placeholder": "/slack/events" },
                { "label": root.tr("用户只读 Token", "User Token Read Only"), "dotpath": "channels.slack.userTokenReadOnly", "placeholder": "true / false" },
                { "label": root.tr("群组允许列表", "Group Allow From"), "dotpath": "channels.slack.groupAllowFrom", "placeholder": "C123, C456", "isList": true },
                { "label": root.tr("私信开关", "DM Enabled"), "dotpath": "channels.slack.dm.enabled", "placeholder": "true / false" },
                { "label": root.tr("私信策略", "DM Policy"), "dotpath": "channels.slack.dm.policy", "placeholder": "open / allowlist" },
                { "label": root.tr("私信允许列表", "DM Allow From"), "dotpath": "channels.slack.dm.allowFrom", "placeholder": "U123, U456", "isList": true }
            ]
        },
        {
            "rowObjectName": "channelRow_dingtalk",
            "headerObjectName": "channelHeader_dingtalk",
            "channelName": root.tr("钉钉", "DingTalk"),
            "enabledPath": "channels.dingtalk.enabled",
            "fields": [
                { "label": root.tr("客户端 ID", "Client ID"), "dotpath": "channels.dingtalk.clientId", "placeholder": "" },
                { "label": root.tr("客户端密钥", "Client Secret"), "dotpath": "channels.dingtalk.clientSecret", "placeholder": "", "isSecret": true },
                { "label": root.tr("允许列表", "Allow From"), "dotpath": "channels.dingtalk.allowFrom", "placeholder": "staff_id_1, staff_id_2", "isList": true }
            ]
        },
        {
            "rowObjectName": "channelRow_qq",
            "headerObjectName": "channelHeader_qq",
            "channelName": "QQ",
            "enabledPath": "channels.qq.enabled",
            "fields": [
                { "label": root.tr("应用 ID", "App ID"), "dotpath": "channels.qq.appId", "placeholder": "" },
                { "label": root.tr("密钥", "Secret"), "dotpath": "channels.qq.secret", "placeholder": "", "isSecret": true },
                { "label": root.tr("允许列表", "Allow From"), "dotpath": "channels.qq.allowFrom", "placeholder": "openid1, openid2", "isList": true }
            ]
        },
        {
            "rowObjectName": "channelRow_email",
            "headerObjectName": "channelHeader_email",
            "channelName": root.tr("邮件", "Email"),
            "enabledPath": "channels.email.enabled",
            "fields": [
                { "label": root.tr("IMAP 主机", "IMAP Host"), "dotpath": "channels.email.imapHost", "placeholder": "imap.gmail.com" },
                { "label": root.tr("IMAP 端口", "IMAP Port"), "dotpath": "channels.email.imapPort", "placeholder": "993", "inputType": "number" },
                { "label": root.tr("IMAP 用户名", "IMAP Username"), "dotpath": "channels.email.imapUsername", "placeholder": "" },
                { "label": root.tr("IMAP 密码", "IMAP Password"), "dotpath": "channels.email.imapPassword", "placeholder": "", "isSecret": true },
                { "label": root.tr("SMTP 主机", "SMTP Host"), "dotpath": "channels.email.smtpHost", "placeholder": "smtp.gmail.com" },
                { "label": root.tr("SMTP 端口", "SMTP Port"), "dotpath": "channels.email.smtpPort", "placeholder": "587", "inputType": "number" },
                { "label": root.tr("SMTP 用户名", "SMTP Username"), "dotpath": "channels.email.smtpUsername", "placeholder": "" },
                { "label": root.tr("SMTP 密码", "SMTP Password"), "dotpath": "channels.email.smtpPassword", "placeholder": "", "isSecret": true },
                { "label": root.tr("发件地址", "From Address"), "dotpath": "channels.email.fromAddress", "placeholder": "" },
                { "label": root.tr("允许列表", "Allow From"), "dotpath": "channels.email.allowFrom", "placeholder": "alice@example.com, bob@example.com", "isList": true }
            ],
            "advancedFields": [
                { "label": root.tr("IMAP 邮箱", "IMAP Mailbox"), "dotpath": "channels.email.imapMailbox", "placeholder": "INBOX" },
                { "label": root.tr("IMAP SSL", "IMAP Use SSL"), "dotpath": "channels.email.imapUseSsl", "placeholder": "true / false" },
                { "label": root.tr("SMTP TLS", "SMTP Use TLS"), "dotpath": "channels.email.smtpUseTls", "placeholder": "true / false" },
                { "label": root.tr("SMTP SSL", "SMTP Use SSL"), "dotpath": "channels.email.smtpUseSsl", "placeholder": "true / false" },
                { "label": root.tr("授权确认", "Consent Granted"), "dotpath": "channels.email.consentGranted", "placeholder": "true / false" },
                { "label": root.tr("自动回复", "Auto Reply Enabled"), "dotpath": "channels.email.autoReplyEnabled", "placeholder": "true / false" },
                { "label": root.tr("轮询间隔秒", "Poll Interval Seconds"), "dotpath": "channels.email.pollIntervalSeconds", "placeholder": "30", "inputType": "number" },
                { "label": root.tr("标记已读", "Mark Seen"), "dotpath": "channels.email.markSeen", "placeholder": "true / false" },
                { "label": root.tr("正文最大字符", "Max Body Chars"), "dotpath": "channels.email.maxBodyChars", "placeholder": "12000", "inputType": "number" },
                { "label": root.tr("主题前缀", "Subject Prefix"), "dotpath": "channels.email.subjectPrefix", "placeholder": "Re: " }
            ]
        },
        {
            "rowObjectName": "channelRow_imessage",
            "headerObjectName": "channelHeader_imessage",
            "channelName": "iMessage",
            "enabledPath": "channels.imessage.enabled",
            "fields": [
                { "label": root.tr("轮询间隔", "Poll Interval"), "dotpath": "channels.imessage.pollInterval", "placeholder": "2.0", "inputType": "number" },
                { "label": root.tr("服务", "Service"), "dotpath": "channels.imessage.service", "placeholder": "iMessage" },
                { "label": root.tr("允许列表", "Allow From"), "dotpath": "channels.imessage.allowFrom", "placeholder": "+8613800138000", "isList": true }
            ]
        },
        {
            "rowObjectName": "channelRow_mochat",
            "headerObjectName": "channelHeader_mochat",
            "channelName": "Mochat",
            "enabledPath": "channels.mochat.enabled",
            "fields": [
                { "label": root.tr("基础地址", "Base URL"), "dotpath": "channels.mochat.baseUrl", "placeholder": "https://mochat.io" },
                { "label": root.tr("Claw 令牌", "Claw Token"), "dotpath": "channels.mochat.clawToken", "placeholder": "", "isSecret": true },
                { "label": root.tr("代理用户 ID", "Agent User ID"), "dotpath": "channels.mochat.agentUserId", "placeholder": "" },
                { "label": root.tr("允许列表", "Allow From"), "dotpath": "channels.mochat.allowFrom", "placeholder": "group1, group2", "isList": true }
            ],
            "advancedFields": [
                { "label": root.tr("Socket 地址", "Socket URL"), "dotpath": "channels.mochat.socketUrl", "placeholder": "" },
                { "label": root.tr("Socket 路径", "Socket Path"), "dotpath": "channels.mochat.socketPath", "placeholder": "/socket.io" },
                { "label": root.tr("禁用 Msgpack", "Disable Msgpack"), "dotpath": "channels.mochat.socketDisableMsgpack", "placeholder": "true / false", "inputType": "bool" },
                { "label": root.tr("重连延迟毫秒", "Reconnect Delay Ms"), "dotpath": "channels.mochat.socketReconnectDelayMs", "placeholder": "1000", "inputType": "number" },
                { "label": root.tr("最大重连延迟毫秒", "Max Reconnect Delay Ms"), "dotpath": "channels.mochat.socketMaxReconnectDelayMs", "placeholder": "10000", "inputType": "number" },
                { "label": root.tr("连接超时毫秒", "Connect Timeout Ms"), "dotpath": "channels.mochat.socketConnectTimeoutMs", "placeholder": "10000", "inputType": "number" },
                { "label": root.tr("刷新间隔毫秒", "Refresh Interval Ms"), "dotpath": "channels.mochat.refreshIntervalMs", "placeholder": "30000", "inputType": "number" },
                { "label": root.tr("监视超时毫秒", "Watch Timeout Ms"), "dotpath": "channels.mochat.watchTimeoutMs", "placeholder": "25000", "inputType": "number" },
                { "label": root.tr("监视上限", "Watch Limit"), "dotpath": "channels.mochat.watchLimit", "placeholder": "100", "inputType": "number" },
                { "label": root.tr("重试延迟毫秒", "Retry Delay Ms"), "dotpath": "channels.mochat.retryDelayMs", "placeholder": "500", "inputType": "number" },
                { "label": root.tr("最大重试次数", "Max Retry Attempts"), "dotpath": "channels.mochat.maxRetryAttempts", "placeholder": "0", "inputType": "number" },
                { "label": root.tr("回复延迟模式", "Reply Delay Mode"), "dotpath": "channels.mochat.replyDelayMode", "placeholder": "off / non-mention" },
                { "label": root.tr("回复延迟毫秒", "Reply Delay Ms"), "dotpath": "channels.mochat.replyDelayMs", "placeholder": "120000", "inputType": "number" },
                { "label": root.tr("会话列表", "Sessions"), "dotpath": "channels.mochat.sessions", "placeholder": "session1, session2", "isList": true },
                { "label": root.tr("面板列表", "Panels"), "dotpath": "channels.mochat.panels", "placeholder": "panel1, panel2", "isList": true }
            ]
        }
    ]
}
