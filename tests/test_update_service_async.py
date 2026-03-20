# ruff: noqa: F403, F405
from __future__ import annotations

from tests._update_service_testkit import *


@pytest.mark.asyncio
async def test_check_async_treats_missing_feed_as_no_update_during_auto_check() -> None:
    from app.backend.update import UpdateService

    class _Config(QObject):
        def get(self, dotpath: str, default: object = None) -> object:
            if dotpath == "ui.update":
                return {
                    "enabled": True,
                    "autoCheck": True,
                    "channel": "stable",
                    "feedUrl": "https://example.com/desktop-update.json",
                }
            return default

    class _Response:
        status_code = 404

        def raise_for_status(self) -> None:
            raise AssertionError("raise_for_status should not be called for 404 feed")

        def json(self) -> object:
            return {}

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb) -> bool:
            return False

        async def get(self, url: str, headers: dict[str, str]) -> _Response:
            assert url == "https://example.com/desktop-update.json"
            assert headers["Accept"] == "application/json"
            return _Response()

    runner = _FakeRunner()
    svc = UpdateService(runner, _Config())
    svc.reloadConfig()
    results: list[tuple[bool, str, object]] = []
    _ = svc._checkFinished.connect(lambda ok, err, rel: results.append((ok, err, rel)))

    with patch("app.backend.update.httpx.AsyncClient", return_value=_Client()):
        await svc._check_async()

    assert results == [(True, "", None)]


@pytest.mark.asyncio
async def test_check_async_treats_missing_feed_as_error_during_manual_check() -> None:
    from app.backend.update import UpdateService

    class _Config(QObject):
        def get(self, dotpath: str, default: object = None) -> object:
            if dotpath == "ui.update":
                return {
                    "enabled": True,
                    "autoCheck": False,
                    "channel": "stable",
                    "feedUrl": "https://example.com/desktop-update.json",
                }
            return default

    class _Response:
        status_code = 404

        def raise_for_status(self) -> None:
            raise AssertionError("raise_for_status should not be called for 404 feed")

        def json(self) -> object:
            return {}

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb) -> bool:
            return False

        async def get(self, url: str, headers: dict[str, str]) -> _Response:
            assert url == "https://example.com/desktop-update.json"
            assert headers["Accept"] == "application/json"
            return _Response()

    runner = _FakeRunner()
    svc = UpdateService(runner, _Config())
    svc.reloadConfig()
    svc._show_check_errors = True
    results: list[tuple[bool, str, object]] = []
    _ = svc._checkFinished.connect(lambda ok, err, rel: results.append((ok, err, rel)))

    with patch("app.backend.update.httpx.AsyncClient", return_value=_Client()):
        await svc._check_async()

    assert results == [
        (False, "Update feed is not published yet (desktop-update.json returned 404).", None)
    ]
