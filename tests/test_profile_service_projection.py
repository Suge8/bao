# ruff: noqa: F403, F405
from __future__ import annotations

from tests._profile_service_testkit import *


def test_profile_service_keeps_registry_projection_consistent(fake_home: Path) -> None:
    shared_workspace = fake_home / ".bao" / "workspace"
    _write_workspace(shared_workspace)

    service = ProfileService()
    service.refreshFromWorkspace(str(shared_workspace))

    assert service.sharedWorkspacePath == str(shared_workspace)
    assert service.activeProfile["id"] == service.activeProfileId
    assert service.activeProfileContext["profileId"] == service.activeProfileId
    assert any(item["isActive"] for item in service.profiles)

    service.createProfile("Work")

    active_profile = service.activeProfile
    work_id = str(active_profile["id"])
    registry_snapshot = service.registrySnapshot
    assert work_id.startswith("prof-")
    assert active_profile["displayName"] == "Work"
    assert active_profile["storageKey"] == "work"
    assert service.activeProfileContext["profileId"] == work_id
    assert service.activeProfileContext["storageKey"] == "work"
    assert registry_snapshot["activeProfileId"] == work_id
    assert registry_snapshot["defaultProfileId"] == "default"
    assert any(
        item["id"] == work_id and item["storage_key"] == "work"
        for item in registry_snapshot["profiles"]
    )
    assert any(item["id"] == work_id and item["isActive"] for item in service.profiles)

    service.deleteProfile(work_id)

    assert service.activeProfileId == "default"
    assert service.activeProfileContext["profileId"] == "default"
    assert service.registrySnapshot["activeProfileId"] == "default"
    assert all(item["id"] != work_id for item in service.profiles)


def test_profile_service_rename_updates_active_projection(fake_home: Path) -> None:
    shared_workspace = fake_home / ".bao" / "workspace"
    _write_workspace(shared_workspace)

    service = ProfileService()
    service.refreshFromWorkspace(str(shared_workspace))
    service.createProfile("Work")
    work_id = str(service.activeProfile["id"])
    service.renameProfile(work_id, "Research")

    assert service.activeProfileId == work_id
    assert service.activeProfile["displayName"] == "Research"
    assert service.activeProfileContext["displayName"] == "Research"
    assert any(
        item["id"] == work_id and item["displayName"] == "Research" and item["isActive"]
        for item in service.profiles
    )


def test_profile_service_update_profile_moves_storage_projection(fake_home: Path) -> None:
    shared_workspace = fake_home / ".bao" / "workspace"
    _write_workspace(shared_workspace)

    service = ProfileService()
    service.refreshFromWorkspace(str(shared_workspace))
    service.createProfile("Work")
    work_id = str(service.activeProfile["id"])
    service.updateProfile(work_id, "Research", "research")

    assert service.activeProfileId == work_id
    assert service.activeProfile["displayName"] == "Research"
    assert service.activeProfile["storageKey"] == "research"
    assert service.activeProfileContext["storageKey"] == "research"
    assert any(
        item["id"] == work_id
        and item["displayName"] == "Research"
        and item["storageKey"] == "research"
        and item["isActive"]
        for item in service.profiles
    )


def test_profile_service_inactive_rename_does_not_emit_active_profile_changed(fake_home: Path) -> None:
    shared_workspace = fake_home / ".bao" / "workspace"
    _write_workspace(shared_workspace)

    service = ProfileService()
    service.refreshFromWorkspace(str(shared_workspace))
    registry, _ = create_profile(
        "Work",
        CreateProfileOptions(shared_workspace=shared_workspace, activate=False),
    )
    work_id = str(registry.profiles[-1].id)
    rename_profile(
        work_id,
        "Research",
        RenameProfileOptions(shared_workspace=shared_workspace),
    )

    profile_changes: list[int] = []
    active_changes: list[int] = []
    _ = service.profilesChanged.connect(lambda: profile_changes.append(1))
    _ = service.activeProfileChanged.connect(lambda: active_changes.append(1))

    service.refreshFromWorkspace(str(shared_workspace))

    assert len(profile_changes) == 1
    assert active_changes == []
