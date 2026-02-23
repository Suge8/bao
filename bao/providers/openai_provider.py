"""OpenAI-Compatible Provider — supports Chat Completions and Responses API with auto-detection."""

from __future__ import annotations

from typing import Any

import httpx
from loguru import logger
from openai import AsyncOpenAI

from bao.providers.api_mode_cache import get_cached_mode, set_cached_mode
from bao.providers.base import LLMProvider, LLMResponse, normalize_tool_calls
from bao.providers.responses_compat import (
    convert_messages_to_responses,
    convert_tools_to_responses,
    parse_responses_json,
)

_ALLOWED_MSG_KEYS = frozenset({"role", "content", "tool_calls", "tool_call_id", "name"})

_PROBE_FALLBACK_CODES = frozenset({404, 405, 501})


class OpenAICompatibleProvider(LLMProvider):
    """Universal OpenAI-compatible provider with Responses API auto-detection.

    When api_mode is "auto" (default), the first request probes the Responses API.
    If supported, all subsequent requests use it; otherwise falls back to Chat Completions.
    The detection result is cached per endpoint to disk with a 7-day TTL.
    """

    PROMPT_CACHING_PROVIDERS = frozenset({"openrouter", "openai"})

    def __init__(
        self,
        api_key: str | None = None,
        api_base: str | None = None,
        default_model: str = "gpt-4o",
        extra_headers: dict[str, str] | None = None,
        provider_name: str | None = None,
        api_mode: str = "auto",
    ):
        super().__init__(api_key, api_base)
        self.default_model = default_model
        self.extra_headers = extra_headers or {}
        self.provider_name = provider_name or "openai"
        self._api_mode = api_mode
        self._effective_base = api_base or "https://api.openai.com/v1"

        headers = {"User-Agent": "bao/1.0"}
        if self.extra_headers:
            headers.update(self.extra_headers)
        self._default_headers = headers
        self._api_key_str = api_key or "dummy-key"

        self._client = AsyncOpenAI(
            api_key=self._api_key_str,
            base_url=self._effective_base,
            default_headers=headers,
        )

    def _resolve_model(self, model: str) -> str:
        prefixes_to_strip = (
            "openrouter/",
            "deepseek/",
            "groq/",
            "anthropic/",
            "gemini/",
            "moonshot/",
            "minimax/",
            "qwen/",
            "glm/",
            "zhipu/",
            "vllm/",
            "ollama/",
            "lm-studio/",
        )
        model_lower = model.lower()
        for prefix in prefixes_to_strip:
            if model_lower.startswith(prefix):
                return model[len(prefix) :]
        return model

    def _supports_prompt_caching(self) -> bool:
        return self.provider_name.lower() in self.PROMPT_CACHING_PROVIDERS

    def _apply_cache_control(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]] | None]:
        if not self._supports_prompt_caching():
            return messages, tools

        new_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                content = msg["content"]
                if isinstance(content, str):
                    new_content = [
                        {"type": "text", "text": content, "cache_control": {"type": "ephemeral"}}
                    ]
                else:
                    new_content = list(content)
                    new_content[-1] = {**new_content[-1], "cache_control": {"type": "ephemeral"}}
                new_messages.append({**msg, "content": new_content})
            else:
                new_messages.append(msg)

        new_tools = tools
        if tools:
            new_tools = list(tools)
            new_tools[-1] = {**new_tools[-1], "cache_control": {"type": "ephemeral"}}

        return new_messages, new_tools

    @staticmethod
    def _sanitize_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        sanitized = []
        for msg in messages:
            clean = {k: v for k, v in msg.items() if k in _ALLOWED_MSG_KEYS}
            if clean.get("role") == "assistant" and "content" not in clean:
                clean["content"] = None
            sanitized.append(clean)
        return sanitized

    def _resolve_effective_mode(self) -> str:
        if self._api_mode in {"responses", "completions"}:
            return self._api_mode
        return get_cached_mode(self._effective_base) or "auto"

    @staticmethod
    def _build_responses_result(payload: dict[str, Any]) -> LLMResponse:
        content, tool_calls, finish_reason, usage = parse_responses_json(payload)
        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=finish_reason,
            usage=usage,
        )

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **extra: Any,
    ) -> LLMResponse:
        original_model = model or self.default_model
        resolved_model = self._resolve_model(original_model)

        if self._supports_prompt_caching():
            messages, tools = self._apply_cache_control(messages, tools)

        max_tokens = max(1, max_tokens)
        mode = self._resolve_effective_mode()

        if mode == "responses":
            return await self._chat_responses(
                resolved_model, messages, tools, max_tokens, temperature
            )
        if mode == "completions":
            return await self._chat_completions(
                resolved_model, messages, tools, max_tokens, temperature
            )

        return await self._chat_with_probe(resolved_model, messages, tools, max_tokens, temperature)

    async def _chat_completions(
        self,
        model: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None,
        max_tokens: int,
        temperature: float,
    ) -> LLMResponse:
        params: dict[str, Any] = {
            "model": model,
            "messages": self._sanitize_messages(messages),
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"

        try:
            response = await self._client.chat.completions.create(**params)
            return self._parse_completions_response(response)
        except Exception as e:
            return LLMResponse(content=f"Error calling LLM: {e}", finish_reason="error")

    def _build_responses_body(
        self,
        model: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None,
        max_tokens: int,
        temperature: float,
    ) -> dict[str, Any]:
        system_prompt, input_items = convert_messages_to_responses(messages)
        body: dict[str, Any] = {
            "model": model,
            "input": input_items,
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            "store": False,
        }
        if system_prompt:
            body["instructions"] = system_prompt
        if tools:
            body["tools"] = convert_tools_to_responses(tools)
            body["tool_choice"] = "auto"
        return body

    def _build_responses_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key_str}",
            "Content-Type": "application/json",
            **self._default_headers,
        }

    async def _chat_responses(
        self,
        model: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None,
        max_tokens: int,
        temperature: float,
    ) -> LLMResponse:
        body = self._build_responses_body(model, messages, tools, max_tokens, temperature)
        url = f"{self._effective_base.rstrip('/')}/responses"
        headers = self._build_responses_headers()

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(url, headers=headers, json=body)
            if resp.status_code != 200:
                raise RuntimeError(f"Responses API HTTP {resp.status_code}: {resp.text[:500]}")
            return self._build_responses_result(resp.json())
        except Exception as e:
            return LLMResponse(content=f"Error calling Responses API: {e}", finish_reason="error")

    async def _chat_with_probe(
        self,
        model: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None,
        max_tokens: int,
        temperature: float,
    ) -> LLMResponse:
        body = self._build_responses_body(model, messages, tools, max_tokens, temperature)
        url = f"{self._effective_base.rstrip('/')}/responses"
        headers = self._build_responses_headers()

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(url, headers=headers, json=body)

            if resp.status_code in _PROBE_FALLBACK_CODES:
                logger.info(
                    f"Responses API not supported ({resp.status_code}), "
                    "falling back to Chat Completions"
                )
                set_cached_mode(self._effective_base, "completions")
                return await self._chat_completions(model, messages, tools, max_tokens, temperature)

            if resp.status_code == 200:
                set_cached_mode(self._effective_base, "responses")
                logger.info("Responses API detected, cached for future requests")
                return self._build_responses_result(resp.json())

            logger.warning(f"Responses API returned {resp.status_code}, trying Chat Completions")
            return await self._chat_completions(model, messages, tools, max_tokens, temperature)

        except Exception as e:
            logger.warning(f"Responses API probe failed ({e}), trying Chat Completions")
            return await self._chat_completions(model, messages, tools, max_tokens, temperature)

    def _parse_completions_response(self, response: Any) -> LLMResponse:
        choice = response.choices[0]
        message = choice.message

        tool_calls = normalize_tool_calls(message)

        usage = {}
        raw_usage = getattr(response, "usage", None)
        if raw_usage:
            usage = {
                "prompt_tokens": raw_usage.prompt_tokens,
                "completion_tokens": raw_usage.completion_tokens,
                "total_tokens": raw_usage.total_tokens,
            }

        reasoning_content = getattr(message, "reasoning_content", None)

        return LLMResponse(
            content=message.content,
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason or "stop",
            usage=usage,
            reasoning_content=reasoning_content,
        )

    def get_default_model(self) -> str:
        return self.default_model
