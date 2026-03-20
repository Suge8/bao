from __future__ import annotations

import importlib
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import cast

from app.backend.asyncio_runner import AsyncioRunner

pytest = importlib.import_module("pytest")
pytestmark = [pytest.mark.integration, pytest.mark.gui]

QtCore = pytest.importorskip("PySide6.QtCore")
QCoreApplication = QtCore.QCoreApplication


@pytest.fixture(scope="module", autouse=True)
def qt_app():
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    yield app


@pytest.fixture()
def runner() -> Iterator[AsyncioRunner]:
    current = AsyncioRunner()
    current.start()
    try:
        yield current
    finally:
        current.shutdown()


def _skills_options(tmp_path: Path, runner: AsyncioRunner):
    from app.backend.skills import SkillsServiceOptions

    return SkillsServiceOptions(
        runner=runner,
        workspace_path=str(tmp_path),
        user_skills_dir=str(tmp_path / "user-skills"),
    )


def test_skills_service_create_save_delete_and_filter(
    tmp_path: Path, runner: AsyncioRunner
) -> None:
    from app.backend.skills import SkillsService

    user_skills_dir = tmp_path / "user-skills"
    service = SkillsService(_skills_options(tmp_path, runner))

    created_events: list[tuple[str, bool]] = []
    _ = service.operationFinished.connect(lambda message, ok: created_events.append((message, ok)))

    assert service.createSkill("my-ui-skill", "Use for premium UI polish.") is True
    assert cast(str, cast(object, service.selectedSkillId)) == "user:my-ui-skill"
    assert cast(int, cast(object, service.userCount)) >= 1
    assert created_events[-1] == ("created", True)

    assert (
        service.saveSelectedContent(
            "---\nname: my-ui-skill\ndescription: Updated UI workflow\n---\n\n# my-ui-skill\n\nBody\n"
        )
        is True
    )
    selected_skill = cast(dict[str, object], cast(object, service.selectedSkill))
    assert selected_skill["description"] == "Updated UI workflow"
    assert created_events[-1] == ("saved", True)

    service.setSourceFilter("user")
    user_items = cast(list[dict[str, object]], cast(object, service.skills))
    assert all(item["source"] == "user" for item in user_items)

    service.setQuery("updated ui")
    filtered_items = cast(list[dict[str, object]], cast(object, service.skills))
    assert len(filtered_items) == 1
    assert filtered_items[0]["name"] == "my-ui-skill"

    service.setQuery("")
    service.setSourceFilter("all")
    assert service.deleteSelectedSkill() is True
    assert created_events[-1] == ("deleted", True)
    assert not (user_skills_dir / "my-ui-skill").exists()

def test_parse_search_output_extracts_skill_refs() -> None:
    from app.backend.skills import SkillsService

    output = """
Install with npx skills add vercel-labs/agent-skills@frontend-design
vercel-labs/agent-skills@frontend-design
Install with npx skills add acme/skills@docs-pro
"""
    parsed = SkillsService.parse_search_output(output)

    assert [item["reference"] for item in parsed] == [
        "vercel-labs/agent-skills@frontend-design",
        "acme/skills@docs-pro",
    ]
    assert parsed[0]["name"] == "frontend-design"
    assert parsed[0]["title"] == "Frontend Design"
    assert parsed[0]["publisher"] == "vercel-labs"
    assert parsed[0]["version"] == "latest"
    assert parsed[0]["installState"] == "available"


