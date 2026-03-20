from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bao.profile import ProfileContext, profile_context_from_mapping, profile_context_to_dict


@dataclass(frozen=True)
class DesktopProfileCoordinatorOptions:
    config_service: Any
    profile_service: Any
    chat_service: Any
    session_service: Any
    memory_service: Any
    cron_service: Any
    heartbeat_service: Any
    skills_service: Any
    default_workspace: str = "~/.bao/workspace"


class DesktopProfileCoordinator:
    def __init__(self, options: DesktopProfileCoordinatorOptions) -> None:
        self._config_service = options.config_service
        self._profile_service = options.profile_service
        self._chat_service = options.chat_service
        self._session_service = options.session_service
        self._memory_service = options.memory_service
        self._cron_service = options.cron_service
        self._heartbeat_service = options.heartbeat_service
        self._skills_service = options.skills_service
        self._default_workspace = options.default_workspace
        self._applied_context: ProfileContext | None = None

    def refresh_from_config(self) -> None:
        workspace_path = self._workspace_path_from_config()
        self._profile_service.refreshFromWorkspace(workspace_path)
        self._skills_service.setWorkspacePath(workspace_path)

    def apply_active_profile(self) -> None:
        context = self._active_profile_context()
        self._chat_service.setProfileContext(profile_context_to_dict(context))
        if context is None:
            self._applied_context = None
            return

        previous = self._applied_context
        self._rebind_local_services(context, previous)
        self._applied_context = context

    def _rebind_local_services(
        self,
        context: ProfileContext,
        previous: ProfileContext | None,
    ) -> None:
        state_root_changed = self._state_root_changed(context, previous)
        if state_root_changed:
            self._session_service.bootstrapStorageRoot(str(context.state_root))
            self._memory_service.setStorageRootHint(str(context.state_root))
        if self._cron_path_changed(context, previous):
            self._cron_service.setLocalStorePath(str(context.cron_store_path))
        if self._heartbeat_path_changed(context, previous):
            self._heartbeat_service.setLocalHeartbeatFilePath(str(context.heartbeat_file))

        self._cron_service.setProfileInfo(context.profile_id, context.display_name)
        self._heartbeat_service.setProfileInfo(context.profile_id, context.display_name)

    @staticmethod
    def _state_root_changed(context: ProfileContext, previous: ProfileContext | None) -> bool:
        return previous is None or context.state_root != previous.state_root

    @staticmethod
    def _cron_path_changed(context: ProfileContext, previous: ProfileContext | None) -> bool:
        return previous is None or context.cron_store_path != previous.cron_store_path

    @staticmethod
    def _heartbeat_path_changed(context: ProfileContext, previous: ProfileContext | None) -> bool:
        return previous is None or context.heartbeat_file != previous.heartbeat_file

    def _active_profile_context(self) -> ProfileContext | None:
        return profile_context_from_mapping(getattr(self._profile_service, "activeProfileContext", None))

    def _workspace_path_from_config(self) -> str:
        workspace_value = self._config_service.get("agents.defaults.workspace", self._default_workspace)
        workspace_raw = workspace_value if isinstance(workspace_value, str) else self._default_workspace
        return str(Path(workspace_raw).expanduser())
