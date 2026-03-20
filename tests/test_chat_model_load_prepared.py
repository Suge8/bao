"""load_prepared reconciliation behaviors."""

from __future__ import annotations

from tests._chat_model_testkit import new_model

pytest_plugins = ("tests._chat_model_testkit",)


def test_load_prepared_skips_reset_when_render_equivalent(qapp):
    from app.backend.chat import ChatMessageModel

    model = new_model()
    raw = [{"role": "assistant", "content": "hello"}, {"role": "user", "content": "world"}]
    prepared = ChatMessageModel.prepare_history(raw)
    resets = []
    model.modelReset.connect(lambda: resets.append(True))

    model.load_prepared(prepared)
    model.load_prepared([dict(item) for item in prepared])

    assert len(resets) == 1


def test_load_prepared_skips_reset_when_only_entrance_flags_differ(qapp):
    from app.backend.chat import ChatMessageModel

    model = new_model()
    model.append_assistant("hello", status="done", entrance_pending=True)
    prepared = ChatMessageModel.prepare_history([{"role": "assistant", "content": "hello", "status": "done"}])
    resets = []
    model.modelReset.connect(lambda: resets.append(True))

    model.load_prepared(prepared)
    assert resets == []


def test_load_prepared_updates_same_length_assistant_row_without_reset(qapp):
    from app.backend.chat import ChatMessageModel

    model = new_model()
    model.append_assistant("", status="typing", entrance_pending=True)
    prepared = ChatMessageModel.prepare_history(
        [{"role": "assistant", "content": "hello", "status": "done", "format": "markdown"}]
    )
    resets = []
    model.modelReset.connect(lambda: resets.append(True))

    model.load_prepared(prepared)
    assert resets == []
    assert model._messages[0]["content"] == "hello"
    assert model._messages[0]["status"] == "done"


def test_load_prepared_preserves_transient_assistant_tail_when_requested(qapp):
    from app.backend.chat import ChatMessageModel

    model = new_model()
    model.append_user("hello")
    model.append_assistant("working", status="done")
    model.append_assistant("", status="typing")
    prepared = ChatMessageModel.prepare_history(
        [{"role": "user", "content": "hello"}, {"role": "tool", "content": "running tool"}]
    )
    resets = []
    model.modelReset.connect(lambda: resets.append(True))

    model.load_prepared(prepared, preserve_transient_tail=True)
    assert resets == []
    assert model.rowCount() == 4
    assert model._messages[1]["role"] == "system"
    assert model._messages[2]["content"] == "working"
    assert model._messages[3]["status"] == "typing"


def test_load_prepared_reconciles_tool_row_and_final_assistant_without_reset(qapp):
    from app.backend.chat import ChatMessageModel

    model = new_model()
    model.append_user("hello")
    model.append_assistant("working", status="done")
    model.append_assistant("", status="typing")
    prepared = ChatMessageModel.prepare_history(
        [
            {"role": "user", "content": "hello"},
            {"role": "tool", "content": "running tool"},
            {"role": "assistant", "content": "final", "status": "done", "format": "markdown"},
        ]
    )
    resets = []
    model.modelReset.connect(lambda: resets.append(True))

    model.load_prepared(prepared, preserve_transient_tail=True)
    assert resets == []
    assert model.rowCount() == 3
    assert model._messages[1]["role"] == "system"
    assert model._messages[2]["content"] == "final"
    assert model._messages[2]["status"] == "done"


def test_load_prepared_reconciles_completed_assistant_tail_without_reset(qapp):
    from app.backend.chat import ChatMessageModel

    model = new_model()
    model.append_user("hello")
    model.append_assistant("working", status="done")
    model.append_assistant("final", status="done")
    prepared = ChatMessageModel.prepare_history(
        [
            {"role": "user", "content": "hello"},
            {"role": "tool", "content": "running tool"},
            {"role": "assistant", "content": "final", "status": "done", "format": "markdown"},
        ]
    )
    resets = []
    model.modelReset.connect(lambda: resets.append(True))

    model.load_prepared(prepared)
    assert resets == []
    assert model.rowCount() == 3
    assert model._messages[1]["role"] == "system"
    assert model._messages[2]["content"] == "final"
    assert model._messages[2]["status"] == "done"


def test_load_prepared_reconciles_assistant_only_split_without_reset(qapp):
    from app.backend.chat import ChatMessageModel

    model = new_model()
    model.append_user("hello")
    model.append_assistant("first", status="typing")
    prepared = ChatMessageModel.prepare_history(
        [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "first", "status": "done", "format": "markdown"},
            {"role": "assistant", "content": "second", "status": "done", "format": "markdown"},
        ]
    )
    resets = []
    model.modelReset.connect(lambda: resets.append(True))

    model.load_prepared(prepared)
    assert resets == []
    assert model.rowCount() == 3
    assert model._messages[1]["content"] == "first"
    assert model._messages[1]["status"] == "done"
    assert model._messages[2]["content"] == "second"
    assert model._messages[2]["status"] == "done"


def test_load_prepared_resets_when_system_entrance_style_changes(qapp):
    from app.backend.chat import ChatMessageModel

    model = new_model()
    prepared = ChatMessageModel.prepare_history(
        [{"role": "system", "content": "hello", "entrance_style": "system"}]
    )
    changed = [dict(prepared[0], entrancestyle="greeting")]
    resets = []
    model.modelReset.connect(lambda: resets.append(True))

    model.load_prepared(prepared)
    model.load_prepared(changed)
    assert len(resets) == 2
