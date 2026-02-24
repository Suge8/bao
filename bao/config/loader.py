import json
import re
from pathlib import Path
from typing import Any

from bao.config.schema import Config

_JSONC_TEMPLATE = """\
{
  // ╔═══════════════════════════════════════════════════════════════╗
  // ║  bao 配置文件 | bao Configuration                            ║
  // ╚═══════════════════════════════════════════════════════════════╝
  // ───────────────────────────────────────────────────────────────
  //  🤖 Agent 配置 | Agent Settings
  // ───────────────────────────────────────────────────────────────
  "agents": {
    "defaults": {
      "workspace": "~/.bao/workspace",
      // 主模型 | Main model
      // 格式 Format: "前缀/模型名" e.g. "openai/gpt-5.2", "deepseek/deepseek-chat"
      // 推荐 Recommended:
      //   "anthropic/claude-opus-4-6"
      //   "zhipu/glm-5"
      //   "moonshot/kimi-k2.5"
      //   "openai/gpt-5.2"
      "model": "",
      // 轻量模型（可选）：后台任务用，节省开销
      // Utility model (optional): for background tasks, saves cost
      "utilityModel": "",
      // 经验模型策略 | Experience model strategy
      //   "utility" — 用轻量模型(默认) | use utility model (default)
      //   "main"    — 用主模型 | use main model
      //   "none"    — 不调用 LLM | no LLM calls
      "experienceModel": "utility",
      // 可切换模型列表，运行时 /model 切换 | Switchable models, use /model at runtime
      "models": [],
      "maxTokens": 8192,
      "temperature": 0.1,
      "maxToolIterations": 20,
      "memoryWindow": 50,
      // 是否向聊天渠道发送进度消息（如"正在处理…"）
      // Whether to send progress messages to chat channels
      "sendProgress": false,
      // 是否向聊天渠道发送工具调用提示（如 web_search("...")）
      // Whether to send tool-call hints to chat channels
      "sendToolHints": false
    }
  },
  // ───────────────────────────────────────────────────────────────
  //  🔑 LLM Providers — 取消注释以启用 | Uncomment to enable
  //
  //  ⚠️  请至少启用一个 | Enable at least one
  //  名称随意，type 决定 SDK | Name freely, type determines SDK
  //  type: "openai" | "anthropic" | "gemini"
  // ───────────────────────────────────────────────────────────────
  "providers": {
    // ── 示例 | Example ─────────────────────────
    // ── OpenAI 兼容 | OpenAI Compatible     //  适用 Supports: OpenAI, OpenRouter, Groq, Moonshot, GLM...
    // "provider-name": {
    //   "type": "openai",
    //   "apiKey": "sk-xxx",
    //   "apiBase": "https://api.openai.com/v1",  // 留空用官方，填代理地址自动兼容 | Empty for official, proxy auto-compatible
    //   "apiMode": "auto"              // "auto" | "responses" | "completions"
    // },
    // ── Anthropic ───────────────────────────────────────────────
    // "provider-name": {
    //   "type": "anthropic",
    //   "apiKey": "sk-xxx",
    //   "apiBase": ""                  // 留空用官方，填代理地址自动兼容 | Empty for official, proxy auto-compatible
    // },
    // ── Google Gemini ───────────────────────────────────────────
    // "provider-name": {
    //   "type": "gemini",
    //   "apiKey": "AI...",
    //   "apiBase": ""                  // 留空用官方 | Empty for official API
    // },
    // ── 添加更多 | Add more ─────────────────────────────────────
    // "your-provider-name": {
    //   "type": "openai",              // openai | anthropic | gemini
    //   "apiKey": "",
    //   "apiBase": ""
    // }
  },
  // ───────────────────────────────────────────────────────────────
  //  💬 聊天渠道 — 取消注释以启用 | Chat Channels — Uncomment to enable
  //  推荐 iMessage（macOS 零配置）| iMessage recommended (macOS, zero config)
  // ───────────────────────────────────────────────────────────────
  "channels": {
    // ── iMessage（推荐 Recommended）─────────────────────────────
    //  仅 macOS | macOS only
    //
    // "imessage": {
    //   "enabled": true,
    //   "pollInterval": 2.0,
    //   "service": "iMessage",
    //   "allowFrom": []
    // },
    //
    // ── Telegram ────────────────────────────────────────────────
    //  Token from @BotFather
    //
    // "telegram": {
    //   "enabled": true,
    //   "token": "123456:ABC-DEF...",
    //   "allowFrom": [],
    //   "proxy": null,
    //   "replyToMessage": false
    // },
    //
    // ── Discord ─────────────────────────────────────────────────
    //  Bot Token + Message Content Intent
    //
    // "discord": {
    //   "enabled": true,
    //   "token": "MTIz...",
    //   "allowFrom": []
    // },
    //
    // ── WhatsApp ────────────────────────────────────────────────
    //  通过 Bridge 扫码 | Connect via bridge, scan QR
    //
    // "whatsapp": {
    //   "enabled": true,
    //   "bridgeUrl": "ws://localhost:3001",
    //   "bridgeToken": "",
    //   "allowFrom": []
    // },
    //
    // ── 飞书 Feishu / Lark ──────────────────────────────────────
    //  App ID + App Secret
    //
    // "feishu": {
    //   "enabled": true,
    //   "appId": "",
    //   "appSecret": "",
    //   "encryptKey": "",
    //   "verificationToken": "",
    //   "allowFrom": []
    // },
    //
    // ── Slack ────────────────────────────────────────────────────
    //  Bot Token (xoxb-...) + App Token (xapp-...)
    //
    // "slack": {
    //   "enabled": true,
    //   "botToken": "xoxb-...",
    //   "appToken": "xapp-...",
    //   "replyInThread": true,
    //   "reactEmoji": "eyes",
    //   "groupPolicy": "mention",
    //   "allowFrom": []
    // },
    //
    // ── 钉钉 DingTalk ───────────────────────────────────────────
    //  AppKey + AppSecret（Stream 模式 | Stream mode）
    //
    // "dingtalk": {
    //   "enabled": true,
    //   "clientId": "",
    //   "clientSecret": "",
    //   "allowFrom": []
    // },
    //
    // ── QQ ───────────────────────────────────────────────────────
    //  App ID + Secret（botpy SDK）
    //
    // "qq": {
    //   "enabled": true,
    //   "appId": "",
    //   "secret": "",
    //   "allowFrom": []
    // },
    //
    // ── Email 邮件 ──────────────────────────────────────────────
    //  IMAP 收件 + SMTP 发件 | IMAP receive + SMTP send
    //
    // "email": {
    //   "enabled": true,
    //   "consentGranted": true,
    //   "imapHost": "imap.gmail.com",
    //   "imapPort": 993,
    //   "imapUsername": "",
    //   "imapPassword": "",
    //   "smtpHost": "smtp.gmail.com",
    //   "smtpPort": 587,
    //   "smtpUsername": "",
    //   "smtpPassword": "",
    //   "fromAddress": "",
    //   "allowFrom": []
    // },
    //
    // ── Mochat ───────────────────────────────────────────────────
    //  Mochat 客服集成 | Mochat customer service
    //
    // "mochat": {
    //   "enabled": true,
    //   "baseUrl": "https://mochat.io",
    //   "clawToken": "",
    //   "agentUserId": "",
    //   "allowFrom": []
    // }
  },
  // ───────────────────────────────────────────────────────────────
  //  🔧 工具配置 | Tool Settings
  // ───────────────────────────────────────────────────────────────
  "tools": {
    // 网页搜索：填 Tavily 或 Brave API Key 启用
    // Web search: fill Tavily or Brave API Key to enable
    "web": {
      "search": {
        "provider": "",
        "tavilyApiKey": "",
        "braveApiKey": ""
      }
    },
    "exec": {
      "timeout": 60
    },
    // 向量嵌入（可选）| Embedding (optional)
    "embedding": {
      "model": "",
      "apiKey": "",
      "baseUrl": ""
    },
    "restrictToWorkspace": false,
    // MCP 服务器，兼容 Claude Desktop / Cursor
    // MCP servers, compatible with Claude Desktop / Cursor
    "mcpServers": {}
  }
}
"""

