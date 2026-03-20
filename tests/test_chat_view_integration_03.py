# ruff: noqa: E402, N802, N815, F403, F405, I001
from __future__ import annotations

from tests._chat_view_integration_testkit import *

@pytest.mark.desktop_ui_smoke
def test_chat_composer_stays_within_window_bounds_at_minimum_window_size(qapp):
    _ = qapp
    engine, root = _load_main_window(
        desktop_preferences=DummyDesktopPreferences(ui_language="en", theme_mode="light", is_dark=False)
    )

    try:
        _ = root.setProperty("width", root.property("minimumWidth"))
        _ = root.setProperty("height", root.property("minimumHeight"))
        composer_bar = _find_object(root, "composerBar")
        message_input = _find_object(root, "chatMessageInput")
        message_list = _find_object(root, "chatMessageList")

        def _composer_within_bounds() -> bool:
            top_left = composer_bar.mapToScene(QPointF(0, 0))
            left = float(top_left.x())
            top = float(top_left.y())
            right = left + float(composer_bar.property("width"))
            bottom = top + float(composer_bar.property("height"))
            window_width = float(root.property("width"))
            window_height = float(root.property("height"))
            return (
                left >= 11.5
                and top >= 11.5
                and right <= window_width - 11.5
                and bottom <= window_height - 11.5
            )

        _wait_until(_composer_within_bounds, attempts=30, step_ms=20)

        composer_top = composer_bar.mapToScene(QPointF(0, 0)).y()
        list_bottom = message_list.mapToScene(
            QPointF(0, float(message_list.property("height")))
        ).y()

        _assert_item_within_window(root, composer_bar, inset=12.0)
        assert composer_top >= list_bottom - 2.0
        assert float(message_input.property("width")) >= 220.0
        assert float(message_input.property("height")) >= 40.0
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


@pytest.mark.desktop_ui_smoke
def test_settings_add_provider_button_stays_actionable_at_minimum_window_size(qapp):
    _ = qapp
    config_service = DummyConfigService(
        model="openai/gpt-4o",
        providers=[{"name": "primary", "type": "openai", "apiKey": "sk-ready", "apiBase": ""}],
    )
    engine, root = _load_main_window(
        config_service,
        desktop_preferences=DummyDesktopPreferences(ui_language="en", theme_mode="light", is_dark=False),
    )

    try:
        _ = root.setProperty("width", root.property("minimumWidth"))
        _ = root.setProperty("height", root.property("minimumHeight"))
        _ = root.setProperty("startView", "settings")
        _process(80)

        settings_view = _find_object(root, "settingsView")
        settings_scroll = _find_object(root, "settingsScroll")
        add_provider_button = _find_object(root, "addProviderHitArea")

        _scroll_item_into_view(root, settings_scroll, add_provider_button)
        _assert_item_within_window(root, add_provider_button, inset=12.0)

        initial_count = len(_provider_list_snapshot(settings_view))
        QTest.mouseClick(root, Qt.LeftButton, Qt.NoModifier, _center_point(add_provider_button))
        _wait_until(
            lambda: len(_provider_list_snapshot(settings_view)) == initial_count + 1,
            attempts=40,
            step_ms=20,
        )
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


@pytest.mark.desktop_ui_smoke
def test_onboarding_long_add_provider_cta_stays_within_minimum_window_width(qapp):
    _ = qapp
    config_service = DummyConfigService(is_valid=False, needs_setup=True, language="en")
    engine, root = _load_main_window(
        config_service,
        desktop_preferences=DummyDesktopPreferences(ui_language="en", theme_mode="light", is_dark=False),
    )

    try:
        _ = root.setProperty("width", root.property("minimumWidth"))
        _ = root.setProperty("height", root.property("minimumHeight"))
        _process(80)

        settings_view = _find_object(root, "settingsView")
        settings_scroll = _find_object(root, "settingsScroll")
        add_provider_button = _find_object(root, "addProviderHitArea")

        assert bool(root.property("setupMode")) is True
        assert bool(settings_view.property("onboardingMode")) is True
        _scroll_item_into_view(root, settings_scroll, add_provider_button)
        _assert_item_within_window(root, add_provider_button, inset=12.0)

        initial_count = len(_provider_list_snapshot(settings_view))
        QTest.mouseClick(root, Qt.LeftButton, Qt.NoModifier, _center_point(add_provider_button))
        _process(150)

        assert len(_provider_list_snapshot(settings_view)) == initial_count + 1
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


