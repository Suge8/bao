#!/bin/bash

set -euo pipefail

cd "$(dirname "$0")/.." || exit 1

OUT_DIR="${1:-/tmp/bao-desktop-ui-baseline-refresh}"
mkdir -p "$OUT_DIR"

export BAO_DESKTOP_UI_SMOKE_DIR="$OUT_DIR"
export BAO_DESKTOP_UI_UPDATE_BASELINES=1

PYTHONPATH=. uv run python -m pytest -q tests/test_desktop_smoke_screenshots.py -m desktop_ui_smoke

echo "desktop ui baselines updated from: $OUT_DIR"
