# ruff: noqa: F403, F405
from __future__ import annotations

from tests._control_tower_workspace_qml_testkit import *


@pytest.mark.parametrize(
    ("selected_profile_qml", "expected_title"),
    [
        ("({})", "指挥舱"),
        (
            '({id: "default", displayName: "日常", totalSessionCount: 2, totalChildSessionCount: 1, isHubLive: true})',
            "指挥舱",
        ),
    ],
)
def test_control_tower_workspace_loads_scope_title(
    qapp,
    selected_profile_qml: str,
    expected_title: str,
):
    _ = qapp
    engine = QQmlEngine()
    component = QQmlComponent(engine)
    component.setData(
        _build_wrapper(
            selected_profile_qml=selected_profile_qml,
            expected_title=expected_title,
        ).encode("utf-8"),
        QUrl("inline:ControlTowerWorkspaceHarness.qml"),
    )

    _wait_until_ready(component)

    assert component.status() == QQmlComponent.Ready, component.errors()
    root = component.create()
    assert root is not None, component.errors()

    try:
        title = root.findChild(QtCore.QObject, "controlTowerScopeTitle")
        assert title is not None
        assert str(title.property("text")) == expected_title
    finally:
        root.deleteLater()
        _process(0)
