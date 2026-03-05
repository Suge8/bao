from datetime import datetime, timedelta, timezone

from pydantic import SecretStr

from bao.agent.commands import format_relative_time
from bao.config.schema import Config, ProviderConfig


def test_anthropic_model_does_not_fallback_to_openai_provider():
    cfg = Config()
    cfg.providers["openai"] = ProviderConfig(type="openai", api_key=SecretStr("test-key"))
    assert cfg.get_provider("anthropic/claude-sonnet-4-20250514") is None


def test_provider_name_match_does_not_infer_type_from_model_name():
    cfg = Config()
    cfg.providers["anthropic"] = ProviderConfig(type="openai", api_key=SecretStr("test-key"))
    provider = cfg.get_provider("anthropic/claude-opus-4-6")
    assert provider is not None
    assert provider.type == "openai"


def test_openai_model_does_not_fallback_to_non_openai_provider():
    cfg = Config()
    cfg.providers["anthropic"] = ProviderConfig(type="anthropic", api_key=SecretStr("test-key"))

    assert cfg.get_provider("openai/gpt-5") is None


def test_model_suffix_does_not_affect_provider_selection() -> None:
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
