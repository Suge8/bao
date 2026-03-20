# ruff: noqa: E402, N802, N815, F403, F405, I001
from __future__ import annotations

from tests._chat_view_integration_shared import *

def _load_inline_qml(
    source: str, *, config_service: QObject | None = None
) -> tuple[QQmlApplicationEngine, QObject]:
    engine = QQmlApplicationEngine()
    engine._test_refs = {"config_service": config_service}
    context = engine.rootContext()
    context.setContextProperty("sizeDropdownMaxHeight", 280)
    context.setContextProperty("spacingSm", 8)
    context.setContextProperty("textSecondary", "#666666")
    context.setContextProperty("textTertiary", "#888888")
    context.setContextProperty("textPrimary", "#111111")
    context.setContextProperty("typeLabel", 14)
    context.setContextProperty("typeCaption", 12)
    context.setContextProperty("typeButton", 14)
    context.setContextProperty("weightMedium", 500)
    context.setContextProperty("letterTight", 0)
    context.setContextProperty("sizeControlHeight", 40)
    context.setContextProperty("radiusSm", 10)
    context.setContextProperty("bgInputFocus", "#FFFFFF")
    context.setContextProperty("bgInputHover", "#F7F7F7")
    context.setContextProperty("bgInput", "#F2F2F2")
    context.setContextProperty("borderFocus", "#FFB33D")
    context.setContextProperty("borderSubtle", "#DDDDDD")
    context.setContextProperty("motionUi", 220)
    context.setContextProperty("motionFast", 180)
    context.setContextProperty("motionMicro", 120)
    context.setContextProperty("easeStandard", QtCore.QEasingCurve.Type.OutCubic)
    context.setContextProperty("sizeFieldPaddingX", 12)
    context.setContextProperty("isDark", False)
    context.setContextProperty("sizeOptionHeight", 36)
    component = QtQml.QQmlComponent(engine)
    component.setData(
        source.encode("utf-8"),
        QUrl.fromLocalFile(str(PROJECT_ROOT / "tests" / "inline_settings_select.qml")),
    )
    root = component.create()
    if root is None:
        errors = "\n".join(err.toString() for err in component.errors())
        raise AssertionError(errors)
    engine._inline_refs = {"component": component, "root": root}
    return engine, root


def _find_object(root: QObject, object_name: str) -> QObject:
    for obj in root.findChildren(QObject):
        if obj.objectName() == object_name:
            return obj
    raise AssertionError(f"object not found: {object_name}")


def _first_visible_sidebar_session_anchor(
    root: QObject, session_list: QObject
) -> tuple[str, float]:
    _ = root
    content_y = float(session_list.property("contentY"))
    content_item = session_list.property("contentItem")
    if not isinstance(content_item, QQuickItem):
        raise AssertionError("sidebar content item not found")
    delegates = []
    for obj in content_item.childItems():
        if not bool(obj.property("anchorReady")):
            continue
        if bool(obj.property("anchorIsHeader")):
            continue
        key = str(obj.property("anchorKey") or "")
        if not key:
            continue
        y = float(obj.property("y"))
        height = float(obj.property("height"))
        if height <= 0:
            continue
        if y + height <= content_y:
            continue
        delegates.append((y, key))
    if not delegates:
        raise AssertionError("visible sidebar session anchor not found")
    delegates.sort(key=lambda item: item[0])
    y, key = delegates[0]
    return key, content_y - y


def _sidebar_session_anchor_offset(session_list: QObject, key: str) -> float:
    content_y = float(session_list.property("contentY"))
    content_item = session_list.property("contentItem")
    if not isinstance(content_item, QQuickItem):
        raise AssertionError("sidebar content item not found")
    for obj in content_item.childItems():
        if not bool(obj.property("anchorReady")):
            continue
        if bool(obj.property("anchorIsHeader")):
            continue
        if str(obj.property("anchorKey") or "") != key:
            continue
        y = float(obj.property("y"))
        height = float(obj.property("height"))
        if height <= 0:
            continue
        if y + height <= content_y:
            continue
        if y >= content_y + float(session_list.property("height")):
            continue
        return content_y - y
    raise AssertionError(f"sidebar anchor not visible: {key}")


def _sidebar_delegate_y(session_list: QObject, key: str) -> float:
    content_item = session_list.property("contentItem")
    if not isinstance(content_item, QQuickItem):
        raise AssertionError("sidebar content item not found")
    for obj in content_item.childItems():
        if not bool(obj.property("anchorReady")):
            continue
        if bool(obj.property("anchorIsHeader")):
            continue
        if str(obj.property("anchorKey") or "") != key:
            continue
        return float(obj.property("y"))
    raise AssertionError(f"sidebar delegate not found: {key}")


def _sidebar_delegate_root(session_list: QObject, key: str) -> QQuickItem:
    content_item = session_list.property("contentItem")
    if not isinstance(content_item, QQuickItem):
        raise AssertionError("sidebar content item not found")
    for obj in content_item.childItems():
        if not bool(obj.property("anchorReady")):
            continue
        if bool(obj.property("anchorIsHeader")):
            continue
        if str(obj.property("anchorKey") or "") != key:
            continue
        return obj
    raise AssertionError(f"sidebar delegate root not found: {key}")


def _find_object_by_property(root: QObject, property_name: str, expected: object) -> QObject:
    for obj in root.findChildren(QObject):
        try:
            if obj.property(property_name) == expected:
                return obj
        except Exception:
            continue
    raise AssertionError(f"object with {property_name}={expected!r} not found")


def _find_visible_object_by_property(
    root: QObject, property_name: str, expected: object
) -> QObject:
    for obj in root.findChildren(QObject):
        try:
            if obj.property(property_name) != expected:
                continue
            if obj.property("visible") is not True:
                continue
            return obj
        except Exception:
            continue
    raise AssertionError(f"visible object with {property_name}={expected!r} not found")


def _provider_list_snapshot(settings_view: QObject) -> list[dict[str, object]]:
    provider_list = settings_view.property("_providerList")
    to_variant = getattr(provider_list, "toVariant", None)
    if callable(to_variant):
        provider_list = to_variant()
    if not isinstance(provider_list, list):
        raise AssertionError("settings provider list is not a list")
    snapshot: list[dict[str, object]] = []
    for item in provider_list:
        if not isinstance(item, dict):
            raise AssertionError("settings provider row is not a dict")
        snapshot.append(item)
    return snapshot

__all__ = [name for name in globals() if name != "__all__" and not (name.startswith("__") and name.endswith("__"))]
