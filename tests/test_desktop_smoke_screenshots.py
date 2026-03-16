from __future__ import annotations

import importlib
from pathlib import Path

from tests.desktop_ui_testkit import (
    DESKTOP_SMOKE_SCREENSHOT_SCENARIOS,
    assert_png_matches_baseline,
    desktop_ui_smoke_output_dir,
    qapp,  # noqa: F401
    resolve_ignore_regions,
    wait_for_scene_contract,
)
from tests.test_chat_view_integration import (
    DummyChatService,
    DummyConfigService,
    EmptyMessagesModel,
    SessionsModel,
    _load_light_main_window,
    _process,
)

pytest = importlib.import_module("pytest")
QtCore = pytest.importorskip("PySide6.QtCore")

Qt = QtCore.Qt

pytestmark = [pytest.mark.desktop_ui_smoke, pytest.mark.usefixtures("qapp")]


def _build_smoke_config_service() -> DummyConfigService:
    config_service = DummyConfigService(
        providers=[
            {
                "name": "primary",
                "type": "openai",
                "apiKey": "sk-test",
                "apiBase": "https://api.openai.com/v1",
            }
        ],
        model="right-gpt/gpt-5.4",
    )
    _ = config_service.save(
        {
            "agents": {
                "defaults": {
                    "model": "right-gpt/gpt-5.4",
                    "utilityModel": "right-gpt/gpt-5.1-codex-mini",
                    "workspace": "~/.bao/workspace",
                }
            },
            "ui": {
                "language": "en",
                "update": {
                    "enabled": True,
                    "autoCheck": False,
                    "channel": "stable",
                    "feedUrl": "https://example.com/desktop-update.json",
                },
            },
        }
    )
    return config_service


def _expected_size(scenario) -> tuple[int, int]:
    return scenario.width or 1100, scenario.height or 720


def _render_screenshot(scenario, output_path: Path) -> tuple[tuple[int, int, int, int], ...]:
    config_service = _build_smoke_config_service()
    chat_service = DummyChatService(
        EmptyMessagesModel(),
        state="idle",
        active_session_ready=False,
        active_session_has_messages=False,
    )
    session_model = SessionsModel([])
    engine, root = _load_light_main_window(
        config_service=config_service,
        session_model=session_model,
        chat_service=chat_service,
    )

    try:
        expected_width, expected_height = _expected_size(scenario)
        _ = root.setProperty("width", expected_width)
        _ = root.setProperty("height", expected_height)
        _ = root.setProperty("startView", scenario.start_view)
        wait_for_scene_contract(root, scenario.scene_contract)

        image = root.grabWindow()
        if image.width() != expected_width or image.height() != expected_height:
            image = image.scaled(
                expected_width,
                expected_height,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        assert image.width() == expected_width
        assert image.height() == expected_height
        assert image.save(str(output_path)), f"failed to save screenshot: {output_path}"
        ignore_regions = resolve_ignore_regions(root, scenario.ignore_regions)
        return ignore_regions
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


@pytest.mark.parametrize("scenario", DESKTOP_SMOKE_SCREENSHOT_SCENARIOS, ids=lambda item: item.name)
def test_desktop_smoke_screenshot_scenarios_render_expected_dimensions(scenario) -> None:
    output_dir = desktop_ui_smoke_output_dir()
    output_path = output_dir / f"{scenario.name}.png"
    if output_path.exists():
        output_path.unlink()

    ignore_regions = _render_screenshot(scenario, output_path)

    assert output_path.is_file(), f"missing screenshot: {output_path}"
    assert output_path.stat().st_size > 0, f"empty screenshot: {output_path}"

    from PIL import Image

    with Image.open(output_path) as image:
        expected_width, expected_height = _expected_size(scenario)
        assert image.size == (expected_width, expected_height), (
            f"unexpected screenshot size for {scenario.name}: {image.size}, output={output_path}"
        )

    assert_png_matches_baseline(
        output_path,
        scenario.name,
        max_changed_pixels=scenario.max_changed_pixels,
        ignore_regions=ignore_regions,
    )
