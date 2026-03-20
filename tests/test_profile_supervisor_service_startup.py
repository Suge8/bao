# ruff: noqa: E402, N802, N815
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from tests._profile_supervisor_service_harness import build_supervisor
from tests._profile_supervisor_service_testkit import model_items, wait_until

pytest_plugins = ("tests._profile_supervisor_service_testkit",)


def test_supervisor_projects_startup_greeting_into_working_and_completed(tmp_path: Path, qt_app, fake_home: Path) -> None:
    _ = qt_app
    _ = fake_home
    harness = build_supervisor(tmp_path)
    try:
        harness.chat_service.startupActivity = {
            "kind": "startup_greeting",
            "status": "running",
            "sessionKey": "desktop:local::main",
            "sessionKeys": ["desktop:local::main", "imessage:13800138000"],
            "channelKeys": ["desktop", "imessage"],
            "updatedAt": datetime.now(timezone.utc).isoformat(),
        }
        harness.supervisor.refresh()
        wait_until(lambda: harness.supervisor.overview.get("profileCount") == 2)
        running_item = next(item for item in model_items(harness.supervisor.workingModel) if str(item.get("kind", "")) == "startup_greeting")
        assert running_item["statusKey"] == "running"
        assert running_item["statusLabel"] == "发送中"
        assert running_item["channelKeys"] == ["imessage", "desktop"]
        assert running_item["accentKey"] == "imessage"
        harness.chat_service.startupActivity = {
            "kind": "startup_greeting",
            "status": "completed",
            "sessionKey": "desktop:local::main",
            "sessionKeys": ["desktop:local::main", "imessage:13800138000"],
            "channelKeys": ["desktop", "imessage"],
            "updatedAt": datetime.now(timezone.utc).isoformat(),
        }
        harness.supervisor.refresh()
        wait_until(lambda: any(str(item.get("kind", "")) == "startup_greeting" for item in model_items(harness.supervisor.completedModel)))
        assert not any(str(item.get("kind", "")) == "startup_greeting" for item in model_items(harness.supervisor.workingModel))
        completed_item = next(item for item in model_items(harness.supervisor.completedModel) if str(item.get("kind", "")) == "startup_greeting")
        assert completed_item["statusKey"] == "completed"
        assert completed_item["statusLabel"] == "已完成"
        assert completed_item["channelKeys"] == ["imessage", "desktop"]
        assert completed_item["routeKind"] == "profile"
    finally:
        harness.runner.shutdown(grace_s=1.0)
