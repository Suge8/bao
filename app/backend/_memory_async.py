from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from pathlib import Path
from typing import Any

from app.backend.asyncio_runner import AsyncioRunner
from bao.agent.memory import ExperienceListRequest

from ._memory_common import (
    EXPERIENCE_DEPRECATED_MODES,
    EXPERIENCE_SORT_OPTIONS,
    ExperienceQueryState,
    RunnerTaskResult,
)


class MemoryServiceAsyncMixin:
    def _set_experience_query(self, query: ExperienceQueryState) -> None:
        self._experience_query = query.query
        self._experience_category = query.category
        self._experience_outcome = query.outcome
        self._experience_deprecated_mode = query.deprecated_mode
        self._experience_min_quality = query.min_quality
        self._experience_sort_by = query.sort_by

    @classmethod
    def _normalize_experience_query(cls, args: tuple[Any, ...]) -> ExperienceQueryState:
        values = [*args, "", "", "", "active", 0, "updated_desc"]
        query = str(values[0] or "").strip()
        category = str(values[1] or "").strip()
        outcome = str(values[2] or "").strip()
        deprecated_mode = str(values[3] or "").strip()
        min_quality = max(0, int(values[4] or 0))
        sort_by = str(values[5] or "").strip()
        return ExperienceQueryState(
            query=query,
            category=category,
            outcome=outcome,
            deprecated_mode=deprecated_mode if deprecated_mode in EXPERIENCE_DEPRECATED_MODES else "active",
            min_quality=min_quality,
            sort_by=sort_by if sort_by in EXPERIENCE_SORT_OPTIONS else "updated_desc",
        )

    def _submit_task(self, kind: str, coro: Coroutine[Any, Any, Any]) -> None:
        blocking = self._is_blocking_kind(kind)
        if blocking and self._blocking_busy:
            coro.close()
            self.operationFinished.emit(self._MUTATION_BUSY_MESSAGE, False)
            return
        future = self._submit_safe(coro)
        if future is None:
            return
        self._set_busy(True)
        if blocking:
            self._set_blocking_busy(True)
        future.add_done_callback(
            lambda done, task_kind=kind, task_blocking=blocking: self._emit_runner_result(
                task_kind,
                task_blocking,
                done,
            )
        )

    def _submit_safe(self, coro: Coroutine[Any, Any, Any]) -> Any:
        try:
            return self._runner.submit(coro)
        except RuntimeError:
            coro.close()
            self._set_error("Asyncio runner is not available.")
            return None

    async def _run_user_io(self, fn: Any, *args: Any, **kwargs: Any) -> Any:
        if isinstance(self._runner, AsyncioRunner):
            return await self._runner.run_user_io(fn, *args, **kwargs)
        return await asyncio.to_thread(fn, *args, **kwargs)

    async def _bootstrap_store(self, storage_root: str, request_seq: int) -> dict[str, Any]:
        root = Path(storage_root).expanduser()
        await self._run_user_io(lambda: root.mkdir(parents=True, exist_ok=True))
        store = await self._run_user_io(self._memory_store_cls, root)
        memory_items = await self._run_user_io(store.list_memory_categories)
        experience_items = await self._load_filtered_experience_items(store)
        return {
            "bootstrap_seq": request_seq,
            "storage_root": str(root),
            "store": store,
            "memory_items": memory_items,
            "experience_items": experience_items,
            "memory_category": self._selected_memory_category_name,
            "experience_key": self._selected_experience_key,
        }

    async def _load_memory_categories(self) -> dict[str, Any]:
        store = self._require_store()
        items = await self._run_user_io(store.list_memory_categories)
        return {"memory_items": items, "memory_category": self._selected_memory_category_name}

    async def _save_memory_category(self, category: str, content: str) -> dict[str, Any]:
        store = self._require_store()
        await self._run_user_io(store.write_long_term, content, category)
        items = await self._run_user_io(store.list_memory_categories)
        detail = await self._run_user_io(store.get_memory_category, category)
        return {"memory_items": items, "memory_category": category, "memory_detail": detail}

    async def _append_memory_category(self, category: str, content: str) -> dict[str, Any]:
        store = self._require_store()
        detail = await self._run_user_io(store.append_memory_category, category, content)
        items = await self._run_user_io(store.list_memory_categories)
        return {"memory_items": items, "memory_category": category, "memory_detail": detail}

    async def _clear_memory_category(self, category: str) -> dict[str, Any]:
        store = self._require_store()
        detail = await self._run_user_io(store.clear_memory_category, category)
        items = await self._run_user_io(store.list_memory_categories)
        return {"memory_items": items, "memory_category": category, "memory_detail": detail}

    async def _save_memory_fact(self, category: str, key: str, content: str) -> dict[str, Any]:
        store = self._require_store()
        detail = await self._run_user_io(store.upsert_memory_fact, category, content, key=key)
        if detail is None:
            raise RuntimeError("Failed to save memory fact")
        items = await self._run_user_io(store.list_memory_categories)
        facts = detail.get("facts") if isinstance(detail, dict) else None
        saved_key = key.strip()
        if not saved_key and isinstance(facts, list) and facts:
            saved_key = str(facts[-1].get("key", ""))
        return {
            "memory_items": items,
            "memory_category": category,
            "memory_detail": detail,
            "memory_fact_key": saved_key,
        }

    async def _delete_memory_fact(self, category: str, key: str) -> dict[str, Any]:
        store = self._require_store()
        detail = await self._run_user_io(store.delete_memory_fact, category, key)
        if detail is None:
            raise RuntimeError("Failed to delete memory fact")
        items = await self._run_user_io(store.list_memory_categories)
        return {"memory_items": items, "memory_category": category, "memory_detail": detail}

    async def _load_experiences(self, seq: int) -> dict[str, Any]:
        store = self._require_store()
        items = await self._load_filtered_experience_items(store)
        detail = None
        if self._selected_experience_key:
            detail = await self._run_user_io(store.get_experience_item, self._selected_experience_key)
        return {"seq": seq, "experience_items": items, "experience_detail": detail}

    async def _load_experience_detail(self, key: str, seq: int) -> dict[str, Any]:
        store = self._require_store()
        detail = await self._run_user_io(store.get_experience_item, key)
        return {"experience_detail": detail, "detail_seq": seq}

    async def _set_experience_deprecated(self, key: str, deprecated: bool) -> dict[str, Any]:
        store = self._require_store()
        ok = await self._run_user_io(store.set_experience_deprecated, key, deprecated)
        if not ok:
            raise RuntimeError("Failed to update experience state")
        items = await self._load_filtered_experience_items(store)
        detail = await self._run_user_io(store.get_experience_item, key)
        return {"experience_items": items, "experience_detail": detail}

    async def _delete_experience(self, key: str) -> dict[str, Any]:
        store = self._require_store()
        ok = await self._run_user_io(store.delete_experience, key)
        if not ok:
            raise RuntimeError("Failed to delete experience")
        items = await self._load_filtered_experience_items(store)
        return {"experience_items": items, "experience_detail": None, "deleted_key": key}

    async def _promote_experience_to_memory(self, key: str, category: str) -> dict[str, Any]:
        store = self._require_store()
        detail = await self._run_user_io(store.promote_experience_to_memory, key, category)
        if detail is None:
            raise RuntimeError("Failed to promote experience")
        items = await self._run_user_io(store.list_memory_categories)
        return {"memory_items": items, "memory_category": category, "memory_detail": detail}

    @staticmethod
    def _is_blocking_kind(kind: str) -> bool:
        return kind in {
            "bootstrap",
            "save_memory",
            "append_memory",
            "clear_memory",
            "save_memory_fact",
            "delete_memory_fact",
            "deprecate_experience",
            "delete_experience",
            "promote_experience",
        }

    def _current_experience_deprecated_filter(self) -> bool | None:
        if self._experience_deprecated_mode == "deprecated":
            return True
        if self._experience_deprecated_mode == "active":
            return False
        return None

    async def _load_filtered_experience_items(self, store: Any) -> list[dict[str, Any]]:
        return await self._run_user_io(
            store.list_experience_items,
            ExperienceListRequest(
                query=self._experience_query,
                category=self._experience_category,
                outcome=self._experience_outcome,
                deprecated=self._current_experience_deprecated_filter(),
                min_quality=self._experience_min_quality,
                sort_by=self._experience_sort_by,
            ),
        )

    def _emit_runner_result(self, kind: str, blocking: bool, future: Any) -> None:
        if future.cancelled():
            self._runnerResult.emit(RunnerTaskResult(kind, blocking, False, "Cancelled", None))
            return
        error = future.exception()
        if error is not None:
            self._runnerResult.emit(RunnerTaskResult(kind, blocking, False, str(error), None))
            return
        self._runnerResult.emit(RunnerTaskResult(kind, blocking, True, "", future.result()))

    def _handle_runner_result(self, result: RunnerTaskResult) -> None:
        self._set_busy(False)
        if result.blocking:
            self._set_blocking_busy(False)
        if not result.ok:
            self._set_error(result.error)
            self.operationFinished.emit(result.error, False)
            return
        self._set_error("")
        data = result.payload if isinstance(result.payload, dict) else {}
        if self._is_stale_payload(result.kind, data):
            if result.kind == "bootstrap":
                stale_store = data.get("store")
                if hasattr(stale_store, "close"):
                    try:
                        stale_store.close()
                    except Exception:
                        pass
            return
        if result.kind == "bootstrap":
            self._storage_root = str(data.get("storage_root") or self._storage_root)
            self._replace_store(data.get("store"))
        self._apply_memory_payload(result.kind, data)
        self._apply_experience_payload(result.kind, data)
        if result.kind == "bootstrap" and not self._ready:
            self._ready = True
            self.readyChanged.emit()
        success_message = self._SUCCESS_MESSAGES.get(result.kind)
        if success_message:
            self.operationFinished.emit(success_message, True)

    def _is_stale_payload(self, kind: str, data: dict[str, Any]) -> bool:
        if kind == "bootstrap":
            seq = int(data.get("bootstrap_seq", 0) or 0)
            storage_root = str(data.get("storage_root") or "")
            return seq < self._latest_bootstrap_request_seq or (
                bool(self._desired_storage_root) and storage_root != self._desired_storage_root
            )
        if kind == "load_experiences":
            return int(data.get("seq", 0) or 0) < self._latest_experience_request_seq
        if kind == "load_experience_detail":
            return int(data.get("detail_seq", 0) or 0) < self._latest_experience_detail_request_seq
        return False