_WORKSPACE_TEMPLATES: dict[str, str] = {
    "PERSONA.md": """# 人设

## 身份

我是运行在 bao 框架里的一个轻量级全能 AGENT。

- 乐于助人、友善
- 简洁、切中要点
- 好奇、乐于学习
- 准确优先于速度
- 保护用户隐私和安全
- 行动透明

## 用户

- **姓名**：（你的名字）
- **时区**：（你的时区）
- **语言**：中文
- **沟通风格**：（随意/正式）
- **角色**：（你的角色，如开发者、研究员）
- **兴趣领域**：（你关注的话题）

## 特殊指令

（对助手行为的任何特定指令）
""",
    "INSTRUCTIONS.md": """# 指令

## 行为准则

- 在执行操作前，始终先说明你要做什么
- 当请求含糊不清时，主动询问确认
- 使用工具来协助完成任务
- 简洁、准确、友善

## 工作区架构

你的工作区包含以下组件：

### 文件

| 文件 | 用途 |
|------|------|
| `PERSONA.md` | 你的人格、价值观和用户档案 |
| `INSTRUCTIONS.md` | 行为规则和工作区文档（本文件） |
| `HEARTBEAT.md` | 定期任务清单，每 30 分钟检查一次 |
| `skills/` | 自定义技能定义（`skills/{name}/SKILL.md`） |

### 数据库（LanceDB — 自动管理）

| 表 | 用途 |
|----|------|
| `memory` | 长期记忆（`key='long_term'`）、对话历史（`type='history'`）和任务经验（`type='experience'`） |
| `memory_vectors` | 可选的语义嵌入，用于记忆和经验搜索 |

### 记忆规则

记忆存储在 LanceDB 中，自动管理。
不要对记忆使用 `read_file`/`write_file`/`edit_file`。
只需确认你需要记住的内容 — 它会在对话整合时自动保存。

### 经验学习（ExperienceLoop）

系统通过闭环反馈循环自动从已完成的任务中学习：

1. 每次任务完成后（使用了 ≥2 个工具或出现错误），系统会提取教训、搜索关键词和推理链，存储为 LanceDB 中的 `type='experience'`
2. 每条经验包含：任务描述、结果（成功/部分成功/失败）、质量评分（1-5）、分类、可操作的教训、搜索关键词、使用计数器（使用次数/成功次数）和推理链
3. 当类似任务出现时，过往经验会被检索并注入到系统提示中
4. 失败的任务会作为警告（⚠️）保留，与正面经验一起呈现，防止重复犯错
5. **系统消息（cron 定时任务等）与普通消息享有完全相同的经验能力**：经验检索 + 经验提取 + 合并清理，确保定时任务也能从过往教训中学习并产生新经验

#### 经验生命周期

- **质量评分**：每条经验评分 1-5，评分越高在搜索中排名越前。
- **统计置信度**：每条经验跟踪 使用次数/成功次数 计数器。置信度采用 Laplace 平滑 `(成功次数+1)/(使用次数+2)`，避免冷启动偏差。≥3 次使用后质量自动调整：成功率 ≥80% → 质量 +1，<40% → 质量 -1。
- **反馈循环**：任务成功完成时记录复用事件（使用次数+1，成功次数+1）。失败则弃用类似的过时经验。
- **冲突检测**：当同一分类下检索到的经验结论矛盾时，会标记 ⚡ 以提醒模型。
- **推理链追踪**：每条经验捕获 agent 中间推理步骤的摘要，存储为 `[Trace]` 以提供更丰富的上下文。
- **分类**：`coding`、`search`、`file`、`config`、`analysis`、`general` — 用于分组和合并。
- **关键词**：每条经验存储 2-5 个搜索关键词，增强超越语义相似性的检索能力。
- **分级衰减**：经验按质量分级设定保留期（质量5=365天, 4=180天, 3=90天, 2=30天, 1=14天），高质量经验衰减更慢，低质量经验更快淘汰。
- **负面学习**：失败的经验会被保留（而非仅弃用），并作为警告呈现，防止重复犯同样的错误。
- **自动清理与免疫**：弃用超过 30 天的条目和质量为 1 且超过 90 天的条目会被自动移除。质量 ≥5 且被复用 ≥3 次的经验免疫清理（除非被明确标记为弃用）。
- **合并**：当同一分类下的经验累积达 ≥3 条时，会定期合并为简洁的高层原则。
- **排名**：搜索结果按 `质量 × 时间衰减 × 置信度` 排序，确保最好、最可靠、最新的经验优先呈现。

搜索模式：
- **有嵌入模型时**：语义向量搜索（质量更高）
- **无嵌入模型时**：关键词匹配降级搜索（仍可工作）

如果在 `agents.defaults` 中配置了 `utilityModel`，经验提取、记忆整合和会话标题生成会使用该轻量模型，而非主模型。

轨迹压缩和收敛验证的模型由 `experienceModel` 配置控制：
- `"utility"`（默认）— 使用轻量模型，未配置 utilityModel 则退化为零成本规则
- `"main"` — 使用主模型（质量最高，但消耗更多）
- `"none"` — 零成本规则，不调用 LLM（仅基于规则的进度摘要）

经验条目自动管理 — 无需手动操作。

### 会话自动命名

每个新会话的首轮对话（用户消息 + 助手回复）完成后，系统会异步调用 `utilityModel` 自动生成一个简短标题（≤20 字），存储在 `session.metadata["title"]` 中。标题语言跟随用户消息语言。该过程不阻塞主响应流程，失败时静默降级（仍使用 `s1`/`s2` 编号）。生成的标题会在 `/session` 列表和会话切换提示中优先展示。

### 轨迹压缩

复杂任务执行中，系统会自动进行跨步骤状态管理：

- **结构化状态压缩**：每 5 步工具调用后，将执行轨迹压缩为 3 维状态（结论/证据/待探索分支），注入下一轮 context 保持全局感知
- **状态递归累积**：每次压缩基于上一次状态更新，而非从头生成，实现跨步骤知识递归积累
- **未完成分支追踪**：压缩状态中显式保留"提到但未执行的方向"，标记 `[Unexplored branches]`，引导模型优先探索未覆盖路径
- **自由采纳指令**：状态注入时附带"可自由判断是否采纳"提示，防止模型过度依赖历史状态而陷入局部最优
- **失败方向记录**：工具出错时结构化记录已失败路径，后续轮次自动规避重复尝试
- **工具结果摘要**：执行轨迹中包含成功结果的前 100 字摘要，为状态压缩提供更丰富的证据
- **收敛验证**：工具调用 ≥8 步后，判断已有信息是否足够回答，足够则提示模型给出最终答案，避免冗余探索
- **Subagent 状态感知**：子任务执行同样具备失败方向追踪和进度注入，确保后台任务也不重复撞墙

简单任务（<5 步工具调用）不触发以上机制，零额外开销。

### 工具策略

`web_search` 工具仅在配置了 Tavily/Brave API key 时才会注册到工具列表。如果你的工具列表中包含 `web_search`，则优先用它搜索信息；如果不包含，说明未配置搜索 API key，此时用 `web_fetch` 访问搜索引擎页面，不要用 `exec` + `curl`。**不要声称拥有工具列表中不存在的工具。**

### 日志

- 默认输出 INFO 级别日志（简洁）
- 使用 `bao gateway -v` 启用 DEBUG 级别详细日志


## 身份与偏好持久化

当用户在日常对话中告诉你以下内容时，使用 `edit_file` 更新 `PERSONA.md`：

- **用户的姓名/昵称、时区、语言、偏好** → 更新 `## 用户` 部分
- **你的昵称、人格特征、沟通风格** → 更新 `## 身份` 部分

`PERSONA.md` 在每次对话开始时加载。如果你不写入，下次就会忘记。

## 定时提醒

使用 `cron` 工具创建提醒和定时任务。详细用法参见 `skills/cron/SKILL.md`（如已安装 cron skill）。

不要只是把提醒写入记忆 — 那不会触发实际通知。

## 心跳任务

`HEARTBEAT.md` 每 30 分钟检查一次。通过编辑此文件来管理定期任务：

```
- [ ] 检查日历并提醒即将到来的事件
- [ ] 扫描收件箱查看紧急邮件
```

当用户要求定期任务时，更新 `HEARTBEAT.md` 而不是创建一次性提醒。

## 上下文管理（Context Management）
bao 内置分层上下文管理，防止长任务耗尽 context window。

### Layer 1：大型 tool 输出外置
当 tool 输出超过阈值（默认 8000 字符），自动外置到 `.bao/context/<session>/outputs/`，messages 中只保留预览+文件指针。

### Layer 2：messages 压实（Compaction）
当 messages 估算大小超过阈值（默认 240KB），自动归档旧的 assistant/tool 成对消息，只保留最近 N 对（默认 4 对）+ 原始请求。

### 配置
在 `~/.bao/config.jsonc` 的 `agents.defaults` 中配置：
```json
{
  "agents": {
    "defaults": {
      "contextManagement": "auto",
      "toolOutputOffloadChars": 8000,
      "toolOutputPreviewChars": 3000,
      "contextCompactBytesEst": 240000,
      "contextCompactKeepRecentToolBlocks": 4,
      "artifactRetentionDays": 7
    }
  }
}
```

| 值 | 说明 |
|---|---|
| `observe` | 默认。仅观察，不触发任何外置或压实 |
| `auto` | 超过阈值时自动触发 Layer 1 + Layer 2 |

外置的文件保存在 `workspace/.bao/context/` 下，`artifactRetentionDays` 天后自动清理。

""",
    "HEARTBEAT.md": """# 心跳任务

此文件每 30 分钟由 bao agent 自动检查。
在下方添加你希望 agent 定期执行的任务。

如果此文件没有任务（只有标题和注释），agent 会跳过本次心跳。

## 进行中的任务

<!-- 在此行下方添加你的定期任务 -->


## 已完成

<!-- 将已完成的任务移到这里或删除 -->

""",
}

