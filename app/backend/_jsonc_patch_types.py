from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Token:
    kind: str
    value: str
    start: int
    end: int


@dataclass
class _Span:
    start: int
    end: int


@dataclass
class _ObjNode:
    children: dict[str, "_ObjNode | _Span"] = field(default_factory=dict)
    close_brace: int = -1
    open_brace: int = -1
    insert_before: int = -1


@dataclass
class PatchError:
    path: list[str]
    message: str


@dataclass
class _InsertionBatch:
    insert_pos: int
    close_brace: int
    had_existing_children: bool
    items: list[tuple[str, object]] = field(default_factory=list)


@dataclass(frozen=True)
class _QueueInsertionRequest:
    node: _ObjNode
    key: str
    value: object
    insertion_batches: dict[int, _InsertionBatch]


@dataclass(frozen=True)
class _CollectPatchRequest:
    node: _ObjNode | _Span
    path: list[str]
    value: object
    patches: list[tuple[int, int, str]]
    insertion_batches: dict[int, _InsertionBatch]
    text: str


@dataclass(frozen=True)
class _ReplaceValueRequest:
    child: _ObjNode | _Span
    key: str
    value: object
    patches: list[tuple[int, int, str]]
    text: str
