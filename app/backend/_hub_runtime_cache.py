from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import Any

from ._hub_common import _session_manager_root

HOT_SESSION_MANAGER_CACHE_LIMIT = 2


def cache_session_manager(
    cache: OrderedDict[str, Any],
    session_manager: object | None,
) -> None:
    root = _session_manager_root(session_manager)
    if root is None:
        return
    key = str(root)
    cache[key] = session_manager
    cache.move_to_end(key)
    while len(cache) > HOT_SESSION_MANAGER_CACHE_LIMIT:
        cache.popitem(last=False)


def remove_cached_session_manager(
    cache: OrderedDict[str, Any],
    session_manager: object | None,
) -> None:
    root = _session_manager_root(session_manager)
    if root is None:
        return
    cache.pop(str(root), None)


def reuse_cached_session_manager(cache: OrderedDict[str, Any], expected_root: Path) -> object | None:
    key = str(expected_root)
    cached = cache.pop(key, None)
    if cached is None:
        return None
    return cached
