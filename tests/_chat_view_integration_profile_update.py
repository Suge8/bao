# ruff: noqa: E402, N802, N815, F403, F405, I001
from __future__ import annotations

from tests._chat_view_integration_shared import *
from tests._chat_view_integration_models import *

class DummyProfileSupervisorService(QObject):
    overviewChanged = Signal()
    profilesChanged = Signal()
    workingChanged = Signal()
    completedChanged = Signal()
    automationChanged = Signal()
    attentionChanged = Signal()
    laneRowsChanged = Signal()
    selectionChanged = Signal()
    busyChanged = Signal(bool)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.refresh_calls = 0
        self.activate_profile_calls: list[str] = []
        self.select_profile_calls: list[str] = []
        self.select_item_calls: list[str] = []
        self.open_target_calls = 0

    @Property(dict, notify=overviewChanged)
    def overview(self) -> dict[str, object]:
        return {
            "liveProfileId": "default",
            "liveHubLive": False,
            "totalSessionCount": 0,
        }

    @Property(QObject, constant=True)
    def profilesModel(self) -> QObject:
        return EmptyMessagesModel(self)

    @Property(QObject, constant=True)
    def workingModel(self) -> QObject:
        return EmptyMessagesModel(self)

    @Property(QObject, constant=True)
    def completedModel(self) -> QObject:
        return EmptyMessagesModel(self)

    @Property(QObject, constant=True)
    def automationModel(self) -> QObject:
        return EmptyMessagesModel(self)

    @Property(QObject, constant=True)
    def attentionModel(self) -> QObject:
        return EmptyMessagesModel(self)

    @Property(int, notify=profilesChanged)
    def profileCount(self) -> int:
        return 0

    @Property(int, notify=workingChanged)
    def workingCount(self) -> int:
        return 0

    @Property(int, notify=completedChanged)
    def completedCount(self) -> int:
        return 0

    @Property(int, notify=automationChanged)
    def automationCount(self) -> int:
        return 0

    @Property(int, notify=attentionChanged)
    def attentionCount(self) -> int:
        return 0

    @Property(dict, notify=selectionChanged)
    def selectedProfile(self) -> dict[str, object]:
        return {}

    @Property(dict, notify=selectionChanged)
    def selectedItem(self) -> dict[str, object]:
        return {}

    @Property(bool, notify=busyChanged)
    def busy(self) -> bool:
        return False

    @Slot()
    def refresh(self) -> None:
        self.refresh_calls += 1

    @Slot(str)
    def selectProfile(self, profile_id: str) -> None:
        self.select_profile_calls.append(profile_id)

    @Slot()
    def clearProfileFilter(self) -> None:
        return None

    @Slot(str)
    def activateProfile(self, profile_id: str) -> None:
        self.activate_profile_calls.append(profile_id)

    @Slot(str)
    def selectItem(self, item_id: str) -> None:
        self.select_item_calls.append(item_id)

    @Slot()
    def clearSelection(self) -> None:
        return None

    @Slot()
    def openSelectedTarget(self) -> None:
        self.open_target_calls += 1


class DummyUpdateService(QObject):
    quitRequested = Signal()

    @Property(str, constant=True)
    def state(self) -> str:
        return "idle"

    @Property(str, constant=True)
    def currentVersion(self) -> str:
        return "0.0.0"

    @Property(str, constant=True)
    def latestVersion(self) -> str:
        return ""

    @Property(str, constant=True)
    def notesMarkdown(self) -> str:
        return ""

    @Property(str, constant=True)
    def errorMessage(self) -> str:
        return ""

    @Property(float, constant=True)
    def downloadProgress(self) -> float:
        return 0.0

    @Slot()
    def reloadConfig(self) -> None:
        return None

    @Slot()
    def checkForUpdates(self) -> None:
        return None

    @Slot()
    def installUpdate(self) -> None:
        return None


class DummyUpdateBridge(QObject):
    @Slot()
    def reloadRequested(self) -> None:
        return None

    @Slot()
    def checkRequested(self) -> None:
        return None

    @Slot()
    def installRequested(self) -> None:
        return None

__all__ = [name for name in globals() if name != "__all__" and not (name.startswith("__") and name.endswith("__"))]
