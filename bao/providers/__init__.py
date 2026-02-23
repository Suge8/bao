"""LLM provider abstraction module."""

from __future__ import annotations

from typing import TYPE_CHECKING
from bao.providers.base import LLMProvider, LLMResponse
from bao.providers.openai_provider import OpenAICompatibleProvider
from bao.providers.anthropic_provider import AnthropicProvider
from bao.providers.gemini_provider import GeminiProvider
from bao.providers.openai_codex_provider import OpenAICodexProvider
from bao.providers.registry import PROVIDERS, ProviderType, find_by_model, find_by_name

if TYPE_CHECKING:
    from bao.config.schema import Config

__all__ = [
    "LLMProvider",
    "LLMResponse",
    "OpenAICompatibleProvider",
    "AnthropicProvider",
    "GeminiProvider",
    "OpenAICodexProvider",
    "make_provider",
]


def make_provider(config: "Config", model: str | None = None) -> LLMProvider:
    """Create the appropriate LLM provider for a given model.

    Routes based on provider type:
    - openai_codex (OAuth) -> OpenAICodexProvider
    - anthropic/* -> AnthropicProvider (native SDK)
    - gemini/* -> GeminiProvider (native SDK)
    - everything else -> OpenAICompatibleProvider (OpenAI-compatible endpoints)
    """
    model = model or config.agents.defaults.model
    provider_name = config.get_provider_name(model)
    provider_config = config.get_provider(model)

    # OAuth provider
    if provider_name == "openai_codex" or model.startswith("openai-codex/"):
        return OpenAICodexProvider(default_model=model)

    # Find provider spec
    spec = (find_by_name(provider_name) if provider_name else None) or find_by_model(model)
    if not spec:
        raise ValueError(f"Cannot determine provider for model '{model}'")

    # Route to native SDK providers
    if spec.provider_type in (ProviderType.ANTHROPIC, ProviderType.GEMINI):
        if not provider_config or not provider_config.api_key:
            raise ValueError(f"No API key configured for '{provider_name}'")
        provider_cls = (
            AnthropicProvider if spec.provider_type == ProviderType.ANTHROPIC else GeminiProvider
        )
        return provider_cls(api_key=provider_config.api_key, default_model=model)

    # OpenAI-compatible providers (default)
    api_base = config.get_api_base(model) or spec.default_api_base
    api_key = provider_config.api_key if provider_config else None
    extra_headers = provider_config.extra_headers if provider_config else None
    api_mode = provider_config.api_mode if provider_config else "auto"
    return OpenAICompatibleProvider(
        api_key=api_key,
        api_base=api_base,
        default_model=model,
        extra_headers=extra_headers,
        provider_name=provider_name,
        api_mode=api_mode,
    )
