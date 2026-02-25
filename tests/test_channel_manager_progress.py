import asyncio
import sys
from contextlib import suppress
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bao.bus.events import OutboundMessage
from bao.bus.queue import MessageBus
from bao.channels.base import BaseChannel
from bao.channels.manager import ChannelManager
from bao.config.schema import Config, IMessageConfig


class _DummyChannel(BaseChannel):
    name = "dummy"

    def __init__(self, bus: MessageBus):
        super().__init__(IMessageConfig(enabled=True), bus)
        self.sent: list[OutboundMessage] = []

    async def start(self) -> None:
        self._running = True

    async def stop(self) -> None:
        self._running = False

    async def send(self, msg: OutboundMessage) -> None:
        self.sent.append(msg)


def _dispatch_one(
    manager: ChannelManager, bus: MessageBus, msg: OutboundMessage, channel: _DummyChannel
) -> None:
    async def _run() -> None:
        task = asyncio.create_task(manager._dispatch_outbound())
        try:
            await bus.publish_outbound(msg)
            for _ in range(20):
                if channel.sent:
                    break
                await asyncio.sleep(0.01)
        finally:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

    asyncio.run(_run())


def test_tool_hint_suppressed_keeps_iteration_boundary() -> None:
    bus = MessageBus()
    cfg = Config()
    cfg.agents.defaults.send_progress = True
    cfg.agents.defaults.send_tool_hints = False

    manager = ChannelManager(cfg, bus)
    dummy = _DummyChannel(bus)
    manager.channels = {"dummy": dummy}

    _dispatch_one(
        manager,
        bus,
        OutboundMessage(
            channel="dummy",
            chat_id="c1",
            content='web_fetch("https://example.com")',
            metadata={"_progress": True, "_tool_hint": True, "_progress_kind": "tool"},
        ),
        dummy,
    )

    assert len(dummy.sent) == 1
    sent = dummy.sent[0]
    assert sent.content == ""
    assert sent.metadata.get("_tool_hint") is True
    assert sent.metadata.get("_tool_hint_suppressed") is True


def test_tool_hint_dropped_when_progress_also_disabled() -> None:
    bus = MessageBus()
    cfg = Config()
    cfg.agents.defaults.send_progress = False
    cfg.agents.defaults.send_tool_hints = False

    manager = ChannelManager(cfg, bus)
    dummy = _DummyChannel(bus)
    manager.channels = {"dummy": dummy}

    _dispatch_one(
        manager,
        bus,
        OutboundMessage(
            channel="dummy",
            chat_id="c2",
            content='web_fetch("https://example.com")',
            metadata={"_progress": True, "_tool_hint": True, "_progress_kind": "tool"},
        ),
        dummy,
    )

    assert dummy.sent == []
