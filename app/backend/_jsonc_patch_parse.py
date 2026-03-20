from __future__ import annotations

import json
import re
from typing import cast

from ._jsonc_patch_types import Token, _ObjNode, _Span

_TOKEN_RE = re.compile(
    r"""
    (?P<COMMENT_LINE>//[^\n]*)
    |(?P<COMMENT_BLOCK>/\*.*?\*/)
    |(?P<STRING>"(?:[^"\\]|\\.)*")
    |(?P<NUMBER>-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)
    |(?P<BOOL>true|false)
    |(?P<NULL>null)
    |(?P<LBRACE>\{)
    |(?P<RBRACE>\})
    |(?P<LBRACKET>\[)
    |(?P<RBRACKET>\])
    |(?P<COLON>:)
    |(?P<COMMA>,)
    |(?P<WS>\s+)
    """,
    re.VERBOSE | re.DOTALL,
)


def _tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    pos = 0
    while pos < len(text):
        match = _TOKEN_RE.match(text, pos)
        if not match:
            raise ValueError(f"Unexpected character at offset {pos}: {text[pos]!r}")
        kind = match.lastgroup
        assert kind is not None
        tokens.append(Token(kind, match.group(), match.start(), match.end()))
        pos = match.end()
    return tokens


class _Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = [
            token for token in tokens if token.kind not in ("WS", "COMMENT_LINE", "COMMENT_BLOCK")
        ]
        self._pos = 0

    def _peek(self) -> Token | None:
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return None

    def _consume(self, kind: str | None = None) -> Token:
        token = self._tokens[self._pos]
        if kind and token.kind != kind:
            raise ValueError(f"Expected {kind}, got {token.kind} at offset {token.start}")
        self._pos += 1
        return token

    def parse_value(self) -> _ObjNode | _Span:
        token = self._peek()
        if token is None:
            raise ValueError("Unexpected end of input")
        if token.kind == "LBRACE":
            return self._parse_object()
        if token.kind == "LBRACKET":
            return self._parse_array()
        self._pos += 1
        return _Span(token.start, token.end)

    def _parse_object(self) -> _ObjNode:
        open_token = self._consume("LBRACE")
        node = _ObjNode(open_brace=open_token.start)
        while True:
            token = self._peek()
            if token is None:
                raise ValueError("Unterminated object")
            if token.kind == "RBRACE":
                node.insert_before = token.start
                node.close_brace = token.start
                self._consume("RBRACE")
                return node
            if token.kind == "COMMA":
                self._consume("COMMA")
                continue
            key_token = self._consume("STRING")
            key = cast(str, json.loads(key_token.value))
            self._consume("COLON")
            node.children[key] = self.parse_value()

    def _parse_array(self) -> _Span:
        start = self._peek()
        assert start is not None
        depth = 0
        begin = start.start
        end = start.end
        while True:
            token = self._peek()
            if token is None:
                raise ValueError("Unterminated array")
            if token.kind == "LBRACKET":
                depth += 1
            elif token.kind == "RBRACKET":
                depth -= 1
                end = token.end
                self._pos += 1
                if depth == 0:
                    return _Span(begin, end)
                continue
            end = token.end
            self._pos += 1


def _strip_comments(text: str) -> str:
    parts: list[str] = []
    for token in _tokenize(text):
        if token.kind in ("COMMENT_LINE", "COMMENT_BLOCK"):
            parts.append(" " * len(token.value))
            continue
        parts.append(token.value)
    return "".join(parts)


def strip_comments(text: str) -> str:
    return _strip_comments(text)
