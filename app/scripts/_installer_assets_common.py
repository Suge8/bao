from __future__ import annotations

import math
from dataclasses import dataclass
from typing import cast

from PIL import Image, ImageDraw, ImageFilter, ImageFont

Size = tuple[int, int]
Bounds = tuple[int, int, int, int]


@dataclass(frozen=True)
class BrandTheme:
    base_top: tuple[int, int, int]
    base_bottom: tuple[int, int, int]
    accent_main: tuple[int, int, int]
    accent_secondary: tuple[int, int, int]
    accent_main_strength: int
    accent_secondary_strength: int
    panel_fill: tuple[int, int, int, int]
    panel_stroke: tuple[int, int, int, int]
    card_fill: tuple[int, int, int, int]
    card_stroke: tuple[int, int, int, int]
    text_primary: tuple[int, int, int, int]
    text_secondary: tuple[int, int, int, int]
    pill_fill: tuple[int, int, int, int]
    pill_text: tuple[int, int, int, int]
    arrow_line: tuple[int, int, int, int]
    arrow_glow: tuple[int, int, int, int]


@dataclass(frozen=True)
class LogoCardSpec:
    bounds: Bounds
    dark: bool


@dataclass(frozen=True)
class TextWrapSpec:
    font: ImageFont.ImageFont | ImageFont.FreeTypeFont
    max_width: int | None


@dataclass(frozen=True)
class TextBlockSpec:
    title: str
    subtitle: str
    anchor: tuple[int, int]
    dark: bool
    title_size: int
    subtitle_size: int
    max_width: int | None = None


@dataclass(frozen=True)
class PillSpec:
    text: str
    bounds: Bounds
    dark: bool
    emphasized: bool


def theme(dark: bool) -> BrandTheme:
    if dark:
        return BrandTheme(
            base_top=(19, 14, 11),
            base_bottom=(11, 8, 6),
            accent_main=(255, 179, 61),
            accent_secondary=(198, 134, 66),
            accent_main_strength=112,
            accent_secondary_strength=74,
            panel_fill=(28, 20, 15, 210),
            panel_stroke=(255, 222, 181, 26),
            card_fill=(38, 28, 22, 226),
            card_stroke=(255, 210, 150, 32),
            text_primary=(247, 239, 231, 255),
            text_secondary=(197, 175, 158, 255),
            pill_fill=(255, 179, 61, 255),
            pill_text=(30, 20, 14, 255),
            arrow_line=(255, 200, 134, 126),
            arrow_glow=(255, 179, 61, 62),
        )
    return BrandTheme(
        base_top=(252, 248, 244),
        base_bottom=(243, 236, 230),
        accent_main=(255, 179, 61),
        accent_secondary=(198, 134, 66),
        accent_main_strength=72,
        accent_secondary_strength=48,
        panel_fill=(255, 252, 248, 224),
        panel_stroke=(182, 142, 104, 28),
        card_fill=(255, 255, 255, 236),
        card_stroke=(201, 170, 138, 40),
        text_primary=(38, 26, 18, 255),
        text_secondary=(107, 86, 73, 255),
        pill_fill=(255, 179, 61, 255),
        pill_text=(30, 20, 14, 255),
        arrow_line=(194, 136, 66, 118),
        arrow_glow=(255, 179, 61, 46),
    )


def ensure_rgba(image: Image.Image, size: Size) -> Image.Image:
    return image.convert("RGBA").resize(size, Image.Resampling.LANCZOS)


