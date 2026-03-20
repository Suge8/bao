from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw

from ._installer_assets_common import (
    LogoCardSpec,
    PillSpec,
    TextBlockSpec,
    build_backdrop,
    draw_pill,
    draw_text_block,
    paste_logo_card,
    rounded_panel,
    theme,
)


@dataclass(frozen=True)
class DmgLayout:
    palette: object
    app_bounds: tuple[int, ...]
    apps_bounds: tuple[int, ...]


def build_wizard_panel(logo: Image.Image, output: Path, *, dark: bool) -> None:
    canvas = build_backdrop((404, 772), dark)
    rounded_panel(canvas, (24, 26, 380, 744), dark=dark)
    draw_pill(canvas, PillSpec(text="Bao Desktop", bounds=(54, 52, 200, 86), dark=dark, emphasized=True))
    paste_logo_card(canvas, logo, LogoCardSpec(bounds=(56, 116, 348, 384), dark=dark))
    draw_text_block(
        canvas,
        TextBlockSpec(
            title="One calm place\nfor AI work.",
            subtitle="Chat, memory, tools, and hub controls stay aligned from first install.",
            anchor=(56, 438),
            dark=dark,
            title_size=40,
            subtitle_size=20,
            max_width=286,
        ),
    )
    draw_pill(canvas, PillSpec(text="Desktop chat", bounds=(56, 640, 184, 676), dark=dark, emphasized=False))
    draw_pill(canvas, PillSpec(text="Memory", bounds=(194, 640, 292, 676), dark=dark, emphasized=False))
    draw_pill(canvas, PillSpec(text="Hub", bounds=(56, 688, 176, 724), dark=dark, emphasized=False))
    canvas.save(output, format="PNG")


def build_wizard_small(logo: Image.Image, output: Path, *, dark: bool) -> None:
    canvas = build_backdrop((128, 128), dark)
    rounded_panel(canvas, (8, 8, 120, 120), dark=dark)
    paste_logo_card(canvas, logo, LogoCardSpec(bounds=(20, 20, 108, 108), dark=dark))
    canvas.save(output, format="PNG")


def build_wizard_back(logo: Image.Image, output: Path, *, dark: bool) -> None:
    canvas = build_backdrop((1194, 864), dark)
    rounded_panel(canvas, (72, 88, 1122, 776), dark=dark)
    draw_pill(
        canvas,
        PillSpec(text="Warm setup, fast start", bounds=(112, 138, 332, 178), dark=dark, emphasized=True),
    )
    bottom = draw_text_block(
        canvas,
        TextBlockSpec(
            title="Install Bao once.\nFinish setup in the app.",
            subtitle="Keep the installer lightweight. Connect channels and tune your workspace after launch, inside Bao.",
            anchor=(112, 214),
            dark=dark,
            title_size=52,
            subtitle_size=22,
            max_width=540,
        ),
    )
    draw_pill(
        canvas,
        PillSpec(text="Windows setup", bounds=(112, bottom + 32, 274, bottom + 68), dark=dark, emphasized=False),
    )
    draw_pill(
        canvas,
        PillSpec(
            text="Local-first config",
            bounds=(286, bottom + 32, 472, bottom + 68),
            dark=dark,
            emphasized=False,
        ),
    )
    draw_pill(
        canvas,
        PillSpec(text="Hub ready", bounds=(112, bottom + 82, 244, bottom + 118), dark=dark, emphasized=False),
    )
    paste_logo_card(canvas, logo, LogoCardSpec(bounds=(774, 164, 1012, 402), dark=dark))
    canvas.save(output, format="PNG")


