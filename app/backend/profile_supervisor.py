from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import Property, QObject, Signal

from app.backend._profile_supervisor_actions import ProfileSupervisorActionsMixin
from app.backend._profile_supervisor_common import (
    _COLLECTION_NAMES,
)
from app.backend._profile_supervisor_common import (
    _SNAPSHOT_FILENAME as _SUPERVISOR_SNAPSHOT_FILENAME,
)
from app.backend._profile_supervisor_results import ProfileSupervisorResultsMixin
from app.backend._profile_supervisor_snapshot_writer import SnapshotWriter
from app.backend._profile_supervisor_storage import (
    _has_session_storage_roots as _has_session_storage_roots_impl,
)
from app.backend.asyncio_runner import AsyncioRunner
from app.backend.list_model import KeyValueListModel
from bao.profile import ensure_profile_registry

_SNAPSHOT_FILENAME = _SUPERVISOR_SNAPSHOT_FILENAME
_has_session_storage_roots = _has_session_storage_roots_impl


@dataclass(frozen=True)
class ProfileSupervisorServices:
    profile_service: Any
    session_service: Any
    chat_service: Any
    cron_service: Any
    heartbeat_service: Any


class ProfileWorkSupervisorService(
    ProfileSupervisorActionsMixin,
    ProfileSupervisorResultsMixin,
    QObject,
):
    overviewChanged = Signal()
    profilesChanged = Signal()
    workingChanged = Signal()
    completedChanged = Signal()
    automationChanged = Signal()
    attentionChanged = Signal()
    selectionChanged = Signal()
    busyChanged = Signal(bool)
    profileNavigationRequested = Signal(str)

    _refreshResult = Signal(object)

    def __init__(
        self,
        runner: AsyncioRunner,
        *,
        services: ProfileSupervisorServices,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._runner = runner
        self._profile_service = services.profile_service
        self._session_service = services.session_service
        self._chat_service = services.chat_service
        self._cron_service = services.cron_service
        self._heartbeat_service = services.heartbeat_service
        self._collection_names = _COLLECTION_NAMES
        self._overview: dict[str, Any] = {}
        self._profiles: list[dict[str, Any]] = []
        self._profiles_model = KeyValueListModel(self)
        self._section_models = {name: KeyValueListModel(self) for name in _COLLECTION_NAMES}
        self._all_items = self._empty_collections()
        self._visible_items = self._empty_collections()
        self._selected_profile_id = ""
        self._selected_item_id = ""
        self._busy = False
        self._hydrated = False
        self._refresh_inflight = False
        self._refresh_requested = False
        self._pending_action: dict[str, Any] | None = None
        self._snapshot_writer = SnapshotWriter(runner, self)
        self._refreshResult.connect(self._handle_refresh_result)
        self._wire_signals()

    @Property(dict, notify=overviewChanged)
    def overview(self) -> dict[str, Any]:
        return dict(self._overview)

    @Property(QObject, constant=True)
    def profilesModel(self) -> QObject:
        return self._profiles_model

    @Property(QObject, constant=True)
    def workingModel(self) -> QObject:
        return self._section_models["working"]

    @Property(QObject, constant=True)
    def completedModel(self) -> QObject:
        return self._section_models["completed"]

    @Property(QObject, constant=True)
    def automationModel(self) -> QObject:
        return self._section_models["automation"]

    @Property(QObject, constant=True)
    def attentionModel(self) -> QObject:
        return self._section_models["attention"]

    @Property(int, notify=profilesChanged)
    def profileCount(self) -> int:
        return len(self._profiles)

    @Property(int, notify=workingChanged)
    def workingCount(self) -> int:
        return len(self._visible_items["working"])

    @Property(int, notify=completedChanged)
    def completedCount(self) -> int:
        return len(self._visible_items["completed"])

    @Property(int, notify=automationChanged)
    def automationCount(self) -> int:
        return len(self._visible_items["automation"])

    @Property(int, notify=attentionChanged)
    def attentionCount(self) -> int:
        return len(self._visible_items["attention"])

    @Property(dict, notify=selectionChanged)
    def selectedProfile(self) -> dict[str, Any]:
        for item in self._profiles:
            if str(item.get("id", "")) == self._selected_profile_id:
                return dict(item)
        return {}

    @Property(dict, notify=selectionChanged)
    def selectedItem(self) -> dict[str, Any]:
        if not self._selected_item_id:
            return {}
        for collection in self._visible_items.values():
            for item in collection:
                if str(item.get("id", "")) == self._selected_item_id:
                    return dict(item)
        return {}

    @Property(bool, notify=selectionChanged)
    def hasSelection(self) -> bool:
        return bool(self._selected_profile_id or self._selected_item_id)

    @Property(bool, notify=busyChanged)
    def busy(self) -> bool:
        return self._busy

    async def _build_projection(self, captured: dict[str, Any]) -> dict[str, Any]:
        return await self._runner.run_bg_io(self._build_projection_sync, captured)

    def _build_projection_sync(self, captured: dict[str, Any]) -> dict[str, Any]:
        from app.backend._profile_supervisor_projection import build_supervisor_projection

        return build_supervisor_projection(
            captured,
            ensure_profile_registry_fn=lambda workspace: ensure_profile_registry(workspace),
        )
