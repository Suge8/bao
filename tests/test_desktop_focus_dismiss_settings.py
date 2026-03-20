# ruff: noqa: E402, N802

from __future__ import annotations

import importlib

pytest = importlib.import_module("pytest")
pytest_plugins = ("tests._desktop_focus_dismiss_shared",)

from app.main import WindowFocusDismissFilter  # noqa: E402
from tests._desktop_focus_dismiss_qml import (  # noqa: E402
    _build_settings_select_and_mouse_area_window,
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


def test_settings_select_popup_closes_without_eating_target_click(qapp):
    _ = qapp
    engine = pytest.importorskip("PySide6.QtQml").QQmlEngine()
    component = pytest.importorskip("PySide6.QtQml").QQmlComponent(engine)
    component.setData(
        _build_settings_select_and_mouse_area_window(),
        pytest.importorskip("PySide6.QtCore").QUrl("inline:SettingsSelectAndMouseAreaHarness.qml"),
    )
    _wait_until_ready(component)

    assert component.status() == QQmlComponent.Ready, component.errors()
    root = component.create()
    assert root is not None, component.errors()
    focus_filter = _install_focus_filter(root, WindowFocusDismissFilter)

    try:
        root.requestActivate()
        _process(30)
        settings_select = root.findChild(QObject, "settingsSelect")
        hit_target = root.findChild(QObject, "hitTarget")
        assert settings_select is not None
        assert hit_target is not None

        select_hit_area = settings_select.findChild(QObject, "settingsSelectHitArea")
        assert select_hit_area is not None

        select_center = select_hit_area.mapToScene(
            QPointF(
                select_hit_area.property("width") / 2,
                select_hit_area.property("height") / 2,
            )
        )
        QTest.mouseClick(
            root,
            Qt.LeftButton,
            Qt.NoModifier,
            QPoint(int(select_center.x()), int(select_center.y())),
        )
        _process(100)

        assert bool(settings_select.property("popupOpen")) is True
        assert bool(root.property("clicked")) is False

        hit_center = hit_target.mapToScene(
            QPointF(hit_target.property("width") / 2, hit_target.property("height") / 2)
        )
        QTest.mouseClick(
            root,
            Qt.LeftButton,
            Qt.NoModifier,
            QPoint(int(hit_center.x()), int(hit_center.y())),
        )
        _process(100)

        assert bool(settings_select.property("popupOpen")) is False
        assert bool(root.property("clicked")) is True
    finally:
        _remove_focus_filter(root, focus_filter)
        root.deleteLater()
        _process(0)
