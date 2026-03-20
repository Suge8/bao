# ruff: noqa: E402, N802, N815, F403, F405, I001
from __future__ import annotations

from tests._chat_view_integration_testkit import *


def _default_session_model() -> SessionsModel:
    return SessionsModel(
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


def _selected_memory_fact(memory_service: object) -> dict[str, object]:
    current_key = str(cast(object, memory_service.selectedMemoryFactKey))
    facts = cast(
        list[dict[str, object]],
        cast(object, memory_service.selectedMemoryCategory).get("facts", []),
    )
    for fact in facts:
        if str(fact.get("key", "")) == current_key:
            return fact
    return facts[0] if facts else {}


def _selected_memory_facts(memory_service: object) -> list[dict[str, object]]:
    return cast(
        list[dict[str, object]],
        cast(object, memory_service.selectedMemoryCategory).get("facts", []),
    )


def _last_memory_fact(memory_service: object) -> dict[str, object]:
    facts = _selected_memory_facts(memory_service)
    return facts[-1] if facts else {}


def _wait_memory_workspace_ready(root: QObject) -> tuple[QObject, QObject, QObject, QObject]:
    _wait_until(
        lambda: any(obj.objectName() == "memoryCategoryEditor" for obj in root.findChildren(QObject))
    )
    return (
        _find_object(root, "memoryCategoryEditor"),
        _find_object(root, "memoryFactEditor"),
        _find_object(root, "memoryFactPrimaryAction"),
        _find_object(root, "memoryFactAddAction"),
    )


def _save_memory_fact(editor: QObject, primary_action: QObject, content: str) -> None:
    editor.setProperty("text", content)
    _process(40)
    assert bool(primary_action.property("buttonEnabled")) is True
    assert QMetaObject.invokeMethod(primary_action, "clicked")


def _add_memory_fact(
    memory_service: object,
    controls: tuple[QObject, QObject, QObject],
    content: str,
) -> None:
    fact_editor, fact_primary, fact_add = controls
    _wait_until(lambda: bool(fact_add.property("buttonEnabled")) is True)
    assert QMetaObject.invokeMethod(fact_add, "clicked")
    _wait_until(lambda: bool(fact_editor.property("readOnly")) is False)
    _wait_until(lambda: str(fact_editor.property("text") or "") == "")
    _save_memory_fact(fact_editor, fact_primary, content)
    _wait_until(
        lambda: str(_last_memory_fact(memory_service).get("content", "")) == content,
        attempts=40,
        step_ms=20,
    )
    _wait_until(
        lambda: str(cast(object, memory_service.selectedMemoryFactKey))
        == str(_last_memory_fact(memory_service).get("key", "")),
        attempts=40,
        step_ms=20,
    )
    _wait_until(lambda: bool(fact_editor.property("readOnly")) is True)
    _wait_until(lambda: str(fact_editor.property("text") or "") == content)


def _prepare_general_memory_category(
    memory_service: object,
    memory_editor: QObject,
    fact_editor: QObject,
) -> tuple[str, list[dict[str, object]], str]:
    memory_service.selectMemoryCategory("general")
    _wait_until(
        lambda: str(cast(object, memory_service.selectedMemoryCategory).get("category", "")) == "general",
        attempts=60,
        step_ms=20,
    )
    general_detail = cast(dict[str, object], cast(object, memory_service.selectedMemoryCategory))
    general_content = str(general_detail.get("content", ""))
    general_facts = cast(list[dict[str, object]], general_detail.get("facts", []))
    assert general_content
    assert general_facts
    _wait_until(
        lambda: str(memory_editor.property("text") or "") == general_content,
        attempts=60,
        step_ms=20,
    )
    _wait_until(
        lambda: str(fact_editor.property("text") or "") == str(general_facts[0].get("content", "")),
        attempts=60,
        step_ms=20,
    )
    return general_content, general_facts, str(general_facts[0].get("key", ""))


def test_skills_workspace_editor_tracks_selected_skill_after_local_edit(qapp, tmp_path):
    _ = qapp

    from app.backend.asyncio_runner import AsyncioRunner
    from app.backend.skills import SkillsService, SkillsServiceOptions

    runner = AsyncioRunner()
    runner.start()
    try:
        skills_service = SkillsService(
            SkillsServiceOptions(
                runner=runner,
                workspace_path=str(tmp_path),
                user_skills_dir=str(tmp_path / "user-skills"),
            )
        )
        skill_ids = {
            str(item.get("name", "")): str(item.get("id", ""))
            for item in cast(list[dict[str, object]], cast(object, skills_service.skills))
        }
        first_skill_id = skill_ids["agent-browser"]
        second_skill_id = skill_ids["clawhub"]
        skills_service.selectSkill(first_skill_id)

        session_model = _default_session_model()
        engine, root = _load_main_window(
            session_model=session_model,
            skills_service=skills_service,
        )

        try:
            root.setProperty("activeWorkspace", "skills")
            _wait_until(
                lambda: any(obj.objectName() == "skillsEditor" for obj in root.findChildren(QObject))
            )

            editor = _find_object(root, "skillsEditor")
            first_content = str(cast(object, skills_service.selectedContent))
            assert first_content
            _wait_until(lambda: str(editor.property("text") or "") == first_content)

            editor.setProperty("text", "stale draft")
            _process(40)

            skills_service.selectSkill(second_skill_id)
            second_content = str(cast(object, skills_service.selectedContent))
            assert second_content
            assert second_content != first_content
            _wait_until(lambda: str(editor.property("text") or "") == second_content)
        finally:
            root.deleteLater()
            engine.deleteLater()
            _process(0)
    finally:
        runner.shutdown()


def test_memory_workspace_editors_track_selected_category(qapp, tmp_path):
    _ = qapp

    from app.backend.asyncio_runner import AsyncioRunner
    from app.backend.memory import MemoryService
    from bao.agent.memory import MemoryStore

    store = MemoryStore(tmp_path)
    store.write_long_term("Project fact A\nProject fact B", "project")
    store.write_long_term("General fact A\nGeneral fact B", "general")
    store.close()

    runner = AsyncioRunner()
    runner.start()
    try:
        memory_service = MemoryService(runner)
        memory_service.setStorageRootHint(str(tmp_path))
        assert bool(cast(object, memory_service.ready)) is False

        session_model = _default_session_model()
        engine, root = _load_main_window(
            session_model=session_model,
            memory_service=memory_service,
        )

        try:
            root.setProperty("activeWorkspace", "memory")
            _wait_until(lambda: bool(cast(object, memory_service.ready)))
            memory_editor, fact_editor, fact_primary, fact_add = _wait_memory_workspace_ready(root)
            _, _, initial_fact_key = _prepare_general_memory_category(
                memory_service, memory_editor, fact_editor
            )
            assert bool(fact_editor.property("readOnly")) is True
            assert str(cast(object, memory_service.selectedMemoryFactKey)) == initial_fact_key

            assert bool(fact_primary.property("buttonEnabled")) is True
            assert QMetaObject.invokeMethod(fact_primary, "clicked")
            _wait_until(lambda: bool(fact_editor.property("readOnly")) is False)

            _save_memory_fact(fact_editor, fact_primary, "General fact updated")
            _wait_until(
                lambda: str(_selected_memory_fact(memory_service).get("content", ""))
                == "General fact updated",
                attempts=60,
                step_ms=20,
            )
            _wait_until(lambda: str(cast(object, memory_service.selectedMemoryFactKey)) == initial_fact_key)
            _wait_until(lambda: bool(fact_editor.property("readOnly")) is True)
            _wait_until(lambda: str(fact_editor.property("text") or "") == "General fact updated")

            _add_memory_fact(
                memory_service,
                (fact_editor, fact_primary, fact_add),
                "General fact C",
            )
        finally:
            root.deleteLater()
            engine.deleteLater()
            _process(0)
    finally:
        runner.shutdown()


def test_session_highlight_slides_between_selected_sessions(qapp):
    _ = qapp

    session_model = SessionsModel(
        [
            {
                "key": "desktop:local::default",
                "title": "Default",
                "updated_at": "2026-03-06T10:00:00",
                "channel": "desktop",
                "has_unread": False,
            },
            {
                "key": "desktop:local::second",
                "title": "Second",
                "updated_at": "2026-03-06T10:01:00",
                "channel": "desktop",
                "has_unread": False,
            },
            {
                "key": "desktop:local::third",
                "title": "Third",
                "updated_at": "2026-03-06T10:02:00",
                "channel": "desktop",
                "has_unread": False,
            },
        ]
    )
    engine, root = _load_main_window(session_model=session_model)

    try:
        session_service = engine._test_refs["session_service"]
        highlight = _find_object(root, "activeSessionHighlight")
        _process(60)

        before_y = float(highlight.property("y"))
        session_service.setActiveKey("desktop:local::third")
        _process(40)
        mid_y = float(highlight.property("y"))
        _process(320)
        final_y = float(highlight.property("y"))

        assert before_y != final_y
        assert min(before_y, final_y) < mid_y < max(before_y, final_y)
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)
