# ruff: noqa: F403, F405
from __future__ import annotations

from tests._desktop_ui_testkit_base import *


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
        width = min(window_width - x, int(float(obj.property("width") or 0)) + spec.padding * 2)
        height = min(
            window_height - y,
            int(float(obj.property("height") or 0)) + spec.padding * 2,
        )
        resolved.append((x, y, max(1, width), max(1, height)))
    return tuple(resolved)


__all__ = [name for name in globals() if not (name.startswith("__") and name.endswith("__"))]
