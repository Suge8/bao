from __future__ import annotations

import concurrent.futures
from typing import Any

from loguru import logger


def cancel_lifecycle_future(future: concurrent.futures.Future[Any] | None) -> bool:
    if future is None or future.done():
        return False
    try:
        return bool(future.cancel())
    except Exception as exc:
        logger.debug("Skip lifecycle future cancel: {}", exc)
        return False


def future_pending(future: concurrent.futures.Future[Any] | None) -> bool:
    return future is not None and not future.done()


def lifecycle_in_progress(service: Any) -> bool:
    return future_pending(service._init_future) or future_pending(service._shutdown_future)


def has_runtime_handles(service: Any) -> bool:
    return any(
        (
            service._dispatcher is not None,
            service._agent is not None,
            service._channels is not None,
            bool(service._background_tasks),
        )
    )


def submit_shutdown_if_needed(service: Any) -> bool:
    if future_pending(service._shutdown_future):
        return True
    if not has_runtime_handles(service):
        return False
    try:
        future = service._runner.submit(service._shutdown_hub())
    except RuntimeError:
        clear_runtime_handles(service)
        return False
    service._shutdown_future = future
    future.add_done_callback(lambda done: handle_shutdown_done(service, done))
    return True


def handle_shutdown_done(service: Any, future: Any) -> None:
    if service._shutdown_future is future:
        service._shutdown_future = None
    try:
        if not future.cancelled():
            future.result()
    except Exception as exc:
        logger.debug("Hub shutdown finished with error: {}", exc)
    finally:
        clear_runtime_handles(service)
        maybe_restart_after_lifecycle(service)


def clear_runtime_handles(service: Any) -> None:
    service._agent = None
    service._channels = None
    service._dispatcher = None
    service._cron = None
    service._heartbeat = None
    service._background_tasks = []
    service._cron_status = {}


def maybe_restart_after_lifecycle(service: Any) -> None:
    if not service._restart_requested or lifecycle_in_progress(service):
        return
    if service._state in ("starting", "running"):
        return
    service._restart_requested = False
    service.start()
