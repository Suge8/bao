# ruff: noqa: F401
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from unittest.mock import patch

pytest = importlib.import_module("pytest")

QtCore = pytest.importorskip("PySide6.QtCore")
QCoreApplication = QtCore.QCoreApplication
QObject = QtCore.QObject


@pytest.fixture(scope="module", autouse=True)
def qt_app():
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    yield app


class _FakeRunner:
    def __init__(self) -> None:
        self.submitted = 0
        self.last_submitted = None

    def submit(self, coro):  # type: ignore[no-untyped-def]
        self.submitted += 1
        self.last_submitted = coro
        coro.close()
        return None


class _CancelableFuture:
    def __init__(self) -> None:
        self.cancelled = False

    def cancel(self) -> None:
        self.cancelled = True


MINIMAL_CONFIG = """{
  "providers": {
    "openaiCompatible": {
      "apiKey": "sk-test",
      "baseUrl": "https://api.openai.com/v1"
    }
  },
  "agents": {
    "defaults": {
      "model": "openai/gpt-4o"
    }
  }
}"""


__all__ = [name for name in globals() if not (name.startswith("__") and name.endswith("__"))]
