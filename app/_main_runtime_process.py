from __future__ import annotations

import signal
import sys
from dataclasses import dataclass
from typing import Callable

from PySide6.QtWidgets import QApplication


@dataclass(frozen=True)
class SingleInstanceState:
    enabled: bool
    server_name: str = ""
    lock: object | None = None


def prepare_single_instance(
    main_module: object,
    *,
    smoke_mode: bool,
) -> tuple[SingleInstanceState, int | None]:
    if not main_module.single_instance_enabled(smoke_mode=smoke_mode):
        return SingleInstanceState(enabled=False), None
    server_name = main_module.single_instance_server_name()
    lock = main_module.acquire_single_instance_lock(server_name)
    if lock is not None:
        return SingleInstanceState(enabled=True, server_name=server_name, lock=lock), None
    if main_module.request_existing_instance_activation(server_name):
        print(main_module.activated_existing_instance_notice(), file=sys.stderr)
        return SingleInstanceState(enabled=True, server_name=server_name), 0
    print(main_module.existing_instance_unresponsive_notice(), file=sys.stderr)
    return SingleInstanceState(enabled=True, server_name=server_name), 1


def release_single_instance_resources(server: object, lock: object) -> None:
    if server is not None:
        server.close()
    if lock is not None:
        lock.unlock()


def install_sigint_quit_handler(app: QApplication) -> Callable[[], None]:
    previous_handler = signal.getsignal(signal.SIGINT)
    interrupted = False

    def handle_sigint(_signum: int, _frame: object) -> None:
        nonlocal interrupted
        if interrupted:
            return
        interrupted = True
        print(
            "🛑 收到 Ctrl-C，正在优雅退出 Bao… / Ctrl-C received, shutting down Bao gracefully…",
            file=sys.stderr,
        )
        app.quit()

    signal.signal(signal.SIGINT, handle_sigint)

    def restore() -> None:
        signal.signal(signal.SIGINT, previous_handler)

    return restore
