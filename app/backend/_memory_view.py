from __future__ import annotations

from typing import Any

from PySide6.QtCore import Slot


class MemoryServiceViewMixin:
    @Slot(str)
    def bootstrapWorkspace(self, workspace_path: str) -> None:
        self.bootstrapStorageRoot(workspace_path)

    @Slot(str)
    def bootstrapStorageRoot(self, storage_root: str) -> None:
        self.setStorageRootHint(storage_root)
        self.ensureHydrated()

    @Slot(str)
    def setStorageRootHint(self, storage_root: str) -> None:
        raw_path = storage_root.strip()
        if not raw_path:
            return
        if raw_path == self._desired_storage_root:
            return
        self._desired_storage_root = raw_path
        if raw_path == self._storage_root or self._store is None:
            return
        self._clear_loaded_state()

    @Slot()
    def ensureHydrated(self) -> None:
        target_root = self._desired_storage_root or self._storage_root
        if not target_root:
            return
        if target_root == self._storage_root and self._store is not None:
            self.refreshAll()
            return
        self._bootstrap_request_seq += 1
        self._latest_bootstrap_request_seq = self._bootstrap_request_seq
        self._submit_task("bootstrap", self._bootstrap_store(target_root, self._latest_bootstrap_request_seq))

    @Slot()
    def refreshAll(self) -> None:
        if self._store is None:
            self.ensureHydrated()
            return
        self.refreshMemoryCategories()
        self.reloadExperiences(
            self._experience_query,
            self._experience_category,
            self._experience_outcome,
            self._experience_deprecated_mode,
            self._experience_min_quality,
            self._experience_sort_by,
        )

    @Slot()
    def refreshMemoryCategories(self) -> None:
        if self._store is None:
            self.ensureHydrated()
            return
        self._submit_task("load_memory", self._load_memory_categories())

    @Slot(str)
    def setMemoryQuery(self, query: str) -> None:
        normalized = str(query or "").strip().lower()
        if normalized == self._memory_query:
            return
        self._memory_query = normalized
        self._refresh_visible_memory_categories()
        self.memoryCategoriesChanged.emit()

    @Slot(str)
    def selectMemoryCategory(self, category: str) -> None:
        normalized = category if category in self._memory_categories_by_name else "project"
        self._apply_selected_memory_category(normalized, self._memory_category_from_cache(normalized))

    @property
    def _memory_categories_by_name(self) -> set[str]:
        from bao.agent.memory import MEMORY_CATEGORIES

        return set(MEMORY_CATEGORIES)

    @Slot(str)
    def selectMemoryFact(self, key: str) -> None:
        normalized = key.strip()
        if not normalized:
            self._apply_selected_memory_fact({})
            return
        selected = self._memory_fact_by_key(self._selected_memory_category(), normalized)
        if selected:
            self._apply_selected_memory_fact(selected)

    @Slot(str, str)
    def saveMemoryCategory(self, category: str, content: str) -> None:
        self._submit_task("save_memory", self._save_memory_category(category, content))

    @Slot(str, str)
    def appendMemoryCategory(self, category: str, content: str) -> None:
        self._submit_task("append_memory", self._append_memory_category(category, content))

    @Slot(str)
    def clearMemoryCategory(self, category: str) -> None:
        self._submit_task("clear_memory", self._clear_memory_category(category))

    @Slot(str, str, str)
    def saveMemoryFact(self, category: str, key: str, content: str) -> None:
        self._submit_task("save_memory_fact", self._save_memory_fact(category, key, content))

    @Slot(str, str)
    def deleteMemoryFact(self, category: str, key: str) -> None:
        self._submit_task("delete_memory_fact", self._delete_memory_fact(category, key))

    @Slot(str, str, str, str, int, str)
    def reloadExperiences(self, *args: Any) -> None:
        query = self._normalize_experience_query(args)
        self._set_experience_query(query)
        if self._store is None:
            self.ensureHydrated()
            return
        self._experience_request_seq += 1
        seq = self._experience_request_seq
        self._latest_experience_request_seq = seq
        self._submit_task("load_experiences", self._load_experiences(seq))

    @Slot(str)
    def selectExperience(self, key: str) -> None:
        normalized = key.strip()
        if not normalized:
            self._selected_experience_key = ""
            self.selectedExperienceChanged.emit()
            return
        self._selected_experience_key = normalized
        cached = self._experience_from_cache(normalized)
        if cached is not None:
            self.selectedExperienceChanged.emit()
        self._experience_detail_request_seq += 1
        seq = self._experience_detail_request_seq
        self._latest_experience_detail_request_seq = seq
        self._submit_task("load_experience_detail", self._load_experience_detail(normalized, seq))

    @Slot(str, bool)
    def setExperienceDeprecated(self, key: str, deprecated: bool) -> None:
        self._submit_task("deprecate_experience", self._set_experience_deprecated(key, deprecated))

    @Slot(str)
    def deleteExperience(self, key: str) -> None:
        self._submit_task("delete_experience", self._delete_experience(key))

    @Slot(str, str)
    def promoteExperienceToMemory(self, key: str, category: str) -> None:
        self._submit_task("promote_experience", self._promote_experience_to_memory(key, category))

    @Slot()
    def shutdown(self) -> None:
        self._desired_storage_root = ""
        self._clear_loaded_state()
