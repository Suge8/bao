from __future__ import annotations

import asyncio

from bao.agent.tool_result import ToolExecutionResult
from bao.agent.tools.base import Tool
from bao.agent.tools.registry import ToolMetadata, ToolRegistry


class _NamedTool(Tool):
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return f"{self._name} tool"

    @property
    def parameters(self) -> dict[str, object]:
        return {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        }

    async def execute(self, **kwargs: object) -> str:
        return str(kwargs.get("text", ""))


def test_registry_blocks_risky_tool_without_explicit_user_intent() -> None:
    registry = ToolRegistry()
    registry.register(_NamedTool("notify"))

    result = asyncio.run(
        registry.execute("notify", {"text": "hello"}, approval_context={"user_text": "帮我看看日志"})
    )

    assert isinstance(result, ToolExecutionResult)
    assert result.status == "error"
    assert result.code == "approval_required"


def test_registry_allows_risky_tool_after_explicit_user_request() -> None:
    registry = ToolRegistry()
    registry.register(_NamedTool("edit_file"))

    result = asyncio.run(
        registry.execute(
            "edit_file",
            {"text": "done"},
            approval_context={"user_text": "请修复这个 bug，并更新 app/main.py"},
        )
    )

    assert result == "done"


def test_registry_metadata_can_override_default_rule() -> None:
    registry = ToolRegistry()
    registry.register(
        _NamedTool("custom_side_effect"),
        metadata=ToolMetadata(approval_scope="notify", risk_level="high"),
    )

    result = asyncio.run(
        registry.execute(
            "custom_side_effect",
            {"text": "hello"},
            approval_context={"user_text": "只是总结一下当前状态"},
        )
    )

    assert isinstance(result, ToolExecutionResult)
    assert result.code == "approval_required"
