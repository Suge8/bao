from datetime import datetime, timedelta, timezone

from pydantic import SecretStr

from bao.agent.commands import format_relative_time
from bao.config.schema import Config, ProviderConfig
from bao.providers.registry import find_by_model


def test_find_by_model_returns_provider_spec():
    """Test that find_by_model returns correct provider spec."""
    spec = find_by_model("anthropic/claude-opus-4-5")

    assert spec is not None
    assert spec.name == "anthropic"


def test_find_by_model_openai_compatible():
    """Test that openai-compatible models return correct spec."""
    spec = find_by_model("openrouter/anthropic/claude-3.5-sonnet")

    assert spec is not None
    assert spec.provider_type.value == "openai"


def test_anthropic_model_does_not_fallback_to_openai_provider():
    cfg = Config()
    cfg.providers["openai"] = ProviderConfig(type="openai", api_key=SecretStr("test-key"))
    assert cfg.get_provider("anthropic/claude-sonnet-4-20250514") is None


def test_provider_name_match_respects_expected_type():
    cfg = Config()
    cfg.providers["anthropic"] = ProviderConfig(type="openai", api_key=SecretStr("test-key"))
    cfg.providers["openai"] = ProviderConfig(type="openai", api_key=SecretStr("ok"))

    assert cfg.get_provider("anthropic/claude-opus-4-6") is None


def test_openai_model_does_not_fallback_to_non_openai_provider():
    cfg = Config()
    cfg.providers["anthropic"] = ProviderConfig(type="anthropic", api_key=SecretStr("test-key"))

    assert cfg.get_provider("openai/gpt-5") is None


def test_codex_suffix_does_not_force_openai_codex_type() -> None:
    spec = find_by_model("right-gpt/gpt-5.3-codex")
    assert spec is not None
    assert spec.provider_type.value == "openai"

    cfg = Config()
    cfg.providers["right-gpt"] = ProviderConfig(
        type="openai",
        api_key=SecretStr("test-key"),
        api_base="https://www.right.codes/codex",
    )

    provider = cfg.get_provider("right-gpt/gpt-5.3-codex")
    assert provider is not None
    assert provider.type == "openai"


def test_openai_codex_prefix_still_matches_codex_provider_without_key() -> None:
    spec = find_by_model("openai-codex/gpt-5.1-codex")
    assert spec is not None
    assert spec.provider_type.value == "openai_codex"

    cfg = Config()
    cfg.providers["openai-codex"] = ProviderConfig(type="openai_codex", api_key=SecretStr(""))

    provider = cfg.get_provider("openai-codex/gpt-5.1-codex")
    assert provider is not None
    assert provider.type == "openai_codex"


def test_format_relative_time_supports_z_suffix() -> None:
    updated = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    assert format_relative_time(updated) == " (刚刚)"


def test_format_relative_time_supports_offset_timestamp() -> None:
    updated = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()

    assert format_relative_time(updated) == " (刚刚)"


def test_format_relative_time_clamps_future_time_to_now() -> None:
    updated = (datetime.now() + timedelta(minutes=5)).replace(microsecond=0).isoformat()

    assert format_relative_time(updated) == " (刚刚)"


def test_format_relative_time_invalid_input_falls_back() -> None:
    assert format_relative_time("invalid-time-value") == " (invalid-time-val)"
