from __future__ import annotations

from typing import Callable, TypeVar

from ._config_common import _as_dict, _as_list, _as_str

_T = TypeVar("_T")


def _validate(changes: dict[str, object], get_value: Callable[[str, _T | None], object | _T | None]) -> str | None:
    channel_token_fields = {
        "channels.telegram.enabled": "channels.telegram.token",
        "channels.discord.enabled": "channels.discord.token",
        "channels.slack.enabled": "channels.slack.botToken",
    }
    for enabled_path, token_path in channel_token_fields.items():
        if changes.get(enabled_path) is not True:
            continue
        token_value = changes.get(token_path)
        if not isinstance(token_value, str):
            saved_token = get_value(token_path, "")
            token = saved_token if isinstance(saved_token, str) else ""
        else:
            token = token_value
        if not token:
            return f"token_required:{enabled_path.split('.')[1]}"
    return None


def _normalize_changes(changes: dict[str, object]) -> dict[str, object]:
    normalized = dict(changes)
    provider_entries = _as_list(normalized.get("providers"))
    if provider_entries is None:
        return normalized
    providers: dict[str, object] = {}
    for entry in provider_entries:
        entry_dict = _as_dict(entry)
        if entry_dict is None:
            continue
        name = _as_str(entry_dict.get("name", "")).strip()
        value = _as_dict(entry_dict.get("value"))
        if not name or value is None:
            continue
        providers[name] = value
    normalized["providers"] = providers
    return normalized


def _collapse_missing_intermediates(
    data: dict[str, object],
    changes: dict[str, object],
) -> dict[str, object]:
    passthrough: dict[str, object] = {}
    needs_collapse: dict[str, dict[str, object]] = {}
    for dotpath, value in changes.items():
        parts = dotpath.split(".")
        if len(parts) < 3:
            passthrough[dotpath] = value
            continue
        node: object = data
        depth = 0
        for part in parts[:-1]:
            node_dict = _as_dict(node)
            if node_dict is None or part not in node_dict:
                break
            node = node_dict[part]
            depth += 1
        if depth == len(parts) - 1:
            passthrough[dotpath] = value
            continue
        collapse_key = ".".join(parts[: depth + 1])
        leaf_key = ".".join(parts[depth + 1 :])
        needs_collapse.setdefault(collapse_key, {})[leaf_key] = value

    for collapse_key, flat_leaves in needs_collapse.items():
        obj: dict[str, object] = {}
        for leaf_path, value in flat_leaves.items():
            leaf_parts = leaf_path.split(".")
            target = obj
            for key in leaf_parts[:-1]:
                nested = _as_dict(target.get(key))
                if nested is None:
                    nested = {}
                    target[key] = nested
                target = nested
            target[leaf_parts[-1]] = value
        passthrough[collapse_key] = obj
    return passthrough
