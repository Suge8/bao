# ruff: noqa: N802, N815
from __future__ import annotations

import importlib
from pathlib import Path

from tests._chat_view_integration_testkit import (
    DummyChatService,
    DummyConfigService,
    DummyCronService,
    DummyHeartbeatService,
    EmptyMessagesModel,
    SessionsModel,
    _load_light_main_window,
    _process,
)
from tests.desktop_ui_testkit import (
    DESKTOP_SMOKE_SCREENSHOT_SCENARIOS,
    assert_item_within_window,
    desktop_ui_smoke_output_dir,
    find_object,
    qapp,  # noqa: F401
    wait_for_scene_contract,
    wait_until,
)

pytest = importlib.import_module("pytest")
QtCore = pytest.importorskip("PySide6.QtCore")

Qt = QtCore.Qt
QObject = QtCore.QObject
Property = QtCore.Property
Signal = QtCore.Signal
Slot = QtCore.Slot

pytestmark = [pytest.mark.gui, pytest.mark.desktop_ui_smoke, pytest.mark.usefixtures("qapp")]


class DummyMemoryService(QObject):
    readyChanged = Signal()
    operationFinished = Signal(str, bool)
    errorChanged = Signal(str)
    selectedMemoryCategoryChanged = Signal()
    selectedMemoryFactChanged = Signal()
    selectedExperienceChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._categories = [
            {
                "category": "project",
                "content": "Bao desktop 需要保持单一路径 UI read-model。",
                "preview": "Bao desktop 需要保持单一路径 UI read-model。",
                "fact_count": 2,
                "updated_label": "刚刚",
                "facts": [
                    {
                        "key": "project-1",
                        "content": "主 workspace 需要在窄宽度下保持可读。",
                        "updated_label": "刚刚",
                        "hit_count": 3,
                    },
                    {
                        "key": "project-2",
                        "content": "不要让列表和详情 pane 互相挤压。",
                        "updated_label": "2 分钟前",
                        "hit_count": 1,
                    },
                ],
            },
            {
                "category": "general",
                "content": "",
                "preview": "还没有内容。",
                "fact_count": 0,
                "updated_label": "",
                "facts": [],
                "is_empty": True,
            },
        ]
        self._experiences = [
            {
                "key": "exp-1",
                "task": "compact layout",
                "preview": "先切单一路径布局，再做细节 polish。",
                "outcome": "success",
                "quality": 4,
                "uses": 3,
                "hit_count": 5,
                "updated_label": "刚刚",
                "deprecated": False,
            }
        ]
        self._selected_category = dict(self._categories[0])
        self._selected_fact = dict(self._selected_category["facts"][0])
        self._selected_experience = dict(self._experiences[0])

    @Property(bool, constant=True)
    def ready(self) -> bool:
        return True

    @Property(bool, constant=True)
    def blockingBusy(self) -> bool:
        return False

    @Property(dict, constant=True)
    def memoryStats(self) -> dict[str, object]:
        return {"used_categories": 1, "total_categories": 4, "total_facts": 2}

    @Property(dict, constant=True)
    def experienceStats(self) -> dict[str, object]:
        return {"active": 1, "deprecated": 0}

    @Property(dict, notify=selectedMemoryCategoryChanged)
    def selectedMemoryCategory(self) -> dict[str, object]:
        return dict(self._selected_category)

    @Property(dict, notify=selectedMemoryFactChanged)
    def selectedMemoryFact(self) -> dict[str, object]:
        return dict(self._selected_fact)

    @Property(str, notify=selectedMemoryFactChanged)
    def selectedMemoryFactKey(self) -> str:
        return str(self._selected_fact.get("key", ""))

    @Property(dict, notify=selectedExperienceChanged)
    def selectedExperience(self) -> dict[str, object]:
        return dict(self._selected_experience)

    @Property("QVariantList", constant=True)
    def memoryCategoryModel(self) -> list[dict[str, object]]:
        return [dict(item) for item in self._categories]

    @Property(int, constant=True)
    def memoryCategoryCount(self) -> int:
        return len(self._categories)

    @Property("QVariantList", constant=True)
    def experienceModel(self) -> list[dict[str, object]]:
        return [dict(item) for item in self._experiences]

    @Property(int, constant=True)
    def experienceCount(self) -> int:
        return len(self._experiences)

    @Property(str, constant=True)
    def error(self) -> str:
        return ""

    @Slot()
    def ensureHydrated(self) -> None:
        return None

    @Slot(str)
    def setMemoryQuery(self, _query: str) -> None:
        return None

    @Slot(str)
    def selectMemoryCategory(self, category: str) -> None:
        for item in self._categories:
            if str(item.get("category", "")) == category:
                self._selected_category = dict(item)
                facts = list(item.get("facts", []))
                self._selected_fact = dict(facts[0]) if facts else {"key": "", "content": "", "updated_label": "", "hit_count": 0}
                self.selectedMemoryCategoryChanged.emit()
                self.selectedMemoryFactChanged.emit()
                return

    @Slot(str)
    def selectMemoryFact(self, key: str) -> None:
        for fact in self._selected_category.get("facts", []):
            if str(fact.get("key", "")) == key:
                self._selected_fact = dict(fact)
                self.selectedMemoryFactChanged.emit()
                return

    @Slot(str, str, str, str, int, str)
    def reloadExperiences(
        self,
        _query: str,
        _category: str,
        _outcome: str,
        _deprecated_mode: str,
        _min_quality: int,
        _sort_by: str,
    ) -> None:
        return None

    @Slot(str)
    def selectExperience(self, key: str) -> None:
        for item in self._experiences:
            if str(item.get("key", "")) == key:
                self._selected_experience = dict(item)
                self.selectedExperienceChanged.emit()
                return

    @Slot()
    def refreshMemoryCategories(self) -> None:
        return None

    @Slot(str, str)
    def saveMemoryCategory(self, _category: str, _content: str) -> None:
        return None

    @Slot(str, str, str)
    def saveMemoryFact(self, _category: str, _key: str, _content: str) -> None:
        return None

    @Slot(str)
    def clearMemoryCategory(self, _category: str) -> None:
        return None

    @Slot(str)
    def deleteExperience(self, _key: str) -> None:
        return None


