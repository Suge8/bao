import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bao.agent.tools.message import MessageTool
from bao.bus.events import OutboundMessage


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
    assert second == "Error: message tool already sent once in this turn. Do not call message again."


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
