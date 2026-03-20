from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path
from typing import cast

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _render_module():
    return importlib.import_module("app.scripts._installer_assets_render")


def build_wizard_panel(logo: Image.Image, output: Path, *, dark: bool) -> None:
    _render_module().build_wizard_panel(logo, output, dark=dark)


def build_wizard_small(logo: Image.Image, output: Path, *, dark: bool) -> None:
    _render_module().build_wizard_small(logo, output, dark=dark)


def build_wizard_back(logo: Image.Image, output: Path, *, dark: bool) -> None:
    _render_module().build_wizard_back(logo, output, dark=dark)


def build_dmg_background(logo: Image.Image, output: Path, *, dark: bool = False) -> None:
    _render_module().build_dmg_background(logo, output, dark=dark)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate unified Windows installer and macOS DMG brand assets"
    )
    _ = parser.add_argument(
        "--source",
        default="app/resources/logo-circle.png",
        help="Source logo path (default: app/resources/logo-circle.png)",
    )
    _ = parser.add_argument(
        "--output-dir",
        default="app/resources/installer",
        help="Output directory for installer PNG assets",
    )
    _ = parser.add_argument(
        "--dmg-background",
        default="app/resources/dmg-background.png",
        help="Output path for the macOS DMG background image",
    )
    args = parser.parse_args()
    source = Path(cast(str, args.source)).expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(f"Source logo not found: {source}")
    output_dir = Path(cast(str, args.output_dir)).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    dmg_background = Path(cast(str, args.dmg_background)).expanduser().resolve()
    dmg_background.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as raw_logo:
        logo = raw_logo.convert("RGBA")
    generated_paths = _render_module().build_all_assets(logo, output_dir, dmg_background)
    print(f"Generated brand assets in {output_dir} and {dmg_background.parent}")
    for path in generated_paths:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
