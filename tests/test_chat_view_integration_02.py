# ruff: noqa: E402, N802, N815, F403, F405, I001
from __future__ import annotations

from tests._chat_view_integration_testkit import *

@pytest.mark.parametrize(
    ("provider_row", "expected_name", "expected_type", "expected_api_base"),
    [
        (
            {"name": "anthropic", "type": "anthropic", "apiKey": "sk-old", "apiBase": ""},
            "anthropic",
            "anthropic",
            "",
        ),
        (
            {
                "name": "openrouter",
                "type": "openai",
                "apiKey": "sk-old",
                "apiBase": "https://openrouter.ai/api/v1",
            },
            "openrouter",
            "openai",
            "https://openrouter.ai/api/v1",
        ),
    ],
)
def test_onboarding_provider_save_stays_in_sync(
    qapp,
    provider_row: dict[str, object],
    expected_name: str,
    expected_type: str,
    expected_api_base: str,
):
    _ = qapp
    config_service = DummyConfigService(
        is_valid=False,
        needs_setup=True,
        providers=[{"name": "primary", "type": "openai", "apiKey": "sk-old", "apiBase": ""}],
    )
    engine, root = _load_main_window(config_service)

    try:
        settings_view = _find_object(root, "settingsView")

        _ = settings_view.setProperty("_providerList", [provider_row])
        _process(30)

        assert QMetaObject.invokeMethod(settings_view, "saveOnboardingProviderStep")

        assert isinstance(config_service.last_saved_changes, dict)
        providers = config_service.last_saved_changes.get("providers")
        assert isinstance(providers, dict)
        assert providers[expected_name]["type"] == expected_type
        assert providers[expected_name]["apiKey"] == "sk-old"
        assert providers[expected_name]["apiBase"] == expected_api_base
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_settings_select_missing_value_does_not_emit_default_current_value(qapp):
    _ = qapp
    qml_import = (PROJECT_ROOT / "app" / "qml").as_uri()
    engine, root = _load_inline_qml(
        f'''
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "{qml_import}"

Item {{
    width: 320
    height: 120

    SettingsSelect {{
        id: select
        objectName: "settingsSelect"
        label: "Context"
        dotpath: "agents.defaults.contextManagement"
        options: [
            {{"label": "off", "value": "off"}},
            {{"label": "auto", "value": "auto"}}
        ]
    }}
}}
'''
    )

    try:
        select = _find_object(root, "settingsSelect")
        _process(0)
        assert select.property("currentValue") is None
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_channel_row_toggle_click_updates_checked_state(qapp):
    _ = qapp
    engine, root = _load_main_window()

    try:
        settings_view = _find_object(root, "settingsView")
        _ = root.setProperty("startView", "settings")
        _ = settings_view.setProperty("_activeTab", 1)
        _process(30)

        toggle = _find_object_by_property(root, "dotpath", "channels.telegram.enabled")
        assert toggle.property("checked") is False
        assert toggle.property("currentValue") is None

        QTest.mouseClick(root, Qt.LeftButton, Qt.NoModifier, _center_point(toggle))
        _process(0)

        assert toggle.property("checked") is True
        assert toggle.property("currentValue") is True
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_channel_section_save_ignores_untouched_disabled_toggle(qapp):
    _ = qapp
    config_service = DummyConfigService(channels={"telegram": {"token": "123456:ABC"}})
    engine, root = _load_main_window(config_service)

    try:
        settings_view = _find_object(root, "settingsView")
        _ = root.setProperty("startView", "settings")
        _ = settings_view.setProperty("_activeTab", 1)
        _process(30)

        save_button = _find_visible_object_by_property(root, "text", "Save")
        QTest.mouseClick(root, Qt.LeftButton, Qt.NoModifier, _center_point(save_button))
        _process(30)

        assert isinstance(config_service.last_saved_changes, dict)
        assert "channels.telegram.enabled" not in config_service.last_saved_changes
        assert config_service.last_saved_changes.get("channels.telegram.token") == "123456:ABC"
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_channel_section_save_persists_touched_toggle(qapp):
    _ = qapp
    config_service = DummyConfigService(channels={"telegram": {"token": "123456:ABC"}})
    engine, root = _load_main_window(config_service)

    try:
        settings_view = _find_object(root, "settingsView")
        _ = root.setProperty("startView", "settings")
        _ = settings_view.setProperty("_activeTab", 1)
        _process(30)

        toggle = _find_object_by_property(root, "dotpath", "channels.telegram.enabled")
        QTest.mouseClick(root, Qt.LeftButton, Qt.NoModifier, _center_point(toggle))
        _process(0)

        save_button = _find_visible_object_by_property(root, "text", "Save")
        QTest.mouseClick(root, Qt.LeftButton, Qt.NoModifier, _center_point(save_button))
        _process(30)

        assert isinstance(config_service.last_saved_changes, dict)
        assert config_service.last_saved_changes.get("channels.telegram.enabled") is True
        assert config_service.last_saved_changes.get("channels.telegram.token") == "123456:ABC"
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_add_new_provider_expands_new_card(qapp):
    _ = qapp
    engine, root = _load_main_window()

    try:
        _ = root.setProperty("startView", "settings")
        settings_view = _find_object(root, "settingsView")
        _process(30)

        assert QMetaObject.invokeMethod(settings_view, "_addNewProvider")
        for _ in range(8):
            _process(30)
            provider_list = _provider_list_snapshot(settings_view)
            if isinstance(provider_list, list) and len(provider_list) == 1:
                break

        provider_list = _provider_list_snapshot(settings_view)
        assert len(provider_list) == 1
        assert provider_list[0]["name"] == "primary"
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


@pytest.mark.desktop_ui_smoke
def test_settings_add_provider_click_works_with_focused_editor(qapp):
    _ = qapp
    config_service = DummyConfigService(
        model="openai/gpt-4o",
        providers=[{"name": "primary", "type": "openai", "apiKey": "sk-ready", "apiBase": ""}],
    )
    engine, root = _load_main_window(config_service)
    focus_filter: WindowFocusDismissFilter | None = None

    try:
        focus_filter = _install_focus_filter(root)
        _ = root.setProperty("startView", "settings")
        settings_view = _find_object(root, "settingsView")
        _process(30)

        workspace_field = _find_object_by_property(root, "placeholderText", "~/.bao/workspace")
        settings_scroll = _find_object(root, "settingsScroll")
        add_provider_button = _find_object(root, "addProviderHitArea")
        initial_content_y = settings_scroll.property("contentItem").property("contentY")

        workspace_field.forceActiveFocus()
        _process(0)
        assert len(_provider_list_snapshot(settings_view)) == 1

        _scroll_item_into_view(root, settings_scroll, add_provider_button)

        QTest.mouseClick(root, Qt.LeftButton, Qt.NoModifier, _center_point(add_provider_button))
        _process(150)

        assert bool(workspace_field.property("activeFocus")) is False
        assert settings_view.property("_pendingExpandProviderName") == ""
        assert len(_provider_list_snapshot(settings_view)) == 2
        assert settings_scroll.property("contentItem").property("contentY") > initial_content_y
    finally:
        _remove_focus_filter(root, focus_filter)
        root.deleteLater()
        engine.deleteLater()
        _process(0)
