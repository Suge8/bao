from __future__ import annotations

import re
from dataclasses import dataclass

_FILE_PATH_RE = re.compile(
    r"(?:^|[\s'\"`(])[\w./-]+\.(?:py|js|ts|tsx|jsx|sh|json|ya?ml|toml|qml|md)(?:$|[\s'\"`),])",
    re.IGNORECASE,
)
_CODE_TERMS = (
    "fix",
    "debug",
    "refactor",
    "implement",
    "write code",
    "edit file",
    "modify file",
    "update file",
    "create file",
    "repo",
    "codebase",
    "test",
    "pytest",
    "lint",
    "build",
    "script",
    "修复",
    "调试",
    "重构",
    "实现",
    "代码",
    "文件",
    "脚本",
    "测试",
    "构建",
)
_COMMAND_TERMS = (
    "run command",
    "shell",
    "terminal",
    "bash",
    "zsh",
    "cli",
    "command",
    "执行命令",
    "命令行",
    "终端",
    "运行命令",
)
_NOTIFY_TERMS = (
    "notify",
    "send message",
    "send to",
    "message",
    "email",
    "telegram",
    "slack",
    "discord",
    "whatsapp",
    "imessage",
    "发给",
    "发到",
    "发送",
    "通知",
    "邮件",
)
_AUTOMATION_TERMS = (
    "cron",
    "schedule",
    "remind",
    "reminder",
    "recurring",
    "every day",
    "every hour",
    "定时",
    "提醒",
    "自动任务",
)
_DESKTOP_TERMS = (
    "desktop",
    "screen",
    "screenshot",
    "window",
    "click",
    "type",
    "drag",
    "scroll",
    "hotkey",
    "桌面",
    "屏幕",
    "截图",
    "点击",
    "输入",
    "拖拽",
    "滚动",
    "快捷键",
)
_BROWSER_TERMS = (
    "browser",
    "website",
    "web page",
    "url",
    "link",
    "login",
    "form",
    "upload",
    "download",
    "浏览器",
    "网站",
    "网页",
    "登录",
    "表单",
)
_MEMORY_TERMS = ("memory", "remember", "forget", "记忆", "记住", "忘记")
_SCOPE_LABELS = {
    "code_write": "修改代码或文件",
    "command": "执行本地命令",
    "notify": "跨渠道发送消息",
    "automation": "创建或修改自动任务",
    "desktop": "操作桌面界面",
    "browser": "驱动交互式浏览器动作",
    "memory_write": "修改长期记忆",
}


@dataclass(frozen=True)
class ToolApprovalRule:
    scope: str = ""
    risk_level: str = "low"
    side_effects: tuple[str, ...] = ()


@dataclass(frozen=True)
class ToolApprovalDecision:
    allowed: bool
    reason: str = ""
    risk_level: str = "low"


_DEFAULT_APPROVAL_RULES = {
    "write_file": ToolApprovalRule("code_write", "medium", ("filesystem_write",)),
    "edit_file": ToolApprovalRule("code_write", "medium", ("filesystem_write",)),
    "exec": ToolApprovalRule("command", "high", ("shell_exec",)),
    "coding_agent": ToolApprovalRule(
        "code_write",
        "medium",
        ("filesystem_write", "subprocess_exec"),
    ),
    "notify": ToolApprovalRule("notify", "high", ("cross_channel_message",)),
    "remember": ToolApprovalRule("memory_write", "medium", ("memory_write",)),
    "forget": ToolApprovalRule("memory_write", "medium", ("memory_write",)),
    "update_memory": ToolApprovalRule("memory_write", "medium", ("memory_write",)),
    "cron": ToolApprovalRule("automation", "high", ("automation_write",)),
    "agent_browser": ToolApprovalRule("browser", "high", ("browser_control",)),
    "click": ToolApprovalRule("desktop", "high", ("desktop_control",)),
    "type_text": ToolApprovalRule("desktop", "high", ("desktop_control",)),
    "key_press": ToolApprovalRule("desktop", "high", ("desktop_control",)),
    "scroll": ToolApprovalRule("desktop", "high", ("desktop_control",)),
    "drag": ToolApprovalRule("desktop", "high", ("desktop_control",)),
}


def _normalize_text(value: object) -> str:
    return " ".join(str(value or "").lower().split())


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _has_code_intent(text: str) -> bool:
    return _contains_any(text, _CODE_TERMS) or bool(_FILE_PATH_RE.search(text))


def _scope_is_allowed(scope: str, text: str) -> bool:
    if not scope:
        return True
    if scope == "code_write":
        return _has_code_intent(text)
    if scope == "command":
        return _has_code_intent(text) or _contains_any(text, _COMMAND_TERMS)
    if scope == "notify":
        return _contains_any(text, _NOTIFY_TERMS)
    if scope == "automation":
        return _contains_any(text, _AUTOMATION_TERMS)
    if scope == "desktop":
        return _contains_any(text, _DESKTOP_TERMS)
    if scope == "browser":
        return _contains_any(text, _BROWSER_TERMS)
    if scope == "memory_write":
        return _contains_any(text, _MEMORY_TERMS)
    return True


def _resolve_rule(
    tool_name: str,
    approval_scope: str,
    risk_level: str,
    side_effects: tuple[str, ...],
) -> ToolApprovalRule:
    if approval_scope:
        return ToolApprovalRule(approval_scope, risk_level, side_effects)
    return _DEFAULT_APPROVAL_RULES.get(tool_name, ToolApprovalRule("", risk_level, side_effects))


def _blocked_reason(tool_name: str, scope: str, risk_level: str, side_effects: tuple[str, ...]) -> str:
    action = _SCOPE_LABELS.get(scope, "执行高风险副作用")
    effects = ", ".join(side_effects)
    suffix = f" Side effects: {effects}." if effects else ""
    return (
        f"Blocked tool '{tool_name}' (risk: {risk_level}) because the current request "
        f"does not clearly ask to {action}.{suffix} Ask the user to confirm before retrying."
    )


def evaluate_tool_approval(
    *,
    tool_name: str,
    user_text: object,
    approval_scope: str,
    risk_level: str,
    side_effects: tuple[str, ...] = (),
) -> ToolApprovalDecision:
    scope = str(approval_scope or "").strip().lower()
    normalized_risk = str(risk_level or "low").strip().lower() or "low"
    rule = _resolve_rule(tool_name, scope, normalized_risk, tuple(side_effects))
    normalized_text = _normalize_text(user_text)
    if _scope_is_allowed(rule.scope, normalized_text):
        return ToolApprovalDecision(allowed=True, risk_level=rule.risk_level)
    return ToolApprovalDecision(
        allowed=False,
        reason=_blocked_reason(tool_name, rule.scope, rule.risk_level, rule.side_effects),
        risk_level=rule.risk_level,
    )
