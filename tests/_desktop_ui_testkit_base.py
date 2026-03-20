from __future__ import annotations

import importlib
import os
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
QFont = QtGui.QFont
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


CHAT_IDLE_MIN_SCENE_CONTRACT = DesktopSmokeSceneContract(
    object_conditions=(
        DesktopSmokeObjectCondition("sessionRailStage", min_opacity=0.999, min_scale=0.999, min_width=176),
        DesktopSmokeObjectCondition("chatDetailStage", min_opacity=0.999, min_scale=0.999, min_width=180),
        DesktopSmokeObjectCondition("chatEmptyIdleState", visible=True, min_width=100, min_height=1),
        DesktopSmokeObjectCondition("chatEmptyIdleTitle", min_width=100),
        DesktopSmokeObjectCondition("chatEmptyIdleHint", min_width=100),
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
        max_changed_pixels=4500,
        ignore_regions=(
            DesktopSmokeIgnoreRegion("sidebarBrandDock", padding=18),
            DesktopSmokeIgnoreRegion("sidebarBrandMarkMotion", padding=24),
        ),
    ),
    DesktopSmokeScreenshotScenario(
        name="settings",
        start_view="settings",
        scene_contract=SETTINGS_SCENE_CONTRACT,
    ),
    DesktopSmokeScreenshotScenario(
        name="chat-min",
        start_view="chat",
        scene_contract=CHAT_IDLE_MIN_SCENE_CONTRACT,
        width=640,
        height=600,
        ignore_regions=(
            DesktopSmokeIgnoreRegion("sidebarBrandDock", padding=18),
            DesktopSmokeIgnoreRegion("sidebarBrandMarkMotion", padding=24),
        ),
    ),
    DesktopSmokeScreenshotScenario(
        name="settings-min",
        start_view="settings",
        scene_contract=SETTINGS_SCENE_CONTRACT,
        width=640,
        height=600,
    ),
)


def apply_test_app_font(app: QGuiApplication) -> None:
    from app.main import resolve_app_font_family

    font_family = resolve_app_font_family()
    if font_family:
        app.setFont(QFont(font_family))


@pytest.fixture(scope="session")
def qapp():
    app = QGuiApplication.instance()
    if app is None:
        QQuickStyle.setStyle("Basic")
        app = QGuiApplication(sys.argv)
    apply_test_app_font(app)
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
    width = min(int(item.property("width")) + padding * 2, max(1, window_image.width() - x))
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


__all__ = [name for name in globals() if not (name.startswith("__") and name.endswith("__"))]
