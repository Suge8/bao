from __future__ import annotations

import importlib
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

pytest = importlib.import_module("pytest")

QtCore = pytest.importorskip("PySide6.QtCore")
QtGui = pytest.importorskip("PySide6.QtGui")
QtQml = pytest.importorskip("PySide6.QtQml")
QtQuick = pytest.importorskip("PySide6.QtQuick")
QtQuickControls2 = pytest.importorskip("PySide6.QtQuickControls2")

QEventLoop = QtCore.QEventLoop
QObject = QtCore.QObject
QPoint = QtCore.QPoint
QPointF = QtCore.QPointF
QRect = QtCore.QRect
QTimer = QtCore.QTimer
QGuiApplication = QtGui.QGuiApplication
QImage = QtGui.QImage
QQmlComponent = QtQml.QQmlComponent
QQuickItem = QtQuick.QQuickItem
QQuickStyle = QtQuickControls2.QQuickStyle


@dataclass(frozen=True)
class DesktopSmokeIgnoreRegion:
    object_name: str
    padding: int = 0


@dataclass(frozen=True)
class DesktopSmokeRootCondition:
    property_name: str
    expected: object


@dataclass(frozen=True)
class DesktopSmokeObjectCondition:
    object_name: str
    visible: bool | None = None
    min_width: float | None = None
    min_height: float | None = None
    min_opacity: float | None = None
    min_scale: float | None = None


@dataclass(frozen=True)
class DesktopSmokeSceneContract:
    root_conditions: tuple[DesktopSmokeRootCondition, ...] = ()
    object_conditions: tuple[DesktopSmokeObjectCondition, ...] = ()
    settle_cycles: int = 10
    settle_ms: int = 40


SETTINGS_SCENE_CONTRACT = DesktopSmokeSceneContract(
    root_conditions=(DesktopSmokeRootCondition("showingSettings", True),),
    object_conditions=(
        DesktopSmokeObjectCondition("settingsView", visible=True),
        DesktopSmokeObjectCondition("settingsScroll", min_width=1, min_height=1),
    ),
)


CHAT_IDLE_SCENE_CONTRACT = DesktopSmokeSceneContract(
    object_conditions=(
        DesktopSmokeObjectCondition("sessionRailStage", min_opacity=0.999, min_scale=0.999),
        DesktopSmokeObjectCondition("chatDetailStage", min_opacity=0.999, min_scale=0.999),
        DesktopSmokeObjectCondition(
            "chatEmptyIdleState",
            visible=True,
            min_width=1,
            min_height=1,
        ),
    ),
    settle_cycles=4,
)


@dataclass(frozen=True)
class DesktopSmokeScreenshotScenario:
    name: str
    start_view: str
    scene_contract: DesktopSmokeSceneContract
    width: int | None = None
    height: int | None = None
    max_changed_pixels: int = 1500
    ignore_regions: tuple[DesktopSmokeIgnoreRegion, ...] = ()


DESKTOP_SMOKE_SCREENSHOT_SCENARIOS = (
    DesktopSmokeScreenshotScenario(
        name="chat",
        start_view="chat",
        scene_contract=CHAT_IDLE_SCENE_CONTRACT,
        ignore_regions=(DesktopSmokeIgnoreRegion("sidebarBrandMarkMotion", padding=10),),
    ),
    DesktopSmokeScreenshotScenario(
        name="settings",
        start_view="settings",
        scene_contract=SETTINGS_SCENE_CONTRACT,
    ),
    DesktopSmokeScreenshotScenario(
        name="chat-min",
        start_view="chat",
        scene_contract=CHAT_IDLE_SCENE_CONTRACT,
        width=640,
        height=600,
        ignore_regions=(DesktopSmokeIgnoreRegion("sidebarBrandMarkMotion", padding=10),),
    ),
    DesktopSmokeScreenshotScenario(
        name="settings-min",
        start_view="settings",
        scene_contract=SETTINGS_SCENE_CONTRACT,
        width=640,
        height=600,
    ),
)


@pytest.fixture(scope="session")
def qapp():
    app = QGuiApplication.instance()
    if app is None:
        QQuickStyle.setStyle("Basic")
        app = QGuiApplication(sys.argv)
    yield app


def desktop_ui_smoke_output_dir(default_name: str = "bao-desktop-ui-smoke") -> Path:
    configured = os.getenv("BAO_DESKTOP_UI_SMOKE_DIR", "").strip()
    target = Path(configured).expanduser() if configured else Path("/tmp") / default_name
    target.mkdir(parents=True, exist_ok=True)
    return target


