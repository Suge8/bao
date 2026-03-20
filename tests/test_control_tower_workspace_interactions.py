# ruff: noqa: F403, F405
from __future__ import annotations

from pathlib import Path

from tests._control_tower_workspace_qml_testkit import *


def test_control_tower_profile_button_click_does_not_select_card(qapp, tmp_path: Path):
    _ = qapp
    qml_path = tmp_path / "ControlTowerWorkspaceClickHarness.qml"
    qml_path.write_text(
        _build_wrapper(
            selected_profile_qml="({})",
            expected_title="指挥舱",
        ),
        encoding="utf-8",
    )

    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    view.setColor(QtGui.QColor("#FFFDF9"))
    view.setSource(QUrl.fromLocalFile(str(qml_path)))
    assert view.status() == QQuickView.Ready, view.errors()
    view.show()
    _process(100)

    root = view.rootObject()
    assert root is not None

    supervisor = root.findChild(QtCore.QObject, "supervisorHarness")
    assert supervisor is not None
    button = None
    queue = [root] if isinstance(root, QQuickItem) else []
    while queue and button is None:
        current = queue.pop(0)
        if str(current.property("text") or "") == "切换":
            button = current
            break
        queue.extend(current.childItems())
    assert isinstance(button, QQuickItem)

    center = button.mapToScene(QPointF(button.width() / 2.0, button.height() / 2.0)).toPoint()
    QTest.mouseClick(view, Qt.LeftButton, Qt.NoModifier, QPoint(center.x(), center.y()))
    _process(50)

    assert int(supervisor.property("activateCalls")) == 1
    assert int(supervisor.property("selectCalls")) == 0

    view.close()


def test_segmented_tabs_render_selected_highlight_on_first_paint(qapp):
    _ = qapp
    engine = QQmlEngine()
    component = QQmlComponent(engine)
    component.setData(
        _build_segmented_tabs_wrapper().encode("utf-8"),
        QUrl("inline:SegmentedTabsHarness.qml"),
    )

    _wait_until_ready(component)

    assert component.status() == QQmlComponent.Ready, component.errors()
    root = component.create()
    assert root is not None, component.errors()

    try:
        _process(50)
        highlight = root.findChild(QtCore.QObject, "segmentedTabsHighlight")
        assert highlight is not None
        assert float(highlight.property("width")) > 0
        assert float(highlight.property("height")) > 0
    finally:
        root.deleteLater()
        _process(0)


def test_segmented_tabs_hide_highlight_when_current_value_is_unmatched(qapp):
    _ = qapp
    engine = QQmlEngine()
    component = QQmlComponent(engine)
    component.setData(
        _build_segmented_tabs_wrapper("missing").encode("utf-8"),
        QUrl("inline:SegmentedTabsMissingHarness.qml"),
    )

    _wait_until_ready(component)

    assert component.status() == QQmlComponent.Ready, component.errors()
    root = component.create()
    assert root is not None, component.errors()

    try:
        _process(50)
        highlight = root.findChild(QtCore.QObject, "segmentedTabsHighlight")
        assert highlight is not None
        assert bool(highlight.property("visible")) is False
        assert float(highlight.property("width")) == 0.0
    finally:
        root.deleteLater()
        _process(0)


def test_workspace_split_handle_marker_column_fits_small_height(qapp):
    _ = qapp
    engine = QQmlEngine()
    component = QQmlComponent(engine)
    component.setData(
        _build_split_handle_wrapper(28).encode("utf-8"),
        QUrl("inline:WorkspaceSplitHandleHarness.qml"),
    )

    _wait_until_ready(component)

    assert component.status() == QQmlComponent.Ready, component.errors()
    root = component.create()
    assert root is not None, component.errors()

    try:
        _process(50)
        handle = root.findChild(QtCore.QObject, "workspaceSplitHandle")
        column = root.findChild(QtCore.QObject, "workspaceSplitHandleMarkerColumn")
        assert handle is not None
        assert column is not None
        assert int(handle.property("markerCount")) >= 1
        assert float(column.property("implicitHeight")) <= float(handle.property("height"))
    finally:
        root.deleteLater()
        _process(0)
