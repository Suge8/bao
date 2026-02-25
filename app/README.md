# bao Desktop App (实验性)

基于 PySide6 + QML 的桌面客户端，**`bao` CLI 的纯 UI 壳子**。

所有核心逻辑（AgentLoop、Channels、Cron、Heartbeat、startup greeting、首次落盘）均来自 `bao/` core，Desktop 不重复实现任何业务逻辑。配置有效时，App 启动后自动拉起网关，桌面聊天窗口作为 `desktop` channel 与 Telegram、iMessage 等其他渠道共存运行。

当前窗口外观默认使用系统标题栏；在 Windows 上会尝试调用 DWM 请求原生圆角（Windows 11 效果最佳）。

> **⚠️ 实验性功能**：桌面端处于早期开发阶段，API 和行为可能随时变更。

## 快速开始

### 1. 安装依赖

```bash
uv sync --extra desktop
```

### 2. 启动应用

```bash
uv run python app/main.py
```

首次运行自动创建 `~/.bao/config.jsonc` 与默认 workspace（`~/.bao/workspace/`），无需手动初始化。若 `agents.defaults.model` 为空或 providers 中未配置 apiKey，App 自动跳转 Settings 页面引导完成配置。

### 3. 使用流程

1. 打开 App → 若首次使用且未配置 Provider/Model，会自动跳转 Settings 页面；填写配置
2. 点击 Save → 切换到 Chat 页面，网关自动启动
3. Gateway 启动后，桌面聊天 + 所有已启用 Channels 同时运行
4. 可在标题栏右侧查看网关状态、停止或重启网关
5. 修改配置后点击 Save → 在标题栏点击重启即可应用

## 命令行参数

| 参数 | 说明 |
|------|------|
| `--start-view chat\|settings` | 指定首屏（默认 `chat`） |
| `--smoke` | Smoke 测试模式：加载 QML 后 500ms 自动退出 |
| `--smoke-theme-toggle` | Smoke + 主题切换验证 |
| `--smoke-screenshot <path>` | Smoke + 截图保存（便于 UI 回归） |
| `--seed-messages` | 预填充示例消息（调试用） |
| `--qml <path>` | 覆盖 QML 入口文件 |

## 当前限制

- 模拟流式输出（非真 token streaming，P1 计划）
- 配置保存后需手动重启 Gateway（非热重载，by design）
- 仅支持从源码运行（打包为 P2 计划）

> 开发细节（架构、测试命令、UI 坑点、技术要点）见 `AGENTS.md`。
