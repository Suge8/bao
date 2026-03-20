from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QUrl, Slot
from PySide6.QtGui import QDesktopServices

from bao.agent.skill_catalog import USER_SKILL_SOURCE

from ._skills_common import VALID_SOURCE_FILTERS, DiscoverTaskUpdate, _as_dict


class SkillsServiceViewMixin:
    @staticmethod
    def _ui_text(zh: str, en: str) -> str:
        return zh

    @Slot()
    def refresh(self) -> None:
        self._refresh()

    @Slot()
    def hydrateIfNeeded(self) -> None:
        self._refresh_if_hydrated(force=not self._hydrated)

    @Slot("QVariant")
    def setConfigData(self, data: object) -> None:
        next_data = _as_dict(data) or {}
        self._config_data = dict(next_data)
        self._refresh_if_hydrated()

    @Slot(str)
    def setQuery(self, value: str) -> None:
        next_value = value.strip()
        if next_value == self._query:
            return
        self._query = next_value
        self._refresh()

    @Slot(str)
    def setSourceFilter(self, value: str) -> None:
        next_value = value if value in VALID_SOURCE_FILTERS else "all"
        if next_value == self._source_filter:
            return
        self._source_filter = next_value
        self._refresh()

    @Slot(str)
    def selectSkill(self, skill_id: str) -> None:
        self._set_selected(skill_id)

    @Slot(str)
    def setDiscoverQuery(self, value: str) -> None:
        next_value = value.strip()
        if next_value == self._discover_query:
            return
        self._discover_query = next_value
        self.changed.emit()

    @Slot(str)
    def setDiscoverReference(self, value: str) -> None:
        next_value = value.strip()
        if next_value == self._discover_reference:
            return
        self._discover_reference = next_value
        self.changed.emit()

    @Slot(str)
    def selectDiscoverItem(self, item_id: str) -> None:
        target = next((item for item in self._discover_results if item.get("id") == item_id), None)
        if target is None:
            return
        self._set_selected_discover_item(dict(target))
        self.changed.emit()

    @Slot()
    def searchRemote(self) -> None:
        query = self._discover_query.strip()
        if not query:
            message = self._ui_text("请先输入搜索内容。", "Search query is required.")
            self._set_error(message)
            self.operationFinished.emit(message, False)
            return
        self._set_discover_task(
            DiscoverTaskUpdate(
                state="working",
                kind="search",
                message=self._ui_text(f"正在搜索：{query}", f"Searching for '{query}'"),
                reference=query,
            )
        )
        self._submit_task("search_remote", self._search_remote(query))

    @Slot(result=bool)
    def installDiscoverReference(self) -> bool:
        reference = self._discover_reference.strip()
        if not reference:
            message = self._ui_text("请先填写技能引用。", "Skill reference is required.")
            self._set_error(message)
            self.operationFinished.emit(message, False)
            return False
        self._set_discover_task(
            DiscoverTaskUpdate(
                state="working",
                kind="install",
                message=self._ui_text(f"正在导入：{reference}", f"Importing {reference}"),
                reference=reference,
            )
        )
        self._submit_task("install_reference", self._install_reference(reference))
        return True

    @Slot(str, str, result=bool)
    def createSkill(self, name: str, description: str) -> bool:
        try:
            record = self._catalog.create_user_skill(name, description)
        except Exception as exc:
            self.operationFinished.emit(str(exc), False)
            return False
        self._refresh(preferred_skill_id=str(record.get("id") or ""))
        self.operationFinished.emit("created", True)
        return True

    @Slot(str, result=bool)
    def saveSelectedContent(self, content: str) -> bool:
        skill = self._selected_skill()
        if skill.get("source") != USER_SKILL_SOURCE:
            self.operationFinished.emit(self._ui_text("只有用户技能可以编辑。", "Only user skills can be edited."), False)
            return False
        try:
            record = self._catalog.update_user_skill(str(skill.get("name") or ""), content)
        except Exception as exc:
            self.operationFinished.emit(str(exc), False)
            return False
        self._refresh(preferred_skill_id=str(record.get("id") or ""))
        self.operationFinished.emit("saved", True)
        return True

    @Slot(result=bool)
    def deleteSelectedSkill(self) -> bool:
        skill = self._selected_skill()
        if skill.get("source") != USER_SKILL_SOURCE:
            self.operationFinished.emit(self._ui_text("只有用户技能可以删除。", "Only user skills can be deleted."), False)
            return False
        deleted_name = str(skill.get("name") or "")
        try:
            self._catalog.delete_user_skill(deleted_name)
        except Exception as exc:
            self.operationFinished.emit(str(exc), False)
            return False
        self._refresh()
        self.operationFinished.emit("deleted", True)
        return True

    @Slot(result=bool)
    def openSelectedFolder(self) -> bool:
        target = self._selected_skill().get("path")
        if not isinstance(target, str) or not target:
            return False
        skill_file = Path(target)
        if not skill_file.exists():
            return False
        return QDesktopServices.openUrl(QUrl.fromLocalFile(str(skill_file.parent)))

    @Slot(result=bool)
    def openUserSkillsFolder(self) -> bool:
        target = self._catalog.user_skills
        target.mkdir(parents=True, exist_ok=True)
        return QDesktopServices.openUrl(QUrl.fromLocalFile(str(target)))

    @Slot(result=bool)
    def openSkillsRegistry(self) -> bool:
        return QDesktopServices.openUrl(QUrl("https://skills.sh/"))

    @Slot(str)
    def setWorkspacePath(self, workspace_path: str) -> None:
        next_path = Path(workspace_path).expanduser()
        if next_path == self._workspace_path:
            return
        self._workspace_path = next_path
        self.changed.emit()