_PERSONA_EN = """# Persona

## Identity

I am bao, a lightweight AI assistant.

- Helpful, friendly
- Concise, to the point
- Curious, eager to learn
- Accuracy over speed
- Protect user privacy and security
- Transparent in actions

## User

- **Name**: (your name)
- **Timezone**: (your timezone)
- **Language**: English
- **Communication style**: (casual/formal)
- **Role**: (your role, e.g. developer, researcher)
- **Interests**: (topics you care about)

## Special Instructions

(Any specific instructions for the assistant)
"""

_INSTRUCTIONS_EN = """# Instructions

## Guidelines

- Always explain what you're about to do before taking action
- Ask for clarification when requests are ambiguous
- Use tools to assist with tasks
- Be concise, accurate, and friendly

## Workspace Architecture

Your workspace contains:

### Files

| File | Purpose |
|------|---------|
| `PERSONA.md` | Your personality, values, and user profile |
| `INSTRUCTIONS.md` | Behavior rules and workspace docs (this file) |
| `HEARTBEAT.md` | Periodic task checklist, checked every 30 minutes |
| `skills/` | Custom skill definitions (`skills/{name}/SKILL.md`) |

### Database (LanceDB — Auto-managed)

| Table | Purpose |
|-------|---------|
| `memory` | Long-term memory (`key='long_term'`), conversation history (`type='history'`), and task experience (`type='experience'`) |
| `memory_vectors` | Optional semantic embeddings for memory and experience search |

### Memory Rules

Memory is stored in LanceDB and managed automatically.
Do not use `read_file`/`write_file`/`edit_file` on memory.
Just confirm what you need to remember — it will be saved during conversation consolidation.

### Experience Learning (ExperienceLoop)

The system automatically learns from completed tasks via a closed-loop feedback cycle:

1. After each task (≥2 tools used or errors occurred), the system extracts lessons, search keywords, and reasoning chains, stored as `type='experience'` in LanceDB
2. Each experience includes: task description, outcome (success/partial/failure), quality score (1-5), category, actionable lessons, search keywords, usage counters (uses/successes), and reasoning chain
3. When similar tasks arise, past experiences are retrieved and injected into the system prompt
4. Failed tasks are kept as warnings (⚠️) alongside positive experiences to prevent repeating mistakes
5. **System messages (cron tasks, etc.) have the same experience capabilities**: retrieval + extraction + merge cleanup, ensuring scheduled tasks also learn from past lessons

#### Experience Lifecycle

- **Quality score**: Each experience rated 1-5; higher scores rank first in search.
- **Statistical confidence**: Each experience tracks uses/successes counters. Confidence uses Laplace smoothing `(successes+1)/(uses+2)` to avoid cold-start bias. After ≥3 uses, quality auto-adjusts: success rate ≥80% → quality +1, <40% → quality -1.
- **Feedback loop**: Successful task completion records reuse events (uses+1, successes+1). Failure deprecates similar outdated experiences.
- **Conflict detection**: When retrieved experiences in the same category contradict each other, they are flagged with ⚡.
- **Reasoning chain tracking**: Each experience captures a summary of agent intermediate reasoning steps, stored as `[Trace]`.
- **Categories**: `coding`, `search`, `file`, `config`, `analysis`, `general` — for grouping and merging.
- **Keywords**: Each experience stores 2-5 search keywords to enhance retrieval beyond semantic similarity.
- **Graded decay**: Experiences have quality-based retention periods (quality 5=365d, 4=180d, 3=90d, 2=30d, 1=14d). Higher quality decays slower, lower quality is pruned faster.
- **Negative learning**: Failed experiences are retained (not just deprecated) and presented as warnings.
- **Auto-cleanup & immunity**: Deprecated entries older than 30 days and quality-1 entries older than 90 days are removed. Quality ≥5 with ≥3 reuses are immune from cleanup (unless explicitly deprecated).
- **Merging**: When ≥3 experiences accumulate in the same category, they are periodically merged into concise high-level principles.
- **Ranking**: Search results sorted by `quality × time_decay × confidence`, ensuring the best, most reliable, freshest experiences surface first.

Search modes:
- **With embedding model**: Semantic vector search (higher quality)
- **Without embedding model**: Keyword matching fallback (still works)

If `utilityModel` is configured in `agents.defaults`, experience extraction, memory consolidation, and session title generation use that lightweight model instead of the main model.

Trajectory compression and convergence verification model controlled by `experienceModel` config:
- `"utility"` (default) — use lightweight model; falls back to zero-cost rules if utilityModel not configured
- `"main"` — use main model (highest quality, but more expensive)
- `"none"` — zero-cost rules, no LLM calls (rule-based progress summaries only)

Experience entries are managed automatically — no manual action needed.

### Session Auto-Naming

After the first exchange (user message + assistant reply) in each new session, the system asynchronously calls `utilityModel` to generate a short title (≤20 chars), stored in `session.metadata["title"]`. Title language follows the user's message language. This does not block the main response flow; on failure it silently falls back to `s1`/`s2` numbering. Generated titles are shown in `/session` lists and session switch prompts.

### Trajectory Compression

During complex task execution, the system automatically manages cross-step state:

- **Structured state compression**: Every 5 tool calls, the execution trajectory is compressed into 3 dimensions (conclusions/evidence/unexplored branches), injected into the next round's context for global awareness
- **Recursive state accumulation**: Each compression builds on the previous state rather than regenerating from scratch, enabling recursive knowledge accumulation across steps
- **Unexplored branch tracking**: Compressed state explicitly preserves "mentioned but unexecuted directions", marked as `[Unexplored branches]`, guiding the model to prioritize uncovered paths
- **Free adoption**: State injection includes a "feel free to adopt or ignore" hint, preventing over-reliance on historical state
- **Failed direction logging**: Tool errors are structurally recorded as failed paths, automatically avoided in subsequent rounds
- **Tool result summaries**: Execution traces include the first 100 chars of successful results, providing richer evidence for state compression
- **Convergence verification**: After ≥8 tool calls, checks whether existing information is sufficient to answer; if so, prompts the model to give a final answer
- **Subagent state awareness**: Subtasks also have failed direction tracking and progress injection, ensuring background tasks don't repeat mistakes

Simple tasks (<5 tool calls) don't trigger these mechanisms — zero overhead.

### Tool Strategy

`web_search` is only registered when a Tavily/Brave API key is configured. If `web_search` is in your tool list, prefer it for information retrieval; if not, it means no search API key is configured — use `web_fetch` to access search engine pages instead of `exec` + `curl`. **Do not claim to have tools that are not in your tool list.**

### Logging

- Default: INFO level logs (concise)
- Use `bao gateway -v` for DEBUG level verbose logs


## Identity & Preference Persistence

When the user mentions the following in daily conversation, use `edit_file` to update `PERSONA.md`:

- **User's name/nickname, timezone, language, preferences** → Update `## User` section
- **Your nickname, personality traits, communication style** → Update `## Identity` section

`PERSONA.md` is loaded at the start of every conversation. If you don't write it, you'll forget next time.

## Reminders

Use the `cron` tool to create reminders and scheduled tasks. See `skills/cron/SKILL.md` for detailed usage (if cron skill is installed).

Don't just write reminders to memory — that won't trigger actual notifications.

## Heartbeat Tasks

`HEARTBEAT.md` is checked every 30 minutes. Manage periodic tasks by editing this file:

```
- [ ] Check calendar and remind about upcoming events
- [ ] Scan inbox for urgent emails
```

When users request periodic tasks, update `HEARTBEAT.md` instead of creating one-time reminders.

## Context Management
bao has built-in layered context management to prevent long tasks from exhausting the context window.

### Layer 1: Large Tool Output Offloading
When tool output exceeds the threshold (default 8000 chars), it is automatically offloaded to `.bao/context/<session>/outputs/`, with only a preview + file pointer kept in messages.

### Layer 2: Message Compaction
When estimated message size exceeds the threshold (default 240KB), older assistant/tool message pairs are archived, keeping only the most recent N pairs (default 4) + the original request.

### Configuration
Configure in `~/.bao/config.jsonc` under `agents.defaults`:
```json
{
  "agents": {
    "defaults": {
      "contextManagement": "auto",
      "toolOutputOffloadChars": 8000,
      "toolOutputPreviewChars": 3000,
      "contextCompactBytesEst": 240000,
      "contextCompactKeepRecentToolBlocks": 4,
      "artifactRetentionDays": 7
    }
  }
}
```

| Value | Description |
|---|---|
| `observe` | Default. Observe only, no offloading or compaction triggered |
| `auto` | Automatically triggers Layer 1 + Layer 2 when thresholds are exceeded |

Offloaded files are saved under `workspace/.bao/context/`, automatically cleaned up after `artifactRetentionDays` days.
"""


