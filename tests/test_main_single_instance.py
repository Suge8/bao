from __future__ import annotations

import sys
import uuid

import pytest
from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtNetwork import QLocalSocket

from app._main_single_instance import (
    DesktopSingleInstanceServer,
    acquire_single_instance_lock,
    activated_existing_instance_notice,
    existing_instance_unresponsive_notice,
    request_existing_instance_activation,
    single_instance_enabled,
    single_instance_server_name,
)


@pytest.fixture(scope="session")
def qapp():
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    yield app


def _process(ms: int) -> None:
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def test_single_instance_server_acknowledges_activation_request(qapp):
    _ = qapp
    server_name = f"bao-test-{uuid.uuid4().hex}"
    activations: list[str] = []
    server = DesktopSingleInstanceServer(server_name, lambda: activations.append("activate"))
    try:
        socket = QLocalSocket()
        socket.connectToServer(server_name)
        assert socket.waitForConnected(1000) is True
        _ = socket.write(b"activate\n")
        _ = socket.flush()
        for _ in range(20):
            _process(20)
            if activations:
                break
        assert activations == ["activate"]
        socket.disconnectFromServer()
    finally:
        server.close()


def test_request_existing_instance_activation_returns_false_when_server_missing() -> None:
    assert request_existing_instance_activation(f"bao-missing-{uuid.uuid4().hex}") is False


def test_acquire_single_instance_lock_blocks_second_claim() -> None:
    server_name = f"bao-test-{uuid.uuid4().hex}"
    first = acquire_single_instance_lock(server_name)
    assert first is not None
    try:
        second = acquire_single_instance_lock(server_name)
        assert second is None
    finally:
        first.unlock()


def test_single_instance_enabled_skips_smoke_and_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BAO_DESKTOP_DISABLE_SINGLE_INSTANCE", raising=False)
    assert single_instance_enabled(smoke_mode=False) is True
    assert single_instance_enabled(smoke_mode=True) is False

    monkeypatch.setenv("BAO_DESKTOP_DISABLE_SINGLE_INSTANCE", "1")
    assert single_instance_enabled(smoke_mode=False) is False


def test_activated_existing_instance_notice_mentions_env_override() -> None:
    notice = activated_existing_instance_notice()
    assert "✨" in notice
    assert "Bao 已在运行" in notice
    assert "Bao is already running" in notice
    assert "BAO_DESKTOP_DISABLE_SINGLE_INSTANCE=1" in notice


def test_single_instance_server_name_uses_prefix() -> None:
    assert single_instance_server_name().startswith("bao-desktop-")


def test_existing_instance_unresponsive_notice_is_bilingual() -> None:
    notice = existing_instance_unresponsive_notice()
    assert "⚠️" in notice
    assert "暂未响应" in notice
    assert "did not respond" in notice
