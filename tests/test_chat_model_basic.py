"""Basic ChatMessageModel behaviors."""

from __future__ import annotations

import time

import pytest

from tests._chat_model_testkit import Qt, new_model

pytest_plugins = ("tests._chat_model_testkit",)


@pytest.mark.smoke
def test_append_user(qapp):
    model = new_model()
    row = model.append_user("hello")
    assert row == 0
    assert model.rowCount() == 1
    idx = model.index(0)
    assert model.data(idx, Qt.UserRole + 2) == "user"
    assert model.data(idx, Qt.UserRole + 3) == "hello"
    assert model.data(idx, Qt.UserRole + 7) == "userSent"
    assert model.data(idx, Qt.UserRole + 8) is True


@pytest.mark.smoke
def test_append_assistant(qapp):
    model = new_model()
    row = model.append_assistant("hi there")
    idx = model.index(row)
    assert model.data(idx, Qt.UserRole + 2) == "assistant"
    assert model.data(idx, Qt.UserRole + 4) == "markdown"
    assert model.data(idx, Qt.UserRole + 5) == "typing"


def test_update_content(qapp):
    model = new_model()
    row = model.append_assistant("")
    model.update_content(row, "partial")
    assert model.data(model.index(row), Qt.UserRole + 3) == "partial"


def test_set_status(qapp):
    model = new_model()
    row = model.append_assistant("done text", status="typing")
    model.set_status(row, "done")
    assert model.data(model.index(row), Qt.UserRole + 5) == "done"


def test_datachanged_only_one_row(qapp):
    model = new_model()
    model.append_user("a")
    row = model.append_assistant("")
    model.append_user("b")

    changed_rows = []
    model.dataChanged.connect(lambda top, bottom, roles: changed_rows.append((top.row(), bottom.row())))
    model.update_content(row, "new content")
    assert changed_rows == [(row, row)]


def test_large_append(qapp):
    model = new_model()
    start = time.time()
    for index in range(1000):
        model.append_user(f"message {index}")
    elapsed = time.time() - start
    assert model.rowCount() == 1000
    assert elapsed < 2.0, f"Too slow: {elapsed:.2f}s"


def test_clear(qapp):
    model = new_model()
    for index in range(5):
        model.append_user(f"msg {index}")
    model.clear()
    assert model.rowCount() == 0


def test_role_names(qapp):
    values = list(new_model().roleNames().values())
    assert b"attachments" in values
    assert b"content" in values
    assert b"role" in values
    assert b"status" in values


def test_load_history_preserves_attachment_payloads(qapp):
    model = new_model()
    attachments = [
        {
            "fileName": "image.png",
            "fileSizeLabel": "12 KB",
            "filePath": "/tmp/image.png",
            "previewUrl": "file:///tmp/image.png",
            "isImage": True,
            "extensionLabel": "PNG",
        }
    ]
    model.load_history([{"role": "assistant", "content": "see attachment", "attachments": attachments}])
    assert model.data(model.index(0), Qt.UserRole + 10) == attachments


def test_load_history_preserves_memory_references_payloads(qapp):
    model = new_model()
    references = {
        "longTermCategories": ["project"],
        "relatedMemoryCount": 2,
        "experienceCount": 1,
    }
    model.load_history([{"role": "assistant", "content": "已完成", "references": references}])
    assert model.data(model.index(0), Qt.UserRole + 11) == references


def test_load_history_source_renders_as_system(qapp):
    model = new_model()
    model.load_history(
        [
            {"role": "user", "content": "hub started", "_source": "desktop-system"},
            {"role": "assistant", "content": "summary"},
            {"role": "user", "content": "[System: cron] scheduled", "_source": "cron"},
            {"role": "assistant", "content": "ok"},
            {"role": "user", "content": "normal user msg"},
        ]
    )
    assert model.rowCount() == 5
    assert model.data(model.index(0), Qt.UserRole + 2) == "system"
    assert model.data(model.index(1), Qt.UserRole + 2) == "assistant"
    assert model.data(model.index(2), Qt.UserRole + 2) == "system"
    assert model.data(model.index(3), Qt.UserRole + 2) == "assistant"
    assert model.data(model.index(4), Qt.UserRole + 2) == "user"
