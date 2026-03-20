# ruff: noqa: F403, F405
from __future__ import annotations

from tests._desktop_build_scripts_testkit import *


def test_build_mac_script_includes_workspace_package_data() -> None:
    text = _read("app/scripts/build_mac.sh")

    assert '--include-data-dir="$PROJECT_ROOT/app/resources=resources"' in text
    assert "--include-package-data=bao.templates.workspace.en:*.md" in text
    assert "--include-package-data=bao.templates.workspace.zh:*.md" in text
    assert "--include-package=bao.templates.workspace" not in text
    assert "workspace=bao/templates/workspace" not in text
    assert "--noinclude-qt-plugins=tls" in text
    assert "imageformats/libqpdf.dylib" in text
    assert 'BUNDLE_IDENTIFIER="io.github.suge8.bao"' in text
    assert 'CODESIGN_IDENTITY="${BAO_MAC_CODESIGN_IDENTITY:--}"' in text
    assert 'plist_set_or_add "$INFO_PLIST" "CFBundleIdentifier" "$BUNDLE_IDENTIFIER"' in text
    assert (
        'plist_set_or_add "$INFO_PLIST" "NSAppleEventsUsageDescription" "$APPLE_EVENTS_USAGE_DESCRIPTION"'
        in text
    )
    assert 'resign_app_bundle "$OUTPUT_APP"' in text
    assert '/usr/bin/codesign --force --deep --sign "$CODESIGN_IDENTITY" "$app_path"' in text
    assert (
        'codesign --force --deep --options runtime --timestamp --sign "$CODESIGN_IDENTITY"' in text
    )


def test_build_mac_pyinstaller_script_includes_desktop_resources() -> None:
    text = _read("app/scripts/build_mac_pyinstaller.sh")

    assert "uv sync --extra desktop-build-pyinstaller" in _read("app/README.md")
    assert 'app/scripts/stage_desktop_resources.py --destination "$STAGED_RESOURCES_DIR"' in text
    assert "uv run python app/scripts/build_qml_rcc.py" in text
    assert '--qml-root "$PROJECT_ROOT/app/qml"' in text
    assert '--output-rcc "$STAGED_RESOURCES_DIR/desktop_qml.rcc"' in text
    assert '--add-data "$STAGED_RESOURCES_DIR:app/resources"' in text
    assert '--add-data "$PROJECT_ROOT/app/qml:app/qml"' not in text
    assert '--add-data "$PROJECT_ROOT/assets:assets"' in text
    assert '--add-data "$PROJECT_ROOT/bao/skills:bao/skills"' in text
    assert '--add-data "$PROJECT_ROOT/bao/templates/workspace:bao/templates/workspace"' in text
    assert "uv run python app/scripts/update_agent_browser_runtime.py" in text
    assert 'app/scripts/sync_browser_runtime.py --source "$BAO_BROWSER_RUNTIME_SOURCE_DIR"' in text
    assert "uv run python app/scripts/verify_browser_runtime.py --require-ready" in text
    assert (
        'app/scripts/sync_browser_runtime.py --source "$RUNTIME_SOURCE_DIR" --destination "$EMBEDDED_RUNTIME_ROOT"'
        in text
    )
    assert (
        'uv run python app/scripts/verify_browser_runtime.py --runtime-root "$EMBEDDED_RUNTIME_ROOT" --require-ready'
        in text
    )
    assert "--collect-submodules bao.channels" in text
    assert "--collect-submodules bao.providers" in text
    assert '--osx-bundle-identifier "$BUNDLE_IDENTIFIER"' in text
    assert 'CODESIGN_IDENTITY="${BAO_MAC_CODESIGN_IDENTITY:--}"' in text
    assert 'plist_set_or_add "$INFO_PLIST" "CFBundleShortVersionString" "$VERSION"' in text
    assert 'plist_set_or_add "$INFO_PLIST" "CFBundleVersion" "$VERSION"' in text
    assert 'plist_set_or_add "$INFO_PLIST" "CFBundleIdentifier" "$BUNDLE_IDENTIFIER"' in text
    assert (
        'plist_set_or_add "$INFO_PLIST" "NSAppleEventsUsageDescription" "$APPLE_EVENTS_USAGE_DESCRIPTION"'
        in text
    )
    assert 'resign_app_bundle "$OUTPUT_APP"' in text
    assert '/usr/bin/codesign --force --deep --sign "$CODESIGN_IDENTITY" "$app_path"' in text
    assert (
        'codesign --force --deep --options runtime --timestamp --sign "$CODESIGN_IDENTITY"' in text
    )


