from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, cast

from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor, QGuiApplication, QIcon
from PySide6.QtQuick import QQuickWindow


@dataclass(frozen=True)
class WindowLaunchOptions:
    start_view: str
    width: int | None = None
    height: int | None = None


@dataclass(frozen=True)
class SmokeRunOptions:
    seed_messages: bool = False
    smoke: bool = False
    smoke_theme_toggle: bool = False
    smoke_screenshot: str | None = None


def configure_root(root: object, context: object, logo_icon: QIcon | None) -> None:
    from app import main as main_module

    if logo_icon and isinstance(root, QQuickWindow):
        root.setIcon(logo_icon)
    if isinstance(root, QQuickWindow):
        context.app._desktop_tray_controller = main_module.create_desktop_tray_controller(  # type: ignore[attr-defined]
            app=context.app,
            window=root,
            preferences=context.desktop_preferences,
        )
    _ = context.profile_supervisor_service.profileNavigationRequested.connect(
        lambda section: (root.setProperty("startView", "chat"), root.setProperty("activeWorkspace", section))
    )
    _ = root.setProperty("useNativeTitleBar", True)
    if not isinstance(root, QQuickWindow):
        return
    focus_filter = main_module.WindowFocusDismissFilter(root)
    app_instance = QGuiApplication.instance()
    if isinstance(app_instance, QGuiApplication):
        main_module.install_pointer_refresh_hooks(app_instance, root, focus_filter)
    root.installEventFilter(focus_filter)
    if sys.platform != "win32":
        return
    caption_color = main_module.to_qcolor(cast(object, root.property("bgBase")), QColor("#0C0C14"))
    text_color = main_module.to_qcolor(cast(object, root.property("textPrimary")), QColor("#E8E8F0"))
    QTimer.singleShot(
        0,
        lambda: (
            main_module.apply_windows_rounded_corners(root),
            main_module.apply_windows_titlebar_colors(root, caption_color, text_color),
        ),
    )


def apply_startup_options(root: object, options: WindowLaunchOptions) -> None:
    _ = root.setProperty("startView", options.start_view)
    if options.width is not None:
        _ = root.setProperty(
            "width",
            max(options.width, int(cast(object, root.property("minimumWidth")) or 0)),
        )
    if options.height is not None:
        _ = root.setProperty(
            "height",
            max(options.height, int(cast(object, root.property("minimumHeight")) or 0)),
        )


def schedule_deferred_startup(context: object, smoke_mode: bool) -> None:
    def run() -> None:
        context.app._profile_coordinator.refresh_from_config()  # type: ignore[attr-defined]
        if not smoke_mode:
            context.update_service.reloadConfig()
        context.diagnostics_service.refresh()

    QTimer.singleShot(16, run)


def seed_or_smoke(root: object, context: object, options: SmokeRunOptions) -> None:
    messages_model = context.messages_model
    if options.seed_messages:
        _ = messages_model.append_user("Hello, what can you do?")
        _ = messages_model.append_assistant("I can help with code, writing, analysis, and more!", status="done")
    if options.smoke_screenshot:
        out = Path(options.smoke_screenshot).expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)

        def snap() -> None:
            if isinstance(root, QQuickWindow):
                ok = root.grabWindow().save(str(out))
                if not ok:
                    print(f"Smoke screenshot save failed: {out}", file=sys.stderr)
            context.app.quit()

        QTimer.singleShot(1500, snap)
        return
    if options.smoke_theme_toggle:
        QTimer.singleShot(100, cast(Callable[[], None], context.desktop_preferences.toggleTheme))
        QTimer.singleShot(500, context.app.quit)
        return
    if options.smoke:
        QTimer.singleShot(500, context.app.quit)
