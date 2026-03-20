from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from bao.profile import ProfileContext, ProfileRegistry


@dataclass(frozen=True)
class RefreshResultPayload:
    request_seq: int
    workspace_key: str
    ok: bool
    message: str
    payload: object


def registry_snapshot(registry: ProfileRegistry | None) -> dict[str, Any]:
    if registry is None:
        return {}
    return {
        "version": registry.version,
        "defaultProfileId": registry.default_profile_id,
        "activeProfileId": registry.active_profile_id,
        "profiles": [asdict(spec) for spec in registry.profiles],
    }


def project_profiles(
    registry: ProfileRegistry,
    context: ProfileContext,
) -> list[dict[str, Any]]:
    active_id = context.profile_id
    return [
        {
            "id": spec.id,
            "displayName": spec.display_name,
            "storageKey": spec.storage_key,
            "avatarKey": spec.avatar_key,
            "canDelete": spec.id != registry.default_profile_id,
            "enabled": bool(spec.enabled),
            "createdAt": spec.created_at,
            "isActive": spec.id == active_id,
        }
        for spec in registry.profiles
    ]


def active_profile_row(
    rows: list[dict[str, Any]],
    context: ProfileContext | None,
) -> dict[str, Any]:
    active_id = context.profile_id if context is not None else ""
    for item in rows:
        if str(item.get("id", "")) == active_id:
            return dict(item)
    return {}
