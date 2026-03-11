import asyncio
from types import SimpleNamespace
from typing import Any, Self, cast

import pytest

from bao.providers.anthropic_provider import AnthropicProvider
from bao.providers.base import LLMResponse
from bao.providers.openai_provider import OpenAICompatibleProvider
from bao.providers.retry import (
    PROGRESS_RESET,
    compute_retry_delay,
    run_with_retries,
    should_retry_exception,
)

pytestmark = pytest.mark.unit


class _ResponseError(Exception):
    def __init__(self, message: str, status_code: int, retry_after: str | None = None):
        super().__init__(message)
        headers = {}
        if retry_after is not None:
            headers["retry-after"] = retry_after
        self.response = SimpleNamespace(status_code=status_code, headers=headers)


class _StreamChunk:
    def __init__(self, content: str | None = None, finish_reason: str | None = None):
        delta = SimpleNamespace(content=content, reasoning_content=None, tool_calls=None)
        choice = SimpleNamespace(delta=delta, finish_reason=finish_reason)
        self.choices = [choice]


class _FailingStream:
    def __init__(self):
        self._sent_once = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._sent_once:
            self._sent_once = True
            return _StreamChunk(content="partial", finish_reason=None)
        raise RuntimeError("connection reset by peer")


class _SuccessStream:
    def __init__(self):
        self._done = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._done:
            raise StopAsyncIteration
        self._done = True
        return _StreamChunk(content="final", finish_reason="stop")


class _AnthropicStreamContext:
    def __init__(self, events: list[Any]):
        self._events = events
        self._index = 0

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return False

    def __aiter__(self) -> Self:
        return self

    async def __anext__(self) -> Any:
        if self._index >= len(self._events):
            raise StopAsyncIteration
        event = self._events[self._index]
        self._index += 1
        return event

    async def get_final_message(self) -> Any:
        return SimpleNamespace(
            usage=SimpleNamespace(input_tokens=1, output_tokens=1),
            stop_reason="end_turn",
            content=[],
        )


@pytest.mark.smoke
def test_retry_helper_status_and_retry_after() -> None:
    retryable = _ResponseError("service unavailable", 503)
    non_retryable = _ResponseError("unauthorized", 401)
    retry_after = _ResponseError("rate limit", 429, retry_after="5")

    assert should_retry_exception(retryable)
    assert not should_retry_exception(non_retryable)
    assert compute_retry_delay(retry_after, attempt=0, base_delay=1.0) == 5.0


@pytest.mark.smoke
def test_run_with_retries_retries_until_success() -> None:
    attempts = {"count": 0}

    async def _op() -> str:
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise RuntimeError("connection reset by peer")
        return "ok"

    result = asyncio.run(run_with_retries(_op, max_retries=2, base_delay=0.01))

    assert result == "ok"
    assert attempts["count"] == 2


@pytest.mark.smoke
def test_run_with_retries_stops_on_non_retryable_error() -> None:
    attempts = {"count": 0}

    async def _op() -> str:
        attempts["count"] += 1
        raise _ResponseError("unauthorized", 401)

    with pytest.raises(_ResponseError):
        asyncio.run(run_with_retries(_op, max_retries=2, base_delay=0.01))

    assert attempts["count"] == 1


@pytest.mark.smoke
def test_openai_completions_retry_emits_reset_before_second_attempt() -> None:
    provider = OpenAICompatibleProvider(api_key="k", api_base="https://x.com/v1")

    attempts = {"count": 0}

    async def _fake_create(**kwargs):
        del kwargs
        attempts["count"] += 1
        if attempts["count"] == 1:
            return _FailingStream()
        return _SuccessStream()

    provider._client = cast(
        Any,
        SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=_fake_create))),
    )

    chunks: list[str] = []

    async def _on_progress(delta: str) -> None:
        chunks.append(delta)

    async def _run() -> LLMResponse:
        return await provider._chat_completions(
            "gpt-4o",
            [{"role": "user", "content": "hi"}],
            None,
            128,
            0.1,
            _on_progress,
        )

    result = asyncio.run(_run())

    assert result.content == "final"
    assert attempts["count"] == 2
    assert chunks == ["partial", PROGRESS_RESET, "final"]


def test_openai_provider_defers_client_construction() -> None:
    provider = OpenAICompatibleProvider(api_key="k", api_base="https://x.com/v1")

    assert provider._client is None


@pytest.mark.smoke
def test_openai_completions_non_retryable_error_returns_without_retry() -> None:
    provider = OpenAICompatibleProvider(api_key="k", api_base="https://x.com/v1")
    attempts = {"count": 0}
    chunks: list[str] = []

    async def _fake_create(**kwargs):
        del kwargs
        attempts["count"] += 1
        raise _ResponseError("unauthorized", 401)

    async def _on_progress(delta: str) -> None:
        chunks.append(delta)

    provider._client = cast(
        Any,
        SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=_fake_create))),
    )

    async def _run() -> LLMResponse:
        return await provider._chat_completions(
            "gpt-4o",
            [{"role": "user", "content": "hi"}],
            None,
            128,
            0.1,
            _on_progress,
        )

    result = asyncio.run(_run())

    assert attempts["count"] == 1
    assert chunks == []
    assert result.finish_reason == "error"
    assert "unauthorized" in (result.content or "")