LANG_PICKER = "嗨 👋 请选择语言 / Pick your language:\n\n1. 中文\n2. English"
PERSONA_GREETING: dict[str, str] = {
    "zh": (
        "嘿 👋 我是运行在 bao 框架里的 AI 搭子，还没名字呢～\n\n"
        "正式开工之前，先对个暗号：\n\n"
        "1. 给我起个名字呗？\n"
        "2. 你叫啥？怎么称呼你舒服怎么来～\n"
        "3. 平时聊天习惯？随意唠 / 说重点 / 正经点\n\n"
    ),
    "en": (
        "Hey 👋 I'm an AI buddy running on the bao framework — still unnamed tho~\n\n"
        "Before we get rolling, quick intro:\n\n"
        "1. Wanna give me a name?\n"
        "2. What do I call you? Whatever feels right~\n"
        "3. How do you like to chat? Chill / straight to the point / keep it professional\n\n"
    ),
}


def detect_onboarding_stage(workspace: Path) -> str:
    """Detect onboarding stage from file existence.
    Returns:
        'lang_select'  — no INSTRUCTIONS.md yet
        'persona_setup' — has INSTRUCTIONS.md but no PERSONA.md
        'ready'        — both files exist
    """
    if not (workspace / "INSTRUCTIONS.md").exists():
        return "lang_select"
    if not (workspace / "PERSONA.md").exists():
        return "persona_setup"
    return "ready"


