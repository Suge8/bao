from __future__ import annotations

from bao.config.paths import get_workspace_path
from bao.profile import ProfileContext, active_profile_context


def initial_active_profile_context() -> ProfileContext:
    return active_profile_context(shared_workspace=get_workspace_path())
