# ruff: noqa: F403, F405
from __future__ import annotations

from tests._desktop_build_scripts_testkit import *


def test_inno_setup_script_vendors_simplified_chinese_language_file() -> None:
    text = _read("app/scripts/bao_installer.iss")

    assert "ChineseSimplified.isl" in text
    assert "MessagesFile" in text


def test_desktop_release_workflow_supports_rebuilding_existing_tag() -> None:
    text = _read(".github/workflows/desktop-release.yml")

    assert "workflow_dispatch:" in text
    assert "release_ref:" in text
    assert "source_ref: ${{ steps.resolve.outputs.source_ref }}" in text
    assert "ref: ${{ needs.resolve-release.outputs.source_ref }}" in text
    assert "tag_name: ${{ needs.resolve-release.outputs.release_tag }}" in text
    assert "Validate desktop packaging guard rails" in text


def test_desktop_release_workflow_uses_pyinstaller_as_primary_packager() -> None:
    text = _read(".github/workflows/desktop-release.yml")

    build_mac_section = text.split("  build-mac:", maxsplit=1)[1].split(
        "  preflight-windows-installer:", maxsplit=1
    )[0]
    assert "desktop-build-pyinstaller" in build_mac_section
    assert "BAO_DESKTOP_REQUIRE_BROWSER_RUNTIME: '1'" in build_mac_section
    assert "uses: actions/setup-node@v4" in build_mac_section
    assert "node-version: '20'" in build_mac_section
    assert "Refresh managed browser runtime" in build_mac_section
    assert "uv run python app/scripts/update_agent_browser_runtime.py" in build_mac_section
    assert "build_mac_pyinstaller.sh" in build_mac_section
    assert "create_dmg.sh --arch ${{ matrix.arch }} --app-path" in build_mac_section
    assert "create_update_zip.sh --arch ${{ matrix.arch }} --app-path" in build_mac_section
    assert "Detect macOS signing mode" in build_mac_section
    assert "Import Developer ID certificate" in build_mac_section
    assert "Notarize app bundle" in build_mac_section
    assert "Staple app bundle" in build_mac_section
    assert "Notarize DMG" in build_mac_section
    assert "Staple DMG" in build_mac_section
    assert "ccache" not in build_mac_section
    assert "nuitka" not in build_mac_section.lower()


def test_desktop_release_workflow_macos_signing_is_optional() -> None:
    text = _read(".github/workflows/desktop-release.yml")

    assert "BAO_MAC_CODESIGN_IDENTITY" in text
    assert "BAO_MAC_CERT_P12_BASE64" in text
    assert "BAO_MAC_CERT_P12_PASSWORD" in text
    assert "BAO_MAC_NOTARY_APPLE_ID" in text
    assert "BAO_MAC_NOTARY_TEAM_ID" in text
    assert "BAO_MAC_NOTARY_PASSWORD" in text
    assert "BAO_MAC_SIGNING_ENABLED=true" in text
    assert "BAO_MAC_SIGNING_ENABLED=false" in text
    assert "release artifacts will be built without Developer ID signing or notarization" in text
    assert "security import" in text
    assert "xcrun notarytool submit" in text
    assert "xcrun stapler staple" in text
    assert "if: env.BAO_MAC_SIGNING_ENABLED == 'true'" in text


def test_desktop_release_workflow_checks_inno_setup_before_windows_build() -> None:
    text = _read(".github/workflows/desktop-release.yml")

    preflight_index = text.index("  preflight-windows-installer:")
    build_index = text.index("        run: app\\scripts\\build_win_pyinstaller.bat")
    assert preflight_index < build_index
    assert "Validate Inno Setup toolchain early" in text
    assert "BAO_ISCC_EXE=$resolved" in text
    assert "choco install innosetup --version=${{ env.INNOSETUP_VERSION }} -y" in text
    assert "uses: actions/setup-node@v4" in text
    assert "node-version: '20'" in text
    assert "Refresh managed browser runtime" in text
    assert "uv run python app/scripts/update_agent_browser_runtime.py" in text
    assert "BAO_DESKTOP_REQUIRE_BROWSER_RUNTIME: '1'" in text
    assert "BAO_DESKTOP_REQUIRE_PRIMARY: '1'" in text
    assert (
        "package_win_installer.bat --require-primary --build-root dist-pyinstaller\\dist\\Bao"
        in text
    )


def test_desktop_ci_lite_uses_pyinstaller_build_dependencies() -> None:
    text = _read(".github/workflows/desktop-ci-lite.yml")

    assert "desktop-build-pyinstaller" in text
    assert "BAO_DESKTOP_REQUIRE_BROWSER_RUNTIME: '1'" in text
    assert "uses: actions/setup-node@v4" in text
    assert "node-version: '20'" in text
    assert "Refresh managed browser runtime" in text
    assert "uv run python app/scripts/update_agent_browser_runtime.py" in text
    assert "Verify managed browser runtime" in text
    assert "verify_browser_runtime.py --require-ready" in text
    assert "build_mac_pyinstaller.sh" in text
    assert "build_win_pyinstaller.bat" in text
    assert "Ensure Inno Setup" in text
    assert "Create installer smoke artifact" in text
    assert "Validate installer artifact exists" in text
    assert "choco install innosetup --version=${{ env.INNOSETUP_VERSION }} -y" in text


def test_desktop_release_validation_job_does_not_depend_on_uv_cache() -> None:
    text = _read(".github/workflows/desktop-release.yml")

    validate_section = text.split("  validate-version:", maxsplit=1)[1].split(
        "  build-mac:", maxsplit=1
    )[0]
    assert "uses: astral-sh/setup-uv@v4" in validate_section
    assert "enable-cache: true" not in validate_section
