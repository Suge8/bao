from __future__ import annotations

from app.backend.list_model import build_selection_projection
from bao.agent.skill_registry import build_skill_workspace_snapshot

from ._skills_common import DiscoverTaskUpdate, DiscoveryTaskState


class SkillsServiceProjectionMixin:
    def _refresh_if_hydrated(self, *, force: bool = False) -> None:
        if not force and not self._hydrated:
            return
        self._refresh()

    def _refresh(self, *, preferred_skill_id: str | None = None) -> None:
        snapshot = build_skill_workspace_snapshot(
            catalog=self._catalog,
            config_data=self._config_data,
            query=self._query.lower(),
            source_filter=self._source_filter,
            selected_id=preferred_skill_id or self._selected_skill_id,
        )
        self._hydrated = True
        selection = build_selection_projection(
            [dict(item) for item in snapshot.items],
            preferred_id=snapshot.selected_id or self._selected_skill_id,
        )
        next_skills = selection.items
        next_overview = dict(snapshot.overview)
        next_selected_id = selection.selected_id
        next_selected_content = ""
        if next_selected_id:
            selected_skill = self._skills_model.item_by_id(next_selected_id) or selection.selected_item
            source = str(selected_skill.get("source") or "")
            name = str(selected_skill.get("name") or "")
            next_selected_content = self._catalog.read_content(name, source)
        if (
            next_skills == self._skills
            and next_overview == self._overview
            and next_selected_id == self._selected_skill_id
            and next_selected_content == self._selected_content
        ):
            return
        self._skills = next_skills
        self._skills_model.sync_items(self._skills)
        self._overview = next_overview
        self._selected_skill_id = next_selected_id
        self._selected_content = next_selected_content if self._selected_skill_id else ""
        self.changed.emit()

    def _set_selected(self, skill_id: str, *, emit: bool = True) -> None:
        target = next((item for item in self._skills if item.get("id") == skill_id), None)
        if target is None:
            return
        self._selected_skill_id = skill_id
        source = str(target.get("source") or "")
        name = str(target.get("name") or "")
        self._selected_content = self._catalog.read_content(name, source)
        if emit:
            self.changed.emit()

    def _set_discover_results(self, items: object) -> None:
        raw_items = [dict(item) for item in (items if isinstance(items, list) else []) if isinstance(item, dict)]
        selection = build_selection_projection(raw_items, preferred_id=self._selected_discover_id)
        self._discover_results = selection.items
        self._discover_results_model.sync_items(self._discover_results)
        self._selected_discover_id = selection.selected_id
        if selection.selected_item:
            self._set_selected_discover_item(selection.selected_item)
            return
        self._discover_reference = ""

    def _set_selected_discover_item(self, item: dict[str, object]) -> None:
        self._selected_discover_id = str(item.get("id") or "")
        reference = str(item.get("reference") or "")
        if reference:
            self._discover_reference = reference

    def _mark_discover_installed(self, imported_ids: list[str]) -> None:
        if not imported_ids:
            return
        imported_names = {item.split(":", 1)[1] for item in imported_ids if ":" in item}
        next_results: list[dict[str, object]] = []
        next_selected = self._selected_discover_item()
        for item in self._discover_results:
            next_item = dict(item)
            if str(next_item.get("name") or "") in imported_names:
                next_item["installState"] = "installed"
                next_item["installStateLabel"] = {"zh": "已导入", "en": "Installed"}
                next_item["installStateDetail"] = {
                    "zh": "该技能已经导入到用户技能目录。",
                    "en": "This skill has been imported into user skills.",
                }
            next_results.append(next_item)
            if str(next_item.get("id") or "") == self._selected_discover_id:
                next_selected = next_item
        self._discover_results = next_results
        self._discover_results_model.sync_items(self._discover_results)
        if next_selected:
            self._selected_discover_id = str(next_selected.get("id") or "")

    def _set_discover_task(self, task: DiscoverTaskUpdate) -> None:
        next_task = DiscoveryTaskState(
            state=task.state,
            kind=task.kind,
            message=task.message,
            reference=task.reference,
        )
        if next_task != self._discover_task:
            self._discover_task = next_task
            self.changed.emit()

    def _set_busy(self, active: bool) -> None:
        self._busy_count = max(0, self._busy_count + (1 if active else -1))
        next_busy = self._busy_count > 0
        if next_busy == self._busy:
            return
        self._busy = next_busy
        self.busyChanged.emit()

    def _set_error(self, message: str) -> None:
        if message == self._error:
            return
        self._error = message
        self.errorChanged.emit(message)

    def _selected_skill(self) -> dict[str, object]:
        return self._skills_model.item_by_id(self._selected_skill_id)

    def _selected_discover_item(self) -> dict[str, object]:
        return self._discover_results_model.item_by_id(self._selected_discover_id)
