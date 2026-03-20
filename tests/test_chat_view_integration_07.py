# ruff: noqa: E402, N802, N815, F403, F405, I001
from __future__ import annotations

from tests._chat_view_integration_testkit import *

def test_cron_workspace_hides_existing_selection_for_new_draft(qapp):
    _ = qapp

    session_model = SessionsModel(
        [
            {
                "key": "desktop:local::default",
                "title": "Default",
                "updated_at": "2026-03-06T10:00:00",
                "channel": "desktop",
                "has_unread": False,
            }
        ]
    )
    cron_service = DummyCronService()
    engine, root = _load_main_window(session_model=session_model, cron_service=cron_service)

    try:
        root.setProperty("activeWorkspace", "cron")
        _process(120)

        cron_root = _find_object(root, "cronWorkspaceRoot")
        cron_service.selectTask("task-1")
        _process(40)
        cron_service.newDraft()
        _process(40)

        assert cron_service.selectedTaskId == ""
        assert cron_service.editingNewTask is True
        assert cron_root.property("showingExistingTask") is False
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_cron_workspace_switches_between_tasks_and_checks_tabs(qapp):
    _ = qapp

    session_model = SessionsModel(
        [
            {
                "key": "desktop:local::default",
                "title": "Default",
                "updated_at": "2026-03-06T10:00:00",
                "channel": "desktop",
                "has_unread": False,
            }
        ]
    )
    heartbeat_service = DummyHeartbeatService()
    engine, root = _load_main_window(
        session_model=session_model,
        heartbeat_service=heartbeat_service,
    )

    try:
        root.setProperty("activeWorkspace", "cron")
        _process(120)

        cron_root = _find_object(root, "cronWorkspaceRoot")
        tasks_panel = _find_object(root, "automationTasksPanel")
        assert tasks_panel.property("visible") is True

        _process(40)
        cron_root.setProperty("currentPane", "checks")
        _wait_until(lambda: cron_root.property("currentPane") == "checks")

        assert cron_root.property("currentPane") == "checks"
        checks_panel = _find_object(root, "automationChecksPanel")
        edit_button = _find_object(root, "heartbeatInlineEditButton")

        assert checks_panel is not None
        assert bool(tasks_panel.property("visible")) is False
        assert bool(checks_panel.property("visible")) is True
        assert isinstance(checks_panel, QQuickItem)
        assert checks_panel.parentItem() is not tasks_panel
        QTest.mouseClick(root, Qt.LeftButton, Qt.NoModifier, _center_point(edit_button))
        _process(40)
        assert heartbeat_service.open_file_calls == 1

        cron_root.setProperty("currentPane", "tasks")
        _wait_until(lambda: cron_root.property("currentPane") == "tasks")

        assert cron_root.property("currentPane") == "tasks"
        assert tasks_panel is not None
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_cron_workspace_tabbar_stays_centered_when_switching_tabs(qapp):
    _ = qapp

    session_model = SessionsModel(
        [
            {
                "key": "desktop:local::default",
                "title": "Default",
                "updated_at": "2026-03-06T10:00:00",
                "channel": "desktop",
                "has_unread": False,
            }
        ]
    )
    engine, root = _load_main_window(
        session_model=session_model,
        heartbeat_service=DummyHeartbeatService(),
    )

    try:
        root.setProperty("activeWorkspace", "cron")
        _process(120)

        cron_root = _find_object(root, "cronWorkspaceRoot")
        tab_bar = _find_object(root, "automationTabBar")
        initial_x = float(tab_bar.property("x"))

        _process(40)
        cron_root.setProperty("currentPane", "checks")
        _wait_until(lambda: cron_root.property("currentPane") == "checks")
        _process(40)
        checks_x = float(tab_bar.property("x"))

        cron_root.setProperty("currentPane", "tasks")
        _wait_until(lambda: cron_root.property("currentPane") == "tasks")
        _process(40)
        final_x = float(tab_bar.property("x"))

        assert checks_x == pytest.approx(initial_x, abs=0.5)
        assert final_x == pytest.approx(initial_x, abs=0.5)
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


@pytest.mark.parametrize(
    ("workspace_key", "loader_name"),
    [
        ("control_tower", "controlTowerWorkspaceLoader"),
        ("memory", "memoryWorkspaceLoader"),
        ("skills", "skillsWorkspaceLoader"),
        ("tools", "toolsWorkspaceLoader"),
        ("cron", "cronWorkspaceLoader"),
    ],
)
def test_workspace_loaders_keep_items_warm_across_workspace_switches(
    qapp, workspace_key: str, loader_name: str
):
    _ = qapp

    session_model = SessionsModel(
        [
            {
                "key": "desktop:local::default",
                "title": "Default",
                "updated_at": "2026-03-06T10:00:00",
                "channel": "desktop",
                "has_unread": False,
            }
        ]
    )
    engine, root = _load_main_window(session_model=session_model)

    try:
        root.setProperty("activeWorkspace", workspace_key)
        loader = _find_object(root, loader_name)
        _wait_until(lambda: loader.property("item") is not None)

        item = loader.property("item")
        assert item is not None
        assert loader.property("active") is True
        assert item.property("active") is True

        root.setProperty("activeWorkspace", "sessions")
        _wait_until(lambda: item.property("active") is False)

        assert loader.property("active") is True
        assert loader.property("item") is not None
        assert item.property("active") is False

        root.setProperty("activeWorkspace", workspace_key)
        _wait_until(lambda: item.property("active") is True)

        assert loader.property("active") is True
        assert loader.property("item") is not None
        assert item.property("active") is True
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_skills_workspace_loads_from_main_window(qapp):
    _ = qapp

    session_model = SessionsModel(
        [
            {
                "key": "desktop:local::default",
                "title": "Default",
                "updated_at": "2026-03-06T10:00:00",
                "channel": "desktop",
                "has_unread": False,
            }
        ]
    )
    engine, root = _load_main_window(session_model=session_model)

    try:
        root.setProperty("activeWorkspace", "skills")
        _wait_until(
            lambda: any(obj.objectName() == "skillsWorkspaceRoot" for obj in root.findChildren(QObject))
        )

        skills_root = _find_object(root, "skillsWorkspaceRoot")
        assert skills_root.property("visible") is True
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_skills_workspace_segmented_tabs_highlight_on_first_paint(qapp):
    _ = qapp

    session_model = SessionsModel(
        [
            {
                "key": "desktop:local::default",
                "title": "Default",
                "updated_at": "2026-03-06T10:00:00",
                "channel": "desktop",
                "has_unread": False,
            }
        ]
    )
    engine, root = _load_main_window(session_model=session_model)

    try:
        root.setProperty("activeWorkspace", "skills")
        _wait_until(
            lambda: any(obj.objectName() == "skillsWorkspaceRoot" for obj in root.findChildren(QObject))
        )

        def _highlight() -> QObject | None:
            highlights = [
                obj for obj in root.findChildren(QObject) if obj.objectName() == "segmentedTabsHighlight"
            ]
            return highlights[0] if highlights else None

        _wait_until(
            lambda: (
                _highlight() is not None
                and float(_highlight().property("height")) > 0
                and float(_highlight().property("width")) > 0
            )
        )

        highlight = _highlight()
        assert highlight is not None
        assert float(highlight.property("width")) > 0
        assert float(highlight.property("height")) > 0
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)