class DummySkillsService(QObject):
    changed = Signal()
    operationFinished = Signal(str, bool)
    selectedSkillChanged = Signal()
    selectedDiscoverChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._skills: list[dict[str, object]] = []
        self._selected_skill = {
            "id": "frontend-design",
            "name": "frontend-design",
            "displayName": {"zh": "前端设计", "en": "Frontend Design"},
            "displaySummary": {"zh": "做大胆而清晰的界面。", "en": "Build bold and clear interfaces."},
            "summary": "Build bold and clear interfaces.",
            "status": "ready",
            "statusLabel": {"zh": "现在可用", "en": "Ready now"},
            "source": "builtin",
            "always": False,
        }
        self._selected_content = "# Frontend Design\n\nUse bold layouts."
        self._discover_results = [
            {
                "id": "registry/frontend-design",
                "publisher": "vercel-labs",
                "version": "1.0.0",
                "displayName": {"zh": "前端设计", "en": "Frontend Design"},
                "displaySummary": {"zh": "生成高质量前端。", "en": "Create polished frontends."},
                "summary": "Create polished frontends.",
            }
        ]
        self._selected_discover = dict(self._discover_results[0])
        self._query = ""
        self._discover_query = "frontend"
        self._discover_reference = ""
        self._source_filter = "all"

    @Property(dict, constant=True)
    def overview(self) -> dict[str, object]:
        return {"readyCount": 1, "needsSetupCount": 1}

    @Property("QVariantList", constant=True)
    def skillsModel(self) -> list[dict[str, object]]:
        return [dict(item) for item in self._skills]

    @Property(int, constant=True)
    def totalCount(self) -> int:
        return len(self._skills)

    @Property(dict, notify=selectedSkillChanged)
    def selectedSkill(self) -> dict[str, object]:
        return dict(self._selected_skill)

    @Property(str, notify=selectedSkillChanged)
    def selectedSkillId(self) -> str:
        return str(self._selected_skill.get("id", ""))

    @Property(str, notify=selectedSkillChanged)
    def selectedContent(self) -> str:
        return self._selected_content

    @Property(str, constant=True)
    def query(self) -> str:
        return self._query

    @Property(str, constant=True)
    def sourceFilter(self) -> str:
        return self._source_filter

    @Property(bool, constant=True)
    def busy(self) -> bool:
        return False

    @Property("QVariantList", constant=True)
    def discoverResultsModel(self) -> list[dict[str, object]]:
        return [dict(item) for item in self._discover_results]

    @Property(int, constant=True)
    def discoverResultCount(self) -> int:
        return len(self._discover_results)

    @Property(dict, notify=selectedDiscoverChanged)
    def selectedDiscoverItem(self) -> dict[str, object]:
        return dict(self._selected_discover)

    @Property(str, notify=selectedDiscoverChanged)
    def selectedDiscoverId(self) -> str:
        return str(self._selected_discover.get("id", ""))

    @Property(str, constant=True)
    def discoverQuery(self) -> str:
        return self._discover_query

    @Property(str, constant=True)
    def discoverReference(self) -> str:
        return self._discover_reference

    @Property(dict, constant=True)
    def discoverTask(self) -> dict[str, object]:
        return {
            "state": "completed",
            "kind": "search",
            "message": "Found 1 matching skill.",
            "reference": "vercel-labs/agent-skills@frontend-design",
        }

    @Slot(str)
    def setQuery(self, _query: str) -> None:
        return None

    @Slot(str)
    def setSourceFilter(self, _value: str) -> None:
        return None

    @Slot()
    def openUserSkillsFolder(self) -> None:
        return None

    @Slot(str)
    def setDiscoverQuery(self, _query: str) -> None:
        return None

    @Slot()
    def searchRemote(self) -> None:
        return None

    @Slot(str)
    def setDiscoverReference(self, _reference: str) -> None:
        return None

    @Slot()
    def installDiscoverReference(self) -> None:
        return None

    @Slot()
    def openSkillsRegistry(self) -> None:
        return None


