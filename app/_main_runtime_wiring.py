from __future__ import annotations

from typing import Callable, cast

from app.backend._hub_access import DesktopHubAccess


def wire_services(context: object, main_module: object) -> None:
    wire_chat_language(context, main_module)
    wire_config_exports(context, main_module)
    wire_session_services(context)
    wire_profile_coordinator(context, main_module)
    wire_update_bridge(context)


def wire_chat_language(context: object, main_module: object) -> None:
    set_language = cast(Callable[[str], None], context.chat_service.setLanguage)
    set_language(main_module.effective_desktop_language(context.desktop_preferences))
    _ = context.desktop_preferences.effectiveLanguageChanged.connect(
        lambda: set_language(main_module.effective_desktop_language(context.desktop_preferences))
    )


def wire_config_exports(context: object, main_module: object) -> None:
    set_channels = cast(Callable[[list[str]], None], context.chat_service.setConfiguredHubChannels)

    def refresh_channels() -> None:
        set_channels(main_module.configured_hub_channels(context.config_service))

    refresh_channels()
    main_module.connect_on_config_change(context.config_service, refresh_channels)
    main_module.bind_exported_config(
        context.config_service,
        cast(Callable[[object], None], context.chat_service.setConfigData),
    )
    main_module.bind_exported_config(context.config_service, context.tools_service.setConfigData)
    main_module.bind_exported_config(context.config_service, context.skills_service.setConfigData)


def wire_session_services(context: object) -> None:
    hub_access = DesktopHubAccess()
    hub_access.set_dispatcher_provider(lambda: getattr(context.chat_service, "_dispatcher", None))
    cast(Callable[[object], None], context.session_service.setHubAccess)(hub_access)
    cast(Callable[[object], None], context.chat_service.setHubAccess)(hub_access)
    cast(Callable[[object], None], context.session_service.setHubDispatcherProvider)(
        lambda: getattr(context.chat_service, "_dispatcher", None)
    )
    _ = context.session_service.hubLocalPortsReady.connect(
        cast(Callable[[object], None], context.chat_service.setFallbackHubPorts)
    )
    cast(Callable[[object], None], context.cron_service.setSessionService)(context.session_service)
    cast(Callable[[object], None], context.heartbeat_service.setSessionService)(context.session_service)
    set_cron_language = cast(Callable[[str], None], context.cron_service.setLanguage)
    set_heartbeat_language = cast(Callable[[str], None], context.heartbeat_service.setLanguage)
    _ = context.desktop_preferences.effectiveLanguageChanged.connect(
        lambda: set_cron_language("zh" if context.desktop_preferences.property("effectiveLanguage") == "zh" else "en")
    )
    _ = context.desktop_preferences.effectiveLanguageChanged.connect(
        lambda: set_heartbeat_language("zh" if context.desktop_preferences.property("effectiveLanguage") == "zh" else "en")
    )
    _ = context.chat_service.stateChanged.connect(
        lambda state: (
            context.cron_service.setHubRunning(state == "running"),
            context.heartbeat_service.setHubRunning(state == "running"),
        )
    )
    _ = getattr(context.chat_service, "cronServiceChanged").connect(context.cron_service.setLiveCronService)
    _ = getattr(context.chat_service, "heartbeatServiceChanged").connect(
        context.heartbeat_service.setLiveHeartbeatService
    )
    _ = context.chat_service.hubReady.connect(context.session_service.setHubReady)
    _ = context.session_service.activeKeyChanged.connect(
        cast(Callable[[str], None], context.chat_service.setSessionKey)
    )
    _ = context.session_service.activeSummaryChanged.connect(
        cast(Callable[[str, object, object], None], context.chat_service.setSessionSummary)
    )
    _ = context.session_service.activeSessionMetaChanged.connect(
        lambda: context.chat_service.setActiveSessionReadOnly(
            context.session_service.property("activeSessionReadOnly")
        )
    )
    _ = context.session_service.startupTargetReady.connect(
        cast(Callable[[str], None], context.chat_service.notifyStartupSessionReady)
    )
    _ = context.session_service.deleteCompleted.connect(
        cast(Callable[[str, bool, str], None], context.chat_service.handle_session_deleted)
    )


def wire_profile_coordinator(context: object, main_module: object) -> None:
    from app.backend.profile_binding import (
        DesktopProfileCoordinator,
        DesktopProfileCoordinatorOptions,
    )

    profile_coordinator = DesktopProfileCoordinator(
        DesktopProfileCoordinatorOptions(
            config_service=context.config_service,
            profile_service=context.profile_service,
            chat_service=context.chat_service,
            session_service=context.session_service,
            memory_service=context.memory_service,
            cron_service=context.cron_service,
            heartbeat_service=context.heartbeat_service,
            skills_service=context.skills_service,
        )
    )
    _ = context.profile_service.activeProfileChanged.connect(profile_coordinator.apply_active_profile)
    main_module.connect_on_config_change(context.config_service, profile_coordinator.refresh_from_config)
    main_module.connect_on_config_change(
        context.config_service,
        context.profile_supervisor_service.refreshIfHydrated,
    )
    context.app._profile_coordinator = profile_coordinator  # type: ignore[attr-defined]


def wire_update_bridge(context: object) -> None:
    _ = context.update_bridge.checkRequested.connect(context.update_service.check_for_updates)
    _ = context.update_bridge.installRequested.connect(context.update_service.install_update)
    _ = context.update_bridge.reloadRequested.connect(context.update_service.reloadConfig)
    _ = context.update_service.quitRequested.connect(context.app.quit)
