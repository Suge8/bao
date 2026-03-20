from __future__ import annotations

import asyncio
import copy
from typing import Any

from loguru import logger

from bao.profile import ProfileContext, profile_context_from_mapping


async def init_hub_stack(service: Any) -> tuple[Any, list[str]]:
    from bao.config.loader import ensure_first_run, get_config_path, load_config
    from bao.config.schema import Config
    from bao.hub.builder import BuildHubStackOptions, build_hub_stack
    from bao.providers import make_provider

    ensure_first_run()
    config_path = get_config_path()
    if service._config_data is not None:
        config = Config.model_validate(copy.deepcopy(service._config_data))
    else:
        try:
            config = load_config(config_path)
        except SystemExit as exc:
            raise RuntimeError(f"Config unavailable at {config_path}") from exc
    profile_context = profile_context_from_mapping(service._profile_context_data)
    provider = make_provider(config)
    reuse_sm = service._reusable_session_manager(config, profile_context)
    stack = build_hub_stack(
        config,
        provider,
        BuildHubStackOptions(
            session_manager=reuse_sm,
            on_channel_error=service._handle_channel_error,
            profile_context=profile_context,
        ),
    )
    service._agent = stack.agent
    service._dispatcher = getattr(stack, "dispatcher", None) or stack.agent
    service._channels = stack.channels
    service._cron = stack.cron
    service._heartbeat = stack.heartbeat
    await start_hub_background_services(service, stack, profile_context)
    service._sync_dispatcher_runtime_state(update_hub_bindings=True, emit_hub_ready=False)
    return stack.session_manager, stack.channels.enabled_channels


async def start_hub_background_services(
    service: Any,
    stack: Any,
    profile_context: ProfileContext | None,
) -> None:
    loop = asyncio.get_running_loop()
    dispatcher_runner = getattr(stack, "dispatcher", None) or stack.agent
    service._cron_status = stack.cron.status()
    service._background_tasks = [
        loop.create_task(dispatcher_runner.run()),
        loop.create_task(stack.channels.start_all()),
        loop.create_task(run_startup_greeting(service, stack, profile_context=profile_context)),
    ]


async def run_startup_greeting(
    service: Any,
    stack: Any,
    *,
    profile_context: ProfileContext | None,
) -> None:
    from bao.hub.builder import StartupGreetingOptions, send_startup_greeting

    try:
        await send_startup_greeting(
            stack.agent,
            stack.bus,
            StartupGreetingOptions(
                config=stack.config,
                on_desktop_startup_message=lambda msg: service._startupMessage.emit(msg),
                on_startup_activity=lambda payload: service._startupActivityUpdate.emit(payload),
                channels=stack.channels,
                session_manager=stack.session_manager,
                profile_context=profile_context,
            ),
        )
    except Exception as exc:
        service._startupActivityUpdate.emit(
            {
                "kind": "startup_greeting",
                "status": "error",
                "error": str(exc),
            }
        )
        logger.warning("Desktop startup greeting failed: {}", exc)
        return
    service._startupActivityUpdate.emit({"status": "completed"})