def desktop_ui_baseline_dir() -> Path:
    return Path(__file__).resolve().parent / "fixtures" / "desktop_ui_baselines"


def desktop_ui_diff_output_dir() -> Path:
    target = desktop_ui_smoke_output_dir() / "diff"
    target.mkdir(parents=True, exist_ok=True)
    return target


def desktop_ui_update_baselines_enabled() -> bool:
    return os.getenv("BAO_DESKTOP_UI_UPDATE_BASELINES", "").strip() == "1"


def process_events(ms: int) -> None:
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def wait_until_ready(component: QQmlComponent, timeout_ms: int = 500) -> None:
    remaining = timeout_ms
    while component.status() == QQmlComponent.Loading and remaining > 0:
        process_events(25)
        remaining -= 25


def wait_until(predicate, *, attempts: int = 20, step_ms: int = 20) -> None:
    for _ in range(attempts):
        if predicate():
            return
        process_events(step_ms)
    raise AssertionError("condition not met before timeout")


def center_point(item) -> QPoint:
    center = item.mapToScene(QPointF(item.property("width") / 2, item.property("height") / 2))
    return QPoint(int(center.x()), int(center.y()))


def assert_item_within_window(root, item, *, inset: float = 0.0) -> None:
    top_left = item.mapToScene(QPointF(0, 0))
    left = float(top_left.x())
    top = float(top_left.y())
    right = left + float(item.property("width"))
    bottom = top + float(item.property("height"))
    window_width = float(root.property("width"))
    window_height = float(root.property("height"))

    assert left >= inset - 0.5
    assert top >= inset - 0.5
    assert right <= window_width - inset + 0.5
    assert bottom <= window_height - inset + 0.5


def grab_item_image(root, item, *, padding: int = 10) -> QImage:
    window_image = root.grabWindow()
    top_left = item.mapToScene(QPointF(0, 0))
    x = max(0, int(top_left.x()) - padding)
    y = max(0, int(top_left.y()) - padding)
    width = min(
        int(item.property("width")) + padding * 2,
        max(1, window_image.width() - x),
    )
    height = min(
        int(item.property("height")) + padding * 2,
        max(1, window_image.height() - y),
    )
    return window_image.copy(QRect(x, y, width, height))


def count_pixel_differences(image_a: QImage, image_b: QImage) -> int:
    width = min(image_a.width(), image_b.width())
    height = min(image_a.height(), image_b.height())
    changed = 0
    for y in range(height):
        for x in range(width):
            if image_a.pixel(x, y) != image_b.pixel(x, y):
                changed += 1
    return changed


def scroll_item_into_view(root, scroll_view, item) -> None:
    content_item = scroll_view.property("contentItem")
    if not isinstance(content_item, QQuickItem):
        raise AssertionError("settings scroll content item not found")
    window_height = float(root.property("height"))
    current_y = float(content_item.property("contentY"))
    top_left = item.mapToScene(QPointF(0, 0))
    item_top = float(top_left.y())
    item_bottom = item_top + float(item.property("height"))
    lower_bound = window_height - 96.0
    upper_bound = 96.0
    if item_bottom > lower_bound:
        content_item.setProperty("contentY", current_y + (item_bottom - lower_bound))
        process_events(50)
        current_y = float(content_item.property("contentY"))
        top_left = item.mapToScene(QPointF(0, 0))
        item_top = float(top_left.y())
    if item_top < upper_bound:
        content_item.setProperty("contentY", max(0.0, current_y - (upper_bound - item_top)))
        process_events(50)


def find_object(root: QObject, object_name: str) -> QObject:
    for obj in root.findChildren(QObject):
        if obj.objectName() == object_name:
            return obj
    raise AssertionError(f"object not found: {object_name}")


def find_optional_object(root: QObject, object_name: str) -> QObject | None:
    for obj in root.findChildren(QObject):
        if obj.objectName() == object_name:
            return obj
    return None


def _root_condition_matches(root: QObject, condition: DesktopSmokeRootCondition) -> bool:
    return root.property(condition.property_name) == condition.expected


def _object_condition_matches(root: QObject, condition: DesktopSmokeObjectCondition) -> bool:
    obj = find_optional_object(root, condition.object_name)
    if obj is None:
        return False
    if condition.visible is not None and bool(obj.property("visible")) != condition.visible:
        return False
    if condition.min_width is not None and float(obj.property("width") or 0) < condition.min_width:
        return False
    if condition.min_height is not None and float(obj.property("height") or 0) < condition.min_height:
        return False
    if condition.min_opacity is not None and float(obj.property("opacity") or 0) < condition.min_opacity:
        return False
    if condition.min_scale is not None and float(obj.property("scale") or 0) < condition.min_scale:
        return False
    return True


