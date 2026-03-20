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


@dataclass(frozen=True, slots=True)
class ClickFeedbackCase:
    role: str
    entrance_style: str
    flash_name: str
    ripple_name: str
    sheen_name: str


_MESSAGE_CLICK_CASES = [
    ClickFeedbackCase("assistant", "none", "copyFlash", "copyRipple", "copySheen"),
    ClickFeedbackCase("assistant", "greeting", "systemCopyFlash", "systemCopyRipple", "systemCopySheen"),
    ClickFeedbackCase("system", "none", "systemCopyFlash", "systemCopyRipple", "systemCopySheen"),
    ClickFeedbackCase("system", "greeting", "systemCopyFlash", "systemCopyRipple", "systemCopySheen"),
]


@pytest.mark.parametrize("case", _MESSAGE_CLICK_CASES)
def test_message_click_feedback_restored(qapp, case: ClickFeedbackCase):
    _ = qapp
    _engine, _component, root = create_component(
        build_wrapper(WrapperOptions(role=case.role, entrance_style=case.entrance_style)),
        "inline:MessageBubbleHarness.qml",
    )

    try:
        bubble = root.findChild(QObject, "bubble")
        flash = root.findChild(QObject, case.flash_name)
        ripple = root.findChild(QObject, case.ripple_name)
        sheen = root.findChild(QObject, case.sheen_name)

        assert bubble is not None
        assert flash is not None
        assert ripple is not None
        assert sheen is not None

        start_progress = float(sheen.property("progress"))
        assert QMetaObject.invokeMethod(bubble, "copyCurrentMessage")
        _process(40)

        assert float(flash.property("opacity")) >= 0.0
        assert float(ripple.property("opacity")) >= 0.0
        assert float(sheen.property("progress")) >= start_progress
    finally:
        root.deleteLater()
        _process(0)


def test_message_bubble_shows_attachment_strip(qapp):
    _ = qapp
    _engine, _component, root = create_component(
        build_wrapper(
            WrapperOptions(
                role="assistant",
                entrance_style="none",
                content="这里有附件",
                attachments_qml='[{fileName: "image.png", fileSizeLabel: "12 KB", filePath: "/tmp/image.png", previewUrl: "file:///tmp/image.png", isImage: true, extensionLabel: "PNG"}]',
            )
        ),
        "inline:MessageBubbleAttachmentHarness.qml",
    )

    try:
        strip = root.findChild(QObject, "attachmentStrip")
        assert strip is not None
        assert bool(strip.property("visible")) is True
        assert float(strip.property("width")) > 0
    finally:
        root.deleteLater()
        _process(0)


def test_short_pending_user_message_keeps_compact_bubble_width(qapp):
    _ = qapp
    _engine, _component, root = create_component(
        build_wrapper(WrapperOptions(role="user", entrance_style="none", content="1", status="pending")),
        "inline:MessageBubblePendingUserHarness.qml",
    )

    try:
        bubble = root.findChild(QObject, "bubbleBody")
        assert bubble is not None
        assert float(bubble.property("width")) < 120.0
    finally:
        root.deleteLater()
        _process(0)


def test_short_user_cjk_message_stays_on_single_line(qapp):
    _ = qapp
    _engine, _component, root = create_component(
        build_wrapper(WrapperOptions(role="user", entrance_style="none", content="你是谁")),
        "inline:MessageBubbleCjkHarness.qml",
    )

    try:
        bubble = root.findChild(QObject, "bubbleBody")
        content_text = root.findChild(QObject, "contentText")
        assert bubble is not None
        assert content_text is not None
        assert int(content_text.property("lineCount")) == 1
        assert float(bubble.property("width")) < 140.0
    finally:
        root.deleteLater()
        _process(0)


def test_message_bubble_shows_memory_reference_summary(qapp):
    _ = qapp
    _engine, _component, root = create_component(
        build_wrapper(
            WrapperOptions(
                role="assistant",
                entrance_style="none",
                content="整理好了",
                references_qml='({longTermCategories: ["project"], relatedMemoryCount: 2, experienceCount: 1})',
            )
        ),
        "inline:MessageBubbleReferenceHarness.qml",
    )

    try:
        bubble = root.findChild(QObject, "bubbleBody")
        reference_text = root.findChild(QObject, "referenceText")
        assert bubble is not None
        assert reference_text is not None
        assert bool(reference_text.property("visible")) is True
        assert "2" in str(reference_text.property("text"))
        assert "1" in str(reference_text.property("text"))
        assert float(bubble.property("width")) > 280.0
        assert float(reference_text.property("width")) == pytest.approx(
            float(bubble.property("width")) - 32.0,
            abs=1.0,
        )
    finally:
        root.deleteLater()
        _process(0)
