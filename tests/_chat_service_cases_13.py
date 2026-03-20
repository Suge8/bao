# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._chat_service_testkit import *


def test_stop_cancels_inflight_init_future_and_keeps_state_stopped() -> None:
    svc, _model = make_service()
    init_future: concurrent.futures.Future[object] = concurrent.futures.Future()
    submitted: list[str] = []

    def _submit(coro: Coroutine[Any, Any, object]) -> concurrent.futures.Future[object]:
        submitted.append(coro.cr_code.co_name)
        coro.close()
        return init_future

    svc._runner.submit = MagicMock(side_effect=_submit)

    svc.start()
    svc.stop()

    assert submitted == ["_init_hub"]
    assert init_future.cancelled() is True
    assert svc.state == "stopped"
    assert svc.lastError == ""


def test_stale_init_completion_submits_shutdown_when_cancel_cannot_interrupt_running_init() -> None:
    svc, _model = make_service()
    init_future: concurrent.futures.Future[object] = concurrent.futures.Future()
    init_future.set_running_or_notify_cancel()
    shutdown_future: concurrent.futures.Future[object] = concurrent.futures.Future()
    submitted: list[str] = []

    def _submit(coro: Coroutine[Any, Any, object]) -> concurrent.futures.Future[object]:
        submitted.append(coro.cr_code.co_name)
        coro.close()
        return init_future if len(submitted) == 1 else shutdown_future

    svc._runner.submit = MagicMock(side_effect=_submit)

    svc.start()
    svc.stop()
    svc._dispatcher = object()
    svc._agent = object()
    svc._channels = object()
    init_future.set_result((MagicMock(), ["telegram"]))

    assert submitted == ["_init_hub", "_shutdown_hub"]
    assert svc.state == "stopped"


def test_restart_waits_for_shutdown_completion_before_restarting() -> None:
    svc, _model = make_service()
    shutdown_future: concurrent.futures.Future[object] = concurrent.futures.Future()
    restarted_init_future: concurrent.futures.Future[object] = concurrent.futures.Future()
    submitted: list[str] = []

    def _submit(coro: Coroutine[Any, Any, object]) -> concurrent.futures.Future[object]:
        submitted.append(coro.cr_code.co_name)
        coro.close()
        return shutdown_future if len(submitted) == 1 else restarted_init_future

    svc._runner.submit = MagicMock(side_effect=_submit)
    svc._state = "running"
    svc._dispatcher = object()

    svc.restart()

    assert submitted == ["_shutdown_hub"]
    assert svc.state == "stopped"

    shutdown_future.set_result(None)

    assert submitted == ["_shutdown_hub", "_init_hub"]
    assert svc.state == "starting"
