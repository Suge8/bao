from __future__ import annotations

import json

from ._jsonc_patch_parse import _Parser, _strip_comments, _tokenize
from ._jsonc_patch_types import (
    PatchError,
    _CollectPatchRequest,
    _InsertionBatch,
    _ObjNode,
    _QueueInsertionRequest,
    _ReplaceValueRequest,
    _Span,
)


def _line_indent(text: str, pos: int) -> str:
    line_start = text.rfind("\n", 0, pos)
    if line_start == -1:
        line_start = -1
    indent = ""
    for ch in text[line_start + 1 : pos]:
        if ch not in (" ", "\t"):
            break
        indent += ch
    return indent


def _brace_indent(text: str, close_brace: int) -> str:
    line_start = text.rfind("\n", 0, close_brace)
    if line_start == -1:
        return ""
    indent = ""
    for ch in text[line_start + 1 : close_brace]:
        if ch not in (" ", "\t"):
            break
        indent += ch
    return indent


def _queue_insertion(request: _QueueInsertionRequest) -> None:
    insert_pos = request.node.insert_before
    batch = request.insertion_batches.get(insert_pos)
    if batch is None:
        batch = _InsertionBatch(
            insert_pos=insert_pos,
            close_brace=request.node.close_brace,
            had_existing_children=bool(request.node.children),
        )
        request.insertion_batches[insert_pos] = batch
    batch.items.append((request.key, request.value))


def _dump_json_value(value: object, *, indent: str) -> str:
    if not isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    rendered = json.dumps(value, ensure_ascii=False, indent=2)
    lines = rendered.splitlines()
    if len(lines) <= 1:
        return rendered
    return lines[0] + "\n" + "\n".join(indent + line for line in lines[1:])


def _build_insertion_patch(batch: _InsertionBatch, text: str) -> tuple[int, int, str]:
    value_indent = _brace_indent(text, batch.close_brace) + "  "
    pieces: list[str] = []
    for idx, (key, value) in enumerate(batch.items):
        prefix = ",\n" if batch.had_existing_children or idx > 0 else "\n"
        rendered_value = _dump_json_value(value, indent=value_indent)
        pieces.append(
            prefix
            + value_indent
            + json.dumps(key, ensure_ascii=False)
            + ": "
            + rendered_value
        )
    return batch.insert_pos, batch.insert_pos, "".join(pieces)


def patch_jsonc(text: str, changes: dict[str, object]) -> tuple[str, list[PatchError]]:
    tokens = _tokenize(text)
    parser = _Parser(tokens)
    try:
        root = parser.parse_value()
    except ValueError as exc:
        return text, [PatchError([], f"Parse error: {exc}")]
    if not isinstance(root, _ObjNode):
        return text, [PatchError([], "Root is not a JSON object")]

    patches: list[tuple[int, int, str]] = []
    errors: list[PatchError] = []
    insertion_batches: dict[int, _InsertionBatch] = {}
    for dotpath, new_value in changes.items():
        path = dotpath.split(".")
        error = _collect_patch(
            _CollectPatchRequest(
                node=root,
                path=path,
                value=new_value,
                patches=patches,
                insertion_batches=insertion_batches,
                text=text,
            )
        )
        if error:
            errors.append(PatchError(path, error))
    for batch in insertion_batches.values():
        patches.append(_build_insertion_patch(batch, text))
    if not patches:
        return text, errors

    result = text
    for start, end, replacement in sorted(patches, key=lambda patch: patch[0], reverse=True):
        result = result[:start] + replacement + result[end:]
    try:
        json.loads(_strip_comments(result))
    except (json.JSONDecodeError, ValueError) as exc:
        return text, errors + [PatchError([], f"Post-patch validation failed: {exc}")]
    return result, errors


def _collect_patch(request: _CollectPatchRequest) -> str | None:
    if not request.path:
        return "Empty path"
    if not isinstance(request.node, _ObjNode):
        return f"Cannot descend into scalar at remaining path {request.path}"

    key = request.path[0]
    rest = request.path[1:]
    if key in request.node.children:
        child = request.node.children[key]
        if rest:
            return _collect_patch(
                _CollectPatchRequest(
                    node=child,
                    path=rest,
                    value=request.value,
                    patches=request.patches,
                    insertion_batches=request.insertion_batches,
                    text=request.text,
                )
            )
        return _replace_existing_value(
            _ReplaceValueRequest(
                child=child,
                key=key,
                value=request.value,
                patches=request.patches,
                text=request.text,
            )
        )
    if rest:
        return f"Intermediate key {key!r} not found; cannot create nested path"
    if request.node.insert_before == -1:
        return f"Cannot determine insertion point for key {key!r}"
    _queue_insertion(
        _QueueInsertionRequest(
            node=request.node,
            key=key,
            value=request.value,
            insertion_batches=request.insertion_batches,
        )
    )
    return None


def _replace_existing_value(request: _ReplaceValueRequest) -> str | None:
    if isinstance(request.child, _Span):
        indent = _line_indent(request.text, request.child.start)
        request.patches.append(
            (
                request.child.start,
                request.child.end,
                _dump_json_value(request.value, indent=indent),
            )
        )
        return None
    if request.child.open_brace == -1:
        return f"Cannot locate open brace for object at key {request.key!r}"
    indent = _line_indent(request.text, request.child.open_brace)
    request.patches.append(
        (
            request.child.open_brace,
            request.child.close_brace + 1,
            _dump_json_value(request.value, indent=indent),
        )
    )
    return None
