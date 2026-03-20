from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bao.profile import ProfileContext

_HUB_CHANNEL_ORDER = (
    "telegram",
    "discord",
    "whatsapp",
    "feishu",
    "slack",
    "email",
    "qq",
    "dingtalk",
    "imessage",
)

_CHANNEL_ERROR_LABELS = {
    "unavailable": ("通道不可用", "Channel unavailable"),
    "start_failed": ("通道启动失败", "Channel start failed"),
    "send_failed": ("通道发送失败", "Channel send failed"),
    "stop_failed": ("通道停止失败", "Channel stop failed"),
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_hub_channels(channels: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for name in _HUB_CHANNEL_ORDER:
        if name in channels and name not in seen:
            ordered.append(name)
            seen.add(name)
    for name in channels:
        if name not in seen:
            ordered.append(name)
            seen.add(name)
    return ordered


def _session_manager_root(session_manager: object) -> Path | None:
    workspace = getattr(session_manager, "workspace", None)
    if workspace is None:
        return None
    return Path(str(workspace)).expanduser()


def _target_session_root(config: Any, profile_context: ProfileContext | None) -> Path:
    if profile_context is not None:
        return profile_context.state_root
    return Path(str(config.workspace_path)).expanduser()
