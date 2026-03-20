# ruff: noqa: F403, F405
from __future__ import annotations

from tests._profile_service_testkit import *


def test_profile_service_refresh_from_workspace_is_async_with_runner(
    qt_app: QCoreApplication,
    fake_home: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _ = qt_app
    import app.backend.profile as profile_module

    shared_workspace = fake_home / ".bao" / "workspace"
    _write_workspace(shared_workspace)

    real_loader = profile_module.load_active_profile_snapshot
    release_loader = threading.Event()
    loader_started = threading.Event()
    loader_threads: list[int] = []

    def blocked_loader(*, shared_workspace: Path):
        loader_threads.append(threading.get_ident())
        loader_started.set()
        assert release_loader.wait(1.0)
        return real_loader(shared_workspace=shared_workspace)

    monkeypatch.setattr(profile_module, "load_active_profile_snapshot", blocked_loader)
    runner = AsyncioRunner()
    runner.start()
    try:
        service = ProfileService(runner)
        active_changes: list[int] = []
        _ = service.activeProfileChanged.connect(lambda: active_changes.append(1))

        started_at = time.perf_counter()
        service.refreshFromWorkspace(str(shared_workspace))
        elapsed = time.perf_counter() - started_at

        assert elapsed < 0.2
        assert loader_started.wait(0.5)
        assert service.activeProfileId == ""
        assert active_changes == []

        release_loader.set()
        _wait_until(lambda: service.activeProfileId == "default")

        assert service.sharedWorkspacePath == str(shared_workspace)
        assert active_changes == [1]
        assert loader_threads and loader_threads[0] != threading.get_ident()
    finally:
        runner.shutdown()


def test_profile_service_sync_action_invalidates_stale_async_refresh(
    qt_app: QCoreApplication,
    fake_home: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _ = qt_app
    import app.backend.profile as profile_module

    shared_workspace = fake_home / ".bao" / "workspace"
    _write_workspace(shared_workspace)

    stale_snapshot = profile_module.load_active_profile_snapshot(shared_workspace=shared_workspace)
    release_loader = threading.Event()
    loader_started = threading.Event()
    loader_finished = threading.Event()

    def blocked_loader(*, shared_workspace: Path):
        loader_started.set()
        assert release_loader.wait(1.0)
        loader_finished.set()
        return stale_snapshot

    monkeypatch.setattr(profile_module, "load_active_profile_snapshot", blocked_loader)
    runner = AsyncioRunner()
    runner.start()
    try:
        service = ProfileService(runner)
        service.refreshFromWorkspace(str(shared_workspace))

        assert loader_started.wait(0.5)
        service.createProfile("Work")

        work_id = str(service.activeProfile["id"])
        assert work_id.startswith("prof-")
        assert service.activeProfile["displayName"] == "Work"

        release_loader.set()
        assert loader_finished.wait(0.5)
        _spin(100)

        assert service.activeProfileId == work_id
        assert service.activeProfile["displayName"] == "Work"
    finally:
        runner.shutdown()


def test_profile_service_coalesces_same_workspace_refresh_while_inflight(
    qt_app: QCoreApplication,
    fake_home: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _ = qt_app
    import app.backend.profile as profile_module

    shared_workspace = fake_home / ".bao" / "workspace"
    _write_workspace(shared_workspace)

    real_loader = profile_module.load_active_profile_snapshot
    release_loader = threading.Event()
    loader_started = threading.Event()
    loader_calls = 0

    def blocked_loader(*, shared_workspace: Path):
        nonlocal loader_calls
        loader_calls += 1
        loader_started.set()
        assert release_loader.wait(1.0)
        return real_loader(shared_workspace=shared_workspace)

    monkeypatch.setattr(profile_module, "load_active_profile_snapshot", blocked_loader)
    runner = AsyncioRunner()
    runner.start()
    try:
        service = ProfileService(runner)
        service.refreshFromWorkspace(str(shared_workspace))
        assert loader_started.wait(0.5)

        service.refreshFromWorkspace(str(shared_workspace))
        _spin(100)

        assert loader_calls == 1

        release_loader.set()
        _wait_until(lambda: service.activeProfileId == "default")
        assert loader_calls == 1
    finally:
        runner.shutdown()