@pytest.mark.desktop_ui_smoke
def test_settings_save_click_works_with_open_settings_select_popup(qapp):
    _ = qapp
    config_service = DummyConfigService(
        model="openai/gpt-4o",
        providers=[{"name": "primary", "type": "openai", "apiKey": "sk-ready", "apiBase": ""}],
    )
    engine, root = _load_main_window(config_service)

    try:
        _ = root.setProperty("startView", "settings")
        popup_owner = _find_visible_object_by_property(root, "popupOpen", False)
        save_button = _find_visible_object_by_property(root, "text", "Save")
        _process(30)

        popup_owner.openPopup()
        _process(100)

        assert bool(popup_owner.property("popupOpen")) is True

        QTest.mouseClick(root, Qt.LeftButton, Qt.NoModifier, _center_point(save_button))
        _process(100)

        assert isinstance(config_service.last_saved_changes, dict)
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_settings_channel_header_click_works_with_focused_editor(qapp):
    _ = qapp
    config_service = DummyConfigService(
        model="openai/gpt-4o",
        providers=[{"name": "primary", "type": "openai", "apiKey": "sk-ready", "apiBase": ""}],
        channels={"telegram": {"enabled": True, "token": "123456:ABC"}},
    )
    engine, root = _load_main_window(config_service)
    focus_filter: WindowFocusDismissFilter | None = None

    try:
        focus_filter = _install_focus_filter(root)
        _ = root.setProperty("startView", "settings")
        settings_view = _find_object(root, "settingsView")
        _ = settings_view.setProperty("_activeTab", 1)
        _process(30)

        workspace_field = _find_object_by_property(root, "placeholderText", "~/.bao/workspace")
        channel_row = _find_object(root, "channelRow_telegram")
        channel_header = _find_object(root, "channelHeader_telegram")

        workspace_field.forceActiveFocus()
        _process(0)

        assert bool(workspace_field.property("activeFocus")) is True
        assert bool(channel_row.property("expanded")) is False

        QTest.mouseClick(root, Qt.LeftButton, Qt.NoModifier, _center_point(channel_header))
        _process(50)

        assert bool(channel_row.property("expanded")) is True
        assert bool(workspace_field.property("activeFocus")) is False

        QTest.mouseClick(root, Qt.LeftButton, Qt.NoModifier, _center_point(channel_header))
        _process(50)

        assert bool(channel_row.property("expanded")) is False
    finally:
        _remove_focus_filter(root, focus_filter)
        root.deleteLater()
        engine.deleteLater()
        _process(0)


@pytest.mark.parametrize("initial_enabled", [False, True])
def test_channel_section_save_preserves_existing_enabled_value(qapp, initial_enabled):
    _ = qapp
    config_service = DummyConfigService(
        channels={"telegram": {"enabled": initial_enabled, "token": "123456:ABC"}}
    )
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
        assert config_service.last_saved_changes.get("channels.telegram.enabled") is initial_enabled
        assert config_service.last_saved_changes.get("channels.telegram.token") == "123456:ABC"
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_onboarding_final_cta_requires_model_selection(qapp):
    _ = qapp
    config_service = DummyConfigService(
        is_valid=False,
        needs_setup=True,
        providers=[{"name": "primary", "type": "openai", "apiKey": "sk-ready", "apiBase": ""}],
    )
    engine, root = _load_main_window(config_service)

    try:
        settings_view = _find_object(root, "settingsView")
        model_section = _find_object_by_property(
            settings_view, "actionText", "Save and start chatting"
        )
        model_field = _find_object(root, "onboardingPrimaryModelField")

        _process(30)
        assert settings_view.property("providerConfigured") is True
        assert settings_view.property("onboardingModelReady") is False
        assert model_section.property("actionEnabled") is False

        model_field.setCurrentText("openai/gpt-4o")
        _process(30)

        assert settings_view.property("onboardingModelReady") is True
        assert model_section.property("actionEnabled") is True
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_sidebar_empty_state_click_creates_new_session(qapp):
    _ = qapp
    engine, root = _load_main_window()

    try:
        session_service = engine._test_refs["session_service"]
        empty_state = _find_object(root, "sidebarEmptyState")

        assert bool(empty_state.property("visible")) is True

        QTest.mouseClick(root, Qt.LeftButton, Qt.NoModifier, _center_point(empty_state))
        _process(0)

        assert session_service.new_session_calls == [""]
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)
