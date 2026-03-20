# ruff: noqa: E402, N802

from __future__ import annotations

from dataclasses import dataclass

import pytest

pytest_plugins = ("tests._message_bubble_testkit",)

from tests._message_bubble_testkit import (
    QObject,
    WrapperOptions,
    _process,
    build_wrapper,
    create_component,
)


@dataclass(frozen=True, slots=True)
class AuraCase:
    role: str
    entrance_style: str


@pytest.mark.parametrize(
    "case",
    [
        AuraCase("system", "none"),
        AuraCase("system", "greeting"),
        AuraCase("assistant", "greeting"),
    ],
)
def test_system_aura_near_stays_within_bubble_width(qapp, case: AuraCase):
    _ = qapp
    _engine, _component, root = create_component(
        build_wrapper(WrapperOptions(role=case.role, entrance_style=case.entrance_style)),
        "inline:MessageBubbleHarness.qml",
    )

    try:
        aura = root.findChild(QObject, "systemAuraNear")
        bubble = root.findChild(QObject, "systemBubble")

        assert aura is not None
        assert bubble is not None
        assert float(aura.property("width")) == float(bubble.property("width"))
        assert float(aura.property("x")) == float(bubble.property("x"))
    finally:
        root.deleteLater()
        _process(0)


def test_date_divider_renders_above_bubble(qapp):
    _ = qapp
    _engine, _component, root = create_component(
        build_wrapper(
            WrapperOptions(
                role="assistant",
                entrance_style="none",
                content="新的时间段。",
                show_date_divider=True,
                date_divider_text="3/7",
            )
        ),
        "inline:MessageBubbleHarness.qml",
    )

    try:
        divider = root.findChild(QObject, "dateDivider")
        divider_text = root.findChild(QObject, "dateDividerText")
        bubble_body = root.findChild(QObject, "bubbleBody")

        assert divider is not None
        assert divider_text is not None
        assert bubble_body is not None
        assert bool(divider.property("visible")) is True
        assert str(divider_text.property("text")) == "3/7"
        assert float(bubble_body.property("y")) >= float(divider.property("height"))
    finally:
        root.deleteLater()
        _process(0)


def test_typing_indicator_morphs_into_content_in_same_bubble(qapp):
    _ = qapp
    _engine, _component, root = create_component(
        build_wrapper(
            WrapperOptions(
                role="assistant",
                entrance_style="assistantReceived",
                content="",
                status="typing",
            )
        ),
        "inline:MessageBubbleTypingMorphHarness.qml",
    )

    try:
        bubble = root.findChild(QObject, "bubble")
        typing = root.findChild(QObject, "typingIndicator")
        content = root.findChild(QObject, "contentText")

        assert bubble is not None
        assert typing is not None
        assert content is not None
        assert float(typing.property("opacity")) > 0.98
        assert float(content.property("opacity")) < 0.02

        bubble.setProperty("content", "Bao 在这。")
        bubble.setProperty("status", "done")
        _process(40)

        assert 0.0 < float(typing.property("opacity")) < 1.0
        assert 0.0 < float(content.property("opacity")) < 1.0
        assert float(content.property("scale")) < 1.0

        _process(320)

        assert float(typing.property("opacity")) < 0.02
        assert float(content.property("opacity")) > 0.98
        assert abs(float(content.property("scale")) - 1.0) < 0.01
    finally:
        root.deleteLater()
        _process(0)


def test_pending_surface_settles_when_user_message_finishes(qapp):
    _ = qapp
    _engine, _component, root = create_component(
        build_wrapper(
            WrapperOptions(
                role="user",
                entrance_style="userSent",
                content="我已经发出去了。",
                status="pending",
            )
        ),
        "inline:MessageBubblePendingFinalizeHarness.qml",
    )

    try:
        bubble = root.findChild(QObject, "bubble")
        overlay = root.findChild(QObject, "pendingOverlay")

        assert bubble is not None
        assert overlay is not None
        assert float(overlay.property("opacity")) > 0.98
        assert float(overlay.property("scale")) > 1.0

        bubble.setProperty("status", "done")
        _process(60)

        assert 0.0 < float(overlay.property("opacity")) < 1.0
        assert 1.0 < float(overlay.property("scale")) < 1.017

        _process(360)

        assert float(overlay.property("opacity")) < 0.02
        assert abs(float(overlay.property("scale")) - 1.0) < 0.01
    finally:
        root.deleteLater()
        _process(0)