@pytest.mark.smoke
def test_anthropic_retry_emits_reset_before_second_attempt() -> None:
    provider = AnthropicProvider(api_key="k")
    attempts = {"count": 0}

    def _stream(**kwargs):
        del kwargs
        attempts["count"] += 1
        if attempts["count"] == 1:
            return _AnthropicStreamContext(
                [
                    SimpleNamespace(
                        type="content_block_delta",
                        delta=SimpleNamespace(type="text_delta", text="partial"),
                    )
                ]
            )
        return _AnthropicStreamContext(
            [
                SimpleNamespace(
                    type="content_block_delta",
                    delta=SimpleNamespace(type="text_delta", text="final"),
                )
            ]
        )

    provider._client = cast(Any, SimpleNamespace(messages=SimpleNamespace(stream=_stream)))

    chunks: list[str] = []

    async def _on_progress(delta: str) -> None:
        chunks.append(delta)

    async def _run() -> LLMResponse:
        return await provider.chat(
            messages=[{"role": "user", "content": "hi"}],
            model="claude-sonnet-4-20250514",
            on_progress=_on_progress,
        )

    original_get_final = _AnthropicStreamContext.get_final_message

    async def _failing_get_final(self):
        if attempts["count"] == 1:
            raise RuntimeError("connection reset by peer")
        return await original_get_final(self)

    _AnthropicStreamContext.get_final_message = _failing_get_final
    try:
        result = asyncio.run(_run())
    finally:
        _AnthropicStreamContext.get_final_message = original_get_final

    assert result.content == "final"
    assert attempts["count"] == 2
    assert chunks == ["partial", PROGRESS_RESET, "final"]


def test_openai_completions_cancelled_error_not_swallowed() -> None:
    provider = OpenAICompatibleProvider(api_key="k", api_base="https://x.com/v1")

    async def _raise_cancelled(**kwargs):
        del kwargs
        raise asyncio.CancelledError()

    provider._client = cast(
        Any,
        SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=_raise_cancelled))),
    )

    async def _run() -> LLMResponse:
        return await provider._chat_completions(
            "gpt-4o",
            [{"role": "user", "content": "hi"}],
            None,
            128,
            0.1,
            None,
        )

    try:
        asyncio.run(_run())
    except asyncio.CancelledError:
        return

    raise AssertionError("CancelledError should propagate")


def test_anthropic_cancelled_error_not_swallowed() -> None:
    provider = AnthropicProvider(api_key="k")

    class _CancelledStreamContext:
        async def __aenter__(self) -> Self:
            return self

        async def __aexit__(self, exc_type, exc, tb) -> bool:
            return False

        def __aiter__(self) -> Self:
            return self

        async def __anext__(self) -> Any:
            raise asyncio.CancelledError()

        async def get_final_message(self) -> Any:
            raise AssertionError("should not reach final message")

    provider._client = cast(
        Any,
        SimpleNamespace(
            messages=SimpleNamespace(stream=lambda **kwargs: _CancelledStreamContext())
        ),
    )

    async def _run() -> LLMResponse:
        return await provider.chat(
            messages=[{"role": "user", "content": "hi"}],
            model="claude-sonnet-4-20250514",
        )

    with pytest.raises(asyncio.CancelledError):
        asyncio.run(_run())


def test_responses_mode_auto_falls_back_to_completions(monkeypatch) -> None:
    provider = OpenAICompatibleProvider(api_key="k", api_base="https://x.com/v1")

    class _Resp:
        status_code = 503
        text = "upstream unavailable"

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            del exc_type, exc, tb
            return False

        async def post(self, *args, **kwargs):
            del args, kwargs
            return _Resp()

    async def _fake_chat(*args, **kwargs):
        del args, kwargs
        return LLMResponse(content="fallback-ok", finish_reason="stop")

    monkeypatch.setattr(
        "bao.providers.openai_provider.httpx.AsyncClient", lambda timeout: _Client()
    )
    monkeypatch.setattr(provider, "_chat_completions", _fake_chat)

    result = asyncio.run(
        provider._chat_responses(
            "gpt-4o",
            [{"role": "user", "content": "hi"}],
            None,
            256,
            0.1,
        )
    )
    assert result.content == "fallback-ok"


def test_responses_mode_fallback_on_http_error(monkeypatch) -> None:
    provider = OpenAICompatibleProvider(api_key="k", api_base="https://x.com/v1")

    class _Resp:
        status_code = 503
        text = "upstream unavailable"

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            del exc_type, exc, tb
            return False

        async def post(self, *args, **kwargs):
            del args, kwargs
            return _Resp()

    async def _fake_chat(*args, **kwargs):
        del args, kwargs
        return LLMResponse(content="fallback-503", finish_reason="stop")

    monkeypatch.setattr(
        "bao.providers.openai_provider.httpx.AsyncClient", lambda timeout: _Client()
    )
    monkeypatch.setattr(provider, "_chat_completions", _fake_chat)

    result = asyncio.run(
        provider._chat_responses(
            "gpt-4o",
            [{"role": "user", "content": "hi"}],
            None,
            256,
            0.1,
        )
    )

    assert result.content == "fallback-503"
