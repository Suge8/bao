from __future__ import annotations

from pathlib import Path

pytest = __import__("pytest")
pytestmark = [pytest.mark.desktop_ui_smoke]

QML_DIR = Path(__file__).resolve().parents[1] / "app" / "qml"


def _read_qml(name: str) -> str:
    return (QML_DIR / name).read_text(encoding="utf-8")


def _read_strings(name: str) -> str:
    return (QML_DIR / name).read_text(encoding="utf-8")


def test_profile_popup_uses_listview_focus_and_keyboard_contract() -> None:
    popup = _read_qml("SidebarProfilePopup.qml")

    assert "ProfileCountBadge" in popup
    assert 'objectName: "profilePopupCountBadge"' in popup
    assert "readonly property string profileCountLabel" in popup
    assert 'objectName: "profilePopupEmptyState"' in popup
    assert "SidebarProfilePopupEmptyState" in popup
    assert "visible: !root.hasProfiles" in popup
    assert 'objectName: "profilePopupList"' in popup
    assert "keyNavigationEnabled: true" in popup
    assert "keyNavigationWraps: true" in popup
    assert "KeyNavigation.tab:" in popup
    assert "KeyNavigation.backtab:" in popup
    assert "Keys.onReturnPressed" in popup
    assert "Qt.Key_F2" in popup
    assert "function syncCurrentIndexToActiveProfile()" in popup
    assert "profileListView.forceActiveFocus()" in popup
    assert "onProfileCountChanged" in popup
    assert "profileListView.count > 0 ? profileListView" not in popup
    assert "onCountChanged:" not in popup


def test_profile_count_badge_uses_caller_supplied_label_text() -> None:
    badge = _read_qml("ProfileCountBadge.qml")
    assert "property string labelText" in badge
    assert "property bool isChinese" not in badge
    assert "root.labelText.length > 0 ? root.labelText : String(root.count)" in badge


def test_profile_popup_row_uses_listview_width_fact_source() -> None:
    row = _read_qml("SidebarProfilePopupRow.qml")
    assert "width: ListView.view ? ListView.view.width : 0" in row
    assert "sidebarRoot.activateProfile(root.profileId)" in row
    assert "sidebarRoot.closeProfilePopup()" not in row


def test_profile_create_row_exposes_keyboard_focus_anchor() -> None:
    create_row = _read_qml("SidebarProfileCreateRow.qml")
    assert 'inputObjectName: "profileCreateField"' in create_row
    assert "nextTabTarget:" in create_row
    assert "previousTabTarget:" in create_row


def test_profile_rename_bubble_exposes_editor_anchor_for_ui_tests() -> None:
    bubble = _read_qml("SidebarProfileRenameBubble.qml")
    assert 'objectName: "profileRenameField"' in bubble
    assert "nextTabTarget:" in bubble
    assert "previousTabTarget:" in bubble


def test_control_tower_profiles_pane_reuses_profile_count_badge() -> None:
    pane = _read_qml("ControlTowerProfilesPane.qml")
    assert "ProfileCountBadge" in pane
    assert "labelText: pane.profileCountLabel" in pane
    assert "readonly property int profileListCacheBuffer" in pane
    assert "required property color actionAccent" in pane
    assert "required property color statusError" in pane
    assert "cacheBuffer: 960" not in pane
    assert "delegate: ControlTowerProfileCard" in pane


def test_control_tower_profile_card_derives_runtime_state_once() -> None:
    card = _read_qml("ControlTowerProfileCard.qml")
    info_chip = _read_qml("ControlTowerInfoChip.qml")
    assert "required property int cardHeight" in card
    assert "required property color actionAccent" in card
    assert "required property color actionCurrentHoverFill" in card
    assert "required property color statusSuccess" in card
    assert "readonly property bool isSelected" in card
    assert "readonly property color accentColor" in card
    assert "readonly property string actionText" in card
    assert "ControlTowerMetricBadge" in card
    assert "ControlTowerInfoChip" in card
    assert "readonly property var metricItems" not in card
    assert "width: ListView.view ? ListView.view.width : 0" in card
    assert "text: channelsLabel" in card
    assert "fillColor: isCurrent ? \"transparent\" : card.actionAccent" in card
    assert "accentHover" not in card
    assert "objectName: chipId.length > 0 ? \"controlTowerInfoChip_\" + chipId : \"\"" in info_chip


def test_control_tower_hero_panel_uses_explicit_metric_components() -> None:
    hero = _read_qml("ControlTowerHeroPanel.qml")
    workspace = _read_qml("ControlTowerWorkspace.qml")
    logic = _read_qml("ControlTowerWorkspaceLogic.js")
    metric_strip = _read_qml("ControlTowerHeroMetricStrip.qml")

    assert "ControlTowerHeroMetricStrip" in hero
    assert "scopeMetricCards()" not in hero
    assert "function scopeMetricCards()" not in workspace
    assert "function scopeMetricCards(root)" not in logic
    assert 'objectName: "controlTowerHeroMetric_" + metricId' in metric_strip
    assert "Rectangle {" not in metric_strip
    assert "border.width" not in metric_strip


def test_control_tower_lane_list_uses_derived_cache_buffer() -> None:
    lane_list = _read_qml("ControlTowerLaneList.qml")
    lane_panel = _read_qml("ControlTowerLanePanel.qml")
    assert "readonly property int laneItemHeight" in lane_list
    assert "readonly property int laneListSpacing" in lane_list
    assert "readonly property int laneListCacheBuffer" in lane_list
    assert "readonly property color itemAccentColor" in lane_list
    assert "ControlTowerInfoChip" in lane_list
    assert "cacheBuffer: 720" not in lane_list
    assert "required property int typeCaption" in lane_panel


def test_control_tower_workspace_uses_explicit_selected_profile_and_lane_kind() -> None:
    workspace = _read_qml("ControlTowerWorkspace.qml")
    assert "readonly property string selectedProfileId" in workspace
    assert "readonly property var overviewSectionKinds" in workspace
    assert "readonly property color workspaceActionAccent" in workspace
    assert "Object.keys(selectedProfile)" not in workspace
    assert 'model: ["working", "completed", "attention", "automation"]' not in workspace
    assert "parent.modelData" not in workspace


def test_profile_count_badge_strings_live_in_main_string_tables() -> None:
    zh = _read_strings("MainStringsZh.js")
    en = _read_strings("MainStringsEn.js")
    assert '"profile_count_badge": "%1 个分身"' in zh
    assert '"profile_count_badge": "%1 profiles"' in en


def test_profile_popup_empty_state_component_uses_shared_strings() -> None:
    empty_state = _read_qml("SidebarProfilePopupEmptyState.qml")
    assert "profile_empty_title" in empty_state
    assert "profile_empty_hint" in empty_state
