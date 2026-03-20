from __future__ import annotations

import importlib
import os
import sys
from dataclasses import dataclass
from typing import Callable

from PySide6.QtGui import QFont, QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

from app._main_runtime_process import (
    install_sigint_quit_handler,
    prepare_single_instance,
    release_single_instance_resources,
)
from app._main_runtime_qml import report_invalid_qml
from app._main_runtime_window import (
    SmokeRunOptions,
    WindowLaunchOptions,
    apply_startup_options,
    configure_root,
    schedule_deferred_startup,
    seed_or_smoke,
)
from app._main_runtime_wiring import wire_services


@dataclass
class DesktopRuntimeContext:
    app: QApplication
    runner: object
    messages_model: object
    chat_service: object
    config_service: object
    profile_service: object
    session_service: object
    cron_service: object
    heartbeat_service: object
    memory_service: object
    skills_service: object
    tools_service: object
    profile_supervisor_service: object
    update_service: object
    diagnostics_service: object
    desktop_preferences: object
    update_bridge: object
    system_ui_language: str


@dataclass(frozen=True)
class ServiceBuildRequest:
    engine: QQmlApplicationEngine
    app: QApplication
    qml_url: object
    report_startup_failure: Callable[..., None]
def run_desktop_app() -> int:
    from app import main as main_module
    from bao.runtime_diagnostics import configure_desktop_logging, report_startup_failure

    smoke, qml, smoke_theme_toggle, start_view, seed_messages, smoke_screenshot, window_width, window_height = main_module.parse_args()
    smoke_mode = main_module.is_smoke_run(smoke, smoke_theme_toggle, smoke_screenshot)
    _ = configure_desktop_logging()
    qml_url = main_module.resolve_qml_url(qml)
    invalid = report_invalid_qml(qml_url, report_startup_failure)
    if invalid is not None:
        return invalid
    single_instance_state, early_exit = prepare_single_instance(main_module, smoke_mode=smoke_mode)
    if early_exit is not None:
        return early_exit
    app, logo_icon = _prepare_application(main_module)
    single_instance_server = None
    if single_instance_state.enabled:
        single_instance_server = main_module.DesktopSingleInstanceServer(single_instance_state.server_name, parent=app)
    engine = QQmlApplicationEngine()
    services = _build_services(
        ServiceBuildRequest(
            engine=engine,
            app=app,
            qml_url=qml_url,
            report_startup_failure=report_startup_failure,
        )
    )
    if services is None:
        release_single_instance_resources(single_instance_server, single_instance_state.lock)
        return 1
    root, context = services
    configure_root(root, context, logo_icon)
    if single_instance_server is not None:
        single_instance_server.set_activate_callback(lambda: main_module.activate_window(root))
    apply_startup_options(
        root,
        WindowLaunchOptions(start_view=start_view, width=window_width, height=window_height),
    )
    schedule_deferred_startup(context, smoke_mode)
    seed_or_smoke(
        root,
        context,
        SmokeRunOptions(
            seed_messages=seed_messages,
            smoke=smoke,
            smoke_theme_toggle=smoke_theme_toggle,
            smoke_screenshot=smoke_screenshot,
        ),
    )
    restore_sigint_handler = install_sigint_quit_handler(app)
    ret = app.exec()
    restore_sigint_handler()
    main_module.shutdown_desktop_services(
        context.update_service,
        context.chat_service,
        context.session_service,
        context.memory_service,
    )
    release_single_instance_resources(single_instance_server, single_instance_state.lock)
    context.runner.shutdown(grace_s=5.0 if smoke_mode else 2.0)
    return ret


def _prepare_application(main_module: object) -> tuple[QApplication, QIcon | None]:
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"
    if os.getenv("BAO_QML_DISABLE_DISK_CACHE") == "1":
        os.environ["QML_DISABLE_DISK_CACHE"] = "1"
    main_module.configure_qt_style()
    app = QApplication(sys.argv)
    app_font_family = main_module.resolve_app_font_family()
    if app_font_family:
        app.setFont(QFont(app_font_family))
    logo_path = main_module.resolve_app_icon_path()
    logo_icon = main_module.load_app_icon(logo_path) if logo_path else None
    if logo_icon:
        app.setWindowIcon(logo_icon)
    return app, logo_icon


def _build_services(request: ServiceBuildRequest) -> tuple[object, DesktopRuntimeContext] | None:
    context = _create_runtime_context(request)
    if context is None:
        return None
    return _load_root_object(request, context)


def _create_runtime_context(request: ServiceBuildRequest) -> DesktopRuntimeContext | None:
    runtime = _build_core_services()
    return _build_desktop_context(request, runtime)


