from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QResource, QUrl
from PySide6.QtGui import QFontDatabase
from PySide6.QtQuick import QQuickWindow
from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from app._main_focus import (
    WindowFocusDismissFilter,
    install_pointer_refresh_hooks,
    refresh_pointer_if_window_active,
)
from app._main_icons import (
    apply_windows_rounded_corners,
    apply_windows_titlebar_colors,
    build_monochrome_tray_icon,
    configure_qt_style,
    load_app_icon,
    load_tray_icon,
    to_qcolor,
)
from app._main_paths import (
    BUNDLED_APP_FONT_FAMILY_PREFIX,
    BUNDLED_APP_FONT_FILENAME,
    DEFAULT_APP_ICON_RELATIVE_PATHS,
    QML_RCC_RELATIVE_PATHS,
    QML_RESOURCE_MAIN_URL,
    TRAY_APP_ICON_RELATIVE_PATHS,
    WINDOWS_APP_ICON_FALLBACK_RELATIVE_PATHS,
    WINDOWS_APP_ICON_RELATIVE_PATHS,
    preferred_system_font_family,
)
from app._main_paths import (
    resolve_app_icon_path as _resolve_app_icon_path_impl,
)
from app._main_paths import (
    resolve_app_resource_path as _resolve_app_resource_path_impl,
)
from app._main_paths import (
    resolve_bundled_app_font_path as _resolve_bundled_app_font_path_impl,
)
from app._main_paths import (
    resolve_qml_path as _resolve_qml_path_impl,
)
from app._main_paths import (
    resolve_tray_icon_path as _resolve_tray_icon_path_impl,
)
from app._main_runtime import run_desktop_app
from app._main_single_instance import (
    DesktopSingleInstanceServer,
    acquire_single_instance_lock,
    activate_window,
    activated_existing_instance_notice,
    existing_instance_unresponsive_notice,
    request_existing_instance_activation,
    single_instance_enabled,
    single_instance_lock_path,
    single_instance_server_name,
)
from app._main_tray import (
    DesktopTrayController,
    DesktopTrayControllerOptions,
    HideOnCloseEventFilter,
)
from app._main_utils import (
    bind_exported_config,
    configured_hub_channels,
    connect_on_config_change,
    detect_system_ui_language,
    effective_desktop_language,
    is_smoke_run,
    parse_args,
    shutdown_desktop_services,
)

_REGISTERED_QML_BUNDLE: str | None = None


def resolve_qml_path(qml_arg: str | None) -> Path:
    return _resolve_qml_path_impl(qml_arg, current_file=__file__, sys_module=sys)


def resolve_app_resource_path(*relative_paths: str) -> Path | None:
    return _resolve_app_resource_path_impl(*relative_paths, current_file=__file__, sys_module=sys)


def resolve_app_icon_path() -> Path | None:
    return _resolve_app_icon_path_impl(resolver=resolve_app_resource_path, sys_platform=sys.platform)


def resolve_tray_icon_path() -> Path | None:
    return _resolve_tray_icon_path_impl(
        resolver=resolve_app_resource_path,
        app_icon_fn=resolve_app_icon_path,
    )


def resolve_bundled_app_font_path() -> Path | None:
    return _resolve_bundled_app_font_path_impl(resolver=resolve_app_resource_path)


def register_qml_resource_bundle() -> bool:
    global _REGISTERED_QML_BUNDLE
    if _REGISTERED_QML_BUNDLE is not None:
        return True
    bundle_path = resolve_app_resource_path(*QML_RCC_RELATIVE_PATHS)
    if bundle_path is None or not QResource.registerResource(str(bundle_path)):
        return False
    _REGISTERED_QML_BUNDLE = str(bundle_path)
    return True


def resolve_qml_url(qml_arg: str | None) -> QUrl:
    if qml_arg:
        return QUrl.fromLocalFile(str(resolve_qml_path(qml_arg)))
    if register_qml_resource_bundle():
        return QUrl(QML_RESOURCE_MAIN_URL)
    if getattr(sys, "frozen", False):
        return QUrl()
    return QUrl.fromLocalFile(str(resolve_qml_path(None)))


def resolve_app_font_family() -> str | None:
    font_path = resolve_bundled_app_font_path()
    if font_path is not None:
        font_id = QFontDatabase.addApplicationFont(str(font_path))
        if font_id != -1:
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                return families[0]
    return preferred_system_font_family()


def create_desktop_tray_controller(
    *, app: QApplication, window: QQuickWindow, preferences: object
) -> DesktopTrayController | None:
    if not QSystemTrayIcon.isSystemTrayAvailable():
        return None
    tray_icon_path = resolve_tray_icon_path()
    if tray_icon_path is None:
        return None
    tray_icon = load_tray_icon(tray_icon_path, dark_mode=bool(preferences.property("isDark")))
    if tray_icon is None:
        return None
    app.setQuitOnLastWindowClosed(False)
    return DesktopTrayController(
        DesktopTrayControllerOptions(
            app=app,
            window=window,
            tray_icon=QSystemTrayIcon(tray_icon, app),
            preferences=preferences,
            icon_path=tray_icon_path,
            translate=lambda zh, en, prefs: zh if effective_desktop_language(prefs) == "zh" else en,
            load_icon=lambda path, dark: load_tray_icon(path, dark_mode=dark),
        )
    )


def main() -> int:
    return run_desktop_app()


__all__ = [
    "DesktopTrayController",
    "BUNDLED_APP_FONT_FAMILY_PREFIX",
    "BUNDLED_APP_FONT_FILENAME",
    "DEFAULT_APP_ICON_RELATIVE_PATHS",
    "HideOnCloseEventFilter",
    "TRAY_APP_ICON_RELATIVE_PATHS",
    "WINDOWS_APP_ICON_FALLBACK_RELATIVE_PATHS",
    "WINDOWS_APP_ICON_RELATIVE_PATHS",
    "WindowFocusDismissFilter",
    "apply_windows_rounded_corners",
    "apply_windows_titlebar_colors",
    "bind_exported_config",
    "build_monochrome_tray_icon",
    "configure_qt_style",
    "configured_hub_channels",
    "connect_on_config_change",
    "create_desktop_tray_controller",
    "detect_system_ui_language",
    "effective_desktop_language",
    "activate_window",
    "acquire_single_instance_lock",
    "activated_existing_instance_notice",
    "install_pointer_refresh_hooks",
    "is_smoke_run",
    "existing_instance_unresponsive_notice",
    "load_app_icon",
    "load_tray_icon",
    "main",
    "parse_args",
    "preferred_system_font_family",
    "request_existing_instance_activation",
    "refresh_pointer_if_window_active",
    "register_qml_resource_bundle",
    "resolve_app_font_family",
    "resolve_app_icon_path",
    "resolve_app_resource_path",
    "resolve_bundled_app_font_path",
    "resolve_qml_path",
    "resolve_qml_url",
    "resolve_tray_icon_path",
    "shutdown_desktop_services",
    "single_instance_enabled",
    "single_instance_lock_path",
    "single_instance_server_name",
    "DesktopSingleInstanceServer",
    "to_qcolor",
]


if __name__ == "__main__":
    raise SystemExit(main())
