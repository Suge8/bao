from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QIcon,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QSurfaceFormat,
)
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQuickControls2 import QQuickStyle


def configure_qt_style() -> None:
    QQuickStyle.setStyle("Basic")
    fmt = QSurfaceFormat()
    fmt.setAlphaBufferSize(8)
    fmt.setSamples(4)
    QSurfaceFormat.setDefaultFormat(fmt)


def load_app_icon(icon_path: Path) -> QIcon | None:
    if icon_path.suffix.lower() == ".ico":
        icon = QIcon(str(icon_path))
        return None if icon.isNull() else icon
    return build_rounded_icon(icon_path) or QIcon(str(icon_path))


def _image_alpha_bounds(image: QImage) -> tuple[int, int, int, int] | None:
    left, top, right, bottom = image.width(), image.height(), -1, -1
    for y in range(image.height()):
        for x in range(image.width()):
            if image.pixelColor(x, y).alpha() <= 0:
                continue
            left, top, right, bottom = min(left, x), min(top, y), max(right, x), max(bottom, y)
    if right < left or bottom < top:
        return None
    return left, top, right, bottom


def build_tray_mask_image(image_path: Path) -> QImage | None:
    source = QImage(str(image_path)).convertToFormat(QImage.Format.Format_ARGB32)
    if source.isNull():
        return None
    mask = QImage(source.size(), QImage.Format.Format_ARGB32)
    mask.fill(Qt.GlobalColor.transparent)
    for y in range(source.height()):
        for x in range(source.width()):
            color = source.pixelColor(x, y)
            if color.alpha() <= 0 or color.lightness() < 150:
                continue
            mask.setPixelColor(x, y, QColor(255, 255, 255, max(0, min(255, color.alpha()))))
    return mask


def build_monochrome_tray_icon(image_path: Path, *, dark_mode: bool) -> QIcon | None:
    mask = build_tray_mask_image(image_path)
    if mask is None or mask.isNull():
        return None
    bounds = _image_alpha_bounds(mask)
    if bounds is None:
        return None
    left, top, right, bottom = bounds
    trimmed = mask.copy(left, top, right - left + 1, bottom - top + 1)
    icon = QIcon()
    tint = QColor("#FFFFFF" if dark_mode else "#121212")
    for px in (16, 18, 20, 22, 24, 32, 40, 44, 48, 64):
        canvas = QPixmap(px, px)
        canvas.fill(Qt.GlobalColor.transparent)
        padding = max(1.0, px * 0.08)
        target = QRectF(padding, padding, px - padding * 2, px - padding * 2)
        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.drawImage(target, trimmed)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(QRectF(0, 0, px, px), tint)
        _ = painter.end()
        icon.addPixmap(canvas)
    if hasattr(icon, "setIsMask"):
        icon.setIsMask(True)
    return None if icon.isNull() else icon


def load_tray_icon(icon_path: Path, *, dark_mode: bool) -> QIcon | None:
    icon = build_monochrome_tray_icon(icon_path, dark_mode=dark_mode)
    if icon is not None:
        return icon
    fallback = QIcon(str(icon_path))
    return None if fallback.isNull() else fallback


def build_rounded_icon(image_path: Path) -> QIcon | None:
    image = QImage(str(image_path))
    if image.isNull():
        return None
    side = min(image.width(), image.height())
    square = image.copy((image.width() - side) // 2, (image.height() - side) // 2, side, side)
    icon = QIcon()
    for px in (16, 20, 24, 32, 48, 64, 128, 256, 512):
        canvas = QPixmap(px, px)
        canvas.fill(Qt.GlobalColor.transparent)
        inset = max(1.0, px * 0.06)
        target = QRectF(inset, inset, px - inset * 2, px - inset * 2)
        radius = target.width() * 0.24
        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(
            QRectF(target.x(), target.y() + max(1.0, px * 0.02), target.width(), target.height()),
            radius,
            radius,
        )
        painter.fillPath(shadow_path, QColor(0, 0, 0, 34 if px >= 64 else 22))
        clip = QPainterPath()
        clip.addRoundedRect(target, radius, radius)
        painter.setClipPath(clip)
        painter.drawImage(target, square)
        gloss = QLinearGradient(target.left(), target.top(), target.left(), target.bottom())
        gloss.setColorAt(0.0, QColor(255, 255, 255, 85 if px >= 64 else 55))
        gloss.setColorAt(0.35, QColor(255, 255, 255, 26 if px >= 64 else 18))
        gloss.setColorAt(0.65, QColor(255, 255, 255, 0))
        painter.fillPath(clip, gloss)
        painter.setClipping(False)
        stroke_width = max(1.0, px * 0.012)
        stroke_rect = target.adjusted(stroke_width / 2, stroke_width / 2, -stroke_width / 2, -stroke_width / 2)
        painter.setPen(QPen(QColor(255, 255, 255, 95 if px >= 64 else 70), stroke_width))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(stroke_rect, max(1.0, radius - stroke_width / 2), max(1.0, radius - stroke_width / 2))
        _ = painter.end()
        icon.addPixmap(canvas)
    return icon


def to_qcolor(value: object, fallback: QColor) -> QColor:
    color = QColor(value)
    return color if color.isValid() else fallback


def _to_colorref(color: QColor) -> int:
    return (color.blue() << 16) | (color.green() << 8) | color.red()


def apply_windows_rounded_corners(window: QQuickWindow) -> bool:
    if sys.platform != "win32":
        return False
    try:
        import ctypes

        pref = ctypes.c_int(2)
        result = ctypes.windll.dwmapi.DwmSetWindowAttribute(
            ctypes.c_void_p(int(window.winId())),
            ctypes.c_uint(33),
            ctypes.byref(pref),
            ctypes.sizeof(pref),
        )
        return int(result) == 0
    except Exception:
        return False


def apply_windows_titlebar_colors(window: QQuickWindow, caption_color: QColor, text_color: QColor) -> bool:
    if sys.platform != "win32":
        return False
    try:
        import ctypes

        ok = False
        for attr, raw in ((35, _to_colorref(caption_color)), (36, _to_colorref(text_color))):
            value = ctypes.c_uint(raw)
            result = ctypes.windll.dwmapi.DwmSetWindowAttribute(
                ctypes.c_void_p(int(window.winId())),
                ctypes.c_uint(attr),
                ctypes.byref(value),
                ctypes.sizeof(value),
            )
            ok = ok or int(result) == 0
        return ok
    except Exception:
        return False