def test_skills_service_tracks_discovery_task_and_marks_installed(
    tmp_path: Path, runner: AsyncioRunner
) -> None:
    from app.backend.skills import DiscoverTaskUpdate, SkillsService

    service = SkillsService(_skills_options(tmp_path, runner))
    service._set_discover_results(  # type: ignore[attr-defined]
        [
            {
                "id": "vercel-labs/agent-skills@frontend-design",
                "reference": "vercel-labs/agent-skills@frontend-design",
                "name": "frontend-design",
                "title": "Frontend Design",
                "publisher": "vercel-labs",
                "version": "latest",
                "summary": "Import Frontend Design from vercel-labs/agent-skills",
                "trustNote": {"zh": "信任说明", "en": "Trust note"},
                "requires": ["npx skills"],
                "installState": "available",
                "installStateLabel": {"zh": "可导入", "en": "Ready to import"},
                "installStateDetail": {"zh": "可导入", "en": "Ready to import"},
            }
        ]
    )

    service._set_discover_task(  # type: ignore[attr-defined]
        DiscoverTaskUpdate(
            state="working",
            kind="install",
            message="Importing vercel-labs/agent-skills@frontend-design",
            reference="vercel-labs/agent-skills@frontend-design",
        )
    )
    task_snapshot = cast(dict[str, str], cast(object, service.discoverTask))
    assert task_snapshot["state"] == "working"
    assert task_snapshot["kind"] == "install"
    assert cast(str, cast(object, service.discoverTaskState)) == "working"
    assert cast(str, cast(object, service.discoverTaskKind)) == "install"

    service._mark_discover_installed(["user:frontend-design"])  # type: ignore[attr-defined]
    selected = cast(dict[str, object], cast(object, service.selectedDiscoverItem))
    assert selected["installState"] == "installed"


def test_import_installed_skills_copies_into_user_skills(
    tmp_path: Path, runner: AsyncioRunner
) -> None:
    from app.backend.skills import SkillsService

    user_skills_dir = tmp_path / "user-skills"
    service = SkillsService(_skills_options(tmp_path, runner))
    source_root = tmp_path / "temp" / ".agents" / "skills" / "design-ops"
    source_root.mkdir(parents=True)
    (source_root / "SKILL.md").write_text(
        "---\nname: design-ops\ndescription: Design ops\n---\n\n# design-ops\n",
        encoding="utf-8",
    )

    imported_ids = service._import_installed_skills(tmp_path / "temp" / ".agents" / "skills")

    assert imported_ids == ["user:design-ops"]
    assert (user_skills_dir / "design-ops" / "SKILL.md").exists()


def test_import_installed_skills_can_filter_target_names(
    tmp_path: Path, runner: AsyncioRunner
) -> None:
    from app.backend.skills import SkillsService

    user_skills_dir = tmp_path / "user-skills"
    service = SkillsService(_skills_options(tmp_path, runner))
    for skill_name in ("design-ops", "frontend-design"):
        source_dir = tmp_path / ".agents" / "skills" / skill_name
        source_dir.mkdir(parents=True)
        (source_dir / "SKILL.md").write_text(
            f"---\nname: {skill_name}\ndescription: {skill_name}\n---\n\n# {skill_name}\n",
            encoding="utf-8",
        )

    imported_ids = service._import_installed_skills(
        tmp_path / ".agents" / "skills", target_names=["frontend-design"]
    )

    assert imported_ids == ["user:frontend-design"]
    assert not (user_skills_dir / "design-ops").exists()
    assert (user_skills_dir / "frontend-design" / "SKILL.md").exists()


def test_set_workspace_path_keeps_user_skill_root(
    tmp_path: Path, runner: AsyncioRunner
) -> None:
    from app.backend.skills import SkillsService

    user_skills_dir = tmp_path / "user-skills"
    service = SkillsService(_skills_options(tmp_path, runner))

    service.setWorkspacePath(str(tmp_path / "other-workspace"))
    assert service.createSkill("profile-audit", "Use for profile audit tasks.") is True

    assert (user_skills_dir / "profile-audit" / "SKILL.md").exists()
    assert not (tmp_path / "other-workspace" / "profile-audit" / "SKILL.md").exists()


def test_extract_reference_name_returns_skill_suffix() -> None:
    from app.backend.skills import SkillsService

    assert (
        SkillsService._extract_reference_name("vercel-labs/agent-skills@frontend-design")
        == "frontend-design"
    )
