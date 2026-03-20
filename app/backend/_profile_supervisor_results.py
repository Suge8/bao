from __future__ import annotations

from pathlib import Path
from typing import Any

from ._profile_supervisor_common import _COLLECTION_NAMES, _clone_dict_list


class ProfileSupervisorResultsMixin:
    def _on_refresh_done(self, future: Any) -> None:
        self._refresh_inflight = False
        if future.cancelled():
            self._set_busy(False)
            return
        exc = future.exception()
        if exc:
            self._refreshResult.emit(
                {
                    "overview": self._overview,
                    "profiles": self._profiles,
                    **{name: self._all_items.get(name, []) for name in _COLLECTION_NAMES},
                }
            )
            self._set_busy(False)
            return
        self._refreshResult.emit(future.result())

    def _handle_refresh_result(self, payload: object) -> None:
        data = payload if isinstance(payload, dict) else {}
        next_overview = dict(data.get("overview", {}) if isinstance(data, dict) else {})
        next_profiles = [dict(item) for item in data.get("profiles", []) if isinstance(item, dict)]
        next_all_items = {name: _clone_dict_list(data.get(name, [])) for name in _COLLECTION_NAMES}
        overview_changed = next_overview != self._overview
        profiles_changed = next_profiles != self._profiles
        previous_visible = {name: [dict(item) for item in self._visible_items.get(name, [])] for name in _COLLECTION_NAMES}
        self._overview = next_overview
        self._profiles = next_profiles
        self._profiles_model.sync_items(self._profiles)
        valid_profile_ids = {str(item.get("id", "")) for item in self._profiles}
        selection_changed = False
        if self._selected_profile_id and self._selected_profile_id not in valid_profile_ids:
            self._selected_profile_id = ""
            self._selected_item_id = ""
            selection_changed = True
        self._all_items = next_all_items
        self._apply_filter()
        visible_changed = {name: self._visible_items.get(name, []) != previous_visible.get(name, []) for name in _COLLECTION_NAMES}
        self._set_busy(False)
        self._schedule_snapshot_writes(data.get("snapshot_writes", []))
        if selection_changed:
            self.selectionChanged.emit()
        if overview_changed:
            self.overviewChanged.emit()
        if profiles_changed:
            self.profilesChanged.emit()
        self._emit_collection_changes(visible_changed)
        if self._refresh_requested:
            self.refresh()

    def _apply_filter(self) -> None:
        profile_id = self._selected_profile_id
        if not profile_id:
            self._visible_items = {name: [dict(item) for item in items] for name, items in self._all_items.items()}
        else:
            self._visible_items = {
                name: [dict(item) for item in items if str(item.get("profileId", "")) == profile_id]
                for name, items in self._all_items.items()
            }
        if self._selected_item_id and not self.selectedItem:
            self._selected_item_id = ""
            self.selectionChanged.emit()
        for name in _COLLECTION_NAMES:
            self._section_models[name].sync_items(self._visible_items[name])

    def _emit_collection_changes(self, changed: dict[str, bool] | None = None) -> None:
        status = changed or {name: True for name in _COLLECTION_NAMES}
        if status.get("working", False):
            self.workingChanged.emit()
        if status.get("completed", False):
            self.completedChanged.emit()
        if status.get("automation", False):
            self.automationChanged.emit()
        if status.get("attention", False):
            self.attentionChanged.emit()

    def _schedule_snapshot_writes(self, raw_writes: object) -> None:
        if not isinstance(raw_writes, list):
            return
        for item in raw_writes:
            if not isinstance(item, dict):
                continue
            raw_path = str(item.get("path", "") or "")
            payload = item.get("payload")
            if raw_path and isinstance(payload, dict):
                self._snapshot_writer.write(Path(raw_path), payload)

    def _set_busy(self, busy: bool) -> None:
        if self._busy == busy:
            return
        self._busy = busy
        self.busyChanged.emit(busy)
