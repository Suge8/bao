"""Shared helpers for ChatMessageModel tests."""

from __future__ import annotations

import importlib
import sys

pytest = importlib.import_module("pytest")
pytestmark = [pytest.mark.unit, pytest.mark.gui]

QtGui = pytest.importorskip("PySide6.QtGui")
QtCore = pytest.importorskip("PySide6.QtCore")
QGuiApplication = QtGui.QGuiApplication
Qt = QtCore.Qt


@pytest.fixture(scope="session")
def qapp():
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    yield app


def new_model():
    from app.backend.chat import ChatMessageModel

    return ChatMessageModel()
