# ruff: noqa: E402, N802

from __future__ import annotations

from dataclasses import dataclass

import pytest

pytest_plugins = ("tests._message_bubble_testkit",)

from tests._message_bubble_testkit import (
    QMetaObject,
    QObject,
    WrapperOptions,
    _process,
    build_wrapper,
    create_component,
)


def test_tall_assistant_copy_sheen_uses_centered_band(qapp):
    _ = qapp
    content = "在这儿待命，\n你下一句要我接什么我就接什么，\n我会继续在这里。"
    _engine, _component, root = create_component(
        build_wrapper(WrapperOptions(role="assistant", entrance_style="none", content=content)),
        "inline:MessageBubbleHarness.qml",
    )

    try:
        bubble = root.findChild(QObject, "bubble")
        bubble_body = root.findChild(QObject, "bubbleBody")
        sheen = root.findChild(QObject, "copySheen")

        assert bubble is not None
        assert bubble_body is not None
        assert sheen is not None
        assert QMetaObject.invokeMethod(bubble, "copyCurrentMessage")

        _process(60)

        bubble_height = float(bubble_body.property("height"))
        sheen_height = float(sheen.property("height"))
        sheen_y = float(sheen.property("y"))

        assert bubble_height > 60.0
        assert abs(sheen_height - bubble_height) < 1.0
        assert abs(sheen_y) < 1.0
    finally:
        root.deleteLater()
        _process(0)


def test_copy_feedback_restarts_from_baseline_on_second_click(qapp):
    _ = qapp
    _engine, _component, root = create_component(
        build_wrapper(WrapperOptions(role="assistant", entrance_style="none")),
        "inline:MessageBubbleHarness.qml",
    )

    try:
        bubble = root.findChild(QObject, "bubble")
        sheen = root.findChild(QObject, "copySheen")

        assert bubble is not None
        assert sheen is not None
        assert QMetaObject.invokeMethod(bubble, "copyCurrentMessage")
        _process(60)
        first_progress = float(sheen.property("progress"))

        assert QMetaObject.invokeMethod(bubble, "copyCurrentMessage")
        _process(10)

        assert float(sheen.property("progress")) < first_progress
    finally:
        root.deleteLater()
        _process(0)


@pytest.mark.parametrize(
    ("dark", "expected_icon"),
    [(True, "ignite-dark.svg"), (False, "ignite-light.svg")],
)
def test_greeting_icon_uses_theme_specific_asset(qapp, dark: bool, expected_icon: str):
    _ = qapp
    _engine, _component, root = create_component(
        build_wrapper(WrapperOptions(role="assistant", entrance_style="greeting", dark=dark)),
        "inline:MessageBubbleGreetingIconHarness.qml",
    )

    try:
        icon = root.findChild(QObject, "greetingIcon")
        assert icon is not None
        assert expected_icon in str(icon.property("source"))
    finally:
        root.deleteLater()
        _process(0)


def test_light_greeting_uses_flat_bubble_and_compact_height(qapp):
    _ = qapp
    _engine, _component, root = create_component(
        build_wrapper(WrapperOptions(role="assistant", entrance_style="greeting", dark=False)),
        "inline:MessageBubbleGreetingLightHarness.qml",
    )

    try:
        bubble = root.findChild(QObject, "systemBubble")
        gradient = root.findChild(QObject, "greetingGradient")
        sweep = root.findChild(QObject, "greetingSweep")

        assert bubble is not None
        assert gradient is not None
        assert sweep is not None
        assert bool(gradient.property("visible")) is False
        assert bool(sweep.property("visible")) is False
        assert float(bubble.property("height")) <= 44.0
    finally:
        root.deleteLater()
        _process(0)


@dataclass(frozen=True, slots=True)
class EntranceCase:
    role: str
    entrance_style: str
    expected_sign: int


@pytest.mark.parametrize(
    "case",
    [
        EntranceCase("user", "userSent", 1),
        EntranceCase("assistant", "assistantReceived", -1),
    ],
)
def test_message_entrance_animation_has_directional_shift(qapp, case: EntranceCase):
    _ = qapp
    _engine, _component, root = create_component(
        build_wrapper(
            WrapperOptions(
                role=case.role,
                entrance_style=case.entrance_style,
                entrance_pending=True,
            )
        ),
        "inline:MessageBubbleEntranceHarness.qml",
    )

    try:
        bubble = root.findChild(QObject, "bubbleBody")
        shift = root.findChild(QObject, "bubbleEntranceShift")
        glow = root.findChild(QObject, "bubbleEntranceGlow")

        assert bubble is not None
        assert shift is not None
        assert glow is not None
        assert float(bubble.property("opacity")) == 0.0

        _process(40)

        shift_x = float(shift.property("x"))
        assert shift_x * case.expected_sign > 0.0
        assert float(glow.property("opacity")) > 0.0

        _process(420)

        assert abs(float(shift.property("x"))) < 0.6
        assert abs(float(shift.property("y"))) < 0.6
        assert float(bubble.property("opacity")) > 0.98
    finally:
        root.deleteLater()
        _process(0)
