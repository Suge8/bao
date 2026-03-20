# ruff: noqa: F403, F405
from __future__ import annotations

from pathlib import Path

from tests._control_tower_workspace_qml_testkit import *
from tests._desktop_ui_testkit_base import desktop_ui_smoke_output_dir


def _find_quick_item_by_object_name(root: QQuickItem, object_name: str) -> QQuickItem | None:
    queue = [root]
    while queue:
        current = queue.pop(0)
        if str(current.objectName()) == object_name:
            return current
        queue.extend(current.childItems())
    return None


def _save_control_tower_screenshot(view: QQuickView, name: str) -> Path:
    output_dir = desktop_ui_smoke_output_dir("bao-workspace-compact")
    output_path = output_dir / f"{name}.png"
    if output_path.exists():
        output_path.unlink()
    image = view.grabWindow()
    assert image.save(str(output_path)), f"failed to save screenshot: {output_path}"
    return output_path


def test_control_tower_overview_lanes_render_as_separate_panels(qapp, tmp_path: Path):
    _ = qapp
    qml_path = tmp_path / "ControlTowerWorkspaceLaneHarness.qml"
    qml_path.write_text(
        _build_wrapper(
            selected_profile_qml="({id: 'default', displayName: '日常'})",
            expected_title="日常",
        ),
        encoding="utf-8",
    )

    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    view.setColor(QtGui.QColor("#FFFDF9"))
    view.setWidth(1400)
    view.setHeight(920)
    view.setSource(QUrl.fromLocalFile(str(qml_path)))
    assert view.status() == QQuickView.Ready, view.errors()
    view.show()
    _process(120)

    root = view.rootObject()
    assert root is not None

    lane_names = {
        "controlTowerLane_working",
        "controlTowerLane_completed",
        "controlTowerLane_attention",
        "controlTowerLane_automation",
    }

    queue = [root] if isinstance(root, QQuickItem) else []
    lanes: list[QQuickItem] = []
    while queue:
        current = queue.pop(0)
        if str(current.objectName()) in lane_names:
            lanes.append(current)
        queue.extend(current.childItems())

    assert len(lanes) == 4

    for lane in lanes:
        assert float(lane.property("width")) > 0.0
        assert float(lane.property("height")) >= 180.0

    view.close()


def test_control_tower_overview_scrolls_when_content_exceeds_viewport(qapp, tmp_path: Path):
    _ = qapp
    qml_path = tmp_path / "ControlTowerWorkspaceScrollHarness.qml"
    qml_path.write_text(
        _build_wrapper(
            selected_profile_qml="({id: 'default', displayName: '日常'})",
            expected_title="日常",
        ),
        encoding="utf-8",
    )

    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    view.setColor(QtGui.QColor("#FFFDF9"))
    view.setWidth(900)
    view.setHeight(640)
    view.setSource(QUrl.fromLocalFile(str(qml_path)))
    assert view.status() == QQuickView.Ready, view.errors()
    view.show()
    _process(150)

    root = view.rootObject()
    assert root is not None

    overview_scroll = root.findChild(QtCore.QObject, "controlTowerOverviewScroll")
    assert isinstance(overview_scroll, QQuickItem)
    assert float(overview_scroll.property("contentHeight")) > float(overview_scroll.property("height"))

    assert overview_scroll.setProperty("contentY", 120.0)
    _process(30)
    assert float(overview_scroll.property("contentY")) > 0.0

    view.close()


def test_control_tower_compact_layout_stacks_profiles_and_wraps_metrics(qapp, tmp_path: Path):
    _ = qapp
    qml_path = tmp_path / "ControlTowerWorkspaceCompactHarness.qml"
    qml_path.write_text(
        _build_wrapper(
            selected_profile_qml="({id: 'default', displayName: '日常'})",
            expected_title="日常",
        ),
        encoding="utf-8",
    )

    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    view.setColor(QtGui.QColor("#FFFDF9"))
    view.setWidth(420)
    view.setHeight(760)
    view.setSource(QUrl.fromLocalFile(str(qml_path)))
    assert view.status() == QQuickView.Ready, view.errors()
    view.show()
    _process(180)

    root = view.rootObject()
    assert root is not None

    main_split = root.findChild(QtCore.QObject, "controlTowerMainSplit")
    profiles_pane = root.findChild(QtCore.QObject, "controlTowerProfilesPane")
    overview_scroll = root.findChild(QtCore.QObject, "controlTowerOverviewScroll")
    working_lane = _find_quick_item_by_object_name(root, "controlTowerLane_working")
    profiles_metric = _find_quick_item_by_object_name(root, "controlTowerHeroMetric_profiles")
    working_metric = _find_quick_item_by_object_name(root, "controlTowerHeroMetric_working")
    default_profile_card = _find_quick_item_by_object_name(root, "profileCard_default")
    default_profile_metrics = _find_quick_item_by_object_name(root, "profileMetrics_default")
    default_profile_meta = _find_quick_item_by_object_name(root, "profileMeta_default")
    default_children_chip = _find_quick_item_by_object_name(root, "controlTowerInfoChip_default_children")

    assert isinstance(main_split, QQuickItem)
    assert isinstance(profiles_pane, QQuickItem)
    assert isinstance(overview_scroll, QQuickItem)
    assert isinstance(working_lane, QQuickItem)
    assert isinstance(profiles_metric, QQuickItem)
    assert isinstance(working_metric, QQuickItem)
    assert isinstance(default_profile_card, QQuickItem)
    assert isinstance(default_profile_metrics, QQuickItem)
    assert isinstance(default_profile_meta, QQuickItem)
    assert isinstance(default_children_chip, QQuickItem)

    assert main_split.property("orientation") == Qt.Vertical
    assert float(profiles_pane.property("width")) > 300.0
    assert float(overview_scroll.property("width")) > 300.0
    assert float(overview_scroll.property("height")) >= 220.0
    assert float(working_lane.property("width")) > 280.0
    assert float(working_metric.property("y")) > float(profiles_metric.property("y"))
    assert float(default_profile_meta.property("y")) > float(default_profile_metrics.property("y"))
    assert float(default_children_chip.property("width")) <= float(default_profile_card.property("width")) - 32.0
    assert float(default_profile_meta.property("y")) + float(default_profile_meta.property("height")) <= (
        float(default_profile_card.property("height")) - 12.0
    )
    screenshot_path = _save_control_tower_screenshot(view, "control-tower-hero-compact")
    assert screenshot_path.is_file()
    assert screenshot_path.stat().st_size > 0

    view.close()
