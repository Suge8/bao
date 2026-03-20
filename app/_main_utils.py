from __future__ import annotations

import argparse
import re
import subprocess
import sys
from typing import Callable, cast

from PySide6.QtCore import QLocale, QObject


def is_smoke_run(smoke: bool, smoke_theme_toggle: bool, smoke_screenshot: str | None) -> bool:
    return smoke or smoke_theme_toggle or bool(smoke_screenshot)


def shutdown_desktop_services(*services: object) -> None:
    for method_name in ("shutdown", "stop"):
        for service in services:
            method = getattr(service, method_name, None)
            if callable(method):
                method()


def parse_args() -> tuple[bool, str | None, bool, str, bool, str | None, int | None, int | None]:
    parser = argparse.ArgumentParser()
    _ = parser.add_argument("--smoke", action="store_true")
    _ = parser.add_argument("--qml", default=None)
    _ = parser.add_argument("--smoke-theme-toggle", action="store_true")
    _ = parser.add_argument("--start-view", choices=("chat", "settings"), default="chat")
    _ = parser.add_argument("--seed-messages", action="store_true")
    _ = parser.add_argument("--smoke-screenshot", default=None)
    _ = parser.add_argument("--window-width", type=int, default=None)
    _ = parser.add_argument("--window-height", type=int, default=None)
    args = parser.parse_args()
    return (
        bool(cast(object, args.smoke)),
        cast(str | None, args.qml),
        bool(cast(object, args.smoke_theme_toggle)),
        cast(str, args.start_view),
        bool(cast(object, args.seed_messages)),
        cast(str | None, args.smoke_screenshot),
        cast(int | None, args.window_width),
        cast(int | None, args.window_height),
    )


def detect_system_ui_language() -> str:
    candidates: list[str] = []
    sys_locale = QLocale.system()
    try:
        candidates.extend(str(v) for v in sys_locale.uiLanguages())
    except Exception:
        pass
    candidates.extend([str(sys_locale.name()), str(QLocale().name())])
    if sys.platform == "darwin":
        try:
            raw = subprocess.check_output(
                ["defaults", "read", "-g", "AppleLanguages"],
                text=True,
                timeout=1,
            )
            apple_langs = re.findall(r'"([^"]+)"', raw)
            if apple_langs:
                candidates = apple_langs + candidates
        except Exception:
            pass
    for item in candidates:
        tag = item.strip().lower().replace("_", "-")
        if tag.startswith("zh"):
            return "zh"
        if tag.startswith("en"):
            return "en"
    return "en"


def effective_desktop_language(preferences: QObject) -> str:
    value = preferences.property("effectiveLanguage")
    return value if isinstance(value, str) else "en"


def connect_on_config_change(config_service: object, callback: Callable[[], None]) -> None:
    for signal_name in ("configLoaded", "saveDone"):
        signal = getattr(config_service, signal_name, None)
        if signal is not None:
            _ = signal.connect(callback)


def bind_exported_config(config_service: object, apply_fn: Callable[[object], None]) -> None:
    export_data = getattr(config_service, "exportData", None)
    if not callable(export_data):
        return

    def apply_exported_config() -> None:
        apply_fn(export_data())

    apply_exported_config()
    connect_on_config_change(config_service, apply_exported_config)


def configured_hub_channels(config_service: object) -> list[str]:
    order = (
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
    get_value = getattr(config_service, "get", None)
    if not callable(get_value):
        return []
    return [name for name in order if bool(get_value(f"channels.{name}.enabled", False))]