def infer_language(workspace: Path) -> str:
    """Infer language from INSTRUCTIONS.md first line. Defaults to 'zh'."""
    inst = workspace / "INSTRUCTIONS.md"
    if not inst.exists():
        return "zh"
    first_line = inst.read_text(encoding="utf-8").split("\n", 1)[0]
    return "en" if first_line.strip().lower().startswith("# instructions") else "zh"


def write_instructions(workspace: Path, lang: str) -> None:
    """Write INSTRUCTIONS.md in the chosen language (deferred until onboarding)."""
    tpl = _INSTRUCTIONS_EN if lang == "en" else _WORKSPACE_TEMPLATES["INSTRUCTIONS.md"]
    (workspace / "INSTRUCTIONS.md").write_text(tpl, encoding="utf-8")


def write_persona_profile(workspace: Path, lang: str, profile: dict[str, str]) -> None:
    """Write extracted user profile into PERSONA.md, replacing template placeholders."""
    persona = workspace / "PERSONA.md"
    base = _PERSONA_EN if lang == "en" else _WORKSPACE_TEMPLATES["PERSONA.md"]
    content = base
    user_name = profile.get("user_name", "")
    timezone = profile.get("timezone", "")
    style = profile.get("style", "")
    role = profile.get("role", "")
    interests = profile.get("interests", "")
    nickname = profile.get("user_nickname", "")
    bot_name = profile.get("bot_name", "")

    if lang == "zh":
        replacements = {
            "（你的名字）": user_name,
            "（你的时区）": timezone,
            "（随意/正式）": style,
            "（你的角色，如开发者、研究员）": role,
            "（你关注的话题）": interests,
        }
    else:
        replacements = {
            "(your name)": user_name,
            "(your timezone)": timezone,
            "(casual/formal)": style,
            "(your role, e.g. developer, researcher)": role,
            "(topics you care about)": interests,
        }
    for old, new in replacements.items():
        if new:
            content = content.replace(old, new)
    # Update bot name in Identity section if provided
    if bot_name:
        if lang == "zh":
            content = content.replace(
                "我是运行在 bao 框架里的一个轻量级全能 AGENT。",
                f"我是{bot_name}，运行在 bao 框架里的一个轻量级全能 AGENT。",
            )
        else:
            content = content.replace(
                "I am bao, a lightweight AI assistant.",
                f"I am {bot_name}, a lightweight AI assistant.",
            )
    # Append user nickname if provided
    if nickname and nickname != user_name:
        name_val = user_name
        if lang == "zh":
            content = content.replace(
                f"- **姓名**：{name_val}",
                f"- **姓名**：{name_val}（称呼：{nickname}）",
            )
        else:
            content = content.replace(
                f"- **Name**: {name_val}",
                f"- **Name**: {name_val} (call me: {nickname})",
            )
    persona.write_text(content, encoding="utf-8")


