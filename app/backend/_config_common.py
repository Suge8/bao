from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path
from typing import Callable, TypeVar, cast

from PySide6.QtCore import Slot

from bao.config.schema import Config as RuntimeConfig

_F = TypeVar("_F", bound=Callable[..., object])

_PROVIDER_COMMENT_LINES = (
    '// "provider-name": {',
    '//   "apiBase": "https://xxx",',
    '//   "apiKey": "sk-xxx",',
    '//   "extraHeaders": {},',
    '//   "type": "openai/anthropic/gemini"',
    "// }",
)


def _typed_slot(
    *types: type[object] | str,
    name: str | None = None,
    result: type[object] | str | None = None,
) -> Callable[[_F], _F]:
    if name is None and result is None:
        slot_decorator = Slot(*types)
    elif result is None:
        slot_decorator = Slot(*types, name=name)
    elif name is None:
        slot_decorator = Slot(*types, result=result)
    else:
        slot_decorator = Slot(*types, name=name, result=result)
    return cast(Callable[[_F], _F], slot_decorator)


def _as_dict(value: object) -> dict[str, object] | None:
    if isinstance(value, dict):
        return cast(dict[str, object], value)
    return None


def _as_str(value: object, default: str = "") -> str:
    if isinstance(value, str):
        return value
    return default


def _as_list(value: object) -> list[object] | None:
    if isinstance(value, list):
        return cast(list[object], value)
    return None


def _detect_newline(text: str) -> str:
    if "\r\n" in text:
        return "\r\n"
    return "\n"


def _find_matching_brace(text: str, open_brace: int) -> int:
    normal, in_string, escape, line_comment, block_comment = range(5)
    state = normal
    depth = 0
    index = open_brace
    while index < len(text):
        ch = text[index]
        nxt = text[index + 1] if index + 1 < len(text) else ""
        if state == normal:
            if ch == '"':
                state = in_string
            elif ch == "/" and nxt == "/":
                state = line_comment
                index += 1
            elif ch == "/" and nxt == "*":
                state = block_comment
                index += 1
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return index
        elif state == in_string:
            state = escape if ch == "\\" else normal if ch == '"' else in_string
        elif state == escape:
            state = in_string
        elif state == line_comment:
            if ch == "\n":
                state = normal
        elif state == block_comment and ch == "*" and nxt == "/":
            state = normal
            index += 1
        index += 1
    return -1


def _inject_provider_comments(text: str) -> str:
    match = re.search(r'^(?P<indent>\s*)"providers"\s*:\s*\{', text, re.MULTILINE)
    if match is None:
        return text
    open_brace = match.end() - 1
    close_brace = _find_matching_brace(text, open_brace)
    if close_brace == -1:
        return text
    section = text[open_brace + 1 : close_brace]
    if re.search(r'^\s*//\s*"provider-name"\s*:\s*\{', section, re.MULTILINE):
        return text
    base_indent = match.group("indent")
    inner_indent = base_indent + "  "
    newline = _detect_newline(text)
    comment_block = newline.join(f"{inner_indent}{line}" for line in _PROVIDER_COMMENT_LINES)
    suffix = "" if section.strip() else newline + base_indent
    insertion = f"{newline}{comment_block}{suffix}"
    return text[: open_brace + 1] + insertion + text[open_brace + 1 :]


def _write_text_atomic(path: Path, content: str) -> None:
    temp_fd, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
    )
    try:
        with os.fdopen(temp_fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def _apply_ui_defaults(data: dict[str, object], validated: RuntimeConfig) -> None:
    ui_node = _as_dict(data.get("ui"))
    if ui_node is None:
        ui_node = {}
        data["ui"] = ui_node
    update_node = _as_dict(ui_node.get("update"))
    if update_node is None:
        update_node = {}
        ui_node["update"] = update_node
    defaults = validated.ui.update
    update_node.setdefault("enabled", defaults.enabled)
    update_node.setdefault("autoCheck", defaults.auto_check)
    update_node.setdefault("channel", defaults.channel)
    update_node.setdefault("feedUrl", defaults.feed_url)


def _resolved_config_path(current_path: Path | None) -> Path:
    if current_path is not None:
        return current_path
    from bao.config.loader import get_config_path

    return get_config_path()


def _bootstrap_config_path(current_path: Path | None) -> Path:
    path = _resolved_config_path(current_path)
    if path.exists():
        return path
    from bao.config.loader import ensure_first_run, get_config_path

    ensure_first_run()
    return get_config_path()
