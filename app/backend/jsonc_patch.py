"""JSONC round-trip patch writer facade."""

from __future__ import annotations

from ._jsonc_patch_apply import patch_jsonc
from ._jsonc_patch_parse import _strip_comments, strip_comments
from ._jsonc_patch_types import PatchError

_DELETE_SENTINEL = object()

__all__ = [
    "PatchError",
    "_DELETE_SENTINEL",
    "_strip_comments",
    "patch_jsonc",
    "strip_comments",
]
