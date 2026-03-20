# ruff: noqa: F403, F405
from __future__ import annotations

import shutil
from pathlib import Path

from tests._desktop_ui_testkit_base import *


def _zero_shared_transparent_rgb(expected_rgba, actual_rgba):
    expected_copy = expected_rgba.copy()
    actual_copy = actual_rgba.copy()
    expected_pixels = expected_copy.load()
    actual_pixels = actual_copy.load()
    width, height = expected_copy.size

    for y in range(height):
        for x in range(width):
            if expected_pixels[x, y][3] == 0 and actual_pixels[x, y][3] == 0:
                expected_pixels[x, y] = (0, 0, 0, 0)
                actual_pixels[x, y] = (0, 0, 0, 0)

    return expected_copy, actual_copy


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

        expected_rgba, actual_rgba = _zero_shared_transparent_rgb(expected_rgba, actual_rgba)
        compare_bg = Image.new("RGBA", actual_rgba.size, (255, 255, 255, 255))
        expected_visible = Image.alpha_composite(compare_bg, expected_rgba).convert("RGB")
        actual_visible = Image.alpha_composite(compare_bg, actual_rgba).convert("RGB")
        diff_image = ImageChops.difference(expected_visible, actual_visible)
        if ignore_regions:
            draw = ImageDraw.Draw(diff_image)
            for x, y, width, height in ignore_regions:
                draw.rectangle((x, y, x + width - 1, y + height - 1), fill=(0, 0, 0))
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


__all__ = [name for name in globals() if not (name.startswith("__") and name.endswith("__"))]
