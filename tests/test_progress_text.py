import asyncio

from bao.channels.progress_text import (
    IterationBuffer,
    ProgressBuffer,
    final_remainder,
    is_minor_tail,
    sanitize_progress_chunk,
)


def test_sanitize_progress_chunk_trims_leading_and_collapses_blank_lines() -> None:
    text = "\n\nhello\n\n\nworld"
    assert sanitize_progress_chunk(text) == "hello\n\nworld"


def test_final_remainder_with_large_overlap() -> None:
    streamed = "hello world"
    final = "hello world and"
    assert final_remainder(final, streamed) == " and"


def test_final_remainder_without_overlap_returns_full_text() -> None:
    streamed = "abc"
    final = "totally different"
    assert final_remainder(final, streamed) == final


def test_is_minor_tail_for_punctuation_only() -> None:
    assert is_minor_tail("。") is True
    assert is_minor_tail("!?") is True
    assert is_minor_tail("done") is False


def test_empty_tool_hint_still_flushes_iteration_boundary() -> None:
    buf = IterationBuffer()
    assert buf.process("chat", "先查一下", is_progress=True, is_tool_hint=False) == []
    assert buf.process("chat", "", is_progress=True, is_tool_hint=True) == ["先查一下"]


def test_progress_buffer_final_only_sends_tail_after_flushed_progress() -> None:
    sent: list[tuple[str, str]] = []

    async def _send(chat_id: str, text: str) -> None:
        sent.append((chat_id, text))

    buf = ProgressBuffer(_send, min_chars=8)

    async def _run() -> None:
        await buf.handle(
            "chat",
            "这是一个足够长的进度句子，会先发出去。",
            is_progress=True,
            is_tool_hint=False,
        )
        await buf.flush("chat", force=False)
        await buf.handle(
            "chat",
            "这是一个足够长的进度句子，会先发出去。然后再补一句结论。",
            is_progress=False,
            is_tool_hint=False,
        )

    asyncio.run(_run())

    assert sent == [
        ("chat", "这是一个足够长的进度句子，会先发出去。"),
        ("chat", "然后再补一句结论。"),
    ]


def test_progress_buffer_final_includes_unsent_pending_prefix_once() -> None:
    sent: list[tuple[str, str]] = []

    async def _send(chat_id: str, text: str) -> None:
        sent.append((chat_id, text))

    buf = ProgressBuffer(_send)

    async def _run() -> None:
        await buf.handle("chat", "你", is_progress=True, is_tool_hint=False)
        await buf.handle("chat", "好", is_progress=True, is_tool_hint=False)
        await buf.handle("chat", "你好", is_progress=False, is_tool_hint=False)

    asyncio.run(_run())

    assert sent == [("chat", "你好")]


def test_progress_buffer_tail_keeps_space_boundary_without_duplicate_prefix() -> None:
    sent: list[tuple[str, str]] = []

    async def _send(chat_id: str, text: str) -> None:
        sent.append((chat_id, text))

    buf = ProgressBuffer(_send, min_chars=5, hard_chars=6)

    async def _run() -> None:
        await buf.handle("chat", "Hello ", is_progress=True, is_tool_hint=False)
        await buf.flush("chat", force=False)
        await buf.handle("chat", "Hello world", is_progress=False, is_tool_hint=False)

    asyncio.run(_run())

    assert sent == [("chat", "Hello"), ("chat", "world")]
