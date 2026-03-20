from __future__ import annotations

import argparse
import importlib
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class _IconModules:
    image: object
    chops: object
    draw: object
    filter: object


@dataclass(frozen=True)
class _IconFrame:
    inner: int
    radius: int
    size: int


def _load_pil_modules() -> _IconModules:
    return _IconModules(
        image=importlib.import_module("PIL.Image"),
        chops=importlib.import_module("PIL.ImageChops"),
        draw=importlib.import_module("PIL.ImageDraw"),
        filter=importlib.import_module("PIL.ImageFilter"),
    )


def _crop_square_image(image_mod, source: Path):
    img = image_mod.open(source).convert("RGBA")
    side = min(img.width, img.height)
    left = (img.width - side) // 2
    top = (img.height - side) // 2
    return img.crop((left, top, left + side, top + side))


def _build_shadow(modules: _IconModules, frame: _IconFrame):
    shadow = modules.image.new("RGBA", (frame.inner, frame.inner), (0, 0, 0, 0))
    shadow_alpha = modules.image.new("L", (frame.inner, frame.inner), 0)
    modules.draw.Draw(shadow_alpha).rounded_rectangle(
        (0, 0, frame.inner - 1, frame.inner - 1),
        radius=frame.radius,
        fill=170,
    )
    shadow_alpha = shadow_alpha.filter(modules.filter.GaussianBlur(max(2, frame.size // 120)))
    shadow.putalpha(shadow_alpha)
    return shadow


def _build_highlight(modules: _IconModules, frame: _IconFrame, mask):
    highlight_alpha = modules.image.new("L", (frame.inner, frame.inner), 0)
    hdraw = modules.draw.Draw(highlight_alpha)
    top_stop = int(frame.inner * 0.62)
    for y in range(top_stop):
        t = y / max(1, top_stop - 1)
        alpha = int((1.0 - t) ** 1.6 * 105)
        hdraw.line((0, y, frame.inner, y), fill=alpha)
    highlight_alpha = modules.chops.multiply(highlight_alpha, mask)
    highlight = modules.image.new("RGBA", (frame.inner, frame.inner), (255, 255, 255, 0))
    highlight.putalpha(highlight_alpha)
    return highlight


def _build_shade(modules: _IconModules, frame: _IconFrame, mask):
    shade_alpha = modules.image.new("L", (frame.inner, frame.inner), 0)
    sdraw = modules.draw.Draw(shade_alpha)
    start = int(frame.inner * 0.58)
    for y in range(start, frame.inner):
        t = (y - start) / max(1, frame.inner - start - 1)
        alpha = int((t**1.2) * 38)
        sdraw.line((0, y, frame.inner, y), fill=alpha)
    shade_alpha = modules.chops.multiply(shade_alpha, mask)
    shade = modules.image.new("RGBA", (frame.inner, frame.inner), (0, 0, 0, 0))
    shade.putalpha(shade_alpha)
    return shade


def _build_stroke(modules: _IconModules, frame: _IconFrame):
    stroke = modules.image.new("RGBA", (frame.inner, frame.inner), (0, 0, 0, 0))
    stroke_draw = modules.draw.Draw(stroke)
    stroke_w = max(2, frame.size // 256)
    stroke_draw.rounded_rectangle(
        (
            stroke_w // 2,
            stroke_w // 2,
            frame.inner - 1 - stroke_w // 2,
            frame.inner - 1 - stroke_w // 2,
        ),
        radius=max(1, frame.radius - stroke_w // 2),
        outline=(255, 255, 255, 88),
        width=stroke_w,
    )
    return stroke


def _build_rounded_base(source: Path, size: int = 1024):
    modules = _load_pil_modules()
    square = _crop_square_image(modules.image, source)

    canvas = modules.image.new("RGBA", (size, size), (0, 0, 0, 0))
    inner = int(size * 0.88)
    radius = int(inner * 0.24)
    frame = _IconFrame(inner=inner, radius=radius, size=size)

    artwork = square.resize((inner, inner), modules.image.Resampling.LANCZOS)
    mask = modules.image.new("L", (inner, inner), 0)
    draw = modules.draw.Draw(mask)
    draw.rounded_rectangle((0, 0, inner - 1, inner - 1), radius=radius, fill=255)

    shadow = _build_shadow(modules, frame)

    layer = modules.image.new("RGBA", (inner, inner), (0, 0, 0, 0))
    layer.paste(artwork, (0, 0), mask)

    highlight = _build_highlight(modules, frame, mask)
    shade = _build_shade(modules, frame, mask)
    stroke = _build_stroke(modules, frame)

    offset = (size - inner) // 2
    canvas.alpha_composite(shadow, (offset, offset + max(1, size // 72)))
    canvas.alpha_composite(layer, (offset, offset))
    canvas.alpha_composite(highlight, (offset, offset))
    canvas.alpha_composite(shade, (offset, offset))
    canvas.alpha_composite(stroke, (offset, offset))
    return canvas


def _save_ico(base, output: Path) -> None:
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    output.parent.mkdir(parents=True, exist_ok=True)
    base.save(output, format="ICO", sizes=sizes)


def _save_icns(base, output: Path) -> None:
    image_mod = importlib.import_module("PIL.Image")
    iconutil = shutil.which("iconutil")
    if not iconutil:
        raise RuntimeError("iconutil not found; generate .icns on macOS only")

    with tempfile.TemporaryDirectory(prefix="Bao-iconset-") as tmp:
        iconset = Path(tmp) / "logo.iconset"
        iconset.mkdir(parents=True, exist_ok=True)

        sizes = [
            (16, "icon_16x16.png"),
            (32, "icon_16x16@2x.png"),
            (32, "icon_32x32.png"),
            (64, "icon_32x32@2x.png"),
            (128, "icon_128x128.png"),
            (256, "icon_128x128@2x.png"),
            (256, "icon_256x256.png"),
            (512, "icon_256x256@2x.png"),
            (512, "icon_512x512.png"),
            (1024, "icon_512x512@2x.png"),
        ]
        for px, name in sizes:
            base.resize((px, px), image_mod.Resampling.LANCZOS).save(iconset / name, format="PNG")

        output.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [iconutil, "-c", "icns", str(iconset), "-o", str(output)],
            check=True,
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate rounded macOS/Windows desktop icons from a JPG logo"
    )
    parser.add_argument(
        "--source", default="assets/logo.jpg", help="Source image path (default: assets/logo.jpg)"
    )
    parser.add_argument("--ico", default="app/resources/logo.ico", help="Output .ico path")
    parser.add_argument("--icns", default="assets/logo.icns", help="Output .icns path")
    args = parser.parse_args()

    source = Path(args.source).expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(f"Source logo not found: {source}")

    base = _build_rounded_base(source)
    _save_ico(base, Path(args.ico).expanduser().resolve())
    _save_icns(base, Path(args.icns).expanduser().resolve())
    print("Generated rounded icons:")
    print(f"- {Path(args.ico).expanduser().resolve()}")
    print(f"- {Path(args.icns).expanduser().resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