def _build_core_services() -> dict[str, object]:
    from app.backend.asyncio_runner import AsyncioRunner
    from app.backend.chat import ChatMessageModel
    from app.backend.config import ConfigService
    from app.backend.hub import ChatService
    from app.backend.memory import MemoryService
    from app.backend.profile import ProfileService
    from app.backend.profile_supervisor import (
        ProfileSupervisorServices,
        ProfileWorkSupervisorService,
    )
    from app.backend.session import SessionService
    from app.backend.skills import SkillsService, SkillsServiceOptions
    from app.backend.update import UpdateBridge, UpdateService

    cron_bridge_service_cls = getattr(importlib.import_module("app.backend.cron"), "CronBridgeService")
    heartbeat_bridge_service_cls = getattr(importlib.import_module("app.backend.heartbeat"), "HeartbeatBridgeService")
    tools_service_cls = getattr(importlib.import_module("app.backend.tools"), "ToolsService")
    runner = AsyncioRunner()
    runner.start()
    messages_model = ChatMessageModel()
    chat_service = ChatService(messages_model, runner)
    config_service = ConfigService()
    profile_service = ProfileService(runner)
    session_service = SessionService(runner)
    cron_service = cron_bridge_service_cls(runner)
    heartbeat_service = heartbeat_bridge_service_cls(runner)
    memory_service = MemoryService(runner)
    skills_service = SkillsService(SkillsServiceOptions(runner=runner, workspace_path="~/.bao/workspace", eager_refresh=False))
    tools_service = tools_service_cls(runner, config_service)
    return {
        "runner": runner,
        "messages_model": messages_model,
        "chat_service": chat_service,
        "config_service": config_service,
        "profile_service": profile_service,
        "session_service": session_service,
        "cron_service": cron_service,
        "heartbeat_service": heartbeat_service,
        "memory_service": memory_service,
        "skills_service": skills_service,
        "tools_service": tools_service,
        "profile_supervisor_service": ProfileWorkSupervisorService(
            runner,
            services=ProfileSupervisorServices(
                profile_service=profile_service,
                session_service=session_service,
                chat_service=chat_service,
                cron_service=cron_service,
                heartbeat_service=heartbeat_service,
            ),
        ),
        "update_service": UpdateService(runner, config_service),
        "update_bridge": UpdateBridge(),
    }


def _build_desktop_context(
    request: ServiceBuildRequest,
    runtime: dict[str, object],
) -> DesktopRuntimeContext | None:
    from app import main as main_module
    from app.backend.diagnostics import DiagnosticsService
    from app.backend.preferences import DesktopPreferences
    if not _load_desktop_config(runtime["config_service"], request.report_startup_failure):
        return None
    system_ui_language = main_module.detect_system_ui_language()
    desktop_preferences = DesktopPreferences(system_ui_language=system_ui_language)
    context = DesktopRuntimeContext(
        app=request.app,
        runner=runtime["runner"],
        messages_model=runtime["messages_model"],
        chat_service=runtime["chat_service"],
        config_service=runtime["config_service"],
        profile_service=runtime["profile_service"],
        session_service=runtime["session_service"],
        cron_service=runtime["cron_service"],
        heartbeat_service=runtime["heartbeat_service"],
        memory_service=runtime["memory_service"],
        skills_service=runtime["skills_service"],
        tools_service=runtime["tools_service"],
        profile_supervisor_service=runtime["profile_supervisor_service"],
        update_service=runtime["update_service"],
        diagnostics_service=DiagnosticsService(eager_refresh=False),
        desktop_preferences=desktop_preferences,
        update_bridge=runtime["update_bridge"],
        system_ui_language=system_ui_language,
    )
    wire_services(context, main_module)
    return context


def _load_root_object(
    request: ServiceBuildRequest,
    context: DesktopRuntimeContext,
) -> tuple[object, DesktopRuntimeContext] | None:
    request.engine.setInitialProperties(
        {
            "chatService": context.chat_service,
            "configService": context.config_service,
            "profileService": context.profile_service,
            "sessionService": context.session_service,
            "profileSupervisorService": context.profile_supervisor_service,
            "cronService": context.cron_service,
            "heartbeatService": context.heartbeat_service,
            "memoryService": context.memory_service,
            "skillsService": context.skills_service,
            "toolsService": context.tools_service,
            "diagnosticsService": context.diagnostics_service,
            "desktopPreferences": context.desktop_preferences,
            "updateService": context.update_service,
            "updateBridge": context.update_bridge,
            "systemUiLanguage": context.system_ui_language,
        }
    )
    request.engine.load(request.qml_url)
    if not request.engine.rootObjects():
        request.report_startup_failure(
            f"QML load failed: {request.qml_url.toString()}",
            code="qml_load_failed",
            details={"qml_path": request.qml_url.toString()},
        )
        return None
    return request.engine.rootObjects()[0], context


def _load_desktop_config(config_service: object, report_startup_failure: Callable[..., None]) -> bool:
    try:
        config_service.load()
        return True
    except Exception as exc:
        report_startup_failure(f"First-run setup failed: {exc}", code="first_run_failed")
        return False
