# ruff: noqa: N802, N815
from __future__ import annotations

import importlib

from tests._chat_view_integration_testkit import (
    DummyConfigService,
    DummyCronService,
    DummyHeartbeatService,
    _load_light_main_window,
    _process,
)
from tests.desktop_ui_testkit import (
    assert_item_within_window,
    desktop_ui_smoke_output_dir,
    find_object,
    qapp,  # noqa: F401
    wait_until,
)

pytest = importlib.import_module("pytest")
QtCore = pytest.importorskip("PySide6.QtCore")

QObject = QtCore.QObject
Property = QtCore.Property
Signal = QtCore.Signal
Slot = QtCore.Slot

pytestmark = [pytest.mark.gui, pytest.mark.desktop_ui_smoke, pytest.mark.usefixtures("qapp")]


class DummyToolsService(QObject):
    changed = Signal()
    operationFinished = Signal(str, bool)
    selectedItemChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._catalog = [
            {
                "id": "builtin:exec",
                "name": "exec",
                "kind": "builtin",
                "bundle": "core",
                "status": "configured",
                "formKind": "exec",
                "displayName": {"zh": "终端执行", "en": "Terminal Exec"},
                "displaySummary": {
                    "zh": "在运行主机上执行命令，并受超时与沙箱策略约束。",
                    "en": "Run shell commands on the runtime host with sandbox controls.",
                },
                "displayDetail": {
                    "zh": "Exec 是本机命令桥。你可以在这里控制超时、PATH 追加、沙箱模式与工作区边界。",
                    "en": "Exec is the bridge to local shell workflows. Its scope is shaped by timeout, sandbox mode, and workspace restrictions.",
                },
                "displayStatusLabel": {"zh": "已设置", "en": "Configured"},
                "statusDetailDisplay": {
                    "zh": "命令执行受沙箱和工作区边界约束。",
                    "en": "Command execution is governed by sandbox and workspace boundaries.",
                },
                "runtimeStateDisplay": {"zh": "Sandbox semi-auto", "en": "Sandbox semi-auto"},
                "includesSummaryDisplay": {
                    "zh": "这个能力族没有单独的用户侧配置入口。",
                    "en": "This capability family does not expose separate end-user configuration.",
                },
                "configValues": {
                    "timeout": 60,
                    "pathAppend": "/opt/homebrew/bin:/usr/local/bin",
                    "sandboxMode": "semi-auto",
                    "restrictToWorkspace": False,
                },
                "badges": [],
            }
        ]
        self._selected_item = dict(self._catalog[0])

    @Property("QVariantList", constant=True)
    def catalogModel(self) -> list[dict[str, object]]:
        return [dict(item) for item in self._catalog]

    @Property("QVariantList", constant=True)
    def serverModel(self) -> list[dict[str, object]]:
        return []

    @Property(int, constant=True)
    def catalogCount(self) -> int:
        return len(self._catalog)

    @Property(int, constant=True)
    def serverCount(self) -> int:
        return 0

    @Property(str, constant=True)
    def firstCatalogItemId(self) -> str:
        return str(self._catalog[0]["id"])

    @Property(str, constant=True)
    def firstServerItemId(self) -> str:
        return ""

    @Property(dict, notify=selectedItemChanged)
    def selectedItem(self) -> dict[str, object]:
        return dict(self._selected_item)

    @Property(str, notify=selectedItemChanged)
    def selectedItemId(self) -> str:
        return str(self._selected_item.get("id", ""))

    @Property(dict, constant=True)
    def overview(self) -> dict[str, object]:
        return {
            "summaryMetrics": [
                {"key": "available", "displayLabel": {"zh": "当前可用", "en": "Available now"}, "value": 1, "tone": "#F97316"}
            ],
            "exposureDomainOptions": [],
            "observability": [],
            "toolExposureMode": "off",
            "toolExposureDomains": ["core"],
            "restrictToWorkspace": False,
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
        if item_id == self._selected_item["id"]:
            self.selectedItemChanged.emit()

    @Slot(str)
    def setSourceFilter(self, _value: str) -> None:
        return None

    @Slot(str)
    def setQuery(self, _query: str) -> None:
        return None

    @Slot("QVariantMap")
    def saveConfig(self, _payload: dict[str, object]) -> None:
        return None


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


def _load_exec_detail_window():
    tools_service = DummyToolsService()
    engine, root = _load_light_main_window(
        config_service=_build_config_service(),
        cron_service=DummyCronService(),
        heartbeat_service=DummyHeartbeatService(),
        tools_service=tools_service,
    )
    root.setProperty("width", 980)
    root.setProperty("height", 920)
    root.setProperty("startView", "chat")
    root.setProperty("activeWorkspace", "tools")
    _process(260)
    return engine, root


def test_exec_detail_mode_cards_render_and_capture_screenshot() -> None:
    engine, root = _load_exec_detail_window()

    try:
        detail_pane = find_object(root, "toolsInstalledDetailPane")
        wait_until(lambda: float(detail_pane.property("width")) > 0 and float(detail_pane.property("height")) > 0)
        assert_item_within_window(root, detail_pane, inset=8.0)

        for object_name in ("execModeFlow", "execModeSummaryCard", "execRestrictCard"):
            obj = find_object(root, object_name)
            wait_until(lambda obj=obj: float(obj.property("width")) > 0 and float(obj.property("height")) > 0)
            assert float(obj.property("width")) > 0
            assert float(obj.property("height")) > 0

        output_dir = desktop_ui_smoke_output_dir("bao-tools-exec-detail")
        output_path = output_dir / "exec-detail.png"
        if output_path.exists():
            output_path.unlink()
        image = root.grabWindow()
        assert image.save(str(output_path)), f"failed to save screenshot: {output_path}"
        assert output_path.is_file()
        assert output_path.stat().st_size > 0
    finally:
        root.deleteLater()
        engine.deleteLater()
        _process(0)