def wait_for_scene_contract(
    root: QObject,
    contract: DesktopSmokeSceneContract,
    *,
    attempts: int = 40,
    step_ms: int = 20,
) -> None:
    for condition in contract.root_conditions:
        wait_until(
            lambda current=condition: _root_condition_matches(root, current),
            attempts=attempts,
            step_ms=step_ms,
        )
    for condition in contract.object_conditions:
        wait_until(
            lambda current=condition: _object_condition_matches(root, current),
            attempts=attempts,
            step_ms=step_ms,
        )
    for _ in range(contract.settle_cycles):
        process_events(contract.settle_ms)


def resolve_ignore_regions(
    root: QObject, specs: tuple[DesktopSmokeIgnoreRegion, ...]
) -> tuple[tuple[int, int, int, int], ...]:
    if not specs:
        return ()

    window_width = int(float(root.property("width") or 0))
    window_height = int(float(root.property("height") or 0))
    resolved: list[tuple[int, int, int, int]] = []
    for spec in specs:
        obj = find_object(root, spec.object_name)
        if not isinstance(obj, QQuickItem):
            raise AssertionError(f"ignored object is not a QQuickItem: {spec.object_name}")
        top_left = obj.mapToScene(QPointF(0, 0))
        x = max(0, int(top_left.x()) - spec.padding)
        y = max(0, int(top_left.y()) - spec.padding)
        width = min(
            window_width - x,
            int(float(obj.property("width") or 0)) + spec.padding * 2,
        )
        height = min(
            window_height - y,
            int(float(obj.property("height") or 0)) + spec.padding * 2,
        )
        resolved.append((x, y, max(1, width), max(1, height)))
    return tuple(resolved)


def assert_png_matches_baseline(
    actual_path: Path,
    baseline_name: str,
    *,
    max_changed_pixels: int = 0,
    ignore_regions: tuple[tuple[int, int, int, int], ...] = (),
) -> None:
    baseline_dir = desktop_ui_baseline_dir()
    baseline_dir.mkdir(parents=True, exist_ok=True)
    baseline_path = baseline_dir / f"{baseline_name}.png"
    if desktop_ui_update_baselines_enabled():
        shutil.copy2(actual_path, baseline_path)
        return

    if not baseline_path.exists():
        raise AssertionError(
            f"missing baseline: {baseline_path}. "
            "Run `bash scripts/update_desktop_ui_baselines.sh` to create or refresh baselines."
        )

    if baseline_path.read_bytes() == actual_path.read_bytes():
        return

    from PIL import Image, ImageChops, ImageDraw

    diff_dir = desktop_ui_diff_output_dir()
    actual_copy = diff_dir / f"{baseline_name}.actual.png"
    expected_copy = diff_dir / f"{baseline_name}.expected.png"
    diff_copy = diff_dir / f"{baseline_name}.diff.png"
    shutil.copy2(actual_path, actual_copy)
    shutil.copy2(baseline_path, expected_copy)

    with Image.open(actual_path) as actual_image, Image.open(baseline_path) as expected_image:
        actual_rgba = actual_image.convert("RGBA")
        expected_rgba = expected_image.convert("RGBA")
        if actual_rgba.size != expected_rgba.size:
            raise AssertionError(
                f"baseline size mismatch for {baseline_name}: "
                f"actual={actual_rgba.size} expected={expected_rgba.size}. "
                f"actual={actual_copy} expected={expected_copy}"
            )

        diff_image = ImageChops.difference(expected_rgba, actual_rgba)
        if ignore_regions:
            draw = ImageDraw.Draw(diff_image)
            for x, y, width, height in ignore_regions:
                draw.rectangle((x, y, x + width - 1, y + height - 1), fill=(0, 0, 0, 0))
        diff_image.save(diff_copy)
        diff_mask = diff_image.convert("L")
        histogram = diff_mask.histogram()
        changed_pixels = sum(histogram[1:])

    if changed_pixels <= max_changed_pixels:
        return

    raise AssertionError(
        f"visual regression for {baseline_name}: changed_pixels={changed_pixels}, "
        f"allowed={max_changed_pixels}. actual={actual_copy} "
        f"expected={expected_copy} diff={diff_copy}"
    )
