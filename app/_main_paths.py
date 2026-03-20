from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QFontDatabase

BUNDLED_APP_FONT_FILENAME = "OPPO Sans.ttf"
BUNDLED_APP_FONT_FAMILY_PREFIX = ""
BUNDLED_APP_FONT_RELATIVE_PATHS = (
    f"app/resources/fonts/{BUNDLED_APP_FONT_FILENAME}",
    f"resources/fonts/{BUNDLED_APP_FONT_FILENAME}",
)
PREFERRED_SYSTEM_FONT_FAMILIES = (
    "Helvetica Neue",
    ".AppleSystemUIFont",
    "Segoe UI",
    "Arial",
    "Noto Sans",
    "DejaVu Sans",
)
WINDOWS_APP_ICON_RELATIVE_PATHS = ("resources/logo.ico", "app/resources/logo.ico")
WINDOWS_APP_ICON_FALLBACK_RELATIVE_PATHS = (
    "resources/logo-circle.png",
    "app/resources/logo-circle.png",
    "assets/logo.ico",
    "assets/logo.jpg",
    "assets/logo.jpeg",
    "assets/logo.png",
)
DEFAULT_APP_ICON_RELATIVE_PATHS = ("assets/logo.jpg", "assets/logo.jpeg", "assets/logo.png", "assets/logo.ico")
TRAY_APP_ICON_RELATIVE_PATHS = (
    "resources/logo-bun.png",
    "app/resources/logo-bun.png",
    "resources/logo-bun-light.png",
    "app/resources/logo-bun-light.png",
    "resources/logo-bun-dark.png",
    "app/resources/logo-bun-dark.png",
)
QML_RESOURCE_MAIN_URL = "qrc:/app/qml/Main.qml"
QML_RCC_RELATIVE_PATHS = (
    "app/resources/desktop_qml.rcc",
    "resources/desktop_qml.rcc",
    "desktop_qml.rcc",
)


def resolve_qml_path(qml_arg: str | None, *, current_file: str, sys_module: object) -> Path:
    if qml_arg:
        return Path(qml_arg).expanduser().resolve()
    candidates = [Path(current_file).resolve().parent / "qml" / "Main.qml"]
    if getattr(sys_module, "frozen", False):
        exe = Path(getattr(sys_module, "executable", sys.executable)).resolve()
        meipass = getattr(sys_module, "_MEIPASS", "")
        frozen_roots = [
            Path(meipass) if meipass else None,
            exe.parent,
            exe.parent.parent / "Resources",
            exe.parent.parent / "Resources" / "app",
            exe.parent.parent / "Frameworks",
        ]
        for root in frozen_roots:
            if root is None:
                continue
            candidates.extend([root / "qml" / "Main.qml", root / "app" / "qml" / "Main.qml"])
    for path in candidates:
        if path.exists():
            return path.resolve()
    return candidates[0].resolve()


def app_resource_candidate_roots(*, current_file: str, sys_module: object) -> list[Path]:
    src_root = Path(current_file).resolve().parent.parent
    roots = [src_root]
    if not getattr(sys_module, "frozen", False):
        return roots
    exe = Path(getattr(sys_module, "executable", sys.executable)).resolve()
    meipass = getattr(sys_module, "_MEIPASS", "")
    if meipass:
        roots.append(Path(meipass))
    roots.extend([exe.parent, exe.parent.parent / "Resources"])
    unique_roots: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        resolved = root.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique_roots.append(resolved)
    return unique_roots


def resolve_app_resource_path(
    *relative_paths: str, current_file: str, sys_module: object
) -> Path | None:
    for root in app_resource_candidate_roots(current_file=current_file, sys_module=sys_module):
        for relative_path in relative_paths:
            path = root / relative_path
            if path.exists():
                return path.resolve()
    return None


def resolve_app_icon_path(*, resolver: callable, sys_platform: str) -> Path | None:
    if sys_platform == "win32":
        bundled_icon = resolver(*WINDOWS_APP_ICON_RELATIVE_PATHS)
        if bundled_icon is not None:
            return bundled_icon
        return resolver(*WINDOWS_APP_ICON_FALLBACK_RELATIVE_PATHS)
    return resolver(*DEFAULT_APP_ICON_RELATIVE_PATHS)


def resolve_tray_icon_path(*, resolver: callable, app_icon_fn: callable) -> Path | None:
    return resolver(*TRAY_APP_ICON_RELATIVE_PATHS) or app_icon_fn()


def resolve_bundled_app_font_path(*, resolver: callable) -> Path | None:
    return resolver(*BUNDLED_APP_FONT_RELATIVE_PATHS)


def preferred_system_font_family() -> str | None:
    families = set(QFontDatabase.families())
    for family in PREFERRED_SYSTEM_FONT_FAMILIES:
        if family in families:
            return family
    return None
