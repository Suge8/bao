from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from PySide6.QtCore import Property, QObject, Signal

from app.backend._skills_async import (
    NpxSkillDiscoveryProvider,
    SkillDiscoveryProvider,
    SkillsServiceAsyncMixin,
)
from app.backend._skills_common import DiscoverTaskUpdate, DiscoveryTaskState, SkillsServiceOptions
from app.backend._skills_projection import SkillsServiceProjectionMixin
from app.backend._skills_view import SkillsServiceViewMixin
from app.backend.list_model import KeyValueListModel
from bao.agent.skill_catalog import USER_SKILL_SOURCE, SkillCatalog

__all__ = [
    "DiscoverTaskUpdate",
    "NpxSkillDiscoveryProvider",
    "SkillDiscoveryProvider",
    "SkillsService",
    "SkillsServiceOptions",
]


class SkillsService(
    SkillsServiceAsyncMixin,
    SkillsServiceProjectionMixin,
    SkillsServiceViewMixin,
    QObject,
):
    changed: ClassVar[Signal] = Signal()
    busyChanged: ClassVar[Signal] = Signal()
    errorChanged: ClassVar[Signal] = Signal(str)
    operationFinished: ClassVar[Signal] = Signal(str, bool)

    _runnerResult: ClassVar[Signal] = Signal(str, bool, str, object)

    def __init__(self, options: SkillsServiceOptions, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._runner = options.runner
        self._workspace_path: Path = Path(options.workspace_path).expanduser()
        self._catalog: SkillCatalog = SkillCatalog(
            user_skills_dir=(
                Path(options.user_skills_dir).expanduser() if options.user_skills_dir else None
            )
        )
        self._config_data: dict[str, object] = {}
        self._overview: dict[str, object] = {}
        self._discovery_provider: SkillDiscoveryProvider = (
            options.discovery_provider or NpxSkillDiscoveryProvider()
        )
        self._query: str = ""
        self._source_filter: str = "all"
        self._busy: bool = False
        self._busy_count: int = 0
        self._error: str = ""

        self._skills: list[dict[str, object]] = []
        self._skills_model = KeyValueListModel(self)
        self._selected_skill_id: str = ""
        self._selected_content: str = ""

        self._discover_query: str = ""
        self._discover_reference: str = ""
        self._discover_results: list[dict[str, object]] = []
        self._discover_results_model = KeyValueListModel(self)
        self._selected_discover_id: str = ""
        self._discover_task: DiscoveryTaskState = DiscoveryTaskState()
        self._hydrated = False

        self._runnerResult.connect(self._handle_runner_result)
        if options.eager_refresh:
            self._refresh()

    @Property(str, notify=changed)
    def workspacePath(self) -> str:
        return str(self._workspace_path)

    @Property(str, notify=changed)
    def query(self) -> str:
        return self._query

    @Property(str, notify=changed)
    def sourceFilter(self) -> str:
        return self._source_filter

    @Property(dict, notify=changed)
    def overview(self) -> dict[str, object]:
        return dict(self._overview)

    @Property(bool, notify=busyChanged)
    def busy(self) -> bool:
        return self._busy

    @Property(str, notify=errorChanged)
    def lastError(self) -> str:
        return self._error

    @Property(QObject, constant=True)
    def skillsModel(self) -> QObject:
        return self._skills_model

    @Property(list, notify=changed)
    def skills(self) -> list[dict[str, object]]:
        return [dict(item) for item in self._skills]

    @Property(dict, notify=changed)
    def selectedSkill(self) -> dict[str, object]:
        return self._selected_skill()

    @Property(str, notify=changed)
    def selectedSkillId(self) -> str:
        return self._selected_skill_id

    @Property(str, notify=changed)
    def selectedContent(self) -> str:
        return self._selected_content

    @Property(int, notify=changed)
    def totalCount(self) -> int:
        return len(self._skills)

    @Property(int, notify=changed)
    def userCount(self) -> int:
        return sum(1 for item in self._skills if item.get("source") == USER_SKILL_SOURCE)

    @Property(int, notify=changed)
    def builtinCount(self) -> int:
        return sum(1 for item in self._skills if item.get("source") == "builtin")

    @Property(int, notify=changed)
    def attentionCount(self) -> int:
        return sum(1 for item in self._skills if bool(item.get("needsAttention")))

    @Property(str, notify=changed)
    def discoverQuery(self) -> str:
        return self._discover_query

    @Property(str, notify=changed)
    def discoverReference(self) -> str:
        return self._discover_reference

    @Property(QObject, constant=True)
    def discoverResultsModel(self) -> QObject:
        return self._discover_results_model

    @Property(int, notify=changed)
    def discoverResultCount(self) -> int:
        return len(self._discover_results)

    @Property(dict, notify=changed)
    def selectedDiscoverItem(self) -> dict[str, object]:
        return self._selected_discover_item()

    @Property(str, notify=changed)
    def selectedDiscoverId(self) -> str:
        return self._selected_discover_id

    @Property(dict, notify=changed)
    def discoverTask(self) -> dict[str, str]:
        return self._discover_task.to_dict()

    @Property(str, notify=changed)
    def discoverTaskState(self) -> str:
        return self._discover_task.state

    @Property(str, notify=changed)
    def discoverTaskMessage(self) -> str:
        return self._discover_task.message

    @Property(str, notify=changed)
    def discoverTaskKind(self) -> str:
        return self._discover_task.kind

    @Property(str, notify=changed)
    def discoverTaskReference(self) -> str:
        return self._discover_task.reference