class DummyToolsService(QObject):
    changed = Signal()
    operationFinished = Signal(str, bool)
    selectedItemChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._catalog = [
            {
                "id": "builtin-web",
                "name": "web",
                "kind": "builtin",
                "bundle": "web",
                "status": "ready",
                "displayName": {"zh": "网页工具", "en": "Web tools"},
                "displaySummary": {"zh": "抓取、搜索和浏览器能力。", "en": "Fetch, search, and browser capabilities."},
                "displayDetail": {"zh": "集中管理网页相关能力。", "en": "Manage web capabilities in one place."},
                "displayStatusLabel": {"zh": "已就绪", "en": "Ready"},
                "statusDetailDisplay": {"zh": "浏览器运行时已托管。", "en": "Browser runtime is managed."},
                "includesSummaryDisplay": {"zh": "包含 3 个底层工具", "en": "Includes 3 underlying tools"},
                "runtimeStateDisplay": {"zh": "上次成功暴露", "en": "Exposed recently"},
                "formKind": "overview",
                "includedTools": ["web_search", "web_fetch", "agent_browser"],
                "badges": [],
            }
        ]
        self._servers = [
            {
                "id": "mcp-local",
                "name": "local-mcp",
                "kind": "mcp_server",
                "status": "configured",
                "displayName": {"zh": "本地 MCP", "en": "Local MCP"},
                "displaySummary": {"zh": "已配置 2 个工具。", "en": "Configured with 2 tools."},
                "displayDetail": {"zh": "用于本地工作区能力。", "en": "Used for workspace-specific tooling."},
                "displayStatusLabel": {"zh": "已设置", "en": "Configured"},
                "statusDetailDisplay": {"zh": "最近一次探测成功。", "en": "Latest probe succeeded."},
                "runtimeStateDisplay": {"zh": "2 个运行时工具", "en": "2 runtime tools"},
                "formKind": "overview",
                "configValues": {"transport": "stdio"},
                "includedTools": ["foo", "bar"],
                "badges": [],
            }
        ]
        self._selected_item = dict(self._catalog[0])

    @Property("QVariantList", constant=True)
    def catalogModel(self) -> list[dict[str, object]]:
        return [dict(item) for item in self._catalog]

    @Property("QVariantList", constant=True)
    def serverModel(self) -> list[dict[str, object]]:
        return [dict(item) for item in self._servers]

    @Property(int, constant=True)
    def catalogCount(self) -> int:
        return len(self._catalog)

    @Property(int, constant=True)
    def serverCount(self) -> int:
        return len(self._servers)

    @Property(str, constant=True)
    def firstCatalogItemId(self) -> str:
        return str(self._catalog[0]["id"])

    @Property(str, constant=True)
    def firstServerItemId(self) -> str:
        return str(self._servers[0]["id"])

    @Property(dict, notify=selectedItemChanged)
    def selectedItem(self) -> dict[str, object]:
        return dict(self._selected_item)

    @Property(str, notify=selectedItemChanged)
    def selectedItemId(self) -> str:
        return str(self._selected_item.get("id", ""))

    @Property(dict, constant=True)
    def overview(self) -> dict[str, object]:
        return {
            "availableCount": 3,
            "recentExposureCount": 1,
            "healthyMcpCount": 1,
            "attentionCount": 0,
            "summaryMetrics": [
                {"key": "available", "displayLabel": {"zh": "当前可用", "en": "Available now"}, "value": 3, "tone": "#FFB33D"},
                {"key": "mcp_connected", "displayLabel": {"zh": "MCP 已连通", "en": "MCP connected"}, "value": 1, "tone": "#60A5FA"},
            ],
            "exposureDomainOptions": [
                {"key": "core", "displayLabel": {"zh": "核心本地", "en": "Core local"}},
                {"key": "web_research", "displayLabel": {"zh": "网页检索", "en": "Web research"}},
            ],
            "observability": [
                {"label": "web_search", "value": "4"},
                {"label": "agent_browser", "value": "2"},
            ],
            "toolExposureMode": "off",
            "toolExposureDomains": ["core", "web_research"],
            "restrictToWorkspace": True,
        }

    @Property(str, constant=True)
    def query(self) -> str:
        return ""

    @Property(str, constant=True)
    def sourceFilter(self) -> str:
        return "all"

    @Property(bool, constant=True)
    def busy(self) -> bool:
        return False

    @Slot(str)
    def selectItem(self, item_id: str) -> None:
        for row in [*self._catalog, *self._servers]:
            if str(row.get("id", "")) == item_id:
                self._selected_item = dict(row)
                self.selectedItemChanged.emit()
                return

    @Slot(str)
    def setSourceFilter(self, _value: str) -> None:
        return None

    @Slot(str)
    def setQuery(self, _query: str) -> None:
        return None

    @Slot("QVariantMap")
    def saveConfig(self, _payload: dict[str, object]) -> None:
        return None