def test_build_win_pyinstaller_script_includes_desktop_resources() -> None:
    text = _read("app/scripts/build_win_pyinstaller.bat")

    assert 'app\\scripts\\stage_desktop_resources.py --destination "%STAGED_RESOURCES_DIR%"' in text
    assert "uv run python app\\scripts\\build_qml_rcc.py" in text
    assert '--qml-root "%PROJECT_ROOT%\\app\\qml"' in text
    assert '--output-rcc "%STAGED_RESOURCES_DIR%\\desktop_qml.rcc"' in text
    assert '--add-data "%STAGED_RESOURCES_DIR%;app\\resources"' in text
    assert '--add-data "%PROJECT_ROOT%\\app\\qml;app\\qml"' not in text
    assert '--add-data "%PROJECT_ROOT%\\assets;assets"' in text
    assert (
        '--add-data "%PROJECT_ROOT%\\bao\\templates\\workspace;bao\\templates\\workspace"' in text
    )
    assert "app\\scripts\\update_agent_browser_runtime.py" in text
    assert 'app\\scripts\\sync_browser_runtime.py --source "%BAO_BROWSER_RUNTIME_SOURCE_DIR%"' in text
    assert "uv run python app\\scripts\\verify_browser_runtime.py --require-ready" in text
    assert (
        'app\\scripts\\sync_browser_runtime.py --source "%RUNTIME_SOURCE_DIR%" --destination "%EMBEDDED_RUNTIME_ROOT%"'
        in text
    )
    assert (
        'uv run python app\\scripts\\verify_browser_runtime.py --runtime-root "%EMBEDDED_RUNTIME_ROOT%" --require-ready'
        in text
    )
    assert "--collect-submodules bao.channels" in text
    assert "--collect-submodules bao.providers" in text


def test_build_win_script_includes_workspace_package_data() -> None:
    text = _read("app/scripts/build_win.bat")

    assert r'--include-data-dir="%PROJECT_ROOT%\app\resources=resources"' in text
    assert "--include-package-data=bao.templates.workspace.en:*.md" in text
    assert "--include-package-data=bao.templates.workspace.zh:*.md" in text
    assert "--include-package=bao.templates.workspace" not in text
    assert r"workspace=bao\templates\workspace" not in text
    assert "--noinclude-qt-plugins=tls" in text


def test_package_win_installer_script_resolves_inno_setup_before_compile() -> None:
    text = _read("app/scripts/package_win_installer.bat")

    assert "resolve_inno_setup.py" in text
    assert "Resolving Inno Setup compiler" in text
    assert "where uv >nul 2>nul" in text
    assert "Missing value for --build-root" in text
    assert 'if not exist "%BUILD_ROOT%\\Bao.exe" (' in text
    assert "if errorlevel 1 (" in text
    assert (
        '"%ISCC_EXE%" /DMyAppVersion=%VERSION% "/DBuildSource=%BUILD_ROOT%" app\\scripts\\bao_installer.iss'
        in text
    )


def test_mac_packaging_scripts_accept_explicit_app_path() -> None:
    dmg = _read("app/scripts/create_dmg.sh")
    update_zip = _read("app/scripts/create_update_zip.sh")

    assert "--app-path" in dmg
    assert "--app-path" in update_zip


def test_mac_packaging_scripts_prefer_pyinstaller_output_by_default() -> None:
    dmg = _read("app/scripts/create_dmg.sh")
    update_zip = _read("app/scripts/create_update_zip.sh")

    assert 'PYINSTALLER_APP_PATH="$PROJECT_ROOT/dist-pyinstaller/dist/$APP_NAME.app"' in dmg
    assert 'NUITKA_APP_PATH="$PROJECT_ROOT/dist/$APP_NAME.app"' in dmg
    assert 'if [[ -d "$PYINSTALLER_APP_PATH" ]]; then' in dmg
    assert 'APP_PATH="$PYINSTALLER_APP_PATH"' in dmg
    assert 'APP_PATH="$NUITKA_APP_PATH"' in dmg
    assert 'PYINSTALLER_APP_PATH="$PROJECT_ROOT/dist-pyinstaller/dist/$APP_NAME.app"' in update_zip
    assert 'NUITKA_APP_PATH="$PROJECT_ROOT/dist/$APP_NAME.app"' in update_zip


def test_mac_dmg_packaging_refreshes_shared_brand_assets() -> None:
    dmg = _read("app/scripts/create_dmg.sh")

    assert "generate_installer_assets.py" in dmg
    assert '--dmg-background "$PROJECT_ROOT/app/resources/dmg-background.png"' in dmg
    assert 'echo "▸ Refreshing brand assets..."' in dmg


def test_windows_installer_prefers_pyinstaller_output_by_default() -> None:
    text = _read("app/scripts/package_win_installer.bat")

    assert 'for %%i in ("%PROJECT_ROOT%") do set "PROJECT_ROOT=%%~fi"' in text
    assert 'set "PYINSTALLER_BUILD_ROOT=%PROJECT_ROOT%\\dist-pyinstaller\\dist\\Bao"' in text
    assert 'set "NUITKA_BUILD_ROOT=%PROJECT_ROOT%\\dist\\build-win-x64\\main.dist"' in text
    assert 'if exist "%PYINSTALLER_BUILD_ROOT%\\Bao.exe" (' in text
    assert 'set "BUILD_ROOT=%PYINSTALLER_BUILD_ROOT%"' in text
    assert 'set "BUILD_ROOT=%NUITKA_BUILD_ROOT%"' in text
    assert 'set "REQUIRE_PRIMARY=0"' in text
    assert 'if /I "%~1"=="--require-primary" (' in text
    assert 'for %%i in ("%BUILD_ROOT%") do set "BUILD_ROOT=%%~fi"' in text
    assert 'if /I "%BAO_DESKTOP_REQUIRE_PRIMARY%"=="1" (' in text
