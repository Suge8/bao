# bao 规格说明

通过 WhatsApp / iMessage 访问的个人 Claude 助手，具有每个会话的持久记忆和计划任务功能。

---

## 目录

1. [架构](#架构)
2. [目录结构](#目录结构)
3. [配置](#配置)
4. [记忆系统](#记忆系统)
5. [会话管理](#会话管理)
6. [消息流程](#消息流程)
7. [命令](#命令)
8. [计划任务](#计划任务)
9. [MCP 服务器](#mcp-服务器)
10. [部署](#部署)
11. [安全考虑](#安全考虑)

---

## 架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                        HOST (macOS)                                  │
│                   (Main Node.js Process)                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐        │
│  │  WhatsApp    │──┤  iMessage    │─▶│   SQLite Database  │        │
│  │  (baileys)   │  │  (chat.db)   │  │   (messages.db)    │        │
│  └──────────────┘  └──────────────┘  └─────────┬──────────┘        │
│                                                  │                   │
│         ┌────────────────────────────────────────┘                   │
│         │                                                            │
│         ▼                                                            │
│  ┌──────────────────┐    ┌──────────────────┐    ┌───────────────┐  │
│  │  Message Loop    │    │  Scheduler Loop  │    │  IPC Watcher  │  │
│  │  (polls SQLite)  │    │  (checks tasks)  │    │  (file-based) │  │
│  └────────┬─────────┘    └────────┬─────────┘    └───────────────┘  │
│           │                       │                                  │
│           └───────────┬───────────┘                                  │
│                       │ spawns container                             │
│                       ▼                                              │
├─────────────────────────────────────────────────────────────────────┤
│                  APPLE CONTAINER (Linux VM)                          │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    AGENT RUNNER                               │   │
│  │                                                                │   │
│  │  Working directory: /workspace/group (mounted from host)       │   │
│  │  Volume mounts:                                                │   │
│  │    • groups/{name}/ → /workspace/group                         │   │
│  │    • groups/global/ → /workspace/global/ (non-main only)        │   │
│  │    • data/sessions/{group}/.claude/ → /home/node/.claude/      │   │
│  │    • Additional dirs → /workspace/extra/*                      │   │
│  │                                                                │   │
│  │  Tools (all groups):                                           │   │
│  │    • Bash (safe - sandboxed in container!)                     │   │
│  │    • Read, Write, Edit, Glob, Grep (file operations)           │   │
│  │    • WebSearch, WebFetch (internet access)                     │   │
│  │    • agent-browser (browser automation)                        │   │
│  │    • mcp__bao__* (scheduler tools via IPC)                │   │
│  │                                                                │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 技术栈

| 组件          | 技术                                    | 用途                                |
| ------------- | --------------------------------------- | ----------------------------------- |
| WhatsApp 连接 | Node.js (@whiskeysockets/baileys)       | 连接 WhatsApp，收发消息             |
| iMessage 频道 | better-sqlite3 + osascript              | 轮询 chat.db，通过 AppleScript 发送 |
| 消息存储      | SQLite (better-sqlite3)                 | 存储消息用于轮询                    |
| 容器运行时    | Apple Container                         | 用于智能体执行的隔离 Linux 虚拟机   |
| 智能体        | @anthropic-ai/claude-agent-sdk (0.2.29) | 运行带工具和 MCP 服务器的 Claude    |
| 浏览器自动化  | agent-browser + Chromium                | 网页交互和截图                      |
| 运行时        | Node.js 20+                             | 路由和调度的宿主进程                |

---

## 目录结构

```
bao/
├── CLAUDE.md                      # Claude Code 的项目上下文
├── docs/
│   ├── SPEC.md                    # 本规格说明文档
│   ├── REQUIREMENTS.md            # 架构决策
│   └── SECURITY.md                # 安全模型
├── README.md                      # 用户文档
├── package.json                   # Node.js 依赖
├── tsconfig.json                  # TypeScript 配置
├── .mcp.json                      # MCP 服务器配置（参考）
├── .gitignore
│
├── src/
│   ├── index.ts                   # 编排器：状态管理、消息循环、智能体调用
│   ├── channels/
│   │   ├── whatsapp.ts            # WhatsApp 连接、认证、收发消息
│   │   └── imessage.ts            # iMessage 频道（macOS，轮询 chat.db）
│   ├── ipc.ts                     # IPC 监听与任务处理
│   ├── router.ts                  # 消息格式化与出站路由
│   ├── config.ts                  # 配置常量
│   ├── types.ts                   # TypeScript 接口（包含 Channel）
│   ├── logger.ts                  # Pino 日志配置
│   ├── db.ts                      # SQLite 数据库初始化与查询
│   ├── group-queue.ts             # 每群组队列，带全局并发限制
│   ├── mount-security.ts          # 容器挂载白名单校验
│   ├── whatsapp-auth.ts           # 独立的 WhatsApp 认证
│   ├── task-scheduler.ts          # 在到期时运行计划任务
│   └── container-runner.ts        # 在 Apple Container 中生成智能体
│
├── container/
│   ├── Dockerfile                 # 容器镜像（以 'node' 用户运行，包含 Claude Code CLI）
│   ├── build.sh                   # 容器镜像构建脚本
│   ├── agent-runner/              # 容器内部运行的代码
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── src/
│   │       ├── index.ts           # 入口点（查询循环、IPC 轮询、会话恢复）
│   │       └── ipc-mcp-stdio.ts   # 基于 Stdio 的 MCP 服务器，用于宿主通信
│   └── skills/
│       └── agent-browser.md       # 浏览器自动化技能
│
├── dist/                          # 编译后的 JavaScript（gitignored）
│
├── .claude/
│   └── skills/
│       ├── setup/SKILL.md              # /setup - 首次安装
│       ├── customize/SKILL.md          # /customize - 添加功能
│       └── debug/SKILL.md              # /debug - 容器调试
│
├── groups/
│   ├── CLAUDE.md                  # 全局记忆（所有群组可读）
│   ├── main/                      # Self-chat（主控制频道）
│   │   ├── CLAUDE.md              # 主频道记忆
│   │   └── logs/                  # 任务执行日志
│   └── {Group Name}/              # 每群组文件夹（注册时创建）
│       ├── CLAUDE.md              # 群组专属记忆
│       ├── logs/                  # 该群组的任务日志
│       └── *.md                   # 智能体创建的文件
│
├── store/                         # 本地数据（gitignored）
│   ├── auth/                      # WhatsApp 认证状态
│   └── messages.db                # SQLite 数据库（messages, chats, scheduled_tasks, task_run_logs, registered_groups, sessions, router_state）
│
├── data/                          # 应用状态（gitignored）
│   ├── sessions/                  # 每群组会话数据（.claude/ 目录含 JSONL 记录）
│   ├── env/env                    # .env 的副本，用于容器挂载
│   └── ipc/                       # 容器 IPC（messages/, tasks/）
│
├── logs/                          # 运行时日志（gitignored）
│   ├── bao.log               # 宿主 stdout
│   └── bao.error.log         # 宿主 stderr
│   # 注意：每个容器的日志在 groups/{folder}/logs/container-*.log
│
└── launchd/
    └── com.bao.plist         # macOS 服务配置
```

---

## 配置

配置常量位于 `src/config.ts`：

```typescript
import path from 'path';

export const ASSISTANT_NAME = process.env.ASSISTANT_NAME || 'bao';
export const POLL_INTERVAL = 2000;
export const SCHEDULER_POLL_INTERVAL = 60000;

// Paths are absolute (required for container mounts)
const PROJECT_ROOT = process.cwd();
export const STORE_DIR = path.resolve(PROJECT_ROOT, 'store');
export const GROUPS_DIR = path.resolve(PROJECT_ROOT, 'groups');
export const DATA_DIR = path.resolve(PROJECT_ROOT, 'data');

// Container configuration
export const CONTAINER_IMAGE =
  process.env.CONTAINER_IMAGE || 'bao-agent:latest';
export const CONTAINER_TIMEOUT = parseInt(
  process.env.CONTAINER_TIMEOUT || '1800000',
  10,
); // 30min default
export const IPC_POLL_INTERVAL = 1000;
export const IDLE_TIMEOUT = parseInt(process.env.IDLE_TIMEOUT || '1800000', 10); // 30min — keep container alive after last result
export const MAX_CONCURRENT_CONTAINERS = Math.max(
  1,
  parseInt(process.env.MAX_CONCURRENT_CONTAINERS || '5', 10),
);

export const TRIGGER_PATTERN = new RegExp(`^@${ASSISTANT_NAME}\\b`, 'i');
```

**注意：** 路径必须为绝对路径，Apple Container 的卷挂载才能正常工作。

### 容器配置

群组可以通过 SQLite `registered_groups` 表中的 `containerConfig`（以 JSON 格式存储在 `container_config` 列中）配置额外的挂载目录。注册示例：

```typescript
registerGroup('1234567890@g.us', {
  name: 'Dev Team',
  folder: 'dev-team',
  trigger: '@bao',
  added_at: new Date().toISOString(),
  containerConfig: {
    additionalMounts: [
      {
        hostPath: '~/projects/webapp',
        containerPath: 'webapp',
        readonly: false,
      },
    ],
    timeout: 600000,
  },
});
```

额外挂载会出现在容器内的 `/workspace/extra/{containerPath}` 路径。

**Apple Container 挂载语法说明：** 读写挂载使用 `-v host:container`，但只读挂载需要 `--mount "type=bind,source=...,target=...,readonly"`（`:ro` 后缀不起作用）。

### Claude 认证

在项目根目录的 `.env` 文件中配置认证。两种选择：

**选项 1：Claude 订阅（OAuth 令牌）**

```bash
CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...
```

如果你已登录 Claude Code，可以从 `~/.claude/.credentials.json` 中提取令牌。

**选项 2：按量付费 API 密钥**

```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
```

仅认证变量（`CLAUDE_CODE_OAUTH_TOKEN` 和 `ANTHROPIC_API_KEY`）会从 `.env` 中提取并写入 `data/env/env`，然后挂载到容器的 `/workspace/env-dir/env` 并由入口脚本 source。这确保 `.env` 中的其他环境变量不会暴露给智能体。这个变通方案是必要的，因为 Apple Container 在使用 `-i`（交互模式，管道 stdin）时会丢失 `-e` 环境变量。

### 更改助手名称

设置 `ASSISTANT_NAME` 环境变量：

```bash
ASSISTANT_NAME=Bot npm start
```

或者编辑 `src/config.ts` 中的默认值。这会改变：

- 触发模式（消息必须以 `@YourName` 开头）
- 响应前缀（自动添加 `YourName:`）

### launchd 中的占位符

包含 `{{PLACEHOLDER}}` 值的文件需要配置：

- `{{PROJECT_ROOT}}` - bao 安装的绝对路径
- `{{NODE_PATH}}` - node 二进制文件的路径（通过 `which node` 检测）
- `{{HOME}}` - 用户的主目录

---

## 记忆系统

bao 使用基于 CLAUDE.md 文件的层级记忆系统。

### 记忆层级

| 层级     | 位置                      | 读取者   | 写入者   | 用途                             |
| -------- | ------------------------- | -------- | -------- | -------------------------------- |
| **全局** | `groups/CLAUDE.md`        | 所有群组 | 仅主频道 | 所有会话共享的偏好、事实、上下文 |
| **群组** | `groups/{name}/CLAUDE.md` | 该群组   | 该群组   | 群组专属上下文、会话记忆         |
| **文件** | `groups/{name}/*.md`      | 该群组   | 该群组   | 会话中创建的笔记、研究、文档     |

### 记忆工作原理

1. **智能体上下文加载**
   - 智能体以 `cwd` 设置为 `groups/{group-name}/` 运行
   - Claude Agent SDK 使用 `settingSources: ['project']` 自动加载：
     - `../CLAUDE.md`（父目录 = 全局记忆）
     - `./CLAUDE.md`（当前目录 = 群组记忆）

2. **写入记忆**
   - 当用户说"记住这个"时，智能体写入 `./CLAUDE.md`
   - 当用户说"全局记住这个"（仅主频道）时，智能体写入 `../CLAUDE.md`
   - 智能体可以在群组文件夹中创建 `notes.md`、`research.md` 等文件

3. **主频道权限**
   - 只有"主"群组（self-chat）可以写入全局记忆
   - 主频道可以管理注册的群组并为任何群组调度任务
   - 主频道可以为任何群组配置额外的目录挂载
   - 所有群组都有 Bash 访问权限（安全的，因为在容器内运行）

---

## 会话管理

会话实现会话连续性 - Claude 会记住你们聊过的内容。

### 会话工作原理

1. 每个群组在 SQLite 中有一个会话 ID（`sessions` 表，以 `group_folder` 为键）
2. 会话 ID 传递给 Claude Agent SDK 的 `resume` 选项
3. Claude 以完整上下文继续会话
4. 会话记录以 JSONL 文件存储在 `data/sessions/{group}/.claude/`

---

## 消息流程

### 入站消息流程

```
1. User sends WhatsApp/iMessage message
   │
   ▼
2. Baileys receives WhatsApp message / iMessage channel polls chat.db
   │
   ▼
3. Message stored in SQLite (store/messages.db)
   │
   ▼
4. Message loop polls SQLite (every 2 seconds)
   │
   ▼
5. Router checks:
   ├── Is chat_jid in registered groups (SQLite)? → No: ignore
   └── Does message match trigger pattern? → No: store but don't process
   │
   ▼
6. Router catches up conversation:
   ├── Fetch all messages since last agent interaction
   ├── Format with timestamp and sender name
   └── Build prompt with full conversation context
   │
   ▼
7. Router invokes Claude Agent SDK:
   ├── cwd: groups/{group-name}/
   ├── prompt: conversation history + current message
   ├── resume: session_id (for continuity)
   └── mcpServers: bao (scheduler)
   │
   ▼
8. Claude processes message:
   ├── Reads CLAUDE.md files for context
   └── Uses tools as needed (search, email, etc.)
   │
   ▼
9. Router prefixes response with assistant name and sends via WhatsApp
   │
   ▼
10. Router updates last agent timestamp and saves session ID
```

### 触发词匹配

消息必须以触发模式开头（默认：`@bao`）：

- `@bao what's the weather?` → ✅ 触发 Claude
- `@bao help me` → ✅ 触发（不区分大小写）
- `Hey @bao` → ❌ 忽略（触发词不在开头）
- `What's up?` → ❌ 忽略（没有触发词）

### 会话追赶

当触发消息到达时，智能体会收到该聊天中自上次交互以来的所有消息。每条消息都带有时间戳和发送者名称：

```
[Jan 31 2:32 PM] John: hey everyone, should we do pizza tonight?
[Jan 31 2:33 PM] Sarah: sounds good to me
[Jan 31 2:35 PM] John: @bao what toppings do you recommend?
```

这使得智能体即使没有在每条消息中被提及，也能理解会话上下文。

---

## 命令

### 任何群组中可用的命令

| 命令                | 示例                       | 效果           |
| ------------------- | -------------------------- | -------------- |
| `@Assistant [消息]` | `@bao what's the weather?` | 与 Claude 对话 |

### 仅在主频道中可用的命令

| 命令                             | 示例                               | 效果             |
| -------------------------------- | ---------------------------------- | ---------------- |
| `@Assistant add group "Name"`    | `@bao add group "Family Chat"`     | 注册一个新群组   |
| `@Assistant remove group "Name"` | `@bao remove group "Work Team"`    | 取消注册一个群组 |
| `@Assistant list groups`         | `@bao list groups`                 | 显示已注册的群组 |
| `@Assistant remember [事实]`     | `@bao remember I prefer dark mode` | 添加到全局记忆   |

---

## 计划任务

bao 内置了调度器，可以在群组上下文中以完整智能体身份运行任务。

### 调度工作原理

1. **群组上下文**：在某个群组中创建的任务会使用该群组的工作目录和记忆运行
2. **完整智能体能力**：计划任务可以使用所有工具（WebSearch、文件操作等）
3. **可选消息发送**：任务可以使用 `send_message` 工具向其群组发送消息，或静默完成
4. **主频道权限**：主频道可以为任何群组调度任务并查看所有任务

### 调度类型

| 类型       | 值格式      | 示例                           |
| ---------- | ----------- | ------------------------------ |
| `cron`     | Cron 表达式 | `0 9 * * 1`（每周一上午 9 点） |
| `interval` | 毫秒        | `3600000`（每小时）            |
| `once`     | ISO 时间戳  | `2024-12-25T09:00:00Z`         |

### 创建任务

```
User: @bao remind me every Monday at 9am to review the weekly metrics

Claude: [calls mcp__bao__schedule_task]
        {
          "prompt": "Send a reminder to review weekly metrics. Be encouraging!",
          "schedule_type": "cron",
          "schedule_value": "0 9 * * 1"
        }

Claude: Done! I'll remind you every Monday at 9am.
```

### 一次性任务

```
User: @bao at 5pm today, send me a summary of today's emails

Claude: [calls mcp__bao__schedule_task]
        {
          "prompt": "Search for today's emails, summarize the important ones, and send the summary to the group.",
          "schedule_type": "once",
          "schedule_value": "2024-01-31T17:00:00Z"
        }
```

### 管理任务

在任何群组中：

- `@bao list my scheduled tasks` - 查看该群组的任务
- `@bao pause task [id]` - 暂停任务
- `@bao resume task [id]` - 恢复暂停的任务
- `@bao cancel task [id]` - 删除任务

在主频道中：

- `@bao list all tasks` - 查看所有群组的任务
- `@bao schedule task for "Family Chat": [prompt]` - 为其他群组调度任务

---

## MCP 服务器

### bao MCP（内置）

`bao` MCP 服务器根据当前群组的上下文动态创建。

**可用工具：**
| 工具 | 用途 |
|------|------|
| `schedule_task` | 调度周期性或一次性任务 |
| `list_tasks` | 显示任务（群组任务，或主频道显示全部） |
| `get_task` | 获取任务详情和运行历史 |
| `update_task` | 修改任务提示词或调度计划 |
| `pause_task` | 暂停任务 |
| `resume_task` | 恢复暂停的任务 |
| `cancel_task` | 删除任务 |
| `send_message` | 向群组发送 WhatsApp 消息 |

---

## 部署

bao 作为单个 macOS launchd 服务运行。

### 启动顺序

当 bao 启动时，它：

1. **确保 Apple Container 系统正在运行** - 如果需要会自动启动；清理上次运行遗留的孤立 bao 容器
2. 初始化 SQLite 数据库（如果存在 JSON 文件则进行迁移）
3. 从 SQLite 加载状态（注册的群组、会话、路由器状态）
4. 连接到 WhatsApp（在 `connection.open` 时）：
   - 启动调度器循环
   - 启动 IPC 监听器以处理容器消息
   - 使用 `processGroupMessages` 设置每群组队列
   - 恢复关机前未处理的消息
   - 启动消息轮询循环

### 服务：com.bao

**launchd/com.bao.plist:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "...">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.bao</string>
    <key>ProgramArguments</key>
    <array>
        <string>{{NODE_PATH}}</string>
        <string>{{PROJECT_ROOT}}/dist/index.js</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{{PROJECT_ROOT}}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>{{HOME}}/.local/bin:/usr/local/bin:/usr/bin:/bin</string>
        <key>HOME</key>
        <string>{{HOME}}</string>
        <key>ASSISTANT_NAME</key>
        <string>bao</string>
    </dict>
    <key>StandardOutPath</key>
    <string>{{PROJECT_ROOT}}/logs/bao.log</string>
    <key>StandardErrorPath</key>
    <string>{{PROJECT_ROOT}}/logs/bao.error.log</string>
</dict>
</plist>
```

### 管理服务

```bash
# 安装服务
cp launchd/com.bao.plist ~/Library/LaunchAgents/

# 启动服务
launchctl load ~/Library/LaunchAgents/com.bao.plist

# 停止服务
launchctl unload ~/Library/LaunchAgents/com.bao.plist

# 检查状态
launchctl list | grep bao

# 查看日志
tail -f logs/bao.log
```

---

## 安全考虑

### 容器隔离

所有智能体运行在 Apple Container（轻量级 Linux 虚拟机）中，提供：

- **文件系统隔离**：智能体只能访问已挂载的目录
- **安全的 Bash 访问**：命令在容器内运行，而不是在你的 Mac 上
- **网络隔离**：可按容器配置
- **进程隔离**：容器进程不会影响宿主
- **非 root 用户**：容器以非特权 `node` 用户运行（uid 1000）

### 提示注入风险

WhatsApp 消息可能包含试图操纵 Claude 行为的恶意指令。

**缓解措施：**

- 容器隔离限制了影响范围
- 仅处理已注册群组的消息
- 需要触发词（减少意外处理）
- 智能体只能访问其群组已挂载的目录
- 主频道可以为每个群组配置额外目录
- Claude 内置的安全训练

**建议：**

- 仅注册受信任的群组
- 仔细审查额外的目录挂载
- 定期检查计划任务
- 监控日志中的异常活动

### 凭证存储

| 凭证            | 存储位置                       | 备注                                   |
| --------------- | ------------------------------ | -------------------------------------- |
| Claude CLI 认证 | data/sessions/{group}/.claude/ | 每群组隔离，挂载到 /home/node/.claude/ |
| WhatsApp 会话   | store/auth/                    | 自动创建，持续约 20 天                 |

### 文件权限

groups/ 文件夹包含个人记忆，应该加以保护：

```bash
chmod 700 groups/
```

---

## 故障排除

### 常见问题

| 问题                                     | 原因                     | 解决方案                                                             |
| ---------------------------------------- | ------------------------ | -------------------------------------------------------------------- | --------- |
| 消息没有响应                             | 服务未运行               | 检查 `launchctl list                                                 | grep bao` |
| "Claude Code process exited with code 1" | Apple Container 启动失败 | 检查日志；bao 会自动启动容器系统但可能失败                           |
| "Claude Code process exited with code 1" | 会话挂载路径错误         | 确保挂载到 `/home/node/.claude/` 而不是 `/root/.claude/`             |
| 会话不连续                               | 会话 ID 未保存           | 检查 SQLite：`sqlite3 store/messages.db "SELECT * FROM sessions"`    |
| 会话不连续                               | 挂载路径不匹配           | 容器用户是 `node`，HOME=/home/node；会话必须在 `/home/node/.claude/` |
| "QR code expired"                        | WhatsApp 会话过期        | 删除 store/auth/ 并重启                                              |
| "No groups registered"                   | 尚未添加群组             | 在主频道使用 `@bao add group "Name"`                                 |

### 日志位置

- `logs/bao.log` - stdout
- `logs/bao.error.log` - stderr

### 调试模式

手动运行以获取详细输出：

```bash
npm run dev
# 或
node dist/index.js
```
