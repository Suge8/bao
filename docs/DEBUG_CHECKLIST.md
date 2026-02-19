# bao 调试清单

## 已知问题（2026-02-08）

### 1. [已修复] Resume 从过时的树位置分支

当智能体团队生成子智能体 CLI 进程时，它们会写入同一个会话 JSONL。在后续的 `query()` 恢复时，CLI 读取 JSONL 但可能选择一个过时的分支末端（来自子智能体活动之前），导致智能体的响应落在宿主永远不会收到 `result` 的分支上。**修复**：传递 `resumeSessionAt` 并附上最后一条 assistant 消息的 UUID，以明确锚定每次恢复。

### 2. IDLE_TIMEOUT == CONTAINER_TIMEOUT（都是 30 分钟）

两个定时器同时触发，因此容器总是通过硬 SIGKILL（代码 137）退出，而不是通过 `_close` 哨兵优雅关闭。空闲超时应该更短（例如 5 分钟），这样容器可以在消息之间关闭，而容器超时保持 30 分钟作为卡死智能体的安全网。

### 3. 在智能体成功之前游标已推进

`processGroupMessages` 在智能体运行之前就推进了 `lastAgentTimestamp`。如果容器超时，重试时找不到消息（游标已经跳过它们）。超时时消息会永久丢失。

## 快速状态检查

```bash
# 1. 服务是否在运行？
launchctl list | grep bao
# 预期：PID  0  com.bao（PID = 运行中，"-" = 未运行，非零退出 = 崩溃）

# 2. 有正在运行的容器吗？
container ls --format '{{.Names}} {{.Status}}' 2>/dev/null | grep bao

# 3. 有停止的/孤立的容器吗？
container ls -a --format '{{.Names}} {{.Status}}' 2>/dev/null | grep bao

# 4. 服务日志中的最近错误？
grep -E 'ERROR|WARN' logs/bao.log | tail -20

# 5. WhatsApp 是否已连接？（查找最近的连接事件）
grep -E 'Connected to WhatsApp|Connection closed|connection.*close' logs/bao.log | tail -5

# 6. 群组是否已加载？
grep 'groupCount' logs/bao.log | tail -3
```

## 会话记录分支

```bash
# 检查会话调试日志中的并发 CLI 进程
ls -la data/sessions/<group>/.claude/debug/

# 计算处理消息的唯一 SDK 进程数
# 每个 .txt 文件 = 一个 CLI 子进程。多个 = 并发查询。

# 检查记录中的 parentUuid 分支
python3 -c "
import json, sys
lines = open('data/sessions/<group>/.claude/projects/-workspace-group/<session>.jsonl').read().strip().split('\n')
for i, line in enumerate(lines):
  try:
    d = json.loads(line)
    if d.get('type') == 'user' and d.get('message'):
      parent = d.get('parentUuid', 'ROOT')[:8]
      content = str(d['message'].get('content', ''))[:60]
      print(f'L{i+1} parent={parent} {content}')
  except: pass
"
```

## 容器超时排查

```bash
# 检查最近的超时
grep -E 'Container timeout|timed out' logs/bao.log | tail -10

# 检查超时容器的日志文件
ls -lt groups/*/logs/container-*.log | head -10

# 读取最近的容器日志（替换路径）
cat groups/<group>/logs/container-<timestamp>.log

# 检查是否安排了重试以及结果如何
grep -E 'Scheduling retry|retry|Max retries' logs/bao.log | tail -10
```

## 智能体无响应

```bash
# 检查是否从 WhatsApp 接收到消息
grep 'New messages' logs/bao.log | tail -10

# 检查消息是否正在处理（容器已生成）
grep -E 'Processing messages|Spawning container' logs/bao.log | tail -10

# 检查消息是否正在管道传输到活跃容器
grep -E 'Piped messages|sendMessage' logs/bao.log | tail -10

# 检查队列状态 — 有活跃的容器吗？
grep -E 'Starting container|Container active|concurrency limit' logs/bao.log | tail -10

# 检查 lastAgentTimestamp 与最新消息时间戳
sqlite3 store/messages.db "SELECT chat_jid, MAX(timestamp) as latest FROM messages GROUP BY chat_jid ORDER BY latest DESC LIMIT 5;"
```

## 容器挂载问题

```bash
# 检查挂载验证日志（在容器生成时显示）
grep -E 'Mount validated|Mount.*REJECTED|mount' logs/bao.log | tail -10

# 验证挂载白名单是否可读
cat ~/.config/bao/mount-allowlist.json

# 检查数据库中群组的 container_config
sqlite3 store/messages.db "SELECT name, container_config FROM registered_groups;"

# 测试运行容器检查挂载（试运行）
# 将 <group-folder> 替换为群组的文件夹名
container run -i --rm --entrypoint ls bao-agent:latest /workspace/extra/
```

## WhatsApp 认证问题

```bash
# 检查是否请求了二维码（表示认证过期）
grep 'QR\|authentication required\|qr' logs/bao.log | tail -5

# 检查认证文件是否存在
ls -la store/auth/

# 如需重新认证
npm run auth
```

## 服务管理

```bash
# 重启服务
launchctl kickstart -k gui/$(id -u)/com.bao

# 查看实时日志
tail -f logs/bao.log

# 停止服务（注意 — 运行中的容器会分离，不会被杀死）
launchctl bootout gui/$(id -u)/com.bao

# 启动服务
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.bao.plist

# 代码变更后重建
npm run build && launchctl kickstart -k gui/$(id -u)/com.bao
```
