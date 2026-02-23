"""Smoke tests for Responses API auto-detection feature."""

import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bao.providers.api_mode_cache import _normalize_key, get_cached_mode, set_cached_mode, _load
from bao.providers.responses_compat import (
    convert_messages_to_responses,
    convert_tools_to_responses,
    parse_responses_json,
)
from bao.providers.openai_provider import OpenAICompatibleProvider


def test_convert_messages_to_responses():
    messages = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {"id": "call_1", "function": {"name": "search", "arguments": '{"q": "test"}'}}
            ],
        },
        {"role": "tool", "tool_call_id": "call_1", "content": "result"},
    ]
    system_prompt, input_items = convert_messages_to_responses(messages)
    assert system_prompt == "You are helpful.", f"Got: {system_prompt}"
    assert len(input_items) == 4, f"Expected 4 items, got {len(input_items)}"
    assert input_items[0]["role"] == "user"
    assert input_items[1]["type"] == "message"
    assert input_items[1]["role"] == "assistant"
    assert input_items[2]["type"] == "function_call"
    assert input_items[2]["name"] == "search"
    assert input_items[3]["type"] == "function_call_output"
    assert input_items[3]["output"] == "result"
    print("✓ convert_messages_to_responses")


def test_convert_tools_to_responses():
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search",
                "description": "Search",
                "parameters": {"type": "object"},
            },
        }
    ]
    result = convert_tools_to_responses(tools)
    assert len(result) == 1
    assert result[0]["type"] == "function"
    assert result[0]["name"] == "search"
    assert "parameters" in result[0]
    print("✓ convert_tools_to_responses")


def test_parse_responses_json():
    data = {
        "status": "completed",
        "output": [
            {"type": "message", "content": [{"type": "output_text", "text": "Hello!"}]},
            {
                "type": "function_call",
                "call_id": "c1",
                "id": "fc1",
                "name": "tool",
                "arguments": '{"x": 1}',
            },
        ],
        "usage": {"input_tokens": 10, "output_tokens": 20, "total_tokens": 30},
    }
    content, tool_calls, finish_reason, usage = parse_responses_json(data)
    assert content == "Hello!", f"Got: {content}"
    assert len(tool_calls) == 1
    assert tool_calls[0].name == "tool"
    assert tool_calls[0].arguments == {"x": 1}
    assert finish_reason == "stop"
    assert usage["prompt_tokens"] == 10
    assert usage["completion_tokens"] == 20
    print("✓ parse_responses_json")


def test_api_mode_cache():
    import bao.providers.api_mode_cache as cache_mod

    old_cache = cache_mod._cache
    old_file = cache_mod._CACHE_FILE
    cache_mod._cache = None
    cache_mod._CACHE_FILE = Path("/tmp/_bao_test_api_mode_cache.json")
    try:
        if cache_mod._CACHE_FILE.exists():
            cache_mod._CACHE_FILE.unlink()
        cache_mod._cache = None

        assert get_cached_mode("https://example.com/v1") is None
        set_cached_mode("https://example.com/v1", "responses")
        assert get_cached_mode("https://example.com/v1") == "responses"
        assert get_cached_mode("https://example.com/v1/") == "responses"
        assert get_cached_mode("https://OTHER.com/v1") is None

        assert cache_mod._CACHE_FILE.exists()
        data = json.loads(cache_mod._CACHE_FILE.read_text())
        assert "https://example.com/v1" in data
        print("✓ api_mode_cache (set/get/persist)")
    finally:
        cache_mod._cache = old_cache
        cache_mod._CACHE_FILE = old_file
        Path("/tmp/_bao_test_api_mode_cache.json").unlink(missing_ok=True)


def test_provider_resolve_effective_mode():
    p = OpenAICompatibleProvider(api_key="k", api_base="https://test.com/v1", api_mode="responses")
    assert p._resolve_effective_mode() == "responses"

    p2 = OpenAICompatibleProvider(
        api_key="k", api_base="https://test.com/v1", api_mode="completions"
    )
    assert p2._resolve_effective_mode() == "completions"

    p3 = OpenAICompatibleProvider(
        api_key="k", api_base="https://nocache.example.com/v1", api_mode="auto"
    )
    assert p3._resolve_effective_mode() == "auto"
    print("✓ provider _resolve_effective_mode")


def test_provider_init_with_api_mode():
    p = OpenAICompatibleProvider(api_key="k", api_base="https://x.com/v1", api_mode="responses")
    assert p._api_mode == "responses"
    p2 = OpenAICompatibleProvider(api_key="k", api_base="https://x.com/v1")
    assert p2._api_mode == "auto"
    print("✓ provider init api_mode")


def test_make_provider_passes_api_mode():
    from bao.config.schema import Config

    cfg = Config()
    cfg.providers.openai_compatible.api_key = "test-key"
    cfg.providers.openai_compatible.api_mode = "responses"

    from bao.providers import make_provider

    provider = make_provider(cfg, "openai/gpt-4o")
    assert isinstance(provider, OpenAICompatibleProvider)
    assert provider._api_mode == "responses"
    print("✓ make_provider passes api_mode")


def test_utility_model_uses_same_provider_path():
    from bao.config.schema import Config
    from bao.providers import make_provider

    cfg = Config()
    cfg.providers.openai_compatible.api_key = "test-key"
    cfg.providers.openai_compatible.api_base = "https://www.right.codes/codex"
    cfg.providers.openai_compatible.api_mode = "auto"
    cfg.agents.defaults.utility_model = "openai/gpt-4o-mini"

    main_provider = make_provider(cfg, cfg.agents.defaults.model)
    utility_provider = make_provider(cfg, cfg.agents.defaults.utility_model)

    assert isinstance(utility_provider, OpenAICompatibleProvider), (
        f"Utility model should use OpenAICompatibleProvider, got {type(utility_provider)}"
    )
    assert utility_provider._api_mode == "auto"
    assert utility_provider._effective_base == "https://www.right.codes/codex"
    print("✓ utility model uses same OpenAICompatibleProvider with api_mode=auto")


if __name__ == "__main__":
    test_convert_messages_to_responses()
    test_convert_tools_to_responses()
    test_parse_responses_json()
    test_api_mode_cache()
    test_provider_resolve_effective_mode()
    test_provider_init_with_api_mode()
    test_make_provider_passes_api_mode()
    test_utility_model_uses_same_provider_path()
    print("\n🎉 All tests passed!")
