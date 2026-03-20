from __future__ import annotations

import asyncio
import concurrent.futures
import shutil
from collections.abc import Coroutine
from pathlib import Path
from typing import Any

from PySide6.QtCore import Slot

from bao.agent.skill_catalog import USER_SKILL_SOURCE

from ._skills_common import _SKILL_REF_RE, DiscoverTaskUpdate


class SkillDiscoveryProvider:
    async def search(self, query: str) -> dict[str, object]:
        raise NotImplementedError

    async def install(
        self,
        *,
        reference: str,
        workspace_path: Path,
        user_skills_dir: Path,
    ) -> dict[str, object]:
        raise NotImplementedError


class NpxSkillDiscoveryProvider(SkillDiscoveryProvider):
    async def search(self, query: str) -> dict[str, object]:
        process = await asyncio.create_subprocess_exec(
            "npx",
            "--yes",
            "skills",
            "find",
            query,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise RuntimeError(
                (stderr or stdout).decode("utf-8", errors="replace").strip()
                or "skills find failed"
            )
        output = stdout.decode("utf-8", errors="replace")
        return {"items": SkillsServiceAsyncMixin.parse_search_output(output), "raw": output}

    async def install(
        self,
        *,
        reference: str,
        workspace_path: Path,
        user_skills_dir: Path,
    ) -> dict[str, object]:
        source_root = workspace_path / ".agents" / "skills"
        before_names = SkillsServiceAsyncMixin._snapshot_skill_names(source_root)
        process = await asyncio.create_subprocess_exec(
            "npx",
            "--yes",
            "skills",
            "add",
            reference,
            "--agent",
            "codex",
            "--copy",
            "-y",
            cwd=str(workspace_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise RuntimeError(
                (stderr or stdout).decode("utf-8", errors="replace").strip()
                or "skills add failed"
            )
        after_names = SkillsServiceAsyncMixin._snapshot_skill_names(source_root)
        target_names = sorted(after_names - before_names)
        if not target_names:
            reference_name = SkillsServiceAsyncMixin._extract_reference_name(reference)
            if reference_name and reference_name in after_names:
                target_names = [reference_name]
        imported_ids = SkillsServiceAsyncMixin._copy_installed_skills(
            user_skills_dir=user_skills_dir,
            source_root=source_root,
            target_names=target_names or None,
        )
        if not imported_ids:
            raise RuntimeError("No installed skills were produced by skills add.")
        preferred_id = imported_ids[0]
        reference_name = SkillsServiceAsyncMixin._extract_reference_name(reference)
        if reference_name:
            candidate_id = f"{USER_SKILL_SOURCE}:{reference_name}"
            if candidate_id in imported_ids:
                preferred_id = candidate_id
        return {"preferredId": preferred_id, "importedIds": imported_ids}


class SkillsServiceAsyncMixin:
    def _submit_task(self, kind: str, coro: Coroutine[Any, Any, Any]) -> None:
        try:
            future = self._runner.submit(coro)
        except RuntimeError:
            coro.close()
            self._set_error(self._ui_text("异步运行器不可用。", "Asyncio runner is not available."))
            return
        self._set_busy(True)
        future.add_done_callback(lambda done, task_kind=kind: self._emit_runner_result(task_kind, done))

    def _emit_runner_result(self, kind: str, future: concurrent.futures.Future[Any]) -> None:
        try:
            payload = future.result()
            self._runnerResult.emit(kind, True, "", payload)
        except asyncio.CancelledError:
            self._runnerResult.emit(kind, False, "cancelled", None)
        except Exception as exc:
            self._runnerResult.emit(kind, False, str(exc), None)

    @Slot(str, bool, str, object)
    def _handle_runner_result(self, *args: object) -> None:
        kind = str(args[0]) if len(args) > 0 else ""
        ok = bool(args[1]) if len(args) > 1 else False
        message = str(args[2]) if len(args) > 2 else ""
        payload = args[3] if len(args) > 3 else None
        self._set_busy(False)
        if not ok:
            self._set_error(message)
            task_kind = self._task_kind_for_operation(kind)
            self._set_discover_task(
                DiscoverTaskUpdate(
                    state="cancelled" if message == "cancelled" else "failed",
                    kind=task_kind,
                    message=message or self._cancel_message(task_kind),
                    reference=self._discover_task.reference,
                )
            )
            self.operationFinished.emit(message, False)
            return

        self._set_error("")
        if kind == "search_remote":
            result = payload if isinstance(payload, dict) else {}
            items = result.get("items", []) if isinstance(result, dict) else []
            self._set_discover_results(items)
            count = len(self._discover_results)
            self._set_discover_task(
                DiscoverTaskUpdate(
                    state="completed",
                    kind="search",
                    message=(
                        self._ui_text(f"找到 {count} 个候选技能", f"Found {count} candidate skills")
                        if count
                        else self._ui_text("没有找到匹配的技能", "No matching skills found")
                    ),
                    reference=self._discover_query.strip(),
                )
            )
            self.changed.emit()
            self.operationFinished.emit("search_ok", True)
            return

        if kind == "install_reference":
            result = payload if isinstance(payload, dict) else {}
            preferred_id = str(result.get("preferredId") or "")
            self._refresh(preferred_skill_id=preferred_id)
            imported_ids = [str(item) for item in (result.get("importedIds", []) if isinstance(result, dict) else [])]
            self._mark_discover_installed(imported_ids)
            self._set_discover_task(
                DiscoverTaskUpdate(
                    state="completed",
                    kind="install",
                    message=self._ui_text(
                        f"已导入 {len(imported_ids) or 1} 个技能到用户技能目录",
                        f"Imported {len(imported_ids) or 1} skill into user skills",
                    ),
                    reference=self._discover_reference.strip(),
                )
            )
            self.operationFinished.emit("installed", True)

    async def _search_remote(self, query: str) -> dict[str, object]:
        return await self._discovery_provider.search(query)

    async def _install_reference(self, reference: str) -> dict[str, object]:
        return await self._discovery_provider.install(
            reference=reference,
            workspace_path=self._workspace_path,
            user_skills_dir=self._catalog.user_skills,
        )

    def _import_installed_skills(
        self,
        source_root: Path,
        *,
        target_names: list[str] | None = None,
    ) -> list[str]:
        return self._copy_installed_skills(
            user_skills_dir=self._catalog.user_skills,
            source_root=source_root,
            target_names=target_names,
        )

    @staticmethod
    def _copy_installed_skills(
        *,
        user_skills_dir: Path,
        source_root: Path,
        target_names: list[str] | None = None,
    ) -> list[str]:
        if not source_root.exists():
            return []
        imported_ids: list[str] = []
        user_skills_dir.mkdir(parents=True, exist_ok=True)
        allowed_names = set(target_names or [])
        for skill_dir in sorted(source_root.iterdir(), key=lambda item: item.name.lower()):
            if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").exists():
                continue
            if allowed_names and skill_dir.name not in allowed_names:
                continue
            destination = user_skills_dir / skill_dir.name
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(skill_dir, destination)
            imported_ids.append(f"{USER_SKILL_SOURCE}:{skill_dir.name}")
        return imported_ids

    @staticmethod
    def _task_kind_for_operation(kind: str) -> str:
        if kind == "search_remote":
            return "search"
        if kind == "install_reference":
            return "install"
        return ""

    @staticmethod
    def _cancel_message(kind: str) -> str:
        if kind == "search":
            return "已取消搜索"
        if kind == "install":
            return "已取消导入"
        return ""

    @staticmethod
    def _snapshot_skill_names(source_root: Path) -> set[str]:
        if not source_root.exists():
            return set()
        return {
            skill_dir.name
            for skill_dir in source_root.iterdir()
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists()
        }

    @staticmethod
    def _extract_reference_name(reference: str) -> str:
        _repo, _sep, skill_name = reference.partition("@")
        return skill_name.strip()

    @staticmethod
    def parse_search_output(output: str) -> list[dict[str, object]]:
        refs = list(dict.fromkeys(_SKILL_REF_RE.findall(output)))
        items: list[dict[str, object]] = []
        for ref in refs:
            repo, _sep, skill_name = ref.partition("@")
            owner, _slash, repo_name = repo.partition("/")
            title = skill_name.replace("-", " ").replace("_", " ").strip().title() or ref
            items.append(
                {
                    "id": ref,
                    "reference": ref,
                    "name": skill_name or ref,
                    "title": title,
                    "repo": repo,
                    "publisher": owner,
                    "repoName": repo_name,
                    "version": "latest",
                    "summary": f"Import {title} from {repo}",
                    "trustNote": {
                        "zh": "来自公开 skills registry；导入前请检查来源和说明。",
                        "en": "Listed in the public skills registry; review the source and instructions before importing.",
                    },
                    "requires": ["npx skills"],
                    "installState": "available",
                    "installStateLabel": {"zh": "可导入", "en": "Ready to import"},
                    "installStateDetail": {
                        "zh": "可直接导入到用户技能目录。",
                        "en": "Ready to import into user skills.",
                    },
                    "searchText": f"{ref} {skill_name} {repo} {title} {owner} {repo_name}".lower(),
                }
            )
        return items
