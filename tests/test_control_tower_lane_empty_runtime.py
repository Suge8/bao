# ruff: noqa: E402, F403, F405
from __future__ import annotations

pytest_plugins = ("tests._control_tower_workspace_qml_testkit",)

from tests._control_tower_workspace_qml_fragments import (
    supervisor_actions_block,
    supervisor_overview_block,
    supervisor_profiles_block,
    wrapper_footer,
    wrapper_header,
)
from tests._control_tower_workspace_qml_testkit import *


def _build_empty_lane_wrapper() -> str:
    qml_dir = _qml_dir_uri()
    return (
        wrapper_header(qml_dir)
        + supervisor_overview_block()
        + supervisor_profiles_block()
        + """
        property var workingModel: []
        property int workingCount: 0
        property var completedModel: []
        property int completedCount: 0
        property var automationModel: []
        property int automationCount: 0
        property var attentionModel: []
        property int attentionCount: 0
"""
        + supervisor_actions_block("({})")
        + wrapper_footer()
    )


def test_control_tower_empty_lane_workspace_loads_without_property_assignment_errors(qapp):
    _ = qapp
    messages: list[str] = []

    def _handler(_msg_type, _context, message) -> None:
        messages.append(str(message))

    previous_handler = QtCore.qInstallMessageHandler(_handler)
    try:
        engine = QQmlEngine()
        component = QQmlComponent(engine)
        component.setData(
            _build_empty_lane_wrapper().encode("utf-8"),
            QUrl("inline:ControlTowerEmptyLaneHarness.qml"),
        )

        _wait_until_ready(component)

        assert component.status() == QQmlComponent.Ready, component.errors()
        root = component.create()
        assert root is not None, component.errors()

        try:
            _process(60)
            title = root.findChild(QtCore.QObject, "controlTowerScopeTitle")
            assert title is not None
            assert "Cannot assign to non-existent property" not in "\n".join(messages)
        finally:
            root.deleteLater()
            engine.deleteLater()
            _process(0)
    finally:
        QtCore.qInstallMessageHandler(previous_handler)
