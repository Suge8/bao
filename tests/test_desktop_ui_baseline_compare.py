from __future__ import annotations

from pathlib import Path

from PIL import Image

from tests._desktop_ui_testkit_baseline import assert_png_matches_baseline


def _write_png(path: Path, pixels: list[tuple[int, int, int, int]]) -> None:
    image = Image.new("RGBA", (2, 2))
    image.putdata(pixels)
    image.save(path)


def _patch_baseline_dir(tmp_path: Path, monkeypatch) -> Path:
    baseline_dir = tmp_path / "baselines"
    baseline_dir.mkdir()
    monkeypatch.setattr(
        "tests._desktop_ui_testkit_baseline.desktop_ui_baseline_dir",
        lambda: baseline_dir,
    )
    return baseline_dir


def test_assert_png_matches_baseline_ignores_rgb_drift_inside_shared_transparent_pixels(
    tmp_path: Path,
    monkeypatch,
) -> None:
    baseline_dir = _patch_baseline_dir(tmp_path, monkeypatch)
    baseline_path = baseline_dir / "transparent.png"
    actual_path = tmp_path / "actual.png"

    _write_png(
        baseline_path,
        [
            (255, 255, 255, 255),
            (10, 20, 30, 0),
            (255, 255, 255, 255),
            (255, 255, 255, 255),
        ],
    )
    _write_png(
        actual_path,
        [
            (255, 255, 255, 255),
            (200, 180, 160, 0),
            (255, 255, 255, 255),
            (255, 255, 255, 255),
        ],
    )

    assert_png_matches_baseline(actual_path, "transparent", max_changed_pixels=0)


def test_assert_png_matches_baseline_still_flags_visible_pixel_changes(
    tmp_path: Path,
    monkeypatch,
) -> None:
    baseline_dir = _patch_baseline_dir(tmp_path, monkeypatch)
    baseline_path = baseline_dir / "visible.png"
    actual_path = tmp_path / "actual-visible.png"

    _write_png(
        baseline_path,
        [
            (255, 255, 255, 255),
            (255, 255, 255, 255),
            (255, 255, 255, 255),
            (255, 255, 255, 255),
        ],
    )
    _write_png(
        actual_path,
        [
            (255, 255, 255, 255),
            (0, 0, 0, 255),
            (255, 255, 255, 255),
            (255, 255, 255, 255),
        ],
    )

    try:
        assert_png_matches_baseline(actual_path, "visible", max_changed_pixels=0)
    except AssertionError as exc:
        assert "visual regression" in str(exc)
    else:
        raise AssertionError("visible pixel differences should still fail baseline compare")
