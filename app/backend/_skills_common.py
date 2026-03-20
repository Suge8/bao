from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from bao.agent.skill_catalog import USER_SKILL_SOURCE

if TYPE_CHECKING:
    from app.backend._skills_async import SkillDiscoveryProvider
    from app.backend.asyncio_runner import AsyncioRunner

_SKILL_REF_RE = re.compile(r"([A-Za-z0-9._-]+/[A-Za-z0-9._-]+@[A-Za-z0-9._-]+)")
VALID_SOURCE_FILTERS = frozenset(
    {"all", USER_SKILL_SOURCE, "ready", "needs_setup", "instruction_only", "shadowed"}
)


def _as_dict(value: object) -> dict[str, object] | None:
    if isinstance(value, dict):
        return value
    return None


@dataclass(frozen=True)
class DiscoveryTaskState:
    state: str = "idle"
    kind: str = ""
    message: str = ""
    reference: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "state": self.state,
            "kind": self.kind,
            "message": self.message,
            "reference": self.reference,
        }


@dataclass(frozen=True)
class DiscoverTaskUpdate:
    state: str
    kind: str
    message: str
    reference: str


@dataclass(frozen=True)
class SkillsServiceOptions:
    runner: AsyncioRunner
    workspace_path: str
    user_skills_dir: str | None = None
    discovery_provider: SkillDiscoveryProvider | None = None
    eager_refresh: bool = True
