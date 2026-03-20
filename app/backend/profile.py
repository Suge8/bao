from __future__ import annotations

import asyncio
import concurrent.futures
from pathlib import Path
from typing import Any, Callable, ClassVar

from PySide6.QtCore import Property, QObject, Signal, Slot

from app.backend.asyncio_runner import AsyncioRunner
from app.backend.profile_state import (
    RefreshResultPayload,
    active_profile_row,
    project_profiles,
    registry_snapshot,
)
from bao.profile import (
    CreateProfileOptions,
    ProfileContext,
    ProfileRegistry,
    ProfileUpdateOptions,
    RenameProfileOptions,
    create_profile,
    delete_profile,
    load_active_profile_snapshot,
    profile_context_to_dict,
    rename_profile,
    set_active_profile,
    update_profile,
)


class ProfileService(QObject):
    profilesChanged: ClassVar[Signal] = Signal()
    activeProfileChanged: ClassVar[Signal] = Signal()
    errorChanged: ClassVar[Signal] = Signal()
    _refreshResult: ClassVar[Signal] = Signal(object)

    def __init__(self, runner: AsyncioRunner | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._runner = runner
        self._shared_workspace_path = ""
        self._registry: ProfileRegistry | None = None
        self._active_context: ProfileContext | None = None
        self._profile_rows: list[dict[str, Any]] = []
        self._last_error = ""
        self._refresh_generation = 0
        self._refresh_inflight_paths: set[str] = set()
        self._refreshResult.connect(self._handle_refresh_result)

    @Property(list, notify=profilesChanged)
    def profiles(self) -> list[dict[str, Any]]:
        return [dict(item) for item in self._profile_rows]

    @Property(dict, notify=activeProfileChanged)
    def activeProfile(self) -> dict[str, Any]:
        return active_profile_row(self._profile_rows, self._active_context)

    @Property(dict, notify=activeProfileChanged)
    def activeProfileContext(self) -> dict[str, Any]:
        return profile_context_to_dict(self._active_context)

    @Property(str, notify=activeProfileChanged)
    def activeProfileId(self) -> str:
        context = self._active_context
        return context.profile_id if context is not None else ""

    @Property(str, notify=profilesChanged)
    def sharedWorkspacePath(self) -> str:
        return self._shared_workspace_path

    @Property(str, notify=errorChanged)
    def lastError(self) -> str:
        return self._last_error

    @Property(dict, notify=profilesChanged)
    def registrySnapshot(self) -> dict[str, Any]:
        return registry_snapshot(self._registry)

    def _shared_workspace(self) -> Path:
        return Path(self._shared_workspace_path).expanduser()

    def _run_workspace_action(self, action: Callable[[Path], tuple[ProfileRegistry, ProfileContext]]) -> None:
        if not self._shared_workspace_path:
            return
        self._run_action(self._shared_workspace(), action)

    def _run_profile_action(self, profile_id: str, action: Callable[[Path, str], tuple[ProfileRegistry, ProfileContext]]) -> None:
        normalized_id = profile_id.strip()
        if not normalized_id:
            return
        self._run_workspace_action(
            lambda shared_workspace: action(shared_workspace, normalized_id),
        )

    @Slot(str)
    def refreshFromWorkspace(self, workspace_path: str) -> None:
        raw = workspace_path.strip()
        if not raw:
            return
        shared_workspace = Path(raw).expanduser()
        workspace_key = str(shared_workspace)
        if self._runner is None:
            self._run_action(
                shared_workspace,
                lambda workspace: load_active_profile_snapshot(shared_workspace=workspace),
            )
            return
        self._shared_workspace_path = workspace_key
        if workspace_key in self._refresh_inflight_paths:
            return
        self._submit_refresh(self._next_refresh_generation(), shared_workspace)

    @Slot(str)
    def activateProfile(self, profile_id: str) -> None:
        self._run_profile_action(
            profile_id,
            lambda shared_workspace, normalized_id: set_active_profile(
                normalized_id,
                shared_workspace=shared_workspace,
            ),
        )

    @Slot(str)
    def createProfile(self, display_name: str) -> None:
        self._run_workspace_action(
            lambda shared_workspace: create_profile(
                display_name,
                CreateProfileOptions(
                    shared_workspace=shared_workspace,
                    activate=True,
                ),
            ),
        )

    @Slot(str)
    def deleteProfile(self, profile_id: str) -> None:
        self._run_profile_action(
            profile_id,
            lambda shared_workspace, normalized_id: delete_profile(
                normalized_id,
                shared_workspace=shared_workspace,
            ),
        )

    @Slot(str, str)
    def renameProfile(self, profile_id: str, display_name: str) -> None:
        self._run_profile_action(
            profile_id,
            lambda shared_workspace, normalized_id: rename_profile(
                normalized_id,
                display_name,
                RenameProfileOptions(shared_workspace=shared_workspace),
            ),
        )

    @Slot(str, str, str)
    def updateProfile(self, profile_id: str, display_name: str, storage_key: str) -> None:
        self._run_profile_action(
            profile_id,
            lambda shared_workspace, normalized_id: update_profile(
                normalized_id,
                ProfileUpdateOptions(
                    shared_workspace=shared_workspace,
                    display_name=display_name,
                    storage_key=storage_key,
                ),
            ),
        )

    def _run_action(
        self,
        shared_workspace: Path,
        action: Callable[[Path], tuple[ProfileRegistry, ProfileContext]],
    ) -> None:
        self._invalidate_pending_refresh()
        try:
            registry, context = action(shared_workspace)
        except Exception as exc:
            self._set_error(str(exc))
            return
        self._set_error("")
        self._apply_state(registry, context, shared_workspace=shared_workspace)

    def _invalidate_pending_refresh(self) -> None:
        self._next_refresh_generation()

    def _next_refresh_generation(self) -> int:
        self._refresh_generation += 1
        return self._refresh_generation

    def _submit_refresh(self, request_seq: int, shared_workspace: Path) -> None:
        runner = self._runner
        if runner is None:
            return
        workspace_key = str(shared_workspace)
        if workspace_key in self._refresh_inflight_paths:
            return
        self._refresh_inflight_paths.add(workspace_key)
        coro = self._load_snapshot(shared_workspace)
        try:
            future = runner.submit(coro)
        except RuntimeError:
            coro.close()
            self._refresh_inflight_paths.discard(workspace_key)
            self._set_error("Asyncio runner is not available.")
            return
        future.add_done_callback(
            lambda future, seq=request_seq, path=workspace_key: self._emit_refresh_result(
                seq, path, future
            )
        )

    async def _load_snapshot(self, shared_workspace: Path) -> tuple[str, ProfileRegistry, ProfileContext]:
        runner = self._runner
        if runner is None:
            raise RuntimeError("Asyncio runner is not available.")
        registry, context = await runner.run_user_io(
            load_active_profile_snapshot,
            shared_workspace=shared_workspace,
        )
        return str(shared_workspace), registry, context

    def _emit_refresh_result(self, request_seq: int, workspace_key: str, future: Any) -> None:
        try:
            payload = future.result()
            self._refreshResult.emit(
                RefreshResultPayload(
                    request_seq=request_seq,
                    workspace_key=workspace_key,
                    ok=True,
                    message="",
                    payload=payload,
                )
            )
        except (asyncio.CancelledError, concurrent.futures.CancelledError):
            self._refreshResult.emit(
                RefreshResultPayload(
                    request_seq=request_seq,
                    workspace_key=workspace_key,
                    ok=False,
                    message="cancelled",
                    payload=None,
                )
            )
        except Exception as exc:
            self._refreshResult.emit(
                RefreshResultPayload(
                    request_seq=request_seq,
                    workspace_key=workspace_key,
                    ok=False,
                    message=str(exc),
                    payload=None,
                )
            )

    @Slot(object)
    def _handle_refresh_result(self, result: object) -> None:
        if not isinstance(result, RefreshResultPayload):
            self._set_error("Profile refresh returned invalid payload.")
            return
        self._refresh_inflight_paths.discard(result.workspace_key)
        if result.request_seq != self._refresh_generation:
            return
        if not result.ok:
            self._set_error(result.message)
            return
        if not isinstance(result.payload, tuple) or len(result.payload) != 3:
            self._set_error("Profile refresh returned invalid payload.")
            return
        workspace_raw, registry, context = result.payload
        if not isinstance(registry, ProfileRegistry) or not isinstance(context, ProfileContext):
            self._set_error("Profile refresh returned invalid payload.")
            return
        self._set_error("")
        self._apply_state(
            registry,
            context,
            shared_workspace=Path(str(workspace_raw)).expanduser(),
        )

    def _apply_state(self, registry: ProfileRegistry, context: ProfileContext, *, shared_workspace: Path) -> None:
        previous_rows = self._profile_rows
        previous_context = self._active_context
        previous_active_profile = active_profile_row(previous_rows, previous_context)
        workspace_changed = self._shared_workspace_path != str(shared_workspace)
        profile_rows = project_profiles(registry, context)
        active_profile = active_profile_row(profile_rows, context)
        profiles_changed = workspace_changed or registry != self._registry or profile_rows != previous_rows
        active_changed = context != previous_context or active_profile != previous_active_profile
        self._shared_workspace_path = str(shared_workspace)
        self._registry = registry
        self._active_context = context
        self._profile_rows = profile_rows
        if profiles_changed:
            self.profilesChanged.emit()
        if active_changed:
            self.activeProfileChanged.emit()

    def _set_error(self, message: str) -> None:
        if self._last_error == message:
            return
        self._last_error = message
        self.errorChanged.emit()