class DummyEmptyServerToolsService(DummyToolsService):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._servers = []
        self._selected_item = {}

    @Property("QVariantList", constant=True)
    def serverModel(self) -> list[dict[str, object]]:
        return []

    @Property(int, constant=True)
    def serverCount(self) -> int:
        return 0

    @Property(str, constant=True)
    def firstServerItemId(self) -> str:
        return ""


def _build_config_service() -> DummyConfigService:
    config_service = DummyConfigService(
        providers=[
            {
                "name": "primary",
                "type": "openai",
                "apiKey": "sk-test",
                "apiBase": "https://api.openai.com/v1",
            }
        ],
        model="right-gpt/gpt-5.4",
    )
    _ = config_service.save(
        {
            "agents": {"defaults": {"model": "right-gpt/gpt-5.4"}},
            "ui": {"language": "en"},
        }
    )
    return config_service


def _load_workspace_window(workspace_name: str):
    engine, root = _load_light_main_window(
        config_service=_build_config_service(),
        cron_service=DummyCronService(),
        heartbeat_service=DummyHeartbeatService(),
        memory_service=DummyMemoryService(),
        skills_service=DummySkillsService(),
        tools_service=DummyToolsService(),
    )
    root.setProperty("width", 640)
    root.setProperty("height", 600)
    root.setProperty("startView", "chat")
    root.setProperty("activeWorkspace", workspace_name)
    _process(220)
    return engine, root


def _load_tools_workspace_window(*, tools_service: QObject):
    engine, root = _load_light_main_window(
        config_service=_build_config_service(),
        cron_service=DummyCronService(),
        heartbeat_service=DummyHeartbeatService(),
        memory_service=DummyMemoryService(),
        skills_service=DummySkillsService(),
        tools_service=tools_service,
    )
    root.setProperty("width", 640)
    root.setProperty("height", 600)
    root.setProperty("startView", "chat")
    root.setProperty("activeWorkspace", "tools")
    _process(220)
    return engine, root


def _save_workspace_screenshot(root, name: str) -> Path:
    output_dir = desktop_ui_smoke_output_dir("bao-workspace-compact")
    output_path = output_dir / f"{name}.png"
    if output_path.exists():
        output_path.unlink()
    image = root.grabWindow()
    assert image.save(str(output_path)), f"failed to save screenshot: {output_path}"
    return output_path


