from __future__ import annotations

from typing import Any, ClassVar

from PySide6.QtCore import Property, QObject, Signal

from app.backend._memory_async import MemoryServiceAsyncMixin
from app.backend._memory_projection import MemoryServiceProjectionMixin
from app.backend._memory_view import MemoryServiceViewMixin
from app.backend.asyncio_runner import AsyncioRunner
from app.backend.list_model import KeyValueListModel
from bao.agent.memory import MemoryChangeEvent, MemoryStore


class MemoryService(
    MemoryServiceAsyncMixin,
    MemoryServiceProjectionMixin,
    MemoryServiceViewMixin,
    QObject,
):
    readyChanged: ClassVar[Signal] = Signal()
    busyChanged: ClassVar[Signal] = Signal()
    blockingBusyChanged: ClassVar[Signal] = Signal()
    errorChanged: ClassVar[Signal] = Signal(str)
    memoryCategoriesChanged: ClassVar[Signal] = Signal()
    experienceItemsChanged: ClassVar[Signal] = Signal()
    selectedMemoryCategoryChanged: ClassVar[Signal] = Signal()
    selectedMemoryFactChanged: ClassVar[Signal] = Signal()
    selectedMemoryFactKeyChanged: ClassVar[Signal] = Signal()
    selectedExperienceChanged: ClassVar[Signal] = Signal()
    memoryStatsChanged: ClassVar[Signal] = Signal()
    experienceStatsChanged: ClassVar[Signal] = Signal()
    operationFinished: ClassVar[Signal] = Signal(str, bool)
    _runnerResult: ClassVar[Signal] = Signal(object)
    _externalChangeRequested: ClassVar[Signal] = Signal(str, str, str)
    _MUTATION_BUSY_MESSAGE = "Another memory operation is already in progress."
    _SUCCESS_MESSAGES: ClassVar[dict[str, str]] = {
        "save_memory": "Memory saved",
        "append_memory": "Memory updated",
        "clear_memory": "Memory cleared",
        "save_memory_fact": "Memory fact saved",
        "delete_memory_fact": "Memory fact deleted",
        "deprecate_experience": "Experience updated",
        "delete_experience": "Experience deleted",
        "promote_experience": "Experience promoted",
    }

    def __init__(self, runner: AsyncioRunner, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._runner = runner
        self._memory_store_cls = MemoryStore
        self._store: MemoryStore | None = None
        self._storage_root = ""
        self._desired_storage_root = ""
        self._bootstrap_request_seq = 0
        self._latest_bootstrap_request_seq = 0
        self._ready = False
        self._busy = False
        self._busy_count = 0
        self._blocking_busy = False
        self._blocking_busy_count = 0
        self._error = ""
        self._memory_categories: list[dict[str, Any]] = []
        self._experience_items: list[dict[str, Any]] = []
        self._memory_query = ""
        self._filtered_memory_categories: list[dict[str, Any]] = []
        self._memory_category_model = KeyValueListModel(self)
        self._experience_model = KeyValueListModel(self)
        self._selected_memory_fact_key = ""
        self._memory_stats: dict[str, Any] = {}
        self._experience_stats: dict[str, Any] = {}
        self._selected_memory_category_name = "project"
        self._selected_experience_key = ""
        self._experience_query = ""
        self._experience_category = ""
        self._experience_outcome = ""
        self._experience_deprecated_mode = "active"
        self._experience_min_quality = 0
        self._experience_sort_by = "updated_desc"
        self._experience_request_seq = 0
        self._latest_experience_request_seq = 0
        self._experience_detail_request_seq = 0
        self._latest_experience_detail_request_seq = 0
        self._store_listener = self._on_store_change
        self._runnerResult.connect(self._handle_runner_result)
        self._externalChangeRequested.connect(self._handle_external_change)

    @Property(bool, notify=readyChanged)
    def ready(self) -> bool:
        return self._ready

    @Property(bool, notify=busyChanged)
    def busy(self) -> bool:
        return self._busy

    @Property(bool, notify=blockingBusyChanged)
    def blockingBusy(self) -> bool:
        return self._blocking_busy

    @Property(str, notify=errorChanged)
    def lastError(self) -> str:
        return self._error

    @Property(QObject, constant=True)
    def memoryCategoryModel(self) -> QObject:
        return self._memory_category_model

    @Property(QObject, constant=True)
    def experienceModel(self) -> QObject:
        return self._experience_model

    @Property(int, notify=memoryCategoriesChanged)
    def memoryCategoryCount(self) -> int:
        return len(self._filtered_memory_categories)

    @Property(int, notify=experienceItemsChanged)
    def experienceCount(self) -> int:
        return len(self._experience_items)

    @Property(str, notify=memoryCategoriesChanged)
    def memoryQuery(self) -> str:
        return self._memory_query

    @Property(dict, notify=selectedMemoryCategoryChanged)
    def selectedMemoryCategory(self) -> dict[str, Any]:
        return self._selected_memory_category()

    @Property(dict, notify=selectedMemoryFactChanged)
    def selectedMemoryFact(self) -> dict[str, Any]:
        return self._selected_memory_fact()

    @Property(str, notify=selectedMemoryFactKeyChanged)
    def selectedMemoryFactKey(self) -> str:
        return self._selected_memory_fact_key

    @Property(dict, notify=selectedExperienceChanged)
    def selectedExperience(self) -> dict[str, Any]:
        return self._selected_experience()

    @Property(dict, notify=memoryStatsChanged)
    def memoryStats(self) -> dict[str, Any]:
        return dict(self._memory_stats)

    @Property(dict, notify=experienceStatsChanged)
    def experienceStats(self) -> dict[str, Any]:
        return dict(self._experience_stats)

    def _replace_store(self, next_store: object) -> None:
        previous_store = self._store
        self._store = next_store if isinstance(next_store, MemoryStore) else None
        if previous_store is None or previous_store is self._store:
            if isinstance(self._store, MemoryStore) and previous_store is None:
                self._attach_store_listener(self._store)
            return
        self._detach_store_listener(previous_store)
        if isinstance(self._store, MemoryStore):
            self._attach_store_listener(self._store)
        try:
            previous_store.close()
        except Exception:
            pass

    def _clear_loaded_state(self) -> None:
        self._replace_store(None)
        self._storage_root = ""
        if not self._ready and not self._memory_categories and not self._experience_items:
            return
        self._memory_categories = []
        self._filtered_memory_categories = []
        self._experience_items = []
        self._memory_category_model.sync_items([])
        self._experience_model.sync_items([])
        self._memory_stats = {}
        self._experience_stats = {}
        self._selected_memory_fact_key = ""
        self._selected_experience_key = ""
        self._ready = False
        self.memoryCategoriesChanged.emit()
        self.experienceItemsChanged.emit()
        self.memoryStatsChanged.emit()
        self.experienceStatsChanged.emit()
        self.selectedMemoryCategoryChanged.emit()
        self.selectedMemoryFactChanged.emit()
        self.selectedMemoryFactKeyChanged.emit()
        self.selectedExperienceChanged.emit()
        self.readyChanged.emit()

    def _require_store(self) -> MemoryStore:
        if self._store is None:
            raise RuntimeError("Memory workspace is not ready")
        return self._store

    def _set_busy(self, busy: bool) -> None:
        if busy:
            self._busy_count += 1
        else:
            self._busy_count = max(0, self._busy_count - 1)
        normalized = self._busy_count > 0
        if normalized == self._busy:
            return
        self._busy = normalized
        self.busyChanged.emit()

    def _set_blocking_busy(self, busy: bool) -> None:
        if busy:
            self._blocking_busy_count += 1
        else:
            self._blocking_busy_count = max(0, self._blocking_busy_count - 1)
        normalized = self._blocking_busy_count > 0
        if normalized == self._blocking_busy:
            return
        self._blocking_busy = normalized
        self.blockingBusyChanged.emit()

    def _set_error(self, error: str) -> None:
        if error == self._error:
            return
        self._error = error
        self.errorChanged.emit(error)

    def _attach_store_listener(self, store: MemoryStore) -> None:
        add_listener = getattr(store, "add_change_listener", None)
        if callable(add_listener):
            add_listener(self._store_listener)

    def _detach_store_listener(self, store: MemoryStore) -> None:
        remove_listener = getattr(store, "remove_change_listener", None)
        if callable(remove_listener):
            remove_listener(self._store_listener)

    def _on_store_change(self, event: MemoryChangeEvent) -> None:
        self._externalChangeRequested.emit(event.scope, event.category, event.operation)