def get_config_path() -> Path:
    base = Path.home() / ".bao"
    jsonc = base / "config.jsonc"
    if jsonc.exists():
        return jsonc
    return base / "config.json"


def get_data_dir() -> Path:
    from bao.utils.helpers import get_data_path

    return get_data_path()


def load_config(config_path: Path | None = None) -> Config:
    path = config_path or get_config_path()

    if path.exists():
        try:
            text = path.read_text(encoding="utf-8")
            text = _strip_jsonc_comments(text)
            data = json.loads(text)
            data = _migrate_config(data)
            return Config.model_validate(data)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Warning: Failed to load config from {path}: {e}")
            print("Using default configuration.")
        return Config()

    # Auto-init: first run — create config + workspace + templates, then exit cleanly
    config = Config()
    save_config(config)
    _ensure_workspace(config)
    actual = get_config_path()
    print(
        "\n📁 .bao 配置文件夹已创建 / .bao config folder created"
        "\n\n  📝 请编辑文件完成配置 / Please edit to configure:"
        f"\n     {actual}"
        "\n\n  ▶ 然后重新运行 / Then run: bao\n"
    )
    raise SystemExit(0)


def save_config(config: Config, config_path: Path | None = None) -> None:
    path = config_path or get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.suffix != ".jsonc" and not path.exists():
        path = path.with_suffix(".jsonc")

    if path.suffix == ".jsonc" and not path.exists():
        path.write_text(_JSONC_TEMPLATE, encoding="utf-8")
    else:
        data = config.model_dump(by_alias=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def _ensure_workspace(config: Config) -> None:
    workspace = config.workspace_path
    workspace.mkdir(parents=True, exist_ok=True)

    _DEFERRED = {"PERSONA.md", "INSTRUCTIONS.md"}
    for filename, content in _WORKSPACE_TEMPLATES.items():
        if filename in _DEFERRED:
            continue
        fp = workspace / filename
        if not fp.exists():
            fp.write_text(content, encoding="utf-8")

    (workspace / "skills").mkdir(exist_ok=True)


def _strip_jsonc_comments(text: str) -> str:
    return re.sub(
        r'"(?:[^"\\]|\\.)*"|//[^\n]*|/\*[\s\S]*?\*/',
        lambda m: m.group() if m.group().startswith('"') else "",
        text,
    )


def _migrate_config(data: dict[str, Any]) -> dict[str, Any]:
    # --- providers: old fixed-key format → new dict+type format ---
    providers = data.get("providers", {})
    old_key_map = {"openaiCompatible": "openai", "openai_compatible": "openai"}
    for old_key, new_name in old_key_map.items():
        if old_key in providers:
            cfg = providers.pop(old_key)
            cfg.setdefault("type", "openai")
            providers.setdefault(new_name, cfg)
    for name in ("anthropic", "gemini"):
        if name in providers and isinstance(providers[name], dict):
            providers[name].setdefault("type", name)
    # --- tools migrations ---
    tools = data.get("tools", {})
    exec_cfg = tools.get("exec", {})
    if "restrictToWorkspace" in exec_cfg and "restrictToWorkspace" not in tools:
        tools["restrictToWorkspace"] = exec_cfg.pop("restrictToWorkspace")
    search = tools.get("web", {}).get("search", {})
    if "apiKey" in search and "braveApiKey" not in search:
        search["braveApiKey"] = search.pop("apiKey")
    if "tavilyKey" in search and "tavilyApiKey" not in search:
        search["tavilyApiKey"] = search.pop("tavilyKey")
    return data