def _scene_rect(item) -> tuple[float, float, float, float]:
    top_left = item.mapToScene(QtCore.QPointF(0, 0))
    left = float(top_left.x())
    top = float(top_left.y())
    width = float(item.property("width") or 0)
    height = float(item.property("height") or 0)
    return left, top, left + width, top + height


def _assert_no_overlap(first, second) -> None:
    first_width = float(first.property("width") or 0)
    first_height = float(first.property("height") or 0)
    second_width = float(second.property("width") or 0)
    second_height = float(second.property("height") or 0)
    if first_width <= 1 or first_height <= 1 or second_width <= 1 or second_height <= 1:
        return

    first_left, first_top, first_right, first_bottom = _scene_rect(first)
    second_left, second_top, second_right, second_bottom = _scene_rect(second)
    separated = (
        first_right <= second_left + 0.5
        or second_right <= first_left + 0.5
        or first_bottom <= second_top + 0.5
        or second_bottom <= first_top + 0.5
    )
    assert separated, (
        f"objects overlap: {first.objectName()} {first_left, first_top, first_right, first_bottom} "
        f"vs {second.objectName()} {second_left, second_top, second_right, second_bottom}"
    )


def _collect_stackbefore_messages(messages: list[str]) -> list[str]:
    return [message for message in messages if "QQuickItem::stackBefore" in message]


def _find_quick_item_by_object_name(root, object_name: str):
    queue = [root]
    while queue:
        current = queue.pop(0)
        if str(current.objectName()) == object_name:
            return current
        child_items = getattr(current, "childItems", None)
        if callable(child_items):
            queue.extend(child_items())
    raise AssertionError(f"quick item not found: {object_name}")


@pytest.mark.parametrize(
    ("workspace_name", "split_name", "pane_names", "list_name", "header_names"),
    [
        (
            "memory",
            "memoryWorkspaceMainSplit",
            ("memoryWorkspaceBrowserPane", "memoryWorkspaceDetailPane"),
            "memoryCategoryList",
            (
                "memoryWorkspaceHeaderIntro",
                "memoryWorkspaceHeaderTabs",
                "memoryWorkspaceHeaderActions",
            ),
        ),
        (
            "skills",
            "skillsWorkspaceInstalledSplit",
            ("skillsFilterRail", "skillsInstalledListPane", "skillsInstalledDetailPane"),
            "skillsInstalledList",
            (
                "skillsWorkspaceHeaderIntro",
                "skillsWorkspaceHeaderTabs",
                "skillsWorkspaceHeaderActions",
            ),
        ),
        (
            "tools",
            "toolsWorkspaceInstalledSplit",
            ("toolsFilterRail", "toolsCatalogPanel", "toolsInstalledDetailPane"),
            "toolsCatalogList",
            (
                "toolsWorkspaceHeaderIntro",
                "toolsWorkspaceHeaderTabs",
                "toolsWorkspaceHeaderActions",
            ),
        ),
        (
            "cron",
            "cronWorkspaceMainSplit",
            ("cronListPanel", "cronDetailPanel"),
            "cronTaskList",
            (
                "cronWorkspaceHeaderIntro",
                "cronWorkspaceHeaderTabs",
                "cronWorkspaceHeaderActions",
            ),
        ),
    ],
)
def test_workspace_compact_layouts_stack_panes_and_capture_screenshot(
    workspace_name: str,
    split_name: str,
    pane_names: tuple[str, ...],
    list_name: str,
    header_names: tuple[str, ...],
) -> None:
    qt_messages: list[str] = []

    def _handler(_msg_type, _context, message) -> None:
        qt_messages.append(str(message))

    previous_handler = QtCore.qInstallMessageHandler(_handler)
    try:
        engine, root = _load_workspace_window(workspace_name)
        try:
            split = find_object(root, split_name)
            wait_until(lambda: split.property("orientation") == Qt.Vertical)
            assert split.property("orientation") == Qt.Vertical
            assert_item_within_window(root, split, inset=8.0)

            for pane_name in pane_names:
                pane = find_object(root, pane_name)
                assert float(pane.property("width")) >= 220.0, pane_name
                assert_item_within_window(root, pane, inset=8.0)

            list_view = find_object(root, list_name)
            assert bool(list_view.property("reuseItems")) is True
            assert int(list_view.property("cacheBuffer")) >= 720

            header_items = [find_object(root, object_name) for object_name in header_names]
            for header_item in header_items:
                assert_item_within_window(root, header_item, inset=8.0)
            for index, header_item in enumerate(header_items):
                for next_item in header_items[index + 1:]:
                    _assert_no_overlap(header_item, next_item)

            screenshot_path = _save_workspace_screenshot(root, f"{workspace_name}-compact")
            assert screenshot_path.is_file()
            assert screenshot_path.stat().st_size > 0
            assert _collect_stackbefore_messages(qt_messages) == []
        finally:
            root.deleteLater()
            engine.deleteLater()
            _process(0)
    finally:
        QtCore.qInstallMessageHandler(previous_handler)


