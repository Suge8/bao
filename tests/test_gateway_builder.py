"""Tests for bao.gateway.builder — shared gateway stack builder."""

from __future__ import annotations

import asyncio
import dataclasses
from unittest.mock import AsyncMock, MagicMock

import pytest

from bao.gateway.builder import GatewayStack, build_gateway_stack


class TestImports:
    """Verify the public API is importable."""

    def test_imports(self):
        from bao.gateway.builder import (  # noqa: F811
            GatewayStack,  # noqa: F811, F401
            build_gateway_stack,  # noqa: F811
            send_startup_greeting,
        )
        assert callable(build_gateway_stack)
        assert asyncio.iscoroutinefunction(send_startup_greeting)


class TestGatewayStack:
    """Verify GatewayStack dataclass shape."""

    def test_has_seven_fields(self):
        fields = [f.name for f in dataclasses.fields(GatewayStack)]
        assert fields == [
            "config",
            "bus",
            "session_manager",
            "cron",
            "heartbeat",
            "agent",
            "channels",
        ]

    def test_is_dataclass(self):
        assert dataclasses.is_dataclass(GatewayStack)


class TestCronCallbackDefensive:
    """Cron callback must catch exceptions and return 'Error: ...' string."""

    @pytest.fixture()
    def stub_job(self):
        from bao.cron.types import CronJob, CronPayload
        return CronJob(
            id="test-job",
            name="test",
            payload=CronPayload(
                message="hello",
                deliver=False,
                channel="gateway",
                to=None,
            ),
        )

    @pytest.fixture()
    def failing_agent(self):
        agent = MagicMock()
        agent.process_direct = AsyncMock(side_effect=RuntimeError("boom"))
        return agent

    @pytest.mark.asyncio
    async def test_cron_callback_returns_error_string(self, stub_job, failing_agent):
        """When agent.process_direct raises, callback returns 'Error: ...' instead of crashing."""
        # We need to extract the on_cron_job closure.
        # Build a minimal mock cron service that captures the callback.
        _ = None  # placeholder for callback capture (unused in this test path)

        class FakeCron:
            on_job = None
            def __init__(self, path):
                pass

        # Patch the imports inside build_gateway_stack to use our fakes
        import bao.gateway.builder as mod
        from unittest.mock import patch

        fake_bus = MagicMock()
        fake_bus.publish_outbound = AsyncMock()

        with (
            patch.object(mod, "__name__", mod.__name__),
            patch("bao.agent.loop.AgentLoop", return_value=failing_agent),
            patch("bao.bus.queue.MessageBus", return_value=fake_bus),
            patch("bao.channels.manager.ChannelManager", return_value=MagicMock()),
            patch("bao.config.loader.get_data_dir", return_value=MagicMock(__truediv__=lambda s, x: MagicMock(__truediv__=lambda s, x: "/tmp/fake"))),
            patch("bao.cron.service.CronService", side_effect=FakeCron),
            patch("bao.heartbeat.service.HeartbeatService", return_value=MagicMock()),
            patch("bao.session.manager.SessionManager", return_value=MagicMock()),
        ):
            config = MagicMock()
            config.workspace_path = "/tmp/test"
            config.agents.defaults.model = "test"
            config.agents.defaults.temperature = 0.1
            config.agents.defaults.max_tokens = 100
            config.agents.defaults.max_tool_iterations = 5
            config.agents.defaults.memory_window = 10
            config.agents.defaults.models = []
            config.tools.web.search = MagicMock()
            config.tools.exec = MagicMock()
            config.tools.embedding = MagicMock()
            config.tools.restrict_to_workspace = False
            config.tools.mcp_servers = {}

            stack = build_gateway_stack(config, MagicMock())

        # The cron callback is set on the FakeCron instance
        callback = stack.cron.on_job
        assert callback is not None

        result = await callback(stub_job)
        assert isinstance(result, str)
        assert result.startswith("Error: ")
        assert "boom" in result
