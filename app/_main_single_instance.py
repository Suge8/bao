from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QLockFile, QObject, QTimer, Slot
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtQuick import QQuickWindow

_SINGLE_INSTANCE_ENV = "BAO_DESKTOP_DISABLE_SINGLE_INSTANCE"
_SERVER_PREFIX = "bao-desktop"
_LOCK_STALE_MS = 5000
_ACTIVATE_PAYLOAD = b"activate\n"
_ACTIVATE_ACK = b"ok\n"
_ACTIVATION_RETRY_ATTEMPTS = 10
_ACTIVATION_RETRY_DELAY_S = 0.1
_ACTIVATION_NOTICE = (
    "✨ Bao 已在运行，已激活现有窗口。 / "
    "Bao is already running; activated the existing window.\n"
    "💡 如需并行调试，请设置 BAO_DESKTOP_DISABLE_SINGLE_INSTANCE=1。 / "
    "Set BAO_DESKTOP_DISABLE_SINGLE_INSTANCE=1 to allow another instance."
)
_ACTIVATION_FAILURE_NOTICE = (
    "⚠️ Bao 正在启动或已在运行，但现有实例暂未响应。 / "
    "Bao is already starting or running, but the existing instance did not respond.\n"
    "🕒 请稍等片刻后再试。 / Wait a moment and try again."
)


def single_instance_enabled(*, smoke_mode: bool) -> bool:
    if smoke_mode:
        return False
    return os.getenv(_SINGLE_INSTANCE_ENV, "").strip() != "1"


def single_instance_server_name() -> str:
    uid = os.getuid() if hasattr(os, "getuid") else 0
    return f"{_SERVER_PREFIX}-{uid}"


def activated_existing_instance_notice() -> str:
    return _ACTIVATION_NOTICE


def existing_instance_unresponsive_notice() -> str:
    return _ACTIVATION_FAILURE_NOTICE


def single_instance_lock_path(server_name: str) -> Path:
    return Path(tempfile.gettempdir()) / f"{server_name}.lock"


def acquire_single_instance_lock(server_name: str) -> QLockFile | None:
    lock = QLockFile(str(single_instance_lock_path(server_name)))
    lock.setStaleLockTime(_LOCK_STALE_MS)
    if lock.tryLock(0):
        return lock
    return None


def request_existing_instance_activation(
    server_name: str,
    *,
    timeout_ms: int = 250,
    attempts: int = _ACTIVATION_RETRY_ATTEMPTS,
) -> bool:
    for attempt in range(max(1, attempts)):
        if _request_existing_instance_activation_once(server_name, timeout_ms=timeout_ms):
            return True
        if attempt + 1 < attempts:
            time.sleep(_ACTIVATION_RETRY_DELAY_S)
    return False


def _request_existing_instance_activation_once(server_name: str, *, timeout_ms: int) -> bool:
    socket = QLocalSocket()
    socket.connectToServer(server_name)
    if not socket.waitForConnected(timeout_ms):
        return False
    _ = socket.write(_ACTIVATE_PAYLOAD)
    _ = socket.flush()
    if socket.waitForReadyRead(timeout_ms):
        response = bytes(socket.readAll())
        socket.disconnectFromServer()
        return response in {b"", _ACTIVATE_ACK}
    socket.disconnectFromServer()
    return True


def activate_window(window: object) -> None:
    if not isinstance(window, QQuickWindow):
        return
    show_normal = getattr(window, "showNormal", None)
    if callable(show_normal):
        show_normal()
    else:
        window.show()
    raise_fn = getattr(window, "raise_", None)
    if callable(raise_fn):
        raise_fn()
    window.requestActivate()


class DesktopSingleInstanceServer(QObject):
    def __init__(
        self,
        server_name: str,
        on_activate: Callable[[], None] | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._server_name = server_name
        self._on_activate = on_activate
        self._activation_pending = False
        self._server = QLocalServer(self)
        if not self._server.listen(server_name):
            QLocalServer.removeServer(server_name)
            if not self._server.listen(server_name):
                raise RuntimeError(f"Failed to listen on local server: {server_name}")
        self._server.newConnection.connect(self._on_new_connection)

    def set_activate_callback(self, callback: Callable[[], None]) -> None:
        self._on_activate = callback
        if not self._activation_pending:
            return
        self._activation_pending = False
        self._schedule_activation()

    @Slot()
    def close(self) -> None:
        self._server.close()
        QLocalServer.removeServer(self._server_name)

    @Slot()
    def _on_new_connection(self) -> None:
        while self._server.hasPendingConnections():
            socket = self._server.nextPendingConnection()
            if socket is None:
                return
            socket.readyRead.connect(lambda sock=socket: self._handle_socket(sock))
            socket.disconnected.connect(socket.deleteLater)

    def _handle_socket(self, socket: QLocalSocket) -> None:
        payload = bytes(socket.readAll()).decode("utf-8", errors="ignore").strip()
        if payload != "activate":
            socket.disconnectFromServer()
            return
        self._schedule_or_defer_activation()
        _ = socket.write(_ACTIVATE_ACK)
        _ = socket.flush()
        socket.disconnectFromServer()

    def _schedule_or_defer_activation(self) -> None:
        if self._on_activate is None:
            self._activation_pending = True
            return
        self._schedule_activation()

    def _schedule_activation(self) -> None:
        if self._on_activate is None:
            return
        QTimer.singleShot(0, self._on_activate)
