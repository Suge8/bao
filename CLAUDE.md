# bao

个人 Claude 助手。详见 [README.md](README.md)。

## 项目概览

单一 Node.js 进程，连接 WhatsApp/iMessage，将消息路由到运行在 Apple Container（Linux 虚拟机）中的 Claude Agent SDK。每个群组有独立的文件系统和记忆。

## 关键文件

| 文件                                | 用途                                 |
| ----------------------------------- | ------------------------------------ |
| `src/index.ts`                      | 主流程：状态、消息循环、容器调用     |
| `src/channels/whatsapp.ts`          | WhatsApp 连接、认证、收发            |
| `src/channels/imessage.ts`          | iMessage 频道（macOS，轮询 chat.db） |
| `src/ipc.ts`                        | IPC 监听与任务处理                   |
| `src/router.ts`                     | 消息格式化与路由                     |
| `src/config.ts`                     | 触发词、路径、间隔等配置             |
| `src/container-runner.ts`           | 启动容器、挂载目录                   |
| `src/task-scheduler.ts`             | 定时任务                             |
| `src/db.ts`                         | SQLite 操作                          |
| `groups/{name}/CLAUDE.md`           | 群组记忆（隔离）                     |
| `container/skills/agent-browser.md` | 浏览器自动化（容器内可用）           |

## 技能

| 技能         | 用途                     |
| ------------ | ------------------------ |
| `/setup`     | 首次安装、认证、服务配置 |
| `/customize` | 添加功能、修改行为       |
| `/debug`     | 容器问题、日志、排错     |

## 开发

```bash
npm run dev          # 热重载运行
npm run build        # 编译 TypeScript
./container/build.sh # 重建容器镜像
```

服务管理：

```bash
launchctl load ~/Library/LaunchAgents/com.bao.plist
launchctl unload ~/Library/LaunchAgents/com.bao.plist
```

## 容器构建缓存

Apple Container 的 buildkit 会激进缓存构建上下文。`--no-cache` 不会清除 COPY 步骤缓存。强制全新构建：

```bash
container builder stop && container builder rm && container builder start
./container/build.sh
```

验证：`container run -i --rm --entrypoint wc bao-agent:latest -l /app/src/index.ts`
