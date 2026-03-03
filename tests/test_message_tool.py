import asyncio
import importlib

from bao.agent.tools.message import MessageTool
from bao.bus.events import OutboundMessage

pytest = importlib.import_module("pytest")


def test_message_tool_allows_only_one_send_per_turn() -> None:
    sent: list[OutboundMessage] = []

    async def _send_callback(msg: OutboundMessage) -> None:
        sent.append(msg)

    tool = MessageTool(
        send_callback=_send_callback,
        default_channel="imessage",
        default_chat_id="+86100",
    )

    async def _run() -> tuple[str, str]:
        first = await tool.execute(content="hello")
        second = await tool.execute(content="hello again")
        return first, second

    first, second = asyncio.run(_run())
    assert len(sent) == 1
    assert first.startswith("Message sent to imessage:+86100")
    assert (
        second == "Error: message tool already sent once in this turn. Do not call message again."
    )


def test_message_tool_reset_on_new_turn() -> None:
    sent: list[OutboundMessage] = []

    async def _send_callback(msg: OutboundMessage) -> None:
        sent.append(msg)

    tool = MessageTool(
        send_callback=_send_callback,
        default_channel="imessage",
        default_chat_id="+86100",
    )

    async def _run() -> None:
        await tool.execute(content="turn1")
        tool.start_turn()
        await tool.execute(content="turn2")

    asyncio.run(_run())
    assert len(sent) == 2
    assert sent[0].content == "turn1"
    assert sent[1].content == "turn2"


def test_message_tool_single_send_across_child_tasks() -> None:
    sent: list[OutboundMessage] = []

    async def _send_callback(msg: OutboundMessage) -> None:
        sent.append(msg)

    tool = MessageTool(
        send_callback=_send_callback,
        default_channel="imessage",
        default_chat_id="+86100",
    )

    async def _run() -> tuple[str, str, str | None]:
        tool.start_turn()
        first = await asyncio.create_task(tool.execute(content="hello"))
        second = await asyncio.create_task(tool.execute(content="hello again"))
        return first, second, tool.last_sent_summary

    first, second, summary = asyncio.run(_run())
    assert len(sent) == 1
    assert first.startswith("Message sent to imessage:+86100")
    assert (
        second == "Error: message tool already sent once in this turn. Do not call message again."
    )
    assert isinstance(summary, str)
    assert summary.startswith("[message tool sent] imessage:+86100")


def test_message_tool_concurrent_calls_do_not_double_send() -> None:
    sent: list[OutboundMessage] = []
    callback_calls = 0
    release = asyncio.Event()
    first_entered = asyncio.Event()

    async def _send_callback(msg: OutboundMessage) -> None:
        nonlocal callback_calls
        callback_calls += 1
        first_entered.set()
        await release.wait()
        sent.append(msg)

    tool = MessageTool(
        send_callback=_send_callback,
        default_channel="imessage",
        default_chat_id="+86100",
    )

    async def _run() -> tuple[str, str]:
        tool.start_turn()
        first_task = asyncio.create_task(tool.execute(content="hello"))
        second_task = asyncio.create_task(tool.execute(content="hello again"))
        await first_entered.wait()
        await asyncio.sleep(0)
        release.set()
        return await asyncio.gather(first_task, second_task)

    first, second = asyncio.run(_run())
    assert callback_calls == 1
    assert len(sent) == 1
    assert first.startswith("Message sent to imessage:+86100")
    assert (
        second == "Error: message tool already sent once in this turn. Do not call message again."
    )


def test_message_tool_ignores_non_string_message_id_arg() -> None:
    sent: list[OutboundMessage] = []

    async def _send_callback(msg: OutboundMessage) -> None:
        sent.append(msg)

    tool = MessageTool(send_callback=_send_callback)
    tool.set_context("telegram", "100", "123")

    async def _run() -> None:
        await tool.execute(channel="discord", chat_id="chan-1", content="x", message_id=123)

    asyncio.run(_run())
    assert len(sent) == 1
    assert sent[0].reply_to is None
    assert sent[0].metadata.get("message_id") is None


def test_message_tool_does_not_leak_default_reply_to_across_channels() -> None:
    sent: list[OutboundMessage] = []

    async def _send_callback(msg: OutboundMessage) -> None:
        sent.append(msg)

    tool = MessageTool(send_callback=_send_callback)
    tool.set_context(
        "telegram",
        "100",
        "123",
        reply_metadata={"slack": {"thread_ts": "1710000.321", "channel_type": "channel"}},
    )

    async def _run() -> None:
        await tool.execute(channel="discord", chat_id="chan-1", content="x")

    asyncio.run(_run())
    assert len(sent) == 1
    assert sent[0].reply_to is None
    assert sent[0].metadata.get("slack") is None


def test_message_tool_keeps_default_reply_to_in_same_context() -> None:
    sent: list[OutboundMessage] = []

    async def _send_callback(msg: OutboundMessage) -> None:
        sent.append(msg)

    tool = MessageTool(send_callback=_send_callback)
    tool.set_context("telegram", "100", "123")

    async def _run() -> None:
        await tool.execute(content="x")

    asyncio.run(_run())
    assert len(sent) == 1
    assert sent[0].reply_to == "123"
    assert sent[0].metadata.get("message_id") == "123"


def test_message_tool_keeps_thread_metadata_in_same_context() -> None:
    sent: list[OutboundMessage] = []

    async def _send_callback(msg: OutboundMessage) -> None:
        sent.append(msg)

    tool = MessageTool(send_callback=_send_callback)
    tool.set_context(
        "slack",
        "C123",
        "1710000.555",
        reply_metadata={"slack": {"thread_ts": "1710000.555", "channel_type": "channel"}},
    )

    async def _run() -> None:
        await tool.execute(content="x")

    asyncio.run(_run())
    assert len(sent) == 1
    assert sent[0].metadata.get("slack") == {
        "thread_ts": "1710000.555",
        "channel_type": "channel",
    }


def test_message_tool_normalizes_default_target_for_thread_metadata() -> None:
    sent: list[OutboundMessage] = []

    async def _send_callback(msg: OutboundMessage) -> None:
        sent.append(msg)

    tool = MessageTool(send_callback=_send_callback)
    tool.set_context(
        "slack",
        "C123",
        "1710000.555",
        reply_metadata={"slack": {"thread_ts": "1710000.555", "channel_type": "channel"}},
    )

    async def _run() -> None:
        await tool.execute(channel=" Slack ", chat_id="C123 ", content="x")

    asyncio.run(_run())
    assert len(sent) == 1
    assert sent[0].channel == "slack"
    assert sent[0].chat_id == "C123"
    assert sent[0].metadata.get("slack") == {
        "thread_ts": "1710000.555",
        "channel_type": "channel",
    }


def test_message_tool_propagates_cancelled_error() -> None:
    async def _send_callback(_msg: OutboundMessage) -> None:
        raise asyncio.CancelledError()

    tool = MessageTool(
        send_callback=_send_callback,
        default_channel="imessage",
        default_chat_id="+86100",
    )

    async def _run() -> None:
        await tool.execute(content="cancel me")

    with pytest.raises(asyncio.CancelledError):
        asyncio.run(_run())