def load_font(size: int, *, bold: bool) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    font_names = ["DejaVuSans-Bold.ttf", "Arial Bold.ttf"] if bold else ["DejaVuSans.ttf", "Arial.ttf"]
    for name in font_names:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def build_backdrop(size: Size, dark: bool) -> Image.Image:
    palette = theme(dark)
    canvas = vertical_gradient(size, palette.base_top, palette.base_bottom)
    accent_a = radial_glow((size[0] * 2 // 3, size[1] * 2 // 3), palette.accent_main, palette.accent_main_strength)
    accent_b = radial_glow((size[0] // 2, size[1] // 2), palette.accent_secondary, palette.accent_secondary_strength)
    canvas.alpha_composite(accent_a, (int(size[0] * -0.06), int(size[1] * -0.12)))
    canvas.alpha_composite(accent_b, (int(size[0] * 0.58), int(size[1] * 0.24)))
    return canvas


def vertical_gradient(size: Size, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    width, height = size
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        t = y / max(1, height - 1)
        color = tuple(int(top[index] * (1.0 - t) + bottom[index] * t) for index in range(3))
        draw.line((0, y, width, y), fill=(*color, 255))
    return image


def radial_glow(size: Size, color: tuple[int, int, int], strength: int) -> Image.Image:
    width, height = size
    cx = width / 2
    cy = height / 2
    rx = max(1.0, width / 2)
    ry = max(1.0, height / 2)
    pixels: list[tuple[int, int, int, int]] = []
    for y in range(height):
        dy = (y - cy) / ry
        for x in range(width):
            dx = (x - cx) / rx
            distance = min(1.0, math.sqrt(dx * dx + dy * dy))
            factor = 1.0 - distance
            alpha = int(factor * factor * math.sqrt(factor) * strength)
            pixels.append((*color, alpha))
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    glow.putdata(pixels)
    return glow.filter(ImageFilter.GaussianBlur(max(10, min(width, height) // 18)))


def rounded_panel(canvas: Image.Image, bounds: Bounds, *, dark: bool) -> None:
    left, top, right, bottom = bounds
    palette = theme(dark)
    ImageDraw.Draw(canvas).rounded_rectangle(
        bounds,
        radius=max(18, min(right - left, bottom - top) // 10),
        fill=palette.panel_fill,
        outline=palette.panel_stroke,
        width=max(1, min(right - left, bottom - top) // 180),
    )


def paste_logo_card(canvas: Image.Image, logo: Image.Image, spec: LogoCardSpec) -> None:
    left, top, right, bottom = spec.bounds
    palette = theme(spec.dark)
    card = Image.new("RGBA", (right - left, bottom - top), (0, 0, 0, 0))
    card_width, card_height = card.size
    radius = max(18, min(card_width, card_height) // 8)
    shadow = Image.new("RGBA", (card_width, card_height), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (14, 18, card_width - 14, card_height - 6),
        radius=radius,
        fill=(0, 0, 0, 72 if spec.dark else 24),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(max(8, min(card_width, card_height) // 14)))
    canvas.alpha_composite(shadow, (left, top))
    ImageDraw.Draw(card).rounded_rectangle(
        (0, 0, card_width - 1, card_height - 1),
        radius=radius,
        fill=palette.card_fill,
        outline=palette.card_stroke,
        width=max(1, min(card_width, card_height) // 48),
    )
    canvas.alpha_composite(card, (left, top))
    inset = max(18, min(card_width, card_height) // 7)
    logo_size = min(card_width, card_height) - inset * 2
    logo_resized = ensure_rgba(logo, (logo_size, logo_size))
    canvas.alpha_composite(
        logo_resized,
        (left + (card_width - logo_size) // 2, top + (card_height - logo_size) // 2),
    )


def draw_text_block(canvas: Image.Image, spec: TextBlockSpec) -> int:
    palette = theme(spec.dark)
    draw = ImageDraw.Draw(canvas)
    title_font = load_font(spec.title_size, bold=True)
    body_font = load_font(spec.subtitle_size, bold=False)
    wrapped_title = wrap_text(draw, spec.title, TextWrapSpec(font=title_font, max_width=spec.max_width))
    wrapped_subtitle = wrap_text(
        draw,
        spec.subtitle,
        TextWrapSpec(font=body_font, max_width=spec.max_width),
    )
    draw.multiline_text(spec.anchor, wrapped_title, fill=palette.text_primary, font=title_font, spacing=6)
    title_box = draw.multiline_textbbox(spec.anchor, wrapped_title, font=title_font, spacing=6)
    subtitle_y = title_box[3] + max(10, spec.subtitle_size // 2)
    spacing = max(6, spec.subtitle_size // 3)
    subtitle_anchor = (spec.anchor[0], subtitle_y)
    draw.multiline_text(
        subtitle_anchor,
        wrapped_subtitle,
        fill=palette.text_secondary,
        font=body_font,
        spacing=spacing,
    )
    subtitle_box = draw.multiline_textbbox(subtitle_anchor, wrapped_subtitle, font=body_font, spacing=spacing)
    return cast(int, subtitle_box[3])


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    spec: TextWrapSpec,
) -> str:
    if not text or not spec.max_width or spec.max_width <= 0:
        return text
    wrapped_lines: list[str] = []
    for paragraph in text.splitlines():
        words = paragraph.split()
        if not words:
            wrapped_lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if draw.textbbox((0, 0), candidate, font=spec.font)[2] <= spec.max_width:
                current = candidate
            else:
                wrapped_lines.append(current)
                current = word
        wrapped_lines.append(current)
    return "\n".join(wrapped_lines)


def draw_pill(canvas: Image.Image, spec: PillSpec) -> None:
    palette = theme(spec.dark)
    left, top, right, bottom = spec.bounds
    draw = ImageDraw.Draw(canvas)
    fill = palette.pill_fill if spec.emphasized else palette.card_fill
    stroke = palette.pill_fill if spec.emphasized else palette.card_stroke
    text_color = palette.pill_text if spec.emphasized else palette.text_secondary
    draw.rounded_rectangle(spec.bounds, radius=(bottom - top) // 2, fill=fill, outline=stroke, width=1)
    font = load_font(18, bold=True)
    text_box = draw.textbbox((0, 0), spec.text, font=font)
    text_x = left + ((right - left) - (text_box[2] - text_box[0])) // 2
    text_y = top + ((bottom - top) - (text_box[3] - text_box[1])) // 2 - 1
    draw.text((text_x, text_y), spec.text, fill=text_color, font=font)
