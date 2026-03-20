# ruff: noqa: E402, N802

from __future__ import annotations

import importlib
from pathlib import Path
from typing import cast

pytest = importlib.import_module("pytest")
pytest_plugins = ("tests._desktop_focus_dismiss_shared",)

from app.main import (  # noqa: E402
    BUNDLED_APP_FONT_FAMILY_PREFIX,
    WindowFocusDismissFilter,
    refresh_pointer_if_window_active,
    resolve_app_font_family,
)
from tests._desktop_focus_dismiss_qml import _build_window  # noqa: E402
from tests._desktop_focus_dismiss_shared import (  # noqa: E402
    QCoreApplication,
    QPointF,
    QQmlComponent,
    QQmlEngine,
    QQuickWindow,
    Qt,
    _MouseMoveRecorder,
    _process,
    _wait_until_ready,
)


def test_window_focus_dismiss_posts_pointer_refresh_after_mouse_release(qapp):
    _ = qapp
    engine = QQmlEngine()
    component = QQmlComponent(engine)
    component.setData(
        _build_window(), pytest.importorskip("PySide6.QtCore").QUrl("inline:FocusDismissHarness.qml")
    )
    _wait_until_ready(component)

    assert component.status() == QQmlComponent.Ready, component.errors()
    root = component.create()
    assert root is not None, component.errors()
    recorder: _MouseMoveRecorder | None = None

    try:
        recorder = _MouseMoveRecorder()
        root.installEventFilter(recorder)

        focus_filter = WindowFocusDismissFilter(root)
        focus_filter._post_pointer_refresh(  # type: ignore[attr-defined]
            root,
            pytest.importorskip("PySide6.QtGui").QMouseEvent(
                pytest.importorskip("PySide6.QtCore").QEvent.Type.MouseButtonRelease,
                QPointF(10, 10),
                QPointF(10, 10),
                QPointF(10, 10),
                Qt.LeftButton,
                Qt.LeftButton,
                Qt.NoModifier,
            ),
        )
        _process(10)
        QCoreApplication.sendPostedEvents(
            root, pytest.importorskip("PySide6.QtCore").QEvent.Type.MouseMove
        )
        _process(10)

        assert recorder.moves >= 1
    finally:
        if recorder is not None:
            root.removeEventFilter(recorder)
        root.deleteLater()
        _process(0)


def test_refresh_pointer_if_window_active_posts_mouse_move(qapp):
    _ = qapp

    class _FakeApp:
        def applicationState(self):
            return Qt.ApplicationState.ApplicationActive

    class _FakeWindow:
        def isVisible(self):
            return True

    class _FakeFilter:
        def __init__(self) -> None:
            self.calls: list[object] = []

        def _post_pointer_refresh(self, window):
            self.calls.append(window)

    window = _FakeWindow()
    focus_filter = _FakeFilter()

    refresh_pointer_if_window_active(
        cast(object, _FakeApp()),
        cast(QQuickWindow, window),
        cast(WindowFocusDismissFilter, cast(object, focus_filter)),
    )

    assert focus_filter.calls == [window]


def test_resolve_app_font_family_prefers_bundled_font(qapp):
    _ = qapp
    family = resolve_app_font_family()

    assert family is not None
    assert family.startswith(BUNDLED_APP_FONT_FAMILY_PREFIX)


def test_resolve_app_font_family_falls_back_when_bundled_font_missing(qapp, monkeypatch):
    _ = qapp
    monkeypatch.setattr("app.main.resolve_bundled_app_font_path", lambda: None)
    monkeypatch.setattr("app.main.preferred_system_font_family", lambda: "Segoe UI")

    assert resolve_app_font_family() == "Segoe UI"


def test_resolve_app_font_family_falls_back_when_font_registration_fails(qapp, monkeypatch):
    _ = qapp
    monkeypatch.setattr("app.main.resolve_bundled_app_font_path", lambda: Path("/tmp/OPPO Sans.ttf"))
    monkeypatch.setattr("app.main.QFontDatabase.addApplicationFont", lambda _path: -1)
    monkeypatch.setattr("app.main.preferred_system_font_family", lambda: "Segoe UI")

    assert resolve_app_font_family() == "Segoe UI"


def test_resolve_app_font_family_falls_back_when_registered_font_has_no_family(qapp, monkeypatch):
    _ = qapp
    monkeypatch.setattr("app.main.resolve_bundled_app_font_path", lambda: Path("/tmp/OPPO Sans.ttf"))
    monkeypatch.setattr("app.main.QFontDatabase.addApplicationFont", lambda _path: 1)
    monkeypatch.setattr("app.main.QFontDatabase.applicationFontFamilies", lambda _font_id: [])
    monkeypatch.setattr("app.main.preferred_system_font_family", lambda: "Segoe UI")

    assert resolve_app_font_family() == "Segoe UI"


def test_qml_control_inherits_application_font(qapp):
    family = resolve_app_font_family()
    assert family is not None

    original_font = qapp.font()
    qapp.setFont(pytest.importorskip("PySide6.QtGui").QFont(family))
    engine = QQmlEngine()
    component = QQmlComponent(engine)
    component.setData(
        b"import QtQuick 2.15\nimport QtQuick.Controls 2.15\nControl { property string familyName: font.family }",
        pytest.importorskip("PySide6.QtCore").QUrl("inline:FontHarness.qml"),
    )
    _wait_until_ready(component)

    assert component.status() == QQmlComponent.Ready, component.errors()
    root = component.create()
    assert root is not None, component.errors()

    try:
        assert str(root.property("familyName")) == family
    finally:
        qapp.setFont(original_font)
        root.deleteLater()
        _process(0)
