"""Shared gateway stack builder — no UI framework dependencies."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any


@dataclass
class GatewayStack:
    config: Any
    bus: Any
    session_manager: Any
    cron: Any
    heartbeat: Any
    agent: Any
    channels: Any


def build_gateway_stack(config: Any, provider: Any) -> GatewayStack:
    """Build the full gateway service stack from config and provider.

    Returns a :class:`GatewayStack` with all services wired up and ready to start.
    """
    from bao.agent.loop import AgentLoop
    from bao.bus.events import OutboundMessage
    from bao.bus.queue import MessageBus
    from bao.channels.manager import ChannelManager
    from bao.config.loader import get_data_dir
    from bao.cron.service import CronService
    from bao.cron.types import CronJob
    from bao.heartbeat.service import HeartbeatService
    from bao.session.manager import SessionManager

    bus = MessageBus()
    session_manager = SessionManager(config.workspace_path)
    cron = CronService(get_data_dir() / "cron" / "jobs.json")

    agent = AgentLoop(
        bus=bus,
        provider=provider,
        workspace=config.workspace_path,
        model=config.agents.defaults.model,
        temperature=config.agents.defaults.temperature,
        max_tokens=config.agents.defaults.max_tokens,
        max_iterations=config.agents.defaults.max_tool_iterations,
        memory_window=config.agents.defaults.memory_window,
        search_config=config.tools.web.search,
        exec_config=config.tools.exec,
        cron_service=cron,
        embedding_config=config.tools.embedding,
        restrict_to_workspace=config.tools.restrict_to_workspace,
        session_manager=session_manager,
        mcp_servers=config.tools.mcp_servers,
        available_models=config.agents.defaults.models,
        config=config,
    )

    # --- cron callback (defensive, from Desktop version) ---
    async def on_cron_job(job: CronJob) -> str | None:
        from loguru import logger

        try:
            response = await agent.process_direct(
                job.payload.message,
                session_key=f"cron:{job.id}",
                channel=job.payload.channel or "gateway",
                chat_id=job.payload.to or "direct",
            )
        except Exception as e:
            logger.warning("Cron job {} failed: {}", job.id, e)
            return f"Error: {e}"
        if job.payload.deliver and job.payload.to:
            await bus.publish_outbound(
                OutboundMessage(
                    channel=job.payload.channel or "gateway",
                    chat_id=job.payload.to,
                    content=response or "",
                )
            )
        return response

    cron.on_job = on_cron_job

    # --- heartbeat ---
    async def on_heartbeat_execute(tasks: str) -> str:
        """Phase 2: execute heartbeat tasks through the full agent loop."""
        channel, chat_id = "cli", "direct"
        for ch_name in ("telegram", "whatsapp", "discord", "slack", "feishu", "dingtalk", "qq"):
            ch_cfg = getattr(config.channels, ch_name, None)
            if ch_cfg and getattr(ch_cfg, "enabled", False) and getattr(ch_cfg, "allow_from", None):
                channel = ch_name
                chat_id = ch_cfg.allow_from[0].split("|")[0]
                break

        async def _silent(*_args, **_kwargs):
            pass

        return await agent.process_direct(
            tasks,
            session_key="heartbeat",
            channel=channel,
            chat_id=chat_id,
            on_progress=_silent,
        )

    async def on_heartbeat_notify(response: str) -> None:
        """Deliver heartbeat result to the first available channel."""
        for ch_name in ("telegram", "whatsapp", "discord", "slack", "feishu", "dingtalk", "qq"):
            ch_cfg = getattr(config.channels, ch_name, None)
            if ch_cfg and getattr(ch_cfg, "enabled", False) and getattr(ch_cfg, "allow_from", None):
                chat_id = ch_cfg.allow_from[0].split("|")[0]
                await bus.publish_outbound(OutboundMessage(channel=ch_name, chat_id=chat_id, content=response))
                return

    hb_cfg = config.gateway.heartbeat
    heartbeat = HeartbeatService(
        workspace=config.workspace_path,
        provider=provider,
        model=agent.model,
        on_execute=on_heartbeat_execute,
        on_notify=on_heartbeat_notify,
        interval_s=hb_cfg.interval_s,
        enabled=hb_cfg.enabled,
    )

    channels = ChannelManager(config, bus)

    return GatewayStack(
        config=config,
        bus=bus,
        session_manager=session_manager,
        cron=cron,
        heartbeat=heartbeat,
        agent=agent,
        channels=channels,
    )


async def send_startup_greeting(agent: Any, bus: Any, config: Any) -> None:
    """Send startup greeting to all enabled channels.

    Waits 5 seconds after boot, then sends an onboarding prompt or
    a persona-based greeting to every allowed contact.
    """
    from loguru import logger

    from bao.bus.events import OutboundMessage

    await asyncio.sleep(5)

    channel_cfgs = [
        ("telegram", config.channels.telegram),
        ("imessage", config.channels.imessage),
        ("whatsapp", config.channels.whatsapp),
        ("dingtalk", config.channels.dingtalk),
    ]
    targets = [
        (name, uid.split("|")[0])
        for name, cfg in channel_cfgs
        if cfg.enabled and cfg.allow_from
        for uid in cfg.allow_from
    ]
    if not targets:
        return

    from bao.config.loader import (
        LANG_PICKER,
        PERSONA_GREETING,
        detect_onboarding_stage,
        infer_language,
    )

    stage = detect_onboarding_stage(config.workspace_path)
    if stage == "lang_select":
        for ch, cid in targets:
            await bus.publish_outbound(
                OutboundMessage(channel=ch, chat_id=cid, content=LANG_PICKER)
            )
        return
    if stage == "persona_setup":
        greeting = PERSONA_GREETING[infer_language(config.workspace_path)]
        for ch, cid in targets:
            await bus.publish_outbound(
                OutboundMessage(channel=ch, chat_id=cid, content=greeting)
            )
        return

    prompt = (
        "You just came online. Greet the user in character based on your "
        "PERSONA.md personality. Mention the current time naturally. "
        "Don't self-introduce. Keep it short, like an old friend saying hi."
    )
    try:
        greeting = await agent.process_direct(prompt, session_key="system:greeting")
    except Exception as e:
        logger.warning("Startup greeting failed: {}", e)
        return

    if greeting:
        for ch, cid in targets:
            await bus.publish_outbound(
                OutboundMessage(channel=ch, chat_id=cid, content=greeting)
            )