def build_dmg_background(logo: Image.Image, output: Path, *, dark: bool = False) -> None:
    palette = theme(dark)
    canvas = build_backdrop((720, 420), dark)
    rounded_panel(canvas, (28, 28, 692, 392), dark=dark)
    draw_pill(canvas, PillSpec(text="Drag to install", bounds=(52, 48, 188, 82), dark=dark, emphasized=True))
    draw_text_block(
        canvas,
        TextBlockSpec(
            title="Move Bao to Applications.",
            subtitle="One app. One destination. Open it from Applications when the copy finishes.",
            anchor=(52, 102),
            dark=dark,
            title_size=32,
            subtitle_size=18,
            max_width=380,
        ),
    )
    app_bounds = (94, 172, 238, 316)
    apps_bounds = (506, 172, 650, 316)
    paste_logo_card(canvas, logo, LogoCardSpec(bounds=app_bounds, dark=dark))
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(apps_bounds, radius=28, fill=palette.card_fill, outline=palette.card_stroke, width=2)
    draw.rounded_rectangle((apps_bounds[0] + 18, apps_bounds[1] + 16, apps_bounds[0] + 78, apps_bounds[1] + 44), radius=12, fill=palette.pill_fill)
    draw.rounded_rectangle(
        (apps_bounds[0] + 18, apps_bounds[1] + 36, apps_bounds[2] - 18, apps_bounds[3] - 18),
        radius=22,
        fill=(255, 255, 255, 40) if dark else (255, 255, 255, 92),
    )
    layout = DmgLayout(palette=palette, app_bounds=app_bounds, apps_bounds=apps_bounds)
    draw_folder_labels(draw, layout)
    draw_drag_arrow(draw, layout)
    canvas.save(output, format="PNG")


def draw_folder_labels(draw: ImageDraw.ImageDraw, layout: DmgLayout) -> None:
    from ._installer_assets_common import load_font

    label_font = load_font(18, bold=True)
    label_box = draw.textbbox((0, 0), "Applications", font=label_font)
    apps_bounds = layout.apps_bounds
    app_bounds = layout.app_bounds
    label_x = apps_bounds[0] + ((apps_bounds[2] - apps_bounds[0]) - (label_box[2] - label_box[0])) // 2
    draw.text(
        (label_x, apps_bounds[3] + 12),
        "Applications",
        fill=layout.palette.text_secondary,
        font=label_font,
    )
    app_label_box = draw.textbbox((0, 0), "Bao", font=label_font)
    app_label_x = app_bounds[0] + ((app_bounds[2] - app_bounds[0]) - (app_label_box[2] - app_label_box[0])) // 2
    draw.text((app_label_x, app_bounds[3] + 12), "Bao", fill=layout.palette.text_secondary, font=label_font)


def draw_drag_arrow(draw: ImageDraw.ImageDraw, layout: DmgLayout) -> None:
    app_bounds = layout.app_bounds
    apps_bounds = layout.apps_bounds
    line_y = (app_bounds[1] + app_bounds[3]) // 2
    line_start = app_bounds[2] + 22
    line_end = apps_bounds[0] - 30
    draw.line((line_start, line_y, line_end, line_y), fill=layout.palette.arrow_glow, width=18)
    draw.line((line_start, line_y, line_end, line_y), fill=layout.palette.arrow_line, width=4)
    points = [(line_end - 18, line_y - 16), (line_end + 2, line_y), (line_end - 18, line_y + 16)]
    draw.line((points[0], points[1]), fill=layout.palette.arrow_line, width=4)
    draw.line((points[1], points[2]), fill=layout.palette.arrow_line, width=4)


def build_all_assets(logo: Image.Image, output_dir: Path, dmg_background: Path) -> list[Path]:
    generated_paths = [
        output_dir / "wizard-image-light.png",
        output_dir / "wizard-image-dark.png",
        output_dir / "wizard-small-light.png",
        output_dir / "wizard-small-dark.png",
        output_dir / "wizard-back-light.png",
        output_dir / "wizard-back-dark.png",
        dmg_background,
    ]
    build_wizard_panel(logo, generated_paths[0], dark=False)
    build_wizard_panel(logo, generated_paths[1], dark=True)
    build_wizard_small(logo, generated_paths[2], dark=False)
    build_wizard_small(logo, generated_paths[3], dark=True)
    build_wizard_back(logo, generated_paths[4], dark=False)
    build_wizard_back(logo, generated_paths[5], dark=True)
    build_dmg_background(logo, generated_paths[6], dark=False)
    return generated_paths
