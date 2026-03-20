from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from bao.agent.memory import MEMORY_CATEGORIES

from ._memory_common import format_updated_label, parse_updated_at


class MemoryServiceProjectionMixin:
    def _apply_memory_payload(self, kind: str, data: dict[str, Any]) -> None:
        if "memory_items" in data:
            self._apply_memory_items(data.get("memory_items"))
        if "memory_category" in data:
            category = str(data.get("memory_category") or self._selected_memory_category_name)
            self._apply_selected_memory_category(
                category,
                data.get("memory_detail"),
                str(data.get("memory_fact_key") or ""),
            )
            return
        if kind == "load_memory" and not self._selected_memory_category():
            fallback = self._memory_category_from_cache(self._selected_memory_category_name)
            if fallback is None:
                fallback = self._memory_category_from_cache("project")
            self._apply_selected_memory_category(self._selected_memory_category_name, fallback)

    def _apply_experience_payload(self, kind: str, data: dict[str, Any]) -> None:
        if "experience_items" in data:
            self._apply_experience_items(data.get("experience_items"))
        if "experience_detail" in data:
            self._apply_selected_experience_detail(kind, data.get("experience_detail"))
        if kind == "load_experiences" and not self._selected_experience() and self._experience_items:
            self._selected_experience_key = str(self._experience_items[0].get("key", ""))
            self.selectedExperienceChanged.emit()

    def _apply_selected_experience_detail(self, kind: str, detail: object) -> None:
        if isinstance(detail, dict):
            decorated = self._decorate_experience_item(detail)
            self._selected_experience_key = str(decorated.get("key", ""))
            self._upsert_experience_cache(decorated)
        elif detail is None and kind == "delete_experience":
            self._selected_experience_key = ""
        else:
            return
        self.selectedExperienceChanged.emit()

    def _handle_external_change(self, scope: str, category: str, operation: str) -> None:
        del category
        if self._store is None or not self._ready:
            return
        if scope == "experience":
            self.reloadExperiences(
                self._experience_query,
                self._experience_category,
                self._experience_outcome,
                self._experience_deprecated_mode,
                self._experience_min_quality,
                self._experience_sort_by,
            )
            if operation == "promote":
                self.refreshMemoryCategories()
            return
        if scope == "long_term":
            self.refreshMemoryCategories()

    def _decorate_memory_item(self, item: dict[str, Any]) -> dict[str, Any]:
        decorated = dict(item)
        decorated["updated_label"] = format_updated_label(item.get("updated_at"))
        facts = item.get("facts")
        if isinstance(facts, list):
            decorated["facts"] = [
                {
                    **dict(fact),
                    "updated_label": format_updated_label(
                        fact.get("last_hit_at") or fact.get("updated_at")
                    ),
                }
                for fact in facts
                if isinstance(fact, dict)
            ]
        return decorated

    def _decorate_experience_item(self, item: dict[str, Any]) -> dict[str, Any]:
        decorated = dict(item)
        uses = int(item.get("uses", 0) or 0)
        successes = int(item.get("successes", 0) or 0)
        decorated["updated_label"] = format_updated_label(item.get("updated_at"))
        decorated["last_hit_label"] = format_updated_label(item.get("last_hit_at"))
        decorated["success_rate"] = round((successes / uses) * 100, 1) if uses > 0 else 0.0
        return decorated

    def _apply_memory_items(self, items: object) -> None:
        normalized = (
            [self._decorate_memory_item(item) for item in items] if isinstance(items, list) else []
        )
        self._memory_categories = [item for item in normalized if isinstance(item, dict)]
        self._refresh_visible_memory_categories()
        self._memory_stats = self._build_memory_stats(self._memory_categories)
        self.memoryCategoriesChanged.emit()
        self.memoryStatsChanged.emit()

    def _apply_experience_items(self, items: object) -> None:
        normalized = (
            [self._decorate_experience_item(item) for item in items]
            if isinstance(items, list)
            else []
        )
        next_items = [item for item in normalized if isinstance(item, dict)]
        if next_items == self._experience_items:
            return
        self._experience_items = next_items
        self._experience_model.sync_items(self._experience_items)
        self._experience_stats = self._build_experience_stats(self._experience_items)
        self.experienceItemsChanged.emit()
        self.experienceStatsChanged.emit()

    def _refresh_visible_memory_categories(self) -> None:
        query = self._memory_query
        if not query:
            self._filtered_memory_categories = [dict(item) for item in self._memory_categories]
        else:
            self._filtered_memory_categories = [
                dict(item)
                for item in self._memory_categories
                if query
                in " ".join(
                    [
                        str(item.get("category", "") or ""),
                        str(item.get("content", "") or ""),
                        str(item.get("preview", "") or ""),
                    ]
                ).lower()
            ]
        self._memory_category_model.sync_items(self._filtered_memory_categories)

    def _memory_category_from_cache(self, category: str) -> dict[str, Any] | None:
        for item in self._memory_categories:
            if str(item.get("category", "")) == category:
                return dict(item)
        return None

    def _memory_fact_by_key(self, detail: dict[str, Any], key: str) -> dict[str, Any]:
        normalized = key.strip()
        if not normalized:
            return {}
        facts = detail.get("facts")
        if not isinstance(facts, list):
            return {}
        for fact in facts:
            if not isinstance(fact, dict):
                continue
            if str(fact.get("key", "")) == normalized:
                return dict(fact)
        return {}

    def _resolve_selected_memory_fact(
        self, detail: dict[str, Any], preferred_key: str = ""
    ) -> dict[str, Any]:
        selected = self._memory_fact_by_key(detail, preferred_key)
        if selected:
            return selected
        facts = detail.get("facts")
        if not isinstance(facts, list) or not facts:
            return {}
        first = facts[0]
        return dict(first) if isinstance(first, dict) else {}

    def _apply_selected_memory_fact(self, fact: object) -> None:
        selected = dict(fact) if isinstance(fact, dict) else {}
        next_fact_key = str(selected.get("key", "")).strip()
        fact_changed = selected != self._selected_memory_fact()
        key_changed = next_fact_key != self._selected_memory_fact_key
        self._selected_memory_fact_key = next_fact_key
        if fact_changed:
            self.selectedMemoryFactChanged.emit()
        if key_changed:
            self.selectedMemoryFactKeyChanged.emit()

    def _apply_selected_memory_category(
        self, category: str, detail: object, preferred_fact_key: str = ""
    ) -> None:
        normalized_category = category if category in MEMORY_CATEGORIES else "project"
        if isinstance(detail, dict):
            selected = self._decorate_memory_item(detail)
            self._upsert_memory_category_cache(selected)
        else:
            selected = self._memory_category_from_cache(normalized_category) or {}
        selected_fact = self._resolve_selected_memory_fact(
            selected,
            preferred_fact_key or self._selected_memory_fact_key,
        )
        category_changed = selected != self._selected_memory_category()
        fact_changed = selected_fact != self._selected_memory_fact()
        next_fact_key = str(selected_fact.get("key", "")).strip()
        key_changed = next_fact_key != self._selected_memory_fact_key
        self._selected_memory_category_name = normalized_category
        self._selected_memory_fact_key = next_fact_key
        if category_changed:
            self.selectedMemoryCategoryChanged.emit()
        if fact_changed:
            self.selectedMemoryFactChanged.emit()
        if key_changed:
            self.selectedMemoryFactKeyChanged.emit()

    def _experience_from_cache(self, key: str) -> dict[str, Any] | None:
        for item in self._experience_items:
            if str(item.get("key", "")) == key:
                return dict(item)
        return None

    def _selected_memory_category(self) -> dict[str, Any]:
        return self._memory_category_from_cache(self._selected_memory_category_name) or {}

    def _selected_memory_fact(self) -> dict[str, Any]:
        return self._memory_fact_by_key(self._selected_memory_category(), self._selected_memory_fact_key)

    def _selected_experience(self) -> dict[str, Any]:
        return self._experience_from_cache(self._selected_experience_key) or {}

    def _upsert_memory_category_cache(self, detail: dict[str, Any]) -> None:
        category = str(detail.get("category", "") or "")
        if not category:
            return
        replaced = False
        next_items: list[dict[str, Any]] = []
        for item in self._memory_categories:
            if str(item.get("category", "") or "") == category:
                next_items.append(dict(detail))
                replaced = True
            else:
                next_items.append(dict(item))
        if not replaced:
            next_items.append(dict(detail))
        self._memory_categories = next_items
        self._refresh_visible_memory_categories()

    def _upsert_experience_cache(self, detail: dict[str, Any]) -> None:
        key = str(detail.get("key", "") or "")
        if not key:
            return
        replaced = False
        next_items: list[dict[str, Any]] = []
        for item in self._experience_items:
            if str(item.get("key", "") or "") == key:
                next_items.append(dict(detail))
                replaced = True
            else:
                next_items.append(dict(item))
        if not replaced:
            next_items.append(dict(detail))
        self._experience_items = next_items
        self._experience_model.sync_items(self._experience_items)

    @staticmethod
    def _build_memory_stats(items: list[dict[str, Any]]) -> dict[str, Any]:
        used = [item for item in items if not bool(item.get("is_empty", False))]
        latest = max((str(item.get("updated_at", "")) for item in used), default="")
        return {
            "used_categories": len(used),
            "total_categories": len(MEMORY_CATEGORIES),
            "total_chars": sum(int(item.get("char_count", 0) or 0) for item in items),
            "total_facts": sum(int(item.get("fact_count", 0) or 0) for item in items),
            "latest_updated_at": latest,
            "latest_updated_label": format_updated_label(latest),
        }

    @staticmethod
    def _build_experience_stats(items: list[dict[str, Any]]) -> dict[str, Any]:
        recent_count = 0
        for item in items:
            dt = parse_updated_at(item.get("updated_at"))
            if dt is None:
                continue
            recent_cutoff = datetime.now(tz=dt.tzinfo) - timedelta(days=7)
            if dt >= recent_cutoff:
                recent_count += 1
        return {
            "total_count": len(items),
            "active_count": sum(1 for item in items if not bool(item.get("deprecated", False))),
            "deprecated_count": sum(1 for item in items if bool(item.get("deprecated", False))),
            "high_quality_count": sum(1 for item in items if int(item.get("quality", 0) or 0) >= 4),
            "recent_count": recent_count,
        }

