# ruff: noqa: F403, F405
from __future__ import annotations

from tests._desktop_build_scripts_testkit import *


def test_workspace_template_directories_exist() -> None:
    assert (PROJECT_ROOT / "bao/templates/workspace").is_dir()
    assert (PROJECT_ROOT / "bao/templates/workspace/en").is_dir()
    assert (PROJECT_ROOT / "bao/templates/workspace/zh").is_dir()
    assert (PROJECT_ROOT / "bao/templates/workspace/en/INSTRUCTIONS.md").is_file()
    assert (PROJECT_ROOT / "bao/templates/workspace/en/PERSONA.md").is_file()
    assert (PROJECT_ROOT / "bao/templates/workspace/en/HEARTBEAT.md").is_file()
    assert (PROJECT_ROOT / "bao/templates/workspace/zh/INSTRUCTIONS.md").is_file()
    assert (PROJECT_ROOT / "bao/templates/workspace/zh/PERSONA.md").is_file()
    assert (PROJECT_ROOT / "bao/templates/workspace/zh/HEARTBEAT.md").is_file()
    assert (PROJECT_ROOT / "app/resources/installer/ChineseSimplified.isl").is_file()
    assert (PROJECT_ROOT / "app/resources/runtime/browser/README.md").is_file()
    assert (PROJECT_ROOT / "app/resources/runtime/browser/runtime.json").is_file()


def test_bundled_desktop_font_exists() -> None:
    assert (PROJECT_ROOT / "app/resources/fonts/OPPO Sans.ttf").is_file()


def test_bundled_windows_icon_exists() -> None:
    assert (PROJECT_ROOT / "app/resources/logo.ico").is_file()


def test_vendored_chinese_language_file_covers_previous_missing_keys() -> None:
    text = _read("app/resources/installer/ChineseSimplified.isl")

    assert "SelectDirBrowseLabel" in text
    assert "DiskSpaceMBLabel" in text
    assert "PrivilegesRequiredOverrideTitle" in text


def test_windows_icon_pipeline_uses_single_bundled_ico() -> None:
    build_win = _read("app/scripts/build_win.bat")
    installer = _read("app/scripts/bao_installer.iss")
    app_readme = _read("app/README.md")
    main_py = _read("app/main.py")

    assert r'--windows-icon-from-ico="%PROJECT_ROOT%\app\resources\logo.ico"' in build_win
    assert r"SetupIconFile=..\resources\logo.ico" in installer
    assert "app/resources/logo.ico" in app_readme
    assert "WINDOWS_APP_ICON_RELATIVE_PATHS" in main_py
