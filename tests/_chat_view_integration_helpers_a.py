# ruff: noqa: E402, N802, N815, F403, F405, I001
from __future__ import annotations

from tests._chat_view_integration_shared import *
from tests._chat_view_integration_config import *
from tests._chat_view_integration_cron import *
from tests._chat_view_integration_diagnostics import *
from tests._chat_view_integration_models import *
from tests._chat_view_integration_profile_update import *
from tests._chat_view_integration_session import *


def _build_main_window_refs(**overrides: object) -> dict[str, object]:
    messages_model = cast(QAbstractListModel, overrides.get("messages_model") or EmptyMessagesModel())
    session_model = cast(QAbstractListModel, overrides.get("session_model") or messages_model)
    refs = {
        "messages_model": messages_model,
        "chat_service": overrides.get("chat_service") or DummyChatService(messages_model),
        "config_service": overrides.get("config_service") or DummyConfigService(),
        "profile_service": overrides.get("profile_service") or QObject(),
        "session_service": DummySessionService(session_model),
        "profile_supervisor_service": DummyProfileSupervisorService(),
        "update_service": DummyUpdateService(),
        "update_bridge": DummyUpdateBridge(),
        "diagnostics_service": overrides.get("diagnostics_service") or QObject(),
        "cron_service": overrides.get("cron_service") or DummyCronService(),
        "heartbeat_service": overrides.get("heartbeat_service") or DummyHeartbeatService(),
        "desktop_preferences": overrides.get("desktop_preferences") or DummyDesktopPreferences(),
        "memory_service": overrides.get("memory_service") or QObject(),
        "skills_service": overrides.get("skills_service") or QObject(),
        "tools_service": overrides.get("tools_service") or QObject(),
    }
    return refs


def _initial_properties(refs: dict[str, object]) -> dict[str, object]:
    return {
        "chatService": refs["chat_service"],
        "configService": refs["config_service"],
        "profileService": refs["profile_service"],
        "sessionService": refs["session_service"],
        "profileSupervisorService": refs["profile_supervisor_service"],
        "cronService": refs["cron_service"],
        "heartbeatService": refs["heartbeat_service"],
        "memoryService": refs["memory_service"],
        "skillsService": refs["skills_service"],
        "toolsService": refs["tools_service"],
        "diagnosticsService": refs["diagnostics_service"],
        "desktopPreferences": refs["desktop_preferences"],
        "updateService": refs["update_service"],
        "updateBridge": refs["update_bridge"],
        "systemUiLanguage": "en",
    }

def _wait_for_diagnostics_log_tail_ready(root: QObject, scroll: QObject) -> None:
    settle_ms = max(40, int(root.property("motionUi") or 0) + 20)
    _process(settle_ms)
    _wait_until(lambda: not bool(scroll.property("scrollToEndQueued")))


def _scroll_max_y(item: QObject) -> float:
    origin_y = float(item.property("originY"))
    return max(
        origin_y,
        origin_y + float(item.property("contentHeight")) - float(item.property("height")),
    )


def _install_focus_filter(root: QObject) -> WindowFocusDismissFilter:
    focus_filter = WindowFocusDismissFilter(root)
    if hasattr(root, "installEventFilter"):
        root.installEventFilter(focus_filter)
    return focus_filter


def _remove_focus_filter(root: QObject, focus_filter: WindowFocusDismissFilter | None) -> None:
    if focus_filter is None:
        return
    if hasattr(root, "removeEventFilter"):
        root.removeEventFilter(focus_filter)


def _find_chat_input(root: QObject) -> QObject:
    for obj in root.findChildren(QObject):
        if obj.objectName() == "chatMessageInput":
            return obj
    raise AssertionError("chat composer TextArea not found")


def _find_toast(root: QObject) -> QObject:
    for obj in root.findChildren(QObject):
        try:
            if obj.objectName() == "globalToast":
                return obj
        except Exception:
            continue
    raise AssertionError("global toast not found")


def _load_main_window(*args: object, **overrides: object) -> tuple[QQmlApplicationEngine, QObject]:
    if args:
        overrides["config_service"] = args[0]
    refs = _build_main_window_refs(**overrides)
    engine = QQmlApplicationEngine()
    engine._test_refs = refs
    engine.setInitialProperties(_initial_properties(refs))
    engine.load(QUrl.fromLocalFile(str(MAIN_QML_PATH)))
    root_objects = engine.rootObjects()
    assert root_objects
    root = root_objects[0]
    if hasattr(root, "requestActivate"):
        root.requestActivate()
    for _ in range(5):
        _process(30)
    return engine, root


def _load_light_main_window(*args: object, **overrides: object) -> tuple[QQmlApplicationEngine, QObject]:
    if args:
        overrides["config_service"] = args[0]
    return _load_main_window(
        **overrides,
        desktop_preferences=DummyDesktopPreferences(theme_mode="light", is_dark=False),
    )

__all__ = [name for name in globals() if name != "__all__" and not (name.startswith("__") and name.endswith("__"))]
