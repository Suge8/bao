from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QEvent, QObject, Slot
from PySide6.QtGui import QAction
from PySide6.QtQuick import QQuickWindow
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon
from typing_extensions import override


@dataclass(frozen=True)
class HideOnCloseOptions:
    should_hide_on_close: Callable[[], bool]
    on_hide_requested: Callable[[], None]
    on_visibility_changed: Callable[[], None] | None = None


class HideOnCloseEventFilter(QObject):
    def __init__(
        self,
        window: QQuickWindow,
        options: HideOnCloseOptions | None = None,
        **legacy: object,
    ) -> None:
        super().__init__(window)
        if options is None:
            options = HideOnCloseOptions(
                should_hide_on_close=legacy.pop("should_hide_on_close"),  # type: ignore[arg-type]
                on_hide_requested=legacy.pop("on_hide_requested"),  # type: ignore[arg-type]
                on_visibility_changed=legacy.pop("on_visibility_changed", None),  # type: ignore[arg-type]
            )
        self._window = window
        self._options = options

    @override
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        window = getattr(self, "_window", None)
        options = getattr(self, "_options", None)
        if watched is not window or options is None:
            return False
        if event.type() == QEvent.Type.Close and options.should_hide_on_close():
            ignore = getattr(event, "ignore", None)
            if callable(ignore):
                ignore()
            options.on_hide_requested()
            return True
        if (
            options.on_visibility_changed is not None
            and event.type() in {QEvent.Type.Show, QEvent.Type.Hide}
        ):
            options.on_visibility_changed()
        return False


@dataclass(frozen=True)
class DesktopTrayControllerOptions:
    app: QApplication
    window: QQuickWindow
    tray_icon: QSystemTrayIcon
    preferences: QObject
    icon_path: Path
    translate: Callable[[str, str, QObject], str]
    load_icon: Callable[[Path, bool], object | None]


class DesktopTrayController(QObject):
    def __init__(self, options: DesktopTrayControllerOptions, parent: QObject | None = None) -> None:
        super().__init__(parent or options.app)
        self._app = options.app
        self._window = options.window
        self._tray_icon = options.tray_icon
        self._preferences = options.preferences
        self._icon_path = options.icon_path
        self._translate = options.translate
        self._load_icon = options.load_icon
        self._quitting = False
        self._toggle_action = QAction(self)
        self._quit_action = QAction(self)
        self._menu = QMenu()
        self._menu.addAction(self._toggle_action)
        self._menu.addSeparator()
        self._menu.addAction(self._quit_action)
        self._toggle_action.triggered.connect(self.toggle_window_visibility)
        self._quit_action.triggered.connect(self.request_quit)
        self._tray_icon.activated.connect(self._on_tray_activated)
        self._tray_icon.setContextMenu(self._menu)
        self._tray_icon.setToolTip("Bao")
        self._app.aboutToQuit.connect(self._prepare_to_quit)
        self._close_filter = HideOnCloseEventFilter(
            self._window,
            HideOnCloseOptions(
                should_hide_on_close=self.should_hide_on_close,
                on_hide_requested=self.hide_window,
                on_visibility_changed=self.refresh_menu_labels,
            ),
        )
        self._window.installEventFilter(self._close_filter)
        self._connect_preference_signals()
        self.refresh_icon()
        self.refresh_menu_labels()
        self._tray_icon.show()

    def should_hide_on_close(self) -> bool:
        return not self._quitting and self._tray_icon.isVisible()

    def _connect_preference_signals(self) -> None:
        for signal_name, slot in (
            ("effectiveLanguageChanged", self.refresh_menu_labels),
            ("isDarkChanged", self.refresh_icon),
        ):
            signal = getattr(self._preferences, signal_name, None)
            if signal is not None:
                _ = signal.connect(slot)

    def _is_dark(self) -> bool:
        return bool(self._preferences.property("isDark"))

    def _tr(self, zh: str, en: str) -> str:
        return self._translate(zh, en, self._preferences)

    @Slot()
    def refresh_menu_labels(self) -> None:
        self._toggle_action.setText(
            self._tr("显示 Bao", "Show Bao")
            if not self._window.isVisible()
            else self._tr("隐藏 Bao", "Hide Bao")
        )
        self._quit_action.setText(self._tr("退出 Bao", "Quit Bao"))

    @Slot()
    def refresh_icon(self) -> None:
        icon = self._load_icon(self._icon_path, self._is_dark())
        if icon is not None:
            self._tray_icon.setIcon(icon)

    @Slot()
    def restore_window(self) -> None:
        if self._quitting:
            return
        self._window.show()
        self._window.raise_()
        self._window.requestActivate()
        self.refresh_menu_labels()

    @Slot()
    def hide_window(self) -> None:
        if self._quitting:
            return
        self._window.hide()
        self.refresh_menu_labels()

    @Slot()
    def toggle_window_visibility(self) -> None:
        if self._window.isVisible():
            self.hide_window()
            return
        self.restore_window()

    @Slot()
    def request_quit(self) -> None:
        if self._quitting:
            return
        self._prepare_to_quit()
        self._app.quit()

    @Slot()
    def _prepare_to_quit(self) -> None:
        if self._quitting:
            return
        self._quitting = True
        self._tray_icon.hide()

    @Slot(QSystemTrayIcon.ActivationReason)
    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self.toggle_window_visibility()
