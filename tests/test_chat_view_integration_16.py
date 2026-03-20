# ruff: noqa: E402, N802, N815, F403, F405, I001
from __future__ import annotations

from tests._chat_view_integration_testkit import *


class DummyProfileService(QObject):
    profilesChanged = Signal()
    activeProfileChanged = Signal()
    lastErrorChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._active_profile_id = "default"
        self._profiles = [
            {"id": "default", "displayName": "Default", "avatarKey": "mochi", "canDelete": False},
            {"id": "work", "displayName": "Work", "avatarKey": "comet", "canDelete": True},
            {"id": "research", "displayName": "Research", "avatarKey": "plum", "canDelete": True},
        ]
        self.activate_calls: list[str] = []
        self.create_calls: list[str] = []

    def _profile_rows(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for profile in self._profiles:
            rows.append({**profile, "isActive": profile["id"] == self._active_profile_id})
        return rows

    @Property("QVariantList", notify=profilesChanged)
    def profiles(self) -> list[dict[str, object]]:
        return self._profile_rows()

    @Property(str, notify=activeProfileChanged)
    def activeProfileId(self) -> str:
        return self._active_profile_id

    @Property("QVariantMap", notify=activeProfileChanged)
    def activeProfile(self) -> dict[str, object]:
        for profile in self._profile_rows():
            if profile["id"] == self._active_profile_id:
                return profile
        return {}

    @Property(str, notify=lastErrorChanged)
    def lastError(self) -> str:
        return ""

    @Slot(str)
    def activateProfile(self, profile_id: str) -> None:
        self.activate_calls.append(profile_id)
        self._active_profile_id = profile_id
        self.activeProfileChanged.emit()
        self.profilesChanged.emit()

    @Slot(str)
    def createProfile(self, name: str) -> None:
        self.create_calls.append(name)

    @Slot(str, str)
    def renameProfile(self, _profile_id: str, _display_name: str) -> None:
        return None

    @Slot(str)
    def deleteProfile(self, _profile_id: str) -> None:
        return None


class DummyEmptyProfileService(DummyProfileService):
    def __init__(self) -> None:
        super().__init__()
        self._active_profile_id = ""
        self._profiles = []


def _open_profile_popup(root: QObject, profile_bar: QObject, popup: QObject) -> None:
    QTest.mouseClick(root, Qt.LeftButton, Qt.NoModifier, _center_point(profile_bar))
    _wait_until(lambda: bool(popup.property("opened")), attempts=40, step_ms=20)


def _open_profile_popup_with_list_focus(
    root: QObject,
    profile_bar: QObject,
    popup: QObject,
    popup_list: QObject,
) -> None:
    _open_profile_popup(root, profile_bar, popup)
    _wait_until(lambda: bool(popup_list.property("activeFocus")), attempts=40, step_ms=20)


def _find_profile_row_mouse(popup_list: QObject, profile_id: str) -> QObject:
    content_item = popup_list.property("contentItem")
    if not isinstance(content_item, QQuickItem):
        raise AssertionError("profile popup content item not found")
    expected_name = "profileRowMouse_" + profile_id
    for delegate in content_item.childItems():
        for section in delegate.childItems():
            for item in section.childItems():
                if item.objectName() == expected_name:
                    return item
    raise AssertionError(f"object not found: {expected_name}")


@pytest.mark.desktop_ui_smoke
def test_profile_popup_keyboard_navigation_tracks_current_row_and_activates_selection(qapp):
    _ = qapp
    profile_service = DummyProfileService()
    engine, root = _load_main_window(profile_service=profile_service)

    try:
        profile_bar = _find_object(root, "profileBar")
        popup = _find_object(root, "profilePopup")
        popup_list = _find_object(root, "profilePopupList")

        _open_profile_popup_with_list_focus(root, profile_bar, popup, popup_list)
        _wait_until(lambda: int(popup_list.property("currentIndex")) == 0, attempts=40, step_ms=20)

        QTest.keyClick(root, Qt.Key_Down)
        _wait_until(lambda: int(popup_list.property("currentIndex")) == 1, attempts=20, step_ms=20)

        QTest.keyClick(root, Qt.Key_Return)
        _wait_until(lambda: profile_service.activate_calls == ["work"], attempts=20, step_ms=20)
        _wait_until(lambda: not bool(popup.property("opened")), attempts=20, step_ms=20)

        _open_profile_popup_with_list_focus(root, profile_bar, popup, popup_list)
        _wait_until(lambda: int(popup_list.property("currentIndex")) == 1, attempts=40, step_ms=20)
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


@pytest.mark.desktop_ui_smoke
def test_profile_popup_mouse_activation_closes_popup_and_switches_profile(qapp):
    _ = qapp
    profile_service = DummyProfileService()
    engine, root = _load_main_window(profile_service=profile_service)

    try:
        profile_bar = _find_object(root, "profileBar")
        popup = _find_object(root, "profilePopup")
        popup_list = _find_object(root, "profilePopupList")

        _open_profile_popup(root, profile_bar, popup)
        row_mouse = _find_profile_row_mouse(popup_list, "work")
        QTest.mouseClick(root, Qt.LeftButton, Qt.NoModifier, _center_point(row_mouse))

        _wait_until(lambda: profile_service.activate_calls == ["work"], attempts=20, step_ms=20)
        _wait_until(lambda: not bool(popup.property("opened")), attempts=20, step_ms=20)
        assert profile_service.activeProfileId == "work"
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


@pytest.mark.desktop_ui_smoke
def test_profile_popup_tab_navigation_loops_between_list_and_create_field(qapp):
    _ = qapp
    profile_service = DummyProfileService()
    engine, root = _load_main_window(profile_service=profile_service)

    try:
        profile_bar = _find_object(root, "profileBar")
        popup = _find_object(root, "profilePopup")
        popup_list = _find_object(root, "profilePopupList")
        create_field = _find_object(root, "profileCreateField")

        _open_profile_popup_with_list_focus(root, profile_bar, popup, popup_list)

        QTest.keyClick(root, Qt.Key_Tab)
        _wait_until(lambda: bool(create_field.property("activeFocus")), attempts=20, step_ms=20)

        for key in (Qt.Key_O, Qt.Key_P, Qt.Key_S):
            QTest.keyClick(root, key)
        _wait_until(lambda: str(create_field.property("text")) == "ops", attempts=20, step_ms=20)

        QTest.keyClick(root, Qt.Key_Return)
        _wait_until(lambda: profile_service.create_calls == ["ops"], attempts=20, step_ms=20)
        _wait_until(lambda: not bool(popup.property("opened")), attempts=20, step_ms=20)

        _open_profile_popup_with_list_focus(root, profile_bar, popup, popup_list)

        QTest.keyClick(root, Qt.Key_Tab)
        _wait_until(lambda: bool(create_field.property("activeFocus")), attempts=20, step_ms=20)

        QTest.keyClick(root, Qt.Key_Tab, Qt.ShiftModifier)
        _wait_until(lambda: bool(popup_list.property("activeFocus")), attempts=20, step_ms=20)
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


@pytest.mark.desktop_ui_smoke
def test_profile_popup_empty_state_keeps_create_entry_accessible(qapp):
    _ = qapp
    profile_service = DummyEmptyProfileService()
    engine, root = _load_main_window(profile_service=profile_service)

    try:
        profile_bar = _find_object(root, "profileBar")
        popup = _find_object(root, "profilePopup")
        popup_list = _find_object(root, "profilePopupList")
        create_field = _find_object(root, "profileCreateField")
        count_badge = _find_object(root, "profilePopupCountBadge")
        empty_state = _find_object(root, "profilePopupEmptyState")

        _open_profile_popup(root, profile_bar, popup)
        _wait_until(lambda: bool(create_field.property("activeFocus")), attempts=40, step_ms=20)

        assert not bool(popup_list.property("visible"))
        assert bool(empty_state.property("visible"))
        assert int(count_badge.property("count")) == 0

        for key in (Qt.Key_N, Qt.Key_E, Qt.Key_W):
            QTest.keyClick(root, key)
        _wait_until(lambda: str(create_field.property("text")) == "new", attempts=20, step_ms=20)

        QTest.keyClick(root, Qt.Key_Return)
        _wait_until(lambda: profile_service.create_calls == ["new"], attempts=20, step_ms=20)
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)
