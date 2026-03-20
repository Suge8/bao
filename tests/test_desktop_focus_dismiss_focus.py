# ruff: noqa: E402, N802

from __future__ import annotations

import importlib

pytest = importlib.import_module("pytest")
pytest_plugins = ("tests._desktop_focus_dismiss_shared",)

from app.main import WindowFocusDismissFilter  # noqa: E402
from tests._desktop_focus_dismiss_qml import (  # noqa: E402
    _build_editor_and_button_window,
    _build_editor_and_expand_header_window,
    _build_editor_and_mouse_area_window,
    _build_two_editor_window,
    _build_window,
)
from tests._desktop_focus_dismiss_shared import (  # noqa: E402
    QObject,
    QPoint,
    QPointF,
    QQmlComponent,
    Qt,
    QTest,
    _install_focus_filter,
    _process,
    _remove_focus_filter,
    _wait_until_ready,
)


def _create_root(qml_data: bytes, source: str):
    engine = pytest.importorskip("PySide6.QtQml").QQmlEngine()
    component = pytest.importorskip("PySide6.QtQml").QQmlComponent(engine)
    component.setData(qml_data, pytest.importorskip("PySide6.QtCore").QUrl(source))
    _wait_until_ready(component)
    assert component.status() == QQmlComponent.Ready, component.errors()
    root = component.create()
    assert root is not None, component.errors()
    return engine, component, root


def test_window_focus_dismiss_blurs_editor_on_external_click(qapp):
    _ = qapp
    _engine, _component, root = _create_root(_build_window(), "inline:FocusDismissHarness.qml")

    try:
        editor = root.findChild(QObject, "editor")
        assert editor is not None

        editor.forceActiveFocus()
        _process(30)
        assert bool(editor.property("activeFocus")) is True

        focus_filter = WindowFocusDismissFilter(root)
        focus_filter.eventFilter(
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

        assert bool(editor.property("activeFocus")) is False
    finally:
        root.deleteLater()
        _process(0)


def test_window_focus_dismiss_keeps_editor_focus_on_internal_click(qapp):
    _ = qapp
    _engine, _component, root = _create_root(_build_window(), "inline:FocusDismissHarness.qml")

    try:
        editor = root.findChild(QObject, "editor")
        assert editor is not None

        editor.forceActiveFocus()
        _process(30)
        assert bool(editor.property("activeFocus")) is True

        focus_filter = WindowFocusDismissFilter(root)
        focus_filter.eventFilter(
            root,
            pytest.importorskip("PySide6.QtGui").QMouseEvent(
                pytest.importorskip("PySide6.QtCore").QEvent.Type.MouseButtonRelease,
                QPointF(80, 70),
                QPointF(80, 70),
                QPointF(80, 70),
                Qt.LeftButton,
                Qt.LeftButton,
                Qt.NoModifier,
            ),
        )
        _process(0)

        assert bool(editor.property("activeFocus")) is True
    finally:
        root.deleteLater()
        _process(0)


def test_window_focus_dismiss_preserves_single_click_editor_to_editor_focus_transfer(qapp):
    _ = qapp
    _engine, _component, root = _create_root(
        _build_two_editor_window(), "inline:TwoEditorFocusHarness.qml"
    )
    focus_filter = _install_focus_filter(root, WindowFocusDismissFilter)

    try:
        editor_a = root.findChild(QObject, "editorA")
        editor_b = root.findChild(QObject, "editorB")
        assert editor_a is not None
        assert editor_b is not None

        editor_a.forceActiveFocus()
        _process(0)
        assert bool(editor_a.property("activeFocus")) is True
        assert bool(editor_b.property("activeFocus")) is False

        QTest.mouseClick(root, Qt.LeftButton, Qt.NoModifier, QPoint(260, 60))
        _process(0)

        assert bool(editor_a.property("activeFocus")) is False
        assert bool(editor_b.property("activeFocus")) is True
    finally:
        _remove_focus_filter(root, focus_filter)
        root.deleteLater()
        _process(0)


def test_window_focus_dismiss_clears_selection_when_clicking_focusable_non_editor(qapp):
    _ = qapp
    _engine, _component, root = _create_root(
        _build_editor_and_button_window(), "inline:EditorAndButtonHarness.qml"
    )
    focus_filter = _install_focus_filter(root, WindowFocusDismissFilter)

    try:
        editor = root.findChild(QObject, "editor")
        button = root.findChild(QObject, "button")
        assert editor is not None
        assert button is not None

        editor.forceActiveFocus()
        _process(0)
        editor.select(0, 5)
        _process(0)

        assert bool(editor.property("activeFocus")) is True
        assert str(editor.property("selectedText")) == "hello"

        QTest.mouseClick(root, Qt.LeftButton, Qt.NoModifier, QPoint(320, 60))
        _process(0)

        assert bool(editor.property("activeFocus")) is False
        assert str(editor.property("selectedText")) == ""
        assert bool(button.property("activeFocus")) is True
    finally:
        _remove_focus_filter(root, focus_filter)
        root.deleteLater()
        _process(0)


def test_window_focus_dismiss_preserves_single_click_mouse_area_action(qapp):
    _ = qapp
    _engine, _component, root = _create_root(
        _build_editor_and_mouse_area_window(), "inline:EditorAndMouseAreaHarness.qml"
    )
    focus_filter = _install_focus_filter(root, WindowFocusDismissFilter)

    try:
        editor = root.findChild(QObject, "editor")
        click_target = root.findChild(QObject, "clickTarget")
        assert editor is not None
        assert click_target is not None

        editor.forceActiveFocus()
        _process(30)
        assert bool(editor.property("activeFocus")) is True
        assert bool(root.property("clicked")) is False

        QTest.mouseClick(root, Qt.LeftButton, Qt.NoModifier, QPoint(360, 60))
        _process(30)

        assert bool(editor.property("activeFocus")) is False
        assert bool(root.property("clicked")) is True
    finally:
        _remove_focus_filter(root, focus_filter)
        root.deleteLater()
        _process(0)


def test_window_focus_dismiss_preserves_single_click_expand_header_action(qapp):
    _ = qapp
    _engine, _component, root = _create_root(
        _build_editor_and_expand_header_window(), "inline:EditorAndExpandHeaderHarness.qml"
    )
    focus_filter = _install_focus_filter(root, WindowFocusDismissFilter)

    try:
        editor = root.findChild(QObject, "editor")
        header = root.findChild(QObject, "expandHeader")
        assert editor is not None
        assert header is not None

        root.requestActivate()
        _process(30)
        editor.forceActiveFocus()
        _process(30)
        assert bool(editor.property("activeFocus")) is True
        assert bool(root.property("expanded")) is False

        header_center = header.mapToScene(
            QPointF(header.property("width") / 2, header.property("height") / 2)
        )
        QTest.mouseClick(
            root,
            Qt.LeftButton,
            Qt.NoModifier,
            QPoint(int(header_center.x()), int(header_center.y())),
        )
        _process(30)

        assert bool(editor.property("activeFocus")) is False
        assert bool(root.property("expanded")) is True
    finally:
        _remove_focus_filter(root, focus_filter)
        root.deleteLater()
        _process(0)