def test_chat_sidebar_compact_layout_keeps_control_tower_metrics_inside_window() -> None:
    chat_service = DummyChatService(
        EmptyMessagesModel(),
        state="idle",
        active_session_ready=False,
        active_session_has_messages=False,
    )
    session_model = SessionsModel([])
    engine, root = _load_light_main_window(
        config_service=_build_config_service(),
        session_model=session_model,
        chat_service=chat_service,
    )

    try:
        root.setProperty("width", 640)
        root.setProperty("height", 600)
        root.setProperty("startView", "chat")
        wait_for_scene_contract(root, DESKTOP_SMOKE_SCREENSHOT_SCENARIOS[2].scene_contract)

        session_list = find_object(root, "sidebarSessionList")
        control_tower_card = find_object(root, "sidebarControlTowerCard")
        control_tower_title = find_object(root, "sidebarControlTowerTitle")
        metrics_flow = find_object(root, "sidebarControlTowerMetricsFlow")
        sidebar_empty_state = find_object(root, "sidebarEmptyState")
        sidebar_empty_title = find_object(root, "sidebarEmptyTitle")
        sidebar_empty_hint = find_object(root, "sidebarEmptyHint")
        sidebar_empty_cta = find_object(root, "sidebarEmptyCta")
        metric_chips = [
            _find_quick_item_by_object_name(metrics_flow, "sidebarControlTowerMetric_sidebarWorking"),
            _find_quick_item_by_object_name(metrics_flow, "sidebarControlTowerMetric_sidebarAutomation"),
            _find_quick_item_by_object_name(metrics_flow, "sidebarControlTowerMetric_sidebarPending"),
        ]

        assert bool(session_list.property("reuseItems")) is True
        assert int(session_list.property("cacheBuffer")) >= 720

        for item in (
            control_tower_card,
            control_tower_title,
            metrics_flow,
            sidebar_empty_state,
            sidebar_empty_title,
            sidebar_empty_hint,
            sidebar_empty_cta,
            *metric_chips,
        ):
            assert_item_within_window(root, item, inset=8.0)

        for index, metric_chip in enumerate(metric_chips):
            for next_chip in metric_chips[index + 1:]:
                _assert_no_overlap(metric_chip, next_chip)

        screenshot_path = _save_workspace_screenshot(root, "chat-sidebar-compact")
        assert screenshot_path.is_file()
        assert screenshot_path.stat().st_size > 0
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_cron_compact_empty_state_copy_matches_vertical_layout() -> None:
    engine, root = _load_workspace_window("cron")

    try:
        detail_title = find_object(root, "cronDetailEmptyTitle")
        detail_description = find_object(root, "cronDetailEmptyDescription")
        status_summary = find_object(root, "cronStatusSummaryText")

        assert detail_title.property("text") == "Select a task from the list first"
        assert detail_description.property("text") == (
            "After you select one, this area guides you through the setup step by step."
        )
        assert status_summary.property("text") == (
            "After you select one, this area shows status and quick actions."
        )
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)


def test_tools_servers_empty_state_copy_points_to_current_action_location() -> None:
    engine, root = _load_tools_workspace_window(tools_service=DummyEmptyServerToolsService())

    try:
        tools_root = find_object(root, "toolsWorkspaceRoot")
        tools_root.setProperty("currentScope", "servers")
        _process(160)

        catalog_description = find_object(root, "toolsServerCatalogEmptyDescription")
        detail_description = find_object(root, "toolsServerDetailEmptyDescription")

        expected_catalog = "Use Add MCP server in the top right, or import an MCP definition you already use."
        expected_detail = "Pick a configured server from the list, or add one from the top right."
        assert catalog_description.property("text") == expected_catalog
        assert detail_description.property("text") == expected_detail
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)
