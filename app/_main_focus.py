from __future__ import annotations

from typing import cast

from PySide6.QtCore import QCoreApplication, QEvent, QObject, QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QCursor, QGuiApplication, QMouseEvent
from PySide6.QtQml import QQmlProperty
from PySide6.QtQuick import QQuickWindow
from typing_extensions import override

CLICK_AWAY_EDITOR_PROP = "baoClickAwayEditor"


def iter_object_ancestors(obj: QObject | None):
    seen: set[int] = set()
    current = obj
    while current is not None:
        identity = id(current)
        if identity in seen:
            return
        seen.add(identity)
        yield current
        parent_item = getattr(current, "parentItem", None)
        if callable(parent_item):
            item_owner = parent_item()
            if isinstance(item_owner, QObject) and item_owner is not current:
                current = item_owner
                continue
        parent = current.parent()
        current = parent if isinstance(parent, QObject) else None


def is_click_away_editor(obj: QObject | None) -> bool:
    if obj is None:
        return False
    try:
        return bool(obj.property(CLICK_AWAY_EDITOR_PROP))
    except RuntimeError:
        return False


def find_click_away_editor(obj: QObject | None) -> QObject | None:
    for current in iter_object_ancestors(obj):
        if is_click_away_editor(current):
            return current
    return None


class WindowFocusDismissFilter(QObject):
    def refresh_pointer_if_window_active(self) -> None:
        app = QGuiApplication.instance()
        window = self.parent()
        if not isinstance(app, QGuiApplication) or not isinstance(window, QQuickWindow):
            return
        refresh_pointer_if_window_active(app, window, self)

    def on_application_state_changed(self, state: Qt.ApplicationState) -> None:
        if state == Qt.ApplicationState.ApplicationActive:
            self.refresh_pointer_if_window_active()

    def _post_pointer_refresh(
        self, window: QQuickWindow, source_event: QMouseEvent | None = None
    ) -> None:
        if source_event is None:
            global_point = QCursor.pos()
            local_pos = QPointF(window.mapFromGlobal(global_point))
            global_pos = QPointF(global_point)
        else:
            local_pos = source_event.position()
            global_pos = source_event.globalPosition()
        if not QRectF(0.0, 0.0, float(window.width()), float(window.height())).contains(local_pos):
            return
        move_event = QMouseEvent(
            QEvent.Type.MouseMove,
            local_pos,
            global_pos,
            Qt.MouseButton.NoButton,
            QGuiApplication.mouseButtons(),
            QGuiApplication.keyboardModifiers(),
        )
        QCoreApplication.postEvent(window, move_event)

    def _resolve_focused_editor(self, window: QQuickWindow) -> tuple[QObject, object] | None:
        focus_control = cast(QObject | None, QQmlProperty.read(window, "activeFocusControl"))
        focus_item = cast(QObject | None, window.activeFocusItem())
        focus_owner = find_click_away_editor(focus_control) or find_click_away_editor(focus_item)
        if focus_owner is None:
            return None
        hit_test_target = focus_owner if hasattr(focus_owner, "mapFromScene") else focus_item
        if not hasattr(hit_test_target, "mapFromScene"):
            return None
        return focus_owner, hit_test_target

    @staticmethod
    def _click_is_inside_editor(hit_test_target: object, event: QMouseEvent) -> bool:
        map_from_scene = getattr(hit_test_target, "mapFromScene", None)
        contains = getattr(hit_test_target, "contains", None)
        if not callable(map_from_scene) or not callable(contains):
            return False
        return bool(contains(map_from_scene(event.position())))

    @staticmethod
    def _clear_editor_focus(editor: QObject) -> None:
        deselect = getattr(editor, "deselect", None)
        if callable(deselect):
            try:
                _ = deselect()
            except Exception:
                pass
        _ = editor.setProperty("focus", False)

    def _defer_editor_blur(self, window: QQuickWindow, editor: QObject) -> None:
        def apply() -> None:
            try:
                if bool(editor.property("activeFocus")):
                    self._clear_editor_focus(editor)
                self._post_pointer_refresh(window)
            except RuntimeError:
                return

        QTimer.singleShot(0, apply)

    @override
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() != QEvent.Type.MouseButtonRelease:
            return False
        if not isinstance(watched, QQuickWindow) or not isinstance(event, QMouseEvent):
            return False
        resolved = self._resolve_focused_editor(watched)
        if resolved is None:
            self._post_pointer_refresh(watched, event)
            return False
        focus_owner, hit_test_target = resolved
        if not self._click_is_inside_editor(hit_test_target, event):
            self._defer_editor_blur(watched, focus_owner)
            return False
        self._post_pointer_refresh(watched, event)
        return False


def refresh_pointer_if_window_active(
    app: QGuiApplication, window: QQuickWindow, focus_filter: WindowFocusDismissFilter
) -> None:
    if app.applicationState() == Qt.ApplicationState.ApplicationActive and window.isVisible():
        focus_filter._post_pointer_refresh(window)


def install_pointer_refresh_hooks(
    app: QGuiApplication, window: QQuickWindow, focus_filter: WindowFocusDismissFilter
) -> None:
    _ = window
    QTimer.singleShot(0, focus_filter.refresh_pointer_if_window_active)
    _ = app.applicationStateChanged.connect(focus_filter.on_application_state_changed)
